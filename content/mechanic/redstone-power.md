---
title: Redstone Power
description: How redstone power works — which blocks give it, strongly and weakly powered blocks, what each redstone-driven block needs, and which changes it notices.
type: mechanic
categories: [Game mechanics]
aliases: [Redstone circuit, Redstone circuits, Strongly powered, Weakly powered]
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
| {{sprite\|Dispenser}} | it or the block above it is powered: fires 4 ticks later | a power source |
| {{sprite\|Piston}} {{sprite\|Sticky Piston}} | it is powered from any side but its front, or would be one block higher: extends | any block beside it |
| {{sprite\|Powered Rail}} | it or the block above it is powered, or a powered rail it joins is: switches on | any block beside it |
| {{sprite\|Rail}} | power reaches a three-way junction: switches the curve | a power source |

<!-- src: BlockRedstoneWire.java:61; BlockRedstoneTorch.java
     isIndirectlyPowered, tickRate 2; BlockRedstoneRepeater.java ignoreTick;
     BlockDoor.java, BlockTrapDoor.java, BlockTNT.java onNeighborBlockChange;
     BlockNote.java reads isBlockGettingPowered rather than the indirect form;
     BlockDispenser.java onNeighborBlockChange, tickRate 4;
     BlockPistonBase.java isIndirectlyPowered, whose last six tests are the
     neighbours of the block above; BlockRail.java onNeighborBlockChange,
     isNeighborRailPowered -->

A power source here is dust, a torch, a lever, a button, a pressure plate or a
detector rail. A repeater is not one, so a repeater switching beside a door,
trapdoor, TNT, note block, dispenser or rail goes unnoticed.
<!-- src: the var5 > 0 && canProvidePower() test in onNeighborBlockChange of
     BlockDoor, BlockTrapDoor, BlockTNT, BlockNote, BlockDispenser and
     BlockRail; BlockRedstoneRepeater.java canProvidePower returns false -->

## Timing

Power moves through dust, levers, buttons, plates and powered blocks within the
tick. Torches, repeaters and dispensers add the delays above, as
[[Game Tick#Scheduled ticks|scheduled ticks]].
