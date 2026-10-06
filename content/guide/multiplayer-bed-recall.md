---
title: Multiplayer Bed Recall
description: Build a minecart route that carries a sleeping player away, then returns them with the stock Leave Bed button.
type: guide
categories: [Guides]
---

**Multiplayer bed recall** returns a transported, sleeping player to their original [[Bed|bed]] through the stock **Leave Bed** button.
<!-- src: minecraft_server/EntityPlayer.java:592-607 wakeUpPlayer;
     EntityPlayerMP.java:248-257; GuiSleepMP.java:36-49 -->

## Requirements

- A stock dedicated multiplayer server and two players: the sleeper and an awake helper.
- Night in the [[Overworld]].
- An intact, loaded [[Bed|bed]] with a clear space beside it for returning.
- A safe, level [[Minecart|minecart]] route and a walkway for the helper.

The sleeper stays asleep for the entire outward trip. This is not a return button for an awake player. Each trip requires entering the bed again.
<!-- src: Minecraft.java:972-979; GuiSleepMP.java:36-49;
     EntityClientPlayerMP.java:38-52 -->

The helper prevents the night from skipping. The bed's [[Chunk|chunk]] must also stay loaded. The short route below was tested with `view-distance=5`; for a longer route, leave a third awake player at the bed and use a separate helper at the destination.
<!-- src: minecraft_server/World.java:1502-1515,2082-2099;
     EntityPlayer.java:63-68,624-625;
     ChunkProviderServer.java:84-90; PlayerManager.java:11-38 -->

## Building the tested route

Materials: one [[Bed|bed]], one empty [[Minecart|minecart]], 53 [[Rail|rails]], 12 [[Powered Rail|powered rails]], eight [[Redstone Torch|redstone torches]], one [[Lever|lever]], nine [[Torch|torches]], and solid blocks for the floor and backstop.

These coordinates reproduce the test build. X increases east; Z increases south. The floor is at Y=99 and all track components are at Y=100. The whole build can be translated to another level site.

| Part | Position | Placement |
|---|---|---|
| Spawn landing | X=−2–17, Z=−2–17, Y=99 | Solid platform covering the randomized spawn area of the prepared world |
| Floor | X=5–76, Z=5–12, Y=99 | Solid, level platform; keep the space above clear |
| Backstop | X=7, Z=8 | One solid block immediately west of the starting rail |
| Starting rail | X=8, Z=8 | East–west powered rail, initially unpowered |
| Launch lever | X=8, Z=7 | On the floor beside the starting rail, initially off |
| Boosters | X=12, 20, 28, 36, 44, 52, 60, 68; Z=8 | East–west powered rails |
| Booster power | Same X as each booster; Z=7 | Redstone torch on the floor beside each booster |
| Brakes | X=70–72, Z=8 | Three east–west powered rails with no power source |
| Connecting track | Remaining positions from X=9–69, Z=8 | Ordinary rails |
| Bed | Foot at X=8, Z=10; pillow at X=9, Z=10 | Bed pointing east, with a clear floor around it |
| Lighting | X=8, 16, 24, 32, 40, 48, 56, 64, 72; Z=11 | Ordinary torches on the floor |

The spawn landing is needed only for the elevated prepared world. A route built on accessible ground does not need it.
<!-- src: minecraft_server/EntityPlayerMP.java:23-38 (randomized first-login spawn) -->

```text
Departure, top view                          east →

Z=6       helper's walkway → → → → → → → → → →
Z=7           L           T
Z=8       #   P   r   r   r   P   r   r   r ...
Z=9           .   .
Z=10          F   H
Z=11          t
          X=7 8   9  10  11  12

# backstop       L launch lever       T redstone torch
P powered rail   r ordinary rail      . clear return space
F bed foot       H bed pillow         t ordinary torch
```

The ordinary rail after the last booster separates it from the brakes. Keep those brakes unpowered. Keep the starting rail unpowered until the sleep screen opens.
<!-- src: EntityMinecart.java:252-263,386-406;
     test: tools/experiments/bed-recall.py, b173harness 0.1.0, seed 1;
     notified block placement, both client block views checked against server -->

## Using the recall

1. Place the empty [[Minecart|minecart]] on the starting powered rail at X=8, Z=8. Leave the launch lever off.
2. The sleeper right-clicks the cart to mount it. Wait about a second for mounting to settle.
3. Still mounted, the sleeper looks at the [[Bed|bed]] and right-clicks its pillow. **Leave Bed** must appear before departure. If the first click does nothing, click again while the cart remains stopped.
4. The helper switches on the launch lever. The cart carries the sleeper east. The sleeper does not press **Leave Bed** yet.
5. The helper follows the walkway to the brake section. Wait until the cart stops.
6. From beside the track, the helper aims at the cart and attacks it until it disappears. **Stop attacking immediately when the cart breaks.** Do not hit the sleeper.
7. The helper confirms that the cart is gone. The sleeper waits a moment for dismounting to arrive, then clicks **Leave Bed**. The sleeper returns to the clear space beside the original bed.
8. Switch the launch lever off and replace the cart before another trip. The helper can collect the dropped cart at the destination.

<!-- src: minecraft_server/ItemMinecart.java:12-20;
     EntityPlayer.java:512-570 goToSleep (does not dismount);
     NetServerHandler.java:59-71,308-310 (mount handshake and interaction);
     Entity.java:910-911 updateRiderPosition;
     EntityMinecart.java:70-82 (cart destruction dismounts the rider);
     EntityPlayer.java:337-344 (damage wakes a sleeper);
     EntityPlayerMP.java:248-265; NetServerHandler.java:447-455 -->
<!-- test: tools/experiments/bed-recall.py, seed 1, two real clients;
     stock input for cart placement/mounting, bed/lever activation, helper walk,
     cart attacks and GuiSleepMP button. Health unchanged through the recall. -->

## Failure conditions

| Symptom or event | Cause or action |
|---|---|
| Bed or lever does nothing near world spawn | The server's spawn protection blocks the interaction. Give both players operator permission or build outside the protected area. |
| Cart launches before the sleep screen opens | Switch off the launch lever and check that nearby redstone does not power the starting rail. |
| Sleeper wakes before pressing the button | Damage, daylight or loss of the original bed ends sleep. Check for an extra attack after the cart breaks. |
| Button closes the screen but the player stays at the destination | The player is still mounted. Destroy the cart before pressing the button. |
| Original bed breaks or its chunk unloads | The stored bed cannot supply a return position. Keep it intact and loaded. |
| Helper also sleeps or disconnects | The remaining players can complete sleep and advance to morning. Keep an awake helper connected. |
| Server restarts or sleeper reconnects | The transported sleep state does not survive loading the player from disk. Start a new trip. |

<!-- src: minecraft_server/NetServerHandler.java:295-310;
     EntityPlayer.java:63-68,288-298,337-344,592-625;
     World.java:1502-1515,2082-2099;
     test: tools/experiments/bed-recall.py --keep-mounted, seed 1:
     server X=71.11207667940654 and client X=71.09375 after Leave Bed,
     sleep screen closed, rider still attached, health unchanged -->

## Verification and prepared world

The route was tested with two real client JVMs and the dedicated server through **b173harness 0.1.0**, using Mojang's game jars under the Babric loader. The harness prepared the blocks, initial positions and cart inventory. All operating steps used the clients' normal mouse and keyboard input. No sleep, wake or movement packets were injected, and no T3 behaviour deviations were enabled.

| Check | Server position (X, Z) | Client position (X, Z) |
|---|---|---|
| Asleep at the brakes | 71.112, 8.5 | 71.094, 8.5 |
| Cart destroyed, still asleep | 71.112, 8.5 | 71.112, 8.5 |
| After clicking Leave Bed | 8.5, 9.5 | 8.5, 9.5 |

Health stayed unchanged. A separate intact-cart control closed the sleep screen but left the rider at the destination. The tested return distance was about 63 blocks; longer routes and bed-chunk unloading were not runtime-tested.
<!-- test: tools/experiments/bed-recall.py, 2026-10-06, seed 1;
     Fabric Loader 0.19.3, Temurin 17.0.19+10, vanilla generator,
     3 frames/tick, 854x480, lockstep, deviations: none.
     Client SHA-1: 43db9b498cb67058d2e12d394e6507722e71bb45;
     server SHA-1: 2f90dc1cb5ca7e9d71786801b307390a67fcf954.
     Positive run: server 97 actions, 1 flagged (initial inventory),
     sleeper 8 input actions, helper 9 input actions; zero caught exceptions.
     Global summaries counted 49 server and 1 sleeper-client writes to
     EmptyChunk; the active-fixture subscription found no lost server writes.
     Control: server 96 actions, 1 flagged (initial inventory), sleeper 8,
     helper 4; zero caught exceptions; 45 server / 1 helper-client writes
     lost globally; no lost server writes in the active fixture.
     All position/mount/health assertions passed. -->

With the separate [b1.7.3Harness](https://github.com/LochlainnB/b1.7.3Harness) installed, run these commands from the wiki repository:

```bash
b173 run tools/experiments/bed-recall.py -- --output-dir /tmp/bed-recall
b173 run tools/experiments/bed-recall.py -- --keep-mounted
```

The output directory must not already exist. It receives `bed-recall-world.zip`, screenshots and `result.json`. On headless Linux, the client needs Xvfb, Mesa and the `xrandr` utility (`x11-xserver-utils` on Debian).

To use the prepared world on a stock server:

1. Stop the server and back up its existing world. Extract the ZIP's `world` directory into a fresh server directory; do not overwrite a world in use.
2. Set `level-name=world` and `view-distance=5` or greater in `server.properties`. The test used `spawn-monsters=false` and `spawn-animals=false`; a normal Survival build needs protection from mobs.
3. Start the Beta 1.7.3 server. In its console, run `op PlayerA` and `op PlayerB`, replacing the names with the two players' names. The supplied build is inside spawn protection.
4. Both players join using stock clients. The cart, bed and launch lever are beside spawn, at the coordinates above. Use the instructions starting at mounting the cart. If morning has arrived, wait for night or run `time set 14000` in the server console.

The ZIP contains only the generated world, not game jars, mods or saved player accounts.
