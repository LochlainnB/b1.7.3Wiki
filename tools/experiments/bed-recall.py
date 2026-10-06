"""Test stock-input multiplayer bed recall; optionally export the ready-to-use world.

Run from the wiki root with the separate b1.7.3Harness installed:
    b173 run tools/experiments/bed-recall.py -- --output-dir /tmp/bed-recall
    b173 run tools/experiments/bed-recall.py -- --keep-mounted

World construction, initial inventory and positioning are fixture setup. After
arming, both real clients use virtual mouse/keyboard input, not injected packets
or direct sleep, wake, damage, mount or movement calls. No T3 deviations are used.
"""

import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import b173harness as b173


def wait_for(server, condition, label, ticks=200):
    for _ in range(ticks):
        if condition():
            return
        server.step(1)
    raise AssertionError(f"Timed out: {label}")


def aim(server, client, pos):
    # Frame 1 starts before the paused tick boundary; frame 2 is the next render.
    client.input.look_at(pos, frame=2)
    server.step(3)


def snapshot(server, client):
    local = client.state()
    remote = next(p for p in server.players_list() if p["name"] == "Sleeper")
    entity = server.world().entity(remote["id"])
    return {
        "htick": server.htick,
        "server_pos": entity["pos"],
        "client_pos": local["player"]["pos"],
        "server_riding": entity["riding"],
        "client_riding": local["player"]["riding"],
        "health": entity["health"],
        "screen": local["screen"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="new directory for a world ZIP, screenshots and results")
    parser.add_argument("--keep-mounted", action="store_true", help="negative control: leave the cart intact")
    args = parser.parse_args()
    out = args.output_dir
    if out:
        out.mkdir(parents=True, exist_ok=False)

    properties = {"spawn-monsters": "false", "spawn-animals": "false", "view-distance": "5"}
    with b173.server(seed=1, spawn=(8, 100, 8), nether=False, properties=properties) as server:
        world = server.world()
        # Drain the fresh world's generation backlog before clients receive it.
        server.step(400)
        settings = {"renderDistance": "1", "guiScale": "2"}
        sleeper = server.client("Sleeper", settings=settings)
        helper = server.client("Helper", settings=settings)
        server.step(60)

        # Vanilla randomises first login within 10 blocks of spawn. Catch every
        # possible start on the exported world's elevated departure platform.
        world.fill((-2, 99, -2), (17, 99, 17), 1, mode="notify")
        world.fill((-2, 100, -2), (17, 104, 17), 0, mode="notify")
        world.fill((5, 99, 5), (76, 99, 12), 1, mode="notify")
        world.fill((5, 100, 5), (76, 104, 12), 0, mode="notify")
        # East-facing bed: foot, then head. Notify only after both halves exist.
        world.set((8, 100, 10), 26, 3)
        world.set((9, 100, 10), 26, 11, mode="notify")
        world.set((7, 100, 8), 1, mode="notify")
        boosters = range(12, 69, 8)
        for x in range(8, 73):
            powered = x == 8 or x in boosters or x >= 70
            world.set((x, 100, 8), 27 if powered else 66, 1, mode="notify")
        world.set((8, 100, 7), 69, 5, mode="notify")
        for x in boosters:
            world.set((x, 100, 7), 76, 5, mode="notify")
        for x in range(8, 73, 8):
            world.set((x, 100, 11), 50, 5, mode="notify")

        box = ((-2, 99, -2), (76, 101, 17))

        def synced():
            return all(not v["differences"] and not v["unloaded_chunks"]
                       for v in server.compare(box)["clients"].values())

        wait_for(server, synced, "both clients receive the complete build", ticks=400)
        sleeper.teleport((8.5, 100, 9.5))
        helper.teleport((8.5, 100, 6.5))
        server.step(20)
        server.give("Sleeper", 0, 328)
        wait_for(server, lambda: sleeper.world().entity_nbt(sleeper.state()["player"]["id"])["plain"]
                 ["Inventory"] != [], "minecart inventory reaches the client")
        aim(server, sleeper, (8.5, 100.05, 8.5))
        assert sleeper.state()["target"]["block"] == [8, 100, 8]
        sleeper.input.click("use")
        wait_for(server, lambda: bool(sleeper.world().entities(cls="Minecart")), "placed cart reaches the client")
        cart = world.entities(cls="Minecart")[0]
        cart_id = cart["id"]
        server.step(10)
        server.console("time set 14000")
        server.step(3)

        if out:
            world.save_all()
            save = server.dir / "server" / "world"
            with ZipFile(out / "bed-recall-world.zip", "x", compression=ZIP_DEFLATED) as archive:
                for file in sorted(save.rglob("*")):
                    if file.is_file() and (file.name == "level.dat" or file.suffix == ".mcr"):
                        archive.write(file, Path("world") / file.relative_to(save))
            aim(server, helper, (12, 100.3, 9))
            helper.shot(out / "departure.png")
            server.step(1)

        server.packets.enable(full=True)
        # Ignore unrelated generation writes outside the test platform.
        lost = server.events.subscribe("block.write_lost", box=box)
        observations = {}
        aim(server, sleeper, (8.5, 100.75, 8.5))
        assert sleeper.state()["target"]["entity"] == cart_id
        sleeper.input.click("use")
        wait_for(server, lambda: sleeper.state()["player"]["riding"] == cart_id, "mount")
        server.step(20)  # let the vanilla mount teleport handshake finish
        aim(server, sleeper, (9.5, 100.4, 10.5))
        assert sleeper.state()["target"]["block"] == [9, 100, 10]
        sleeper.input.click("use")
        wait_for(server, lambda: (sleeper.state()["screen"] or "").endswith("GuiSleepMP"), "sleep UI")
        server.step(10)
        observations["armed"] = snapshot(server, sleeper)
        assert observations["armed"]["server_riding"] == cart_id
        health = observations["armed"]["health"]

        aim(server, helper, (8.5, 100.2, 7.5))
        helper.input.click("use")
        wait_for(server, lambda: world.block((8, 100, 8))["meta"] == 9, "launch lever")
        helper.input.look(-90, 0, frame=2)
        server.step(3)
        helper.input.hold("W", 290)
        server.step(290)
        server.step(10)  # stop walking and let interpolation settle
        observations["away"] = snapshot(server, sleeper)
        away = observations["away"]
        assert 70 < away["server_pos"][0] < 72, away
        assert 70 < away["client_pos"][0] < 72, away
        assert (away["screen"] or "").endswith("GuiSleepMP"), away
        assert away["server_riding"] == away["client_riding"] == cart_id, away
        assert away["health"] == health, away

        if not args.keep_mounted:
            aim(server, helper, world.entity(cart_id)["pos"])
            for _ in range(10):
                if not world.entities(cls="Minecart"):
                    break
                assert helper.state()["target"].get("entity") == cart_id
                helper.input.click("attack")
                server.step(3)
            assert not world.entities(cls="Minecart"), "cart was not destroyed"
            wait_for(server, lambda: sleeper.state()["player"]["riding"] is None, "dismount reaches the client")
            observations["detached"] = snapshot(server, sleeper)
            detached = observations["detached"]
            assert detached["server_pos"][0] > 70 and detached["client_pos"][0] > 70, detached
            assert detached["health"] == health, "helper hit the sleeper"
            assert (detached["screen"] or "").endswith("GuiSleepMP"), detached

        if out:
            sleeper.shot(out / "before-recall.png")
            server.step(1)
        # Default 854x480 window, GUI scale 2: centre of the stock Leave Bed button.
        assert sleeper.state()["display"] == [854, 480]
        sleeper.input.cursor_gui(213, 210)
        sleeper.input.click("attack")
        wait_for(server, lambda: sleeper.state()["screen"] is None, "Leave Bed closes sleep UI")
        server.step(30)
        observations["after"] = snapshot(server, sleeper)
        after = observations["after"]
        assert after["health"] == health, after
        if args.keep_mounted:
            assert after["server_pos"][0] > 70 and after["client_pos"][0] > 70, after
            assert after["server_riding"] == after["client_riding"] == cart_id, after
        else:
            assert abs(after["server_pos"][0] - 8.5) < 0.1, after
            assert abs(after["server_pos"][2] - 9.5) < 0.1, after
            assert abs(after["client_pos"][0] - 8.5) < 0.1, after
            assert abs(after["client_pos"][2] - 9.5) < 0.1, after
            assert after["server_riding"] is None and after["client_riding"] is None, after
        wakes = [p for p in server.packets.log()
                 if p["jvm"] == sleeper.role and p["event"] == "queued"
                 and p.get("class") == "Packet19EntityAction" and p["fields"]["state"] == 3]
        assert len(wakes) == 1, wakes
        assert not list(lost), "a block write was lost inside the test build"
        summaries = {role: server.summary(on=role) for role in server.jvms}
        assert all(v["exceptions_caught"] == 0 for v in summaries.values()), summaries
        result = {"header": server.header, "keep_mounted": args.keep_mounted,
                  "observations": observations, "wake_packets": wakes, "summaries": summaries}
        print(json.dumps(observations, indent=2), flush=True)
        if out:
            sleeper.shot(out / "after-recall.png")
            server.step(1)
            (out / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print("PASS: leaving the bed while mounted does not give a lasting recall" if args.keep_mounted
              else "PASS: stock Leave Bed recalls an undamaged, detached sleeper on both server and client", flush=True)


if __name__ == "__main__":
    main()
