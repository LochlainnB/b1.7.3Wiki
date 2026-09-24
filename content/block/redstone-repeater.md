---
title: Redstone Repeater
description: A block that passes redstone power one way, from the block behind it to the block in front, after a delay of 2 to 8 ticks.
type: block
subject: {Off: block 93, On: block 94}
categories: [Blocks, Redstone]
---

**Redstone Repeater** is a block that passes [[Redstone Power|redstone power]]
one way, after a delay.

## Obtaining

### Crafting

{{crafting|Redstone Repeater}}

## Usage

### Placing

A repeater is placed on top of a full, solid block, facing away from the
player. It drops as an item when that block goes.
<!-- src: BlockRedstoneRepeater.java:20 canPlaceBlockAt, :86
     onNeighborBlockChange; :131 onBlockPlacedBy turns the player's facing into
     the repeater's, input on the player's side -->

### Setting the delay

Right-clicking a repeater sets its delay to the next of 2, 4, 6 and 8 ticks,
and from 8 back to 2. A new repeater starts at 2.
<!-- src: BlockRedstoneRepeater.java:119 blockActivated; :7 the {1,2,3,4}
     array doubled at :95; :131 placement clears the delay bits -->

## Behaviour

### Power

A repeater takes its input from the block behind it alone. The input is on
when that block is a
[[Redstone Power#Blocks that respond|power source powering the repeater]], a
powered block, or [[Redstone Dust|dust]] carrying power. While on, a repeater
[[Redstone Power#Powered blocks|strongly powers]] the block in front of it, and
nothing else.
<!-- src: BlockRedstoneRepeater.java:103 ignoreTick, :65 isIndirectlyPoweringTo,
     :69 isPoweringTo -->

A [[Wooden Door|door]], [[Trapdoor|trapdoor]], [[TNT]],
[[Note Block|note block]] or [[Dispenser|dispenser]] does not notice a repeater
switching beside it. A repeater is not a
[[Redstone Power#Blocks that respond|power source]] to them.
<!-- src: BlockRedstoneRepeater.java:127 canProvidePower returns false -->

### Delay

A repeater turns on one delay after its input is powered, and then stays on for
at least one delay, however short the input was. It turns off one delay after
its input goes off, if the input is still off by then.
<!-- src: BlockRedstoneRepeater.java:86 onNeighborBlockChange schedules only on
     a mismatch; :28 updateTick always turns an unpowered repeater on, and
     schedules the turn-off at once when the input has already gone -->

Its delay is exact. [[Game Tick#Skipping a delay|Random ticks]] never cut it
short.
<!-- src: BlockRedstoneRepeater's constructor never calls setTickOnLoad -->

## Data values

- Block ID: {{id|Redstone Repeater}} unpowered, {{id|block 94}} powered
- Item ID: {{id|item 356}}
- Translation key: `tile.diode`, `item.diode`
