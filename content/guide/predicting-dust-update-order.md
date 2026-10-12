---
title: Predicting Dust Update Order
description: How to work out which machine on a line of redstone dust acts first — the depth-first order of switching on, the single pass of switching off, and the hash behind both — with a script that does the arithmetic.
type: guide
categories: [Guides]
aliases: [Dust update order, Redstone dust update order]
---

**Predicting dust update order** tells which of the machines on one network of
[[Redstone Dust|redstone dust]] acts first when the dust switches on or off.

## How dust sends block updates

Dust that turns on or off sends [[Game Tick#Block updates|block updates]] around
seven positions: itself and its six neighbours. Around each position, the six
blocks beside it get a block update in the order −x, +x, −y, +y, −z, +z. The seven
positions are taken in **hash order**, which depends on their coordinates and on
the table size, both below.
<!-- src: BlockRedstoneWire.java:160-:168 adds the dust and its six neighbours
     to blocksNeedingUpdate, a HashSet (:10); :45-:53 copies it and sends
     World.notifyBlocksOfNeighborChange (World.java:506) around each in turn -->

A block that responds acts at its first block update after the dust powering
it has changed.

## Switching on

Switching on runs depth first. A dust that turns on sends all of its block
updates, and so turns on every dust beyond it, before the dust that turned it on
moves to its next position.
<!-- src: :88-:97 skip the dust that asked, so a dust's own calculation never
     turns the next dust on; the next dust turns on when one of these block
     updates reaches it, inside that block update -->

Which of a dust's seven positions turns on the next dust depends on the shape of
the line:

| Next dust | Turned on by the position of |
|---|---|
| Level with it | the dust itself |
| One step up | the block under the next dust, or the space above this one, whichever comes first |
| One step down | the space above the next dust, or the block under this one, whichever comes first |

Two branches that leave one dust at the same level both turn on from that dust's
own position. The branch on the −x side goes first, then +x, −z and +z, whatever
the hash says.

## Switching off

The whole network drops to 0 in one calculation, before any block update is
sent. The dust the change reached then sends block updates around every
position of the network in one pass: each dust that switched off and its six
neighbours, in hash order. Nothing in that pass is depth first.
<!-- src: calculateCurrentChanges recurses through every dust whose level
     depends on the removed power before :45 updateAndPropagateCurrentStrength
     copies the set; :160 adds positions for every dust that reaches level 0 or 1.
     tested (harness): the game's World.notifyBlocksOfNeighborChange calls for a
     5-dust line switching off were the 27 positions the script predicts, in
     its order -->

## Hash order

Each position gets a number from its coordinates:

```
h = 8976890 × x + 981131 × y + z
```

kept to 32 bits: add or subtract 4,294,967,296 until it lies from 0 to
4,294,967,295. The top half of `h` is then folded into the bottom half: in
hexadecimal, the first four digits of eight are combined with the last four by
exclusive or. The position's **bucket** is the lowest bits of the result, as
many as the table needs: 4 bits for a table of 16, 5 for 32, 6 for 64, and so
on. Positions go in bucket order, from 0 upwards. Positions that share a bucket
go in the order they were added; for one dust, that is the dust, then −x, +x,
−y, +y, −z, +z.
<!-- src: ChunkPosition.java:23 hashCode; java.util.HashMap.hash and
     iteration on Java 8 and later -->

For the dust at (1, 64, 5), `h` is 71,769,279, or `0x04471CBF`. Folding
`0x0447` into `0x1CBF` gives `0x18F8`. Its last hexadecimal digit, 8, is its
bucket in a table of 16; its lowest five bits, 24, are its bucket in a table of
32.

That is too much arithmetic to do by hand for seven positions, let alone a
network. The script below does it.

## Table size

The table belongs to the game, not to a world. It starts at 16 when the game
starts. When one pass holds more than three quarters of the table, the table
doubles, and it never shrinks until the game is closed. Switching on never grows
it, as each pass holds seven positions. Switching off grows it:

| Network switched off | Table afterwards |
|---|---|
| A line of 3 or 4 dust | 32 |
| A line of 5 to 9 | 64 |
| A line of 10 to 15 | 128 |
| A patch of 6 × 6 | 256 |
| A patch of 8 × 8 | 512 |

<!-- src: java.util.HashMap.resize past a load of 0.75; HashMap.clear keeps
     the table; BlockRedstoneWire.blocksNeedingUpdate is one field of the one
     Block.redstoneWire object. A lever powers at most 15 dust of a line.
     tested (harness): the game's table read by reflection matched the script's
     after each of 340 switchings; four copies of one machine fired one way in
     a fresh session and the other way after a 15-dust line 120 blocks away had
     switched off; in singleplayer, the same after the line switched off in the
     previous world -->

A machine that works in a game just started can fail later in the same session,
once a bigger network anywhere has switched off. Only the rules that do not
depend on the hash hold whatever the table: depth first when switching on, and
the side order at a level junction.

## Which machine acts first

1. Find the table size: 16 in a game just started, otherwise what the largest
   network switched off since gave.
2. **Switching on:** find the dust where the paths to the two machines part.
   If both leave it at the same level, the side order decides. Otherwise list
   that dust's seven positions in hash order, and find the first position that
   continues each path, from the table under Switching on. A machine this
   dust powers directly acts at the first of these positions next to the
   machine. The path whose position comes first acts first.
3. **Switching off:** list every position of the network in one pass. The
   machine next to the earliest position acts first.

The head of an extended [[Piston|piston]] passes its block updates on to the
piston, and the top half of a [[Wooden Door|door]] to the bottom half, so a
machine also acts at the first position next to those.

### Example

A floor lever at (−1, 64, 5) powers dust at (0, 64, 5) and (1, 64, 5). From
(1, 64, 5) one branch runs level along +z, through (1, 64, 6) and (1, 64, 7), to
a piston A at (1, 64, 8). The other steps up onto a block at (2, 64, 5) and runs
through (2, 65, 5) and (3, 65, 5) to a piston B at (4, 65, 5).

The level branch turns on from the position of (1, 64, 5) itself, bucket 8 in
a table of 16. The step branch turns on from the block at (2, 64, 5), bucket 9,
or the space at (1, 65, 5), bucket 12. In a game just started, A extends first.
In a table of 32 the buckets are 24, 9 and 28, and B extends first.
<!-- tested (harness): A then B in a fresh session; B then A after a 4-dust line
     elsewhere had switched off -->

```
python dust_order.py --lever -1,64,5 --dust 0..1,64,5 1,64,6..7 2..3,65,5 --watch A=1,64,8 B=4,65,5 --table 32
```

## The script

Save it as `dust_order.py` and run it with Python 3.8 or later; it needs nothing
else. `--set` lists one dust's seven positions in order; the rest model a whole
network, powered by one floor lever, and report the order the watched blocks
act in. `--trace` prints every pass, indented by depth.
<!-- tested (harness, server, two random seeds): 90 random dust networks, flat
     and stepped, branching, 5 to 17 dust, switched on and off with the table
     carried between them: every block update reaching an unmovable piston
     arrived in the order the script predicted, 180 of 180 switchings, and the
     game's table matched the script's throughout. With movable pistons, 89 of
     90 retraction orders matched; the other piston was set off early by a
     retracting piston's head beside it -->

```python
"""Predict the order redstone dust sends block updates in Minecraft Beta 1.7.3.

Describe a build: dust (each standing on a solid block), extra solid blocks, one floor
lever that powers the dust, and the blocks you want to compare ("watched" blocks, such as
pistons or doors). The script switches the lever and reports the order the watched blocks
act in: the first block update each one gets while powered (lever switched on), or while
unpowered (lever switched off).

    python dust_order.py --lever -1,64,0 --dust 0..4,64,0 4,64,1..3 --watch A=5,64,0 B=4,64,4
    python dust_order.py --lever -1,64,0 --dust 0..4,64,0 --watch A=5,64,0/5,65,0 --off
    python dust_order.py --set 10,64,-3          # the order one dust updates its 7 positions in
    python dust_order.py --table 128 ...         # after a big network has switched off

Coordinates are x,y,z; any of them can be a range a..b. Positions in --solid, --dust and
--watch may overlap only where it makes sense: a watched block is not solid.

The ordering assumes Java 8 or later. Java 7 and earlier hash differently.
"""
import argparse
import re
import sys

# ---- java.util.HashSet<ChunkPosition>, as on Java 8 and later -------------------------

def chunk_position_hash(p):
    """ChunkPosition.hashCode: x * 8976890 + y * 981131 + z, as a 32-bit int."""
    x, y, z = p
    return (x * 8976890 + y * 981131 + z) & 0xFFFFFFFF

def bucket(p, table):
    """HashMap's bucket: the hash with its top 16 bits folded into the bottom 16."""
    h = chunk_position_hash(p)
    return (h ^ (h >> 16)) & (table - 1)

class JavaHashSet:
    """Iterates in bucket order, entries of one bucket in the order they were added.
    The table starts at 16, doubles when the set holds more than 3/4 of it, and never
    shrinks: clear() keeps it."""
    def __init__(self, table=16):
        self.table = table
        self.clear()
    def clear(self):
        self.buckets = [[] for _ in range(self.table)]
        self.members = set()
    def add(self, p):
        if p in self.members:
            return
        self.members.add(p)
        b = self.buckets[bucket(p, self.table)]
        b.append(p)
        if len(b) >= 9:
            if self.table < 64:
                self._grow()
            else:
                sys.exit("a bucket holds 9 entries: Java turns it into a tree, which this script does not model")
        if len(self.members) > self.table * 3 // 4:
            self._grow()
    def _grow(self):
        old = [p for b in self.buckets for p in b]
        self.table *= 2
        self.buckets = [[] for _ in range(self.table)]
        for p in old:
            self.buckets[bucket(p, self.table)].append(p)
    def __iter__(self):
        return iter([p for b in self.buckets for p in b])

# ---- the world -------------------------------------------------------------------------

SIDES = [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]  # block update order

def add(p, d):
    return (p[0] + d[0], p[1] + d[1], p[2] + d[2])

class World:
    def __init__(self, solid, dust, lever, watch, table=16):
        self.solid = set(solid)
        self.dust = {p: 0 for p in dust}
        self.lever, self.lever_on = lever, False
        self.watch = dict(watch)                    # position -> (name, its own position)
        self.wires_provide_power = True
        self.set = JavaHashSet(table)               # BlockRedstoneWire.blocksNeedingUpdate
        self.log = []                               # (event, details)
        self.depth = 0

    def normal(self, p):
        return p in self.solid

    def provider_or_wire(self, p):                  # BlockRedstoneWire.isPowerProviderOrWire
        return p in self.dust or p == self.lever

    # isPoweringTo / isIndirectlyPoweringTo; side is the World.java side number, 0-5
    def powering_to(self, p, side):
        if p == self.lever:
            return self.lever_on
        if p in self.dust:
            return self.wires_provide_power and self.dust[p] > 0 and (side == 1 or self.points(p, side))
        return False

    def indirectly_powering_to(self, p, side):
        if p == self.lever:
            return self.lever_on and side == 1          # a floor lever: the block beneath it
        if p in self.dust:
            return self.powering_to(p, side)
        return False

    def points(self, p, side):                       # BlockRedstoneWire.isPoweringTo, sides 2-5
        x, y, z = p
        n, pw = self.normal, self.provider_or_wire
        west = pw((x - 1, y, z)) or (not n((x - 1, y, z)) and pw((x - 1, y - 1, z)))
        east = pw((x + 1, y, z)) or (not n((x + 1, y, z)) and pw((x + 1, y - 1, z)))
        north = pw((x, y, z - 1)) or (not n((x, y, z - 1)) and pw((x, y - 1, z - 1)))
        south = pw((x, y, z + 1)) or (not n((x, y, z + 1)) and pw((x, y - 1, z + 1)))
        if not n((x, y + 1, z)):
            west = west or (n((x - 1, y, z)) and pw((x - 1, y + 1, z)))
            east = east or (n((x + 1, y, z)) and pw((x + 1, y + 1, z)))
            north = north or (n((x, y, z - 1)) and pw((x, y + 1, z - 1)))
            south = south or (n((x, y, z + 1)) and pw((x, y + 1, z + 1)))
        if not (west or east or north or south):
            return 2 <= side <= 5
        return ((side == 2 and north and not west and not east) or (side == 3 and south and not west and not east)
                or (side == 4 and west and not north and not south) or (side == 5 and east and not north and not south))

    def neighbour_sides(self, p):
        x, y, z = p
        return [((x, y - 1, z), 0), ((x, y + 1, z), 1), ((x, y, z - 1), 2), ((x, y, z + 1), 3), ((x - 1, y, z), 4), ((x + 1, y, z), 5)]

    def getting_powered(self, p):                    # World.isBlockGettingPowered
        return any(self.indirectly_powering_to(q, s) for q, s in self.neighbour_sides(p))

    def indirectly_getting_powered(self, p):         # World.isBlockIndirectlyGettingPowered
        return any(self.getting_powered(q) if self.normal(q) else self.powering_to(q, s)
                   for q, s in self.neighbour_sides(p))

    # ---- block updates
    def update_neighbours(self, p, why):             # World.notifyBlocksOfNeighborChange
        for d in SIDES:
            self.block_update(add(p, d), p, why)

    def block_update(self, q, sender, why):
        if q in self.watch:
            name, home = self.watch[q]
            self.log.append(("update", name, home, sender, why, self.indirectly_getting_powered(home)))
        if q in self.dust:
            self.dust_update(q)

    def dust_update(self, p):                        # updateAndPropagateCurrentStrength
        self.recalculate(p, p)
        entries = list(self.set)
        self.log.append(("set", p, entries, self.set.table, self.depth))
        self.set.clear()
        self.depth += 1
        for e in entries:
            self.update_neighbours(e, f"position {entries.index(e) + 1} of {len(entries)} that dust {p} updates around")
        self.depth -= 1

    def recalculate(self, p, src):                   # calculateCurrentChanges
        x, y, z = p
        old = self.dust[p]
        self.wires_provide_power = False
        powered = self.indirectly_getting_powered(p)
        self.wires_provide_power = True
        level = lambda q, cur: max(cur, self.dust[q]) if q in self.dust else cur
        sides = [(x - 1, z), (x + 1, z), (x, z - 1), (x, z + 1)]
        new = 0
        if powered:
            new = 15
        else:
            for a, c in sides:
                if (a, y, c) != src:
                    new = level((a, y, c), new)
                if self.normal((a, y, c)) and not self.normal((x, y + 1, z)):
                    if (a, y + 1, c) != src:
                        new = level((a, y + 1, c), new)
                elif not self.normal((a, y, c)) and (a, y - 1, c) != src:
                    new = level((a, y - 1, c), new)
            new = max(new - 1, 0)
        if old == new:
            return
        self.dust[p] = new
        below = new
        for a, c in sides:
            for q in ((a, y, c), (a, y + 1 if self.normal((a, y, c)) else y - 1, c)):
                below = max(self.dust[p] - 1, 0) if self.dust[p] > 0 else 0
                if q in self.dust and self.dust[q] != below:
                    self.recalculate(q, p)
        if old == 0 or below == 0:
            for d in [(0, 0, 0)] + SIDES:
                self.set.add(add(p, d))

    def switch_lever(self, on):                      # BlockLever.blockActivated
        self.lever_on = on
        self.update_neighbours(self.lever, "the lever switching")
        self.update_neighbours(self.lever, "the lever switching")
        self.update_neighbours(add(self.lever, (0, -1, 0)), "the lever switching")

# ---- command line ----------------------------------------------------------------------

def positions(text):
    parts = text.lstrip("\0").split(",")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"not x,y,z: {text}")
    ranges = []
    for v in parts:
        if ".." in v[1:]:
            i = v.index("..", 1)
            a, b = int(v[:i]), int(v[i + 2:])
            ranges.append(range(min(a, b), max(a, b) + 1))
        else:
            ranges.append([int(v)])
    return [(x, y, z) for x in ranges[0] for y in ranges[1] for z in ranges[2]]

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dust", nargs="*", default=[], help="dust positions; each stands on a solid block")
    ap.add_argument("--solid", nargs="*", default=[], help="extra solid (full, opaque) blocks")
    ap.add_argument("--lever", help="a floor lever powering the dust; it stands on a solid block")
    ap.add_argument("--watch", nargs="*", default=[],
                    help="NAME=x,y,z blocks to compare, such as pistons; NAME=x,y,z/x,y,z for one that also "
                         "takes block updates at a second position, such as an extended piston's head")
    ap.add_argument("--off", action="store_true", help="switch the lever off instead of on")
    ap.add_argument("--table", type=int, default=16, help="the shared set's table size (16 in a fresh game)")
    ap.add_argument("--set", nargs="*", help="print the order one dust updates its 7 positions in, and stop")
    ap.add_argument("--trace", action="store_true", help="print every set dust builds, in order")
    argv = sys.argv[1:] if argv is None else argv
    # let negative coordinates through: argparse would take "-1,64,0" for an option
    a = ap.parse_args(["\0" + t if re.match(r"-\d", t) else t for t in argv])

    if a.set:
        for text in a.set:
            for p in positions(text):
                s = JavaHashSet(a.table)
                for d in [(0, 0, 0)] + SIDES:
                    s.add(add(p, d))
                names = {add(p, d): n for d, n in zip([(0, 0, 0)] + SIDES, ["dust", "-x", "+x", "-y", "+y", "-z", "+z"])}
                print(f"dust at {p}, table {s.table}:")
                for i, e in enumerate(s):
                    print(f"  {i + 1}. {names[e]:>4} {e}  bucket {bucket(e, s.table)}")
        return

    dust = [p for t in a.dust for p in positions(t)]
    lever = positions(a.lever)[0] if a.lever else None
    if not dust or lever is None:
        ap.error("give --dust and --lever (or --set)")
    solid = {add(p, (0, -1, 0)) for p in dust} | {add(lever, (0, -1, 0))}
    solid |= {p for t in a.solid for p in positions(t)}
    watch = {}
    for t in a.watch:
        name, _, where = t.lstrip("\0").partition("=")
        home, _, also = where.partition("/")
        p = positions(home)[0]
        watch[p] = (name, p)
        if also:
            watch[positions(also)[0]] = (name, p)
    w = World(solid, dust, lever, watch, a.table)
    if a.off:
        w.switch_lever(True)
        w.log.clear()
    w.switch_lever(not a.off)

    if a.trace:
        for ev in w.log:
            if ev[0] == "set" and ev[2]:
                print("  " * ev[4] + f"dust {ev[1]} updates around {len(ev[2])} positions (table {ev[3]}): "
                      + " ".join(f"{e[0]},{e[1]},{e[2]}" for e in ev[2]))
    want = not a.off
    acted, order = set(), []
    for ev in w.log:
        if ev[0] == "update" and ev[1] not in acted and ev[5] == want:
            acted.add(ev[1])
            order.append(ev)
    print(f"dust levels: " + " ".join(f"{p[0]},{p[1]},{p[2]}={v}" for p, v in w.dust.items()))
    print(f"the set's table is now {w.set.table}")
    print("watched blocks act in this order (their first block update while " + ("powered):" if want else "unpowered):"))
    for i, ev in enumerate(order):
        print(f"  {i + 1}. {ev[1]} at {ev[2]}: block update from {ev[3]}, {ev[4]}")
    for p, (n, home) in watch.items():
        if n not in acted and p == home:
            print(f"  {n} at {p} never acts")

if __name__ == "__main__":
    main()
```

## Limits

- The order assumes Java 8 or later. Java 7 and earlier fold the hash another
  way and add positions to the front of a bucket, so the order differs.
- The script models dust on full solid blocks, one floor lever, and blocks that
  act on dust's block updates. It does not model other power sources,
  [[Redstone Torch|torches]] or [[Redstone Repeater|repeaters]] in the line, or
  what the watched blocks do when they act.
- A piston that pushes while the dust is switching on can switch on dust beside
  it inside its push. Pistons of the same kind miss every block update sent
  during that push; see [[Piston#Power]].
