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

## Block updates

A block that changes sends a **block update** to each of its six neighbours,
asking it to check itself again; see [[Game Tick#Block updates]]. Every block
update carries the type of block that sent it.

Most blocks that respond act on any block update. Doors, trapdoors, TNT, note
blocks, dispensers and rails act only on a block update from a **power
source**: dust, a redstone torch, a lever, a button, a pressure plate or a
detector rail. They ignore the rest.
<!-- src: World.java:506 notifyBlocksOfNeighborChange passes one block id to
     every onNeighborBlockChange; the var5 > 0 && canProvidePower() test in
     onNeighborBlockChange of BlockDoor, BlockTrapDoor, BlockTNT, BlockNote,
     BlockDispenser and BlockRail -->

| Change | Its block updates come from |
|---|---|
| A block placed, or its metadata changed | the block |
| A block broken | air, which is not a power source |
| A power source switching, or broken while on | the power source |
| A repeater switching | the repeater, which is not a power source |

<!-- src: World.java:452 setBlockWithNotify and :461
     setBlockAndMetadataWithNotify pass the new id, so breaking passes 0;
     :422 setBlockMetadataWithNotify passes the block's own id; the
     onBlockRemoval of BlockLever, BlockButton, BlockPressurePlate,
     BlockRedstoneTorch (lit) and BlockRedstoneWire send their own id while on;
     BlockRedstoneRepeater.java:127 canProvidePower returns false -->

## Blocks that respond

A block that responds is **powered** when a source beside it powers it, or when
a powered block is beside it. A piston also counts as powered when the space
above it would be, and a dispenser when the block above it is. This is
**quasi-connectivity**.
<!-- src: World.java:2176 isBlockIndirectlyGettingPowered;
     BlockPistonBase.java:97-:108 test the neighbours of the space above;
     BlockDispenser.java:142 tests the block above -->

| Block | Responds when | Acts on |
|---|---|---|
| {{sprite\|Redstone Dust}} | it is powered | any block update |
| {{sprite\|Redstone Torch}} | the block it is attached to is powered: turns off 2 ticks later | any block update |
| {{sprite\|Redstone Repeater}} | the block behind it is a source powering it, a powered block, or dust carrying power | any block update |
| {{sprite\|Wooden Door}} {{sprite\|Iron Door}} | either half is powered: opens | a block update from a power source |
| {{sprite\|Trapdoor}} | it is powered: opens | a block update from a power source |
| {{sprite\|TNT}} | it is powered: lights | a block update from a power source |
| {{sprite\|Note Block}} | it is itself a powered block, strongly or weakly: plays once | a block update from a power source |
| {{sprite\|Dispenser}} | it is powered, directly or by quasi-connectivity: fires 4 ticks later, then again 4 ticks after each later block update it acts on while still powered | a block update from a power source |
| {{sprite\|Piston}} {{sprite\|Sticky Piston}} | it is powered from any side but its front, directly or by quasi-connectivity: extends | any block update |
| {{sprite\|Powered Rail}} | it or the block above it is powered, or a powered rail it joins is: switches on | any block update |
| {{sprite\|Rail}} | power reaches a three-way junction: switches the curve | a block update from a power source |

<!-- src: BlockRedstoneWire.java:61; BlockRedstoneTorch.java
     isIndirectlyPowered, tickRate 2; BlockRedstoneRepeater.java ignoreTick;
     BlockDoor.java, BlockTrapDoor.java, BlockTNT.java onNeighborBlockChange;
     BlockNote.java reads isBlockGettingPowered rather than the indirect form;
     BlockDispenser.java:140 onNeighborBlockChange, tickRate 4, which keeps
     no record of the last state; BlockPistonBase.java isIndirectlyPowered;
     BlockRail.java onNeighborBlockChange, isNeighborRailPowered -->

## Missed updates

A block that responds checks its power only when it gets a block update it acts
on. A change to its power that brings no such block update goes unnoticed, and
the block keeps its old state until its next one.
<!-- src: each block reads its power in onNeighborBlockChange (and updateTick
     where it schedules one); World.java:506 sends block updates only to the
     six neighbours of a changed block -->

| Change | Missed by |
|---|---|
| Power reaching a piston or dispenser only by quasi-connectivity | {{sprite\|Piston}} {{sprite\|Sticky Piston}} {{sprite\|Dispenser}} |
| A repeater switching | {{sprite\|Wooden Door}} {{sprite\|Iron Door}} {{sprite\|Trapdoor}} {{sprite\|TNT}} {{sprite\|Note Block}} {{sprite\|Dispenser}} {{sprite\|Rail}} |
| Dust changing shape but not level, as when a lever is placed or broken beside the end of a line | whatever responds beside the block the dust stops or starts pointing into |
| A piston extending, and anything its push sets off | every other piston of the same kind, normal or sticky |

<!-- src: BlockPistonBase.java:97-:108 and BlockDispenser.java:142 read the
     space or block above, which no block update reaches; BlockRedstoneWire.java:108
     sends nothing when the level is unchanged, though :291 isPoweringTo
     depends on the shape; BlockPistonBase.java:7 ignoreUpdates is one field on
     the shared block object, set at :113 and cleared at :172, and :53 returns
     while it is set.
     tested (harness, server): a piston and a dispenser with a lever beside the
     space or block above them stayed still for 240 ticks, and moved when a
     block was placed beside them; dust whose end was turned into a corner by a
     lever left the piston it had powered extended for 200 ticks, and removing
     the lever left it retracted while powered; a normal piston breaking the
     torch that powered another normal piston left that piston extended, while
     a sticky piston breaking it let the normal piston retract; a piston whose
     push switched on dust left a normal piston at the end of that dust
     retracted -->

A piston left waiting like this is a **block update detector**: it moves at the
next block update it gets. A [[Redstone Torch|redstone torch]] that misses one
also rechecks at its next [[Game Tick#Random ticks|random tick]].

## Update order

### Direction

A block that changes sends its block updates one neighbour at a time, in the
order −x, +x, −y, +y, −z, +z. Each neighbour acts on its block update before the
next one gets its own, and a [[Piston|piston]] moves at once. When one change
reaches two pistons aimed at the same space, the piston updated first takes it.
A machine that relies on two blocks reacting to one change in some order can
work facing one way and fail turned a quarter turn.
<!-- src: World.java:506 notifyBlocksOfNeighborChange; World.java:2369
     playNoteAt runs BlockPistonBase.java:112 playBlock at once.
     tested (harness, server): a floor lever with one piston beside it on the x
     axis and one on the z axis, both aimed at the same empty space; in all
     four rotations the piston on the x axis extended and the other was
     blocked -->

### Dust

{{main|Predicting Dust Update Order}}

[[Redstone Dust|Dust]] that turns on or off sends block updates around itself
and its six neighbours, and takes those seven positions in an order set by a
hash of their coordinates.

- **Switching on** runs depth first. Each dust that turns on sends all of its
  block updates, and so turns on everything beyond it, before the dust that
  turned it on carries on. Branches that leave one dust at the same level go in
  side order: −x, +x, −z, +z.
- **Switching off** drops the whole network at once, then sends block updates
  around every position of it in one pass, in hash order.

The hash order also depends on a table that belongs to the game rather than to
a world. It starts at 16 positions and doubles whenever a network switching off
needs more room than it has. It never shrinks until the game is closed. The same machine can
therefore act differently in two places, and in one place before and after
another network anywhere, even in another world, switches off. Java 7 and
earlier hash differently again from Java 8 and later.
<!-- src: BlockRedstoneWire.java:10 blocksNeedingUpdate is a HashSet on the one
     Block.redstoneWire object; :160-:168 add the dust and its six neighbours;
     :47-:53 send block updates around them in set order; :88-:97 skip the dust
     that asked, so the next dust turns on inside a block update; HashMap.clear
     keeps its table.
     tested (harness, server, JDK 17): 289 copies of one machine, 12 blocks
     apart, a lever, a bent dust line and two pistons racing to push a block
     into one space: one piston won at 234 places and the other at 55, all
     predicted. Four copies fired one way in a fresh session and the other way
     after a 15-dust line 120 blocks away had switched off; in singleplayer,
     the same after the line switched off in the previous world. 90 random
     networks, switched on and off: every block update reaching an unmovable
     piston arrived in the predicted order. JDK 8 changed HashMap.hash (read,
     not run on Java 6 or 7) -->

## Timing

Power moves through dust, levers, buttons, plates and powered blocks within the
tick, and a piston moves within the tick of its block update. Torches, repeaters and
dispensers add the delays above, as
[[Game Tick#Scheduled ticks|scheduled ticks]].

### Waiting in the queue

Every scheduled tick in a dimension waits in one queue, earliest first. When
more than 1000 are due, only the first 1000 run in the current game tick. The
rest are deferred to the next tick, so redstone delays in that dimension run
late. Generating new terrain fills the queue: every block in the underground
pockets of [[Gravel|gravel]] queues a tick as it is placed, a few hundred to a
chunk. On a server, a player arriving in new terrain 3000 blocks away stopped a
clock at spawn for 160 to 185 ticks, when it normally switched every 10.
<!-- src: World.java:17 one TreeSet per world, :1967 TickUpdates, :1972 the
     1000 cap; ChunkProviderGenerate.java:365 WorldGenMinable for gravel,
     WorldGenMinable.java:46 setBlock, BlockSand.java:12 onBlockAdded queues a
     tick 3 ahead. Sand, and the gravel of beaches, is written into the chunk's
     block array (ChunkProviderGenerate.java:151-:159), which runs no block
     code, so it queues nothing.
     tested (harness, server, seed 1): 218,342 ticks were pending at start,
     from 624 chunks: 218,191 gravel, 119 water, 32 lava and no sand; a
     redstone torch at spawn took 52 ticks to switch instead of 4. A second
     player teleporting 3000 to 6000 blocks into new terrain queued 147,000 to
     175,000 ticks each time, and a torch and repeater clock at spawn missed
     beats of 160, 174 and 185 ticks -->

### Lost delays

A delay still waiting is not saved with its chunk. Closing the world loses
every one, and so does unloading a chunk, as a server does when no player is
near. Delays also lapse near the edge of the loaded area; see
[[Chunk#Scheduled ticks and chunk borders|Chunk]]. A redstone torch whose delay is
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
