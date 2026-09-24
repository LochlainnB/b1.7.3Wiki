---
title: Cactus
description: A spiny desert plant that stands on sand with nothing solid beside it, hurts whatever touches it, and smelts into cactus green.
type: block
categories: [Blocks, Plants, Naturally generated]
---

**Cactus** is a spiny plant of [[Desert|deserts]] that hurts whatever touches
it.

## Obtaining

### Natural generation

Cacti generate only in [[Desert]], in 10
[[World Generation#Plants|patches]] per chunk. Each patch makes 10 attempts,
and each cactus is 1 to 3 blocks tall.
<!-- src: ChunkProviderGenerate.java:562-:572 populate; WorldGenCactus.java:7
     the 10 attempts, :12 the height; each block is placed only where
     canBlockStay passes (:15) -->

### Breaking

Breaking a cactus drops it, whatever breaks it.
<!-- src: BlockCactus keeps Block's idDropped and quantityDropped;
     Material.java:131 cactus needs no tool -->

## Usage

### Smelting

{{used in|Cactus}}

## Behaviour

### Where it stands

A cactus stands on [[Sand|sand]] or on another cactus, with no solid block on
any of its four sides. Another cactus counts as solid. [[Water|Water]],
plants, [[Torch|torches]] and [[Snow|snow]] layers do not.
<!-- src: BlockCactus.java:72 canBlockStay, testing Material.isSolid; the
     materials that are not solid are air, water, lava, plants, circuits, fire,
     snow layers and portal (MaterialTransparent, MaterialLiquid,
     MaterialLogic, MaterialPortal); Material.java:131 cactus is solid -->

Placing a cactus checks the same rules. A cactus that cannot stay breaks when a
block beside it changes.
<!-- src: BlockCactus.java:60 canPlaceBlockAt, :64 onNeighborBlockChange -->

### Growing

The top block of a cactus less than 3 blocks tall, with air above it, advances
one of 16 stages on each [[Game Tick#Random ticks|random tick]], and grows a new
block above it on the sixteenth. That is about 5½ minutes a block on average,
in any light.
<!-- src: BlockCactus.java:11 updateTick: air above, fewer than 3 cactus blocks
     in the column, metadata 0 to 15. 16 random ticks at about 410 ticks each
     (World.java:1952). -->

A block that grows beside a solid block breaks at once.
<!-- src: BlockCactus.java:20 places the new block without testing it; :21
     then resets the lower block's stage, which notifies its neighbours
     (World.java:422 setBlockMetadataWithNotify), and the new block's
     onNeighborBlockChange (:64) fails canBlockStay -->

### Damage

A cactus hurts anything touching it for 1
[[Damage#Environmental damage|damage]], attempted every tick. A
[[Dropped Item|dropped item]] that touches one is destroyed.
<!-- src: BlockCactus.java:87 onEntityCollidedWithBlock; Entity.java:514 calls it
     for every block an entity's box overlaps, and the cactus's box is 1/16
     smaller than its space (:30); EntityItem.java:87 attackEntityFrom against
     the item's 5 health (:8) -->

## Data values

- Block ID: {{id|Cactus}}
- Translation key: `tile.cactus`
