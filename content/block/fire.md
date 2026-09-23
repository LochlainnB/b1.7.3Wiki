---
title: Fire
description: A block that burns flammable blocks around it and spreads, going out on its own unless it stands on netherrack.
type: block
categories: [Blocks, Naturally generated]
---

**Fire** is a block that burns the flammable blocks around it and spreads to
new spaces.

## Obtaining

Fire never drops, and cannot be collected.
<!-- src: BlockFire.java:47 quantityDropped returns 0 -->

### Starting a fire

| Source | Where the fire goes |
|---|---|
| {{sprite\|Flint and Steel}} | the space against the clicked face, if it is air |
| {{sprite\|Lava}}, still | an air space up to two blocks above it, beside a block of wood, leaves, wool or TNT |
| [[Weather#Lightning\|Lightning]] | the struck space and up to four around it, on Normal and Hard |
| A [[Ghast\|ghast]] fireball, or a [[Bed\|bed]] used in the [[Nether]] | one in three of the spaces the [[Explosion\|explosion]] clears, where an opaque block is below |

<!-- src: ItemFlintAndSteel.java:35; BlockStationary.java:14 updateTick on a
     random tick, isFlammable reading Material.getBurning, set on wood, leaves,
     cloth and tnt (Material.java:113-:126); EntityLightningBolt.java:16;
     EntityFireball.java:127 and BlockBed.java:45 pass true for fire, which
     Explosion.java:110 applies -->

Fire placed on [[Obsidian|obsidian]] inside a finished frame becomes a
[[Nether Portal#Building a portal|Nether portal]] instead.
<!-- src: BlockFire.java:198 onBlockAdded -->

### Natural generation

Fire [[World Generation#The Nether|generates in patches]] on the Nether's
[[Netherrack|netherrack]].

## Usage

### Crafting ingredient

{{used in|Fire}}

## Behaviour

### Where fire can stand

Fire needs a full, solid, opaque block beneath it, or a flammable block beside
it. It goes out at once anywhere else.
<!-- src: BlockFire.java:183 canPlaceBlockAt, :187 onNeighborBlockChange;
     World.java:1644 isBlockNormalCube -->

### Flammable blocks

Only these blocks burn. **Encouragement** is how readily fire spreads into the
air beside the block, and **flammability** how readily the block itself catches.

| Block | Encouragement | Flammability |
|---|---|---|
| {{sprite\|Tall Grass}}, including ferns | 60 | 100 |
| {{sprite\|Leaves}} | 30 | 60 |
| {{sprite\|Wool}} | 30 | 60 |
| {{sprite\|Bookshelf}} | 30 | 20 |
| {{sprite\|TNT}} | 15 | 100 |
| {{sprite\|Wooden Planks}} | 5 | 20 |
| {{sprite\|Fence}} | 5 | 20 |
| {{sprite\|Wooden Stairs}} | 5 | 20 |
| {{sprite\|Wood}} | 5 | 5 |

<!-- src: BlockFire.java:14 initializeBlock, setBurnRate(id, encouragement,
     flammability) -->

Crafting tables, chests, doors, signs, ladders, wooden slabs and every other
block do not burn.

### Burning

Fire updates every 40 ticks, and on [[Game Tick#Skipping a delay|random
ticks]] as well. Each fire has an age from 0 to 15. An update has a 1 in 3
chance to add 1 to it.
<!-- src: BlockFire.java:51 tickRate 40; :65 var7 + nextInt(3) / 2 -->

On each update, fire tries to burn each of the six blocks around it. A block
catches with a chance of its flammability in 300, or in 250 directly above or
below. A block that catches becomes fire, at a chance of 5 in (age + 10), and
is destroyed otherwise. [[TNT]] that catches is lit instead.
<!-- src: BlockFire.java:72-:77, :117 tryToCatchBlockOnFire -->

Fire goes out:

- when it, or a space beside it on its own level, is rained on; see
  [[Weather#Rain]];
- when nothing beside it is flammable, once its age passes 3;
- when it stands beside a flammable block but not on one, 1 update in 4 once
  its age reaches 15;
- when a player hits the face of a block it stands against;
- when flowing [[Water|water]] or [[Lava|lava]] reaches it.

<!-- src: BlockFire.java:61, :69, :71; World.java:1580 onBlockHit;
     BlockFlowing.java:251 liquidCanDisplaceBlock, as fire's material is not
     solid -->

Fire on [[Netherrack|netherrack]] never goes out, and rain does not reach it.
<!-- src: BlockFire.java:56 var6, which skips every test above but hitting and
     flowing liquid -->

### Spreading

Fire also lights air spaces near it: any space from 1 block below it to 4 above,
within 1 block across, that is air and beside a flammable block. The chance per
update is ⌊(E + 40) ÷ (age + 30)⌋ + 1 in 100, where E is the highest
encouragement beside that space. Two blocks above the fire it is the same figure
in 200, three above in 300, and four above in 400.
<!-- src: BlockFire.java:79-:96; getChanceOfNeighborsEncouragingFire (:159)
     takes the highest encouragement of the six neighbours -->

Fire does not spread into a space that is rained on.
<!-- src: BlockFire.java:97 -->

### Entities

An entity in fire takes damage and catches alight; see
[[Damage#Catching fire]]. A dropped item in fire is destroyed.
<!-- src: Entity.java:523 dealFireDamage; EntityItem.java:83 dealFireDamage
     against the 5 health of :8 -->

## Data values

- Block ID: {{id|Fire}}
- Translation key: `tile.fire`
