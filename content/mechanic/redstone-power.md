---
title: Redstone Power
description: How redstone power works — which blocks give it, strongly and weakly powered blocks, what each redstone-driven block needs and notices, the order updates run in, and why circuits stall, stop or burn out.
type: mechanic
categories: [Game mechanics]
aliases: [Redstone circuit, Redstone circuits, Strongly powered, Weakly powered, Quasi-connectivity, Block update detector, BUD, Update order]
---

**Redstone power** is the on-or-off signal that redstone components send to
the blocks around them.

## Power sources

| Source | Powers these blocks beside it | Powers this solid block | On |
|---|---|---|---|
| {{sprite\|Lever}} | all six | strongly: the block it is attached to | until used again |
| {{sprite\|Button}} | all six | strongly: the block it is attached to | for 20 ticks |
| {{sprite\|Pressure Plate}} | all six | strongly: the block beneath it | while something stands on it |
| {{sprite\|Detector Rail}} | all six | strongly: the block beneath it | while a minecart is on it |
| {{sprite\|Redstone Torch}} | all but the block it is attached to | strongly: the block above it | while the block it is attached to is not powered |
| {{sprite\|Redstone Repeater}} | the block in front of it | strongly: the block in front of it | from 2 to 8 ticks after the block behind it is powered |
| {{sprite\|Redstone Dust}} | the block beneath it, and the blocks it points into | weakly: the same blocks | while it carries power |

<!-- src: isPoweringTo (second column) and isIndirectlyPoweringTo (third) in
     BlockLever.java, BlockButton.java, BlockPressurePlate.java,
     BlockDetectorRail.java, BlockRedstoneTorch.java,
     BlockRedstoneRepeater.java and BlockRedstoneWire.java. Dust's
     isIndirectlyPoweringTo is its isPoweringTo, switched off while dust works
     out its own level (BlockRedstoneWire.java:60), which is what makes the
     blocks it powers weak -->

[[Redstone Dust|Redstone dust]] carries power from block to block, and loses
strength as it goes.

## Powered blocks

A full, solid block is powered only through the table's third column, and then
passes the power on:

- A **strongly powered** block powers every block around it that responds to
  power, [[Redstone Dust|dust]] included.
- A **weakly powered** block powers every block around it that responds to
  power, except dust.

<!-- src: World.java:2151 isBlockGettingPowered reads each neighbour's
     isIndirectlyPoweringTo; World.java:2167 isBlockIndirectlyProvidingPowerTo
     hands that on from a normal cube (World.java:1644 isBlockNormalCube) -->

## Blocks that respond

A block that responds is **powered** when a source beside it powers it, or when
a powered block is beside it.
<!-- src: World.java:2176 isBlockIndirectlyGettingPowered -->

| Block | Responds when | Checks again on a change to |
|---|---|---|
| {{sprite\|Redstone Dust}} | it is powered | any block beside it |
| {{sprite\|Redstone Torch}} | the block it is attached to is powered: turns off 2 ticks later | any block beside it |
| {{sprite\|Redstone Repeater}} | the block behind it is a source powering it, a powered block, or dust carrying power | any block beside it |
| {{sprite\|Wooden Door}} {{sprite\|Iron Door}} | either half is powered: opens | a power source |
| {{sprite\|Trapdoor}} | it is powered: opens | a power source |
| {{sprite\|TNT}} | it is powered: lights | a power source |
| {{sprite\|Note Block}} | it is itself a powered block, strongly or weakly: plays once | a power source |
| {{sprite\|Dispenser}} | it or the block above it is powered: fires 4 ticks later, and again at every check while still powered | a power source |
| {{sprite\|Piston}} {{sprite\|Sticky Piston}} | it is powered from any side but its front, or would be one block higher: extends | any block beside it |
| {{sprite\|Powered Rail}} | it or the block above it is powered, or a powered rail it joins is: switches on | any block beside it |
| {{sprite\|Rail}} | power reaches a three-way junction: switches the curve | a power source |

<!-- src: BlockRedstoneWire.java:61; BlockRedstoneTorch.java
     isIndirectlyPowered, tickRate 2; BlockRedstoneRepeater.java ignoreTick;
     BlockDoor.java, BlockTrapDoor.java, BlockTNT.java onNeighborBlockChange;
     BlockNote.java reads isBlockGettingPowered rather than the indirect form;
     BlockDispenser.java:140 onNeighborBlockChange, tickRate 4, which keeps
     no record of the last state, so every check while powered fires;
     BlockPistonBase.java isIndirectlyPowered, whose last six tests are the
     neighbours of the block above; BlockRail.java onNeighborBlockChange,
     isNeighborRailPowered -->

A power source here is dust, a torch, a lever, a button, a pressure plate or a
detector rail. A repeater is not one.
<!-- src: the var5 > 0 && canProvidePower() test in onNeighborBlockChange of
     BlockDoor, BlockTrapDoor, BlockTNT, BlockNote, BlockDispenser and
     BlockRail; BlockRedstoneRepeater.java canProvidePower returns false -->

## Missed updates

A block that responds checks its power only when it is told of a change in the
last column above. A change to its power that arrives any other way goes
unnoticed, and the block keeps its old state until the next change it is told
of.
<!-- src: each block reads its power in onNeighborBlockChange (and updateTick
     where it schedules one); World.java:506 tells only the six neighbours of
     a changed block -->

| Change that tells nothing | Missed by |
|---|---|
| Power reaching only the space above a piston, or the block above a dispenser | {{sprite\|Piston}} {{sprite\|Sticky Piston}} {{sprite\|Dispenser}} |
| A repeater switching | {{sprite\|Wooden Door}} {{sprite\|Iron Door}} {{sprite\|Trapdoor}} {{sprite\|TNT}} {{sprite\|Note Block}} {{sprite\|Dispenser}} {{sprite\|Rail}} |
| Dust changing shape but not level, as when a lever is placed or broken beside the end of a line | whatever responds beside the block the dust stops or starts pointing into |
| A piston extending, and breaking what is in its way | every other piston of the same kind, normal or sticky |

<!-- src: BlockPistonBase.java:97-:108 and BlockDispenser.java:142 read the
     block above, which no update reaches; BlockRedstoneWire.java:108 tells
     nothing when the level is unchanged, though :291 isPoweringTo depends on
     the shape; BlockPistonBase.java:7 ignoreUpdates is one field on the
     shared block object, set at :113 and cleared at :172, and :53 returns
     while it is set.
     tested (harness, server): a piston and a dispenser with a lever beside the
     space or block above them stayed still for 240 ticks, and moved when a
     block was placed beside them; dust whose end was turned into a corner by a
     lever left the piston it had powered extended for 200 ticks, and removing
     the lever left it retracted while powered; a normal piston breaking the
     torch that powered another normal piston left that piston extended, while
     a sticky piston breaking it let the normal piston retract -->

A piston left waiting like this is a **block update detector**: it moves the
next time any block beside it changes. A
[[Redstone Torch|redstone torch]] that misses an update also rechecks at its
next [[Game Tick#Random ticks|random tick]].

## Update order

### Direction

A block that changes tells its six neighbours one at a time, in the order −x,
+x, −y, +y, −z, +z. Each neighbour acts before the next is told, and a
[[Piston|piston]] moves at once. When one change reaches two pistons aimed at
the same space, the piston told first takes it. A machine that relies on two
blocks reacting to one change in some order can work facing one way and fail
turned a quarter turn.
<!-- src: World.java:506 notifyBlocksOfNeighborChange; World.java:2369
     playNoteAt runs BlockPistonBase.java:112 playBlock at once.
     tested (harness, server): a floor lever with one piston beside it on the x
     axis and one on the z axis, both aimed at the same empty space; in all
     four rotations the piston on the x axis extended and the other was
     blocked -->

### Location

[[Redstone Dust|Dust]] that switches on or off tells the blocks around it in an
order set by a hash of their coordinates. The same machine can work in one
place and fail in another. Java 7 and earlier give a different order from Java
8 and later, so it can also work on one computer and fail on another.
<!-- src: BlockRedstoneWire.java:10 blocksNeedingUpdate is a HashSet;
     :160-:168 add the dust and its six neighbours; :47-:53 tell them in set
     order; ChunkPosition.java:23 hashCode is x * 8976890 + y * 981131 + z.
     Dust down a line switches on inside the notification from the dust
     before it, because :88-:97 skip the dust that asked, so one set's order
     can decide which end of a line acts first.
     tested (harness, server, JDK 17): 289 copies of one machine, 12 blocks
     apart: a lever, a bent dust line, and two pistons racing to push a block
     into one space. One piston won at 234 places and the other at 55. A port
     of the dust code and of java.util.HashMap predicted all 289. JDK 8
     changed HashMap.hash; the same port with the JDK 6 hash disagrees on 107
     of the 289 (read, not run on Java 6) -->

## Timing

Power moves through dust, levers, buttons, plates and powered blocks within the
tick, and a piston moves within the tick that tells it. Torches, repeaters and
dispensers add the delays above, as
[[Game Tick#Scheduled ticks|scheduled ticks]].

### Waiting in the queue

Every scheduled tick in a dimension waits in one queue, and at most 1000 run in
a tick, earliest first. While something else fills the queue, every redstone
delay in that dimension runs late, however far it is from the cause.
Generating new terrain fills it, with a tick for each block of
[[Gravel|gravel]] placed. On a server, a player arriving in new terrain 3000
blocks away stopped a clock at spawn for 160 to 185 ticks, when it normally
switched every 10.
<!-- src: World.java:17 one TreeSet per world, :1967 TickUpdates, :1972 the
     1000 cap; ChunkProviderGenerate.java:365 WorldGenMinable for gravel,
     WorldGenMinable.java:46 setBlock, BlockSand.java:12 onBlockAdded queues a
     tick 3 ahead.
     tested (harness, server, seed 1): 218,191 gravel ticks were pending at
     start, from 624 chunks, and a redstone torch at spawn took 52 ticks to
     switch instead of 4; a second player teleporting 3000 to 6000 blocks into
     new terrain queued 147,000 to 175,000 ticks each time, and a torch and
     repeater clock at spawn missed beats of 160, 174 and 185 ticks -->

### Lost delays

A delay still waiting is not saved with its chunk. Closing the world loses
every one, and so does unloading a chunk, as a server does when no player is
near. Delays also lapse near the edge of the loaded area; see
[[Chunk#Scheduled updates and chunk borders|Chunk]]. A redstone torch whose delay is
lost corrects itself at its next random tick. A repeater does not, so a clock
built with repeaters usually stops for good.
<!-- src: ChunkLoader.java:108-149 writes no ticks; World.java:1984 discards
     a due tick whose chunks are missing; BlockRedstoneTorch.java:38 flags
     random ticks, BlockRedstoneRepeater does not.
     tested (harness, server): 12 torch and repeater clocks, period 20. After
     a server restart, 9 stayed stopped for 3000 ticks, 1 restarted after 1450
     and 2 ran on. After the only player walked away and came back, 10 of 12
     stayed stopped -->

### Random ticks

A [[Game Tick#Skipping a delay|random tick]] can make a redstone torch switch
inside its 2 ticks, and a button, pressure plate or detector rail release inside
its 20. Near a player, the odds are about 1 in 410 for each tick a block waits.

## Torch burnout

{{main|Redstone Torch#Burning out}}

A redstone torch that turns off for the 8th time within 100 ticks burns out.
Every torch in the running game shares one record of turn-offs. A torch in
another world, or in the other dimension of a server, can keep a torch from
relighting.
