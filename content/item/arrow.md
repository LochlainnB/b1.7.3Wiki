---
title: Arrow
description: The ammunition of bows and dispensers, crafted from flint, sticks and feathers, and dropped by skeletons.
type: item
categories: [Items, Weapons]
---

An **arrow** is the ammunition a [[Bow|bow]] fires.

## Obtaining

### Crafting

{{crafting|Arrow}}

### Mob drops

[[Skeleton#Drops|Skeletons]] drop arrows when they die.
<!-- src: EntitySkeleton.java:67 dropFewItems -->

### Picking up

An arrow stuck in a block can be picked up by any player who walks into it, if
a player or a [[Dispenser|dispenser]] fired it. A skeleton's arrows cannot be
picked up.
<!-- src: EntityArrow.java:33 marks an arrow as a player's only when a player
     shot it; BlockDispenser.java:109 marks a dispensed one too; :259
     onCollideWithPlayer gives back only those, once stuck, to whoever touches
     them -->

## Usage

A [[Bow#Firing|bow]] fires arrows from the player's inventory, and a
[[Dispenser#Firing|dispenser]] fires them from its slots.
<!-- src: ItemBow.java:10; BlockDispenser.java:106 -->

## Behaviour

### Flight

A [[Bow|bow]] launches an arrow at 30 blocks per second, a
[[Dispenser|dispenser]] at 22 and a [[Skeleton|skeleton]] at 12. A dispenser's arrows stray six times as far from their aim as
a bow's, and a skeleton's twelve times.
<!-- src: the speed and spread arguments to setArrowHeading, in blocks per
     tick: EntityArrow.java:44 (1.5, 1) for a player, BlockDispenser.java:108
     (1.1, 6), EntitySkeleton.java:45 (0.6, 12). The spread scales a Gaussian
     added to each axis of the direction (EntityArrow.java:55-:57) -->

Each tick an arrow loses 1% of its speed, or 20% in water, and falls 0.6
blocks per second faster.
<!-- src: EntityArrow.java:216-:230, drag 0.99 or 0.8 and gravity 0.03 blocks
     per tick per tick -->

It flies through water, lava and any block with no collision box, such as
[[Tall Grass|tall grass]], [[Torch|torches]] and [[Cobweb|cobwebs]].
<!-- src: EntityArrow.java:128 rayTraceBlocks_do_do(..., false, true): liquids
     fail BlockFluid.java:56 canCollideCheck, and World.java:724 and :846 skip
     a block whose collision box is null, as BlockFlower.java:43 (inherited by
     tall grass), BlockTorch.java:11 and BlockWeb.java:18 return -->

### Hitting

An arrow that hits a mob or player deals [[Damage#Mob attacks|4 damage]] and
disappears. If the target takes no damage, as inside its
[[Damage#The invulnerability window|invulnerability window]], the arrow bounces
back off it instead.
<!-- src: EntityArrow.java:163 attackEntityFrom(owner, 4); :167-:172 reverses
     it at a tenth of its speed when the hit is refused -->

An arrow that hits a block sticks in it. It disappears after 1200 ticks
(1 minute), and falls out if the block is removed or changed.
<!-- src: EntityArrow.java:175-:189 sticks; :110-:123, the 1200-tick count and
     the test of the block's id and metadata -->

## Data values

- Item ID: {{id|Arrow}}
- Entity network ID: {{id|entity 10}}
- Translation key: `item.arrow`
