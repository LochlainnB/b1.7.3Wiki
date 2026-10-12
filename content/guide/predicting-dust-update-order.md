---
title: Predicting Dust Update Order
description: How to work out which of two machines on one line of redstone dust acts first — the update list each dust works through, how switching on and off differ, and how to find the list's order — with a script that does the arithmetic.
type: guide
categories: [Guides]
aliases: [Dust update order, Redstone dust update order, Update list]
---

**Predicting dust update order** works out which of two machines on one
network of [[Redstone Dust|redstone dust]] acts first when the dust switches on
or off.

## The update list

When a dust turns on or off, it tells the blocks around it by sending
[[Game Tick#Block updates|block updates]]. It does this in two steps:

1. It makes an **update list** of seven positions: its own position, and the six
   positions touching it, above, below and on its four sides.
2. It goes down the list one position at a time. At each position, it sends a
   block update to each of the six blocks touching that position, always in the
   same order: −x, +x, −y, +y, −z, +z.

The two steps have different orders:

- **The seven positions on the list** come in an order that depends on where the
  dust is. Each position gets a number from its coordinates, its **bucket**, and
  the list runs from the lowest bucket to the highest.
- **The six block updates sent around one position** always go −x, +x, −y, +y,
  −z, +z.

The example at the end of this page shows one dust's whole list.
<!-- src: BlockRedstoneWire.java:160-:168 put the dust and its six neighbours
     in blocksNeedingUpdate, a HashSet (:10); :45-:53 copy it and call
     World.notifyBlocksOfNeighborChange (World.java:506) for each in turn -->

A block can touch several positions on one list, so one dust can send it several
block updates. A block that responds acts on the first of them that arrives
after its power has changed.

## Reaching the next dust

To find when a dust turns on the dust next to it, find which positions on the
first dust's list touch the next dust:

| The next dust is | It touches these positions on the first dust's list |
|---|---|
| On the same level | only the first dust's own position |
| One block up, on top of the block beside the first dust | the block under the next dust, and the space above the first dust |
| One block down, beside the block under the first dust | the space above the next dust, and the block under the first dust |

A dust on the same level is reached when the list gets to the first dust's own
position, as the six block updates sent around that position include one to it.

The first dust's position is not only on its own list. Every dust beside it has
that position on its list too. So a dust on the same level can also be reached
from the list of another dust beside the first dust, whichever list gets to the
first dust's position sooner. Where a line splits, below, shows when that
matters.

A dust one block up or down is reached at whichever of its two positions comes
first on the list. That can be before or after the first dust's own position.
So the buckets decide whether a branch that steps up or down goes before or
after a branch on the same level.

## Switching on

Switching on runs **depth first**. When a block update from one dust turns on a
second dust, the second dust works through its whole update list at once. The
first dust waits, and sends its next block update only when the second dust has
finished.

For a straight line of three dust, A, B and C, powered from A's end:

1. A turns on, and starts down its update list.
2. When A's list reaches A's own position, A sends a block update to B, and B
   turns on.
3. Before A sends anything else, B goes down its whole update list. When B's
   list reaches B's own position, B sends a block update to C, and C turns on.
4. C goes down its whole list.
5. B finishes the rest of its list.
6. A finishes the rest of its list.

Power therefore runs to the far end of one branch before the dust where two
branches part sends another block update.

## Where a line splits

A **junction** is a dust where a line splits into branches. This section covers
a junction where the first dust of each branch sits right beside the junction,
on the same level: a T or a cross of dust, with no step up or down between the
junction and its branches.

When the junction turns on, its list reaches its own position. The block updates
sent around that position go −x, +x, −y, +y, −z, +z, so the branch on the
earliest of the sides −x, +x, −z, +z turns on first. Call it the first branch.

The first branch does not always fire first. Its first dust now works through
its own update list, and the junction's position is on that list. If the list
reaches the junction's position before the dust's own position, the block
updates sent around the junction reach the other branches and turn them on.
Each runs to its end before the first branch goes any further.

Take dust at x = 0, 1 and 2, all on one level, with power reaching the middle
dust and branches carrying on from both ends:

1. The middle dust's list reaches its own position. Its −x block update turns
   on the dust at x = 0.
2. The dust at x = 0 works through its own list, which includes the middle
   dust's position.
3. If the middle dust's position comes first on that list, the block updates
   sent around it turn on the dust at x = 2, and the +x branch fires to its end.
4. Only then does the x = 0 dust's list reach its own position, and the −x
   branch fires.

If the x = 0 dust's own position comes first on its list instead, the −x branch
fires first.

To compare two branches leaving a junction on one level, take the branch on the
earlier side and look at its first dust's list. If the dust's own position comes
before the junction's position, that branch fires first. If the junction's
position comes first, the other branch does. With three or four branches, the
same check repeats at the first dust of each branch in turn, and the script
follows it.
<!-- tested (harness, server): dust at x = 0 to 6, powered at x = 3 by a floor
     lever beside it, with a piston beyond each end, at 231 places: the +x
     piston extended first at 146, the -x piston at 85, and the script
     predicted all 231 -->
<!-- src: BlockRedstoneWire.java:88-:97 skip the dust that asked, so a dust's
     own calculation never turns the next dust on: the next dust turns on when
     a block update reaches it, and handles its whole list inside that block
     update -->

## Switching off

Switching off does not run depth first:

1. When the power goes, every dust it fed drops to 0 at once, before any block
   update is sent.
2. The dust the change reached first then makes one update list for the whole
   network: every dust that switched off, and every position touching one.
3. It works through that one list, from the lowest bucket up.

The list covers the whole network, so a position at the far end can come before
one next to the power. The machine whose touching position comes earliest on the
list acts first.
<!-- src: calculateCurrentChanges recurses through every dust whose level
     depends on the lost power before :45 updateAndPropagateCurrentStrength
     copies the set; :160 adds positions for every dust that reaches level 0 or 1.
     tested (harness): the game's World.notifyBlocksOfNeighborChange calls for a
     5-dust line switching off were the 27 positions the script predicts, in
     its order -->

## Finding the buckets

A position's bucket comes from its coordinates in four steps:

1. Work out `h = 8976890 × x + 981131 × y + z`.
2. Keep it to 32 bits: add or subtract 4,294,967,296 until `h` is between 0 and
   4,294,967,295.
3. Write `h` as 8 hexadecimal digits, and combine the first four with the last
   four by exclusive or: write both halves in binary, and set each bit of the
   result to 1 where exactly one of the two halves has a 1.
4. The bucket is the lowest bits of the result. How many bits depends on the
   table size: 4 bits for a table of 16 buckets, 5 for 32, 6 for 64, and so on.

Positions with the same bucket keep the order they were added in. For one dust
that is its own position, then −x, +x, −y, +y, −z, +z.
<!-- src: ChunkPosition.java:23 hashCode; java.util.HashMap.hash and its
     iteration on Java 8 and later -->

For the dust at (6, 64, 5), `h` is 116,653,729, which is `06F3 FEA1` in
hexadecimal. `06F3` combined with `FEA1` gives `F852`. With 16 buckets, the
bucket is the last digit, 2. With 32 buckets it is the lowest five bits: `52` is
`0101 0010` in binary, and its lowest five bits, `10010`, make 18.

That is too much arithmetic for seven positions, let alone a whole network.
The script below does it.

## Table size

The table size is the number of buckets. One table serves every dust in the
game, in every world and dimension:

- It starts at 16 buckets when the game starts.
- It doubles when an update list gets more positions than three quarters of the
  table size. The 13th position on one list doubles a table of 16 to 32, the
  25th doubles 32 to 64, and so on. It counts positions, not buckets: two
  positions in the same bucket count as two.
- It never gets smaller until the game is closed.

Switching on never grows it, as each list from switching on has seven
positions. Switching off can, as its one list contains the whole network:

| Network switched off | Positions on its list | Table afterwards |
|---|---|---|
| A straight line of 3 or 4 dust | 17 or 22 | 32 |
| A straight line of 5 to 9 dust | 27 to 47 | 64 |
| A straight line of 10 to 15 dust | 52 to 77 | 128 |
| A square patch of 6 × 6 dust | more than 96 | 256 |
| A square patch of 8 × 8 dust | more than 192 | 512 |

<!-- src: java.util.HashMap.putVal resizes when ++size > threshold, three
     quarters of the table; HashMap.clear keeps the table;
     BlockRedstoneWire.blocksNeedingUpdate is one field of the one
     Block.redstoneWire object. A line of n flat dust has 5n + 2 positions;
     a lever powers at most 15 dust of a line.
     tested (harness): the game's table read by reflection matched the script's
     after each of 340 switchings; four copies of one machine fired one way in
     a fresh session and the other way after a 15-dust line 120 blocks away had
     switched off; in singleplayer, the same after the line switched off in the
     previous world -->

A bigger table changes the buckets of every position. A machine that works in a
game just started can fail later in the same session, once a bigger network
anywhere has switched off. Only one rule holds whatever the table size:
switching on runs depth first.

## Which machine acts first

1. Find the table size: 16 in a game just started, otherwise the size the
   biggest network switched off since then has given it.
2. **Switching on:** find the junction, the dust where the paths to the two
   machines part.
   - If both paths leave it on the same level, use the check under Where a line
     splits.
   - If a path steps up or down, list the junction's update list in order, with
     the script's `--set`. For each path, find the first position on the list
     that touches the next dust on that path. The path whose position comes
     first acts first.
   - A machine powered straight from the junction acts at the first position on
     the list that touches the machine.
3. **Switching off:** run the script with `--off`. The machine whose touching
   position comes first on the network's one list acts first.

The head of an extended [[Piston|piston]] passes its block updates on to the
piston, and the top half of a [[Wooden Door|door]] to the bottom half. Count the
positions touching those as touching the machine.

## Example

{{viewer|dust-order-example}}

A floor lever at (8, 64, 5) powers dust at (7, 64, 5) and at the junction,
(6, 64, 5). From the junction:

- the **gold branch** runs on the same level along −z, through (6, 64, 4) and
  (6, 64, 3), to a piston at (6, 64, 2) carrying a block of gold;
- the **diamond branch** steps up onto a stone block at (5, 64, 5), and runs
  along −x through (5, 65, 5) and (4, 65, 5) to a piston at (3, 65, 5) carrying
  a block of diamond.

The gold branch's first dust touches only one position on the junction's update
list: the junction's own position. The diamond branch's first dust touches two:
the stone block under it, and the space above the junction.

In a game just started, the junction's update list runs:

| Order | Position | Bucket | What its block updates do |
|---|---|---|---|
| 1 | +z, beside the junction | 1 | nothing |
| 2 | the junction itself | 2 | turn on the gold branch: the gold piston extends |
| 3 | −y, the block under the junction | 3 | nothing |
| 4 | −z, the gold branch's first dust | 3 | nothing new |
| 5 | +x, the dust before the junction | 7 | nothing |
| 6 | −x, the stone block | 12 | turn on the diamond branch: the diamond piston extends |
| 7 | +y, the space above the junction | 14 | nothing new |

At step 2 the whole gold branch turns on, one dust after another, and the gold
piston extends. Only then does the junction go on to step 3.

Once any line of 3 or 4 dust has switched off, the table has 32 buckets and the
list runs:

| Order | Position | Bucket | What its block updates do |
|---|---|---|---|
| 1 | +x, the dust before the junction | 7 | nothing |
| 2 | −x, the stone block | 12 | turn on the diamond branch: the diamond piston extends |
| 3 | +y, the space above the junction | 14 | nothing new |
| 4 | +z, beside the junction | 17 | nothing |
| 5 | the junction itself | 18 | turn on the gold branch: the gold piston extends |
| 6 | −y, the block under the junction | 19 | nothing |
| 7 | −z, the gold branch's first dust | 19 | nothing new |

The diamond piston now extends first.
<!-- tested (harness, server): this scene, built as shown at the coordinates
     given: the gold piston extended first in a fresh session, the diamond
     piston first after a 4-dust line elsewhere had switched off -->

```
python dust_order.py --lever 8,64,5 --dust 6..7,64,5 6,64,3..4 4..5,65,5 --solid 3,64,5 --watch gold=6,64,2 diamond=3,65,5 --table 32
```

## The script

Save it as `dust_order.py` and run it with Python 3.8 or later; it needs nothing
else. It models one network of dust on solid blocks, powered by one floor
lever, and reports the order the watched blocks act in. `--set` prints one
dust's update list, `--off` switches the lever off instead of on, and `--trace`
prints every update list, indented to show which dust is waiting on which.
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
    python dust_order.py --set 10,64,-3          # one dust's update list, in order
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
    The table starts at 16 buckets and doubles when the set gets more entries than 3/4
    of that. It never shrinks: clear() keeps it."""
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
            self.update_neighbours(e, f"position {entries.index(e) + 1} of {len(entries)} in the update list of dust {p}")
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
    ap.add_argument("--table", type=int, default=16, help="the table size, in buckets (16 in a game just started)")
    ap.add_argument("--set", nargs="*", help="print one dust's update list in order, and stop")
    ap.add_argument("--trace", action="store_true", help="print every update list, indented by depth")
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
                print(f"update list of the dust at {p}, table {s.table}:")
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
                print("  " * ev[4] + f"dust {ev[1]} works through an update list of {len(ev[2])} positions (table {ev[3]}): "
                      + " ".join(f"{e[0]},{e[1]},{e[2]}" for e in ev[2]))
    want = not a.off
    acted, order = set(), []
    for ev in w.log:
        if ev[0] == "update" and ev[1] not in acted and ev[5] == want:
            acted.add(ev[1])
            order.append(ev)
    print(f"dust levels: " + " ".join(f"{p[0]},{p[1]},{p[2]}={v}" for p, v in w.dust.items()))
    print(f"the table size is now {w.set.table}")
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
