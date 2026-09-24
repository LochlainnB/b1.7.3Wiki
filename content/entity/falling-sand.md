---
title: Falling Sand
description: The entity sand or gravel becomes while it falls, which lands as the block again or drops as an item.
type: entity
subject: FallingSand
aliases: [FallingSand]
categories: [Entities]
---

**Falling Sand** is the entity a block of [[Sand|sand]] or [[Gravel|gravel]]
becomes while it falls.

## Spawning

Sand and gravel fall 3 [[Game Tick#Scheduled ticks|ticks]] after they are
placed, or after a block beside them changes, if the block below is air,
[[Water|water]], [[Lava|lava]] or [[Fire|fire]]. The block becomes a falling
sand entity in the same space.
<!-- src: BlockSand.java:12 onBlockAdded, :16 onNeighborBlockChange, :45
     tickRate 3; :24 tryToFall; :49 canFallBelow -->

Where a chunk within 32 blocks is not loaded, the block moves straight down to
where it would land instead, and no entity is made. A block that falls while a
chunk is being [[World Generation#Population|populated]] moves the same way.
<!-- src: BlockSand.java:27 the checkChunksExist and fallInstantly test,
     :31-:39 the instant drop; ChunkProviderGenerate.java:311 and :602,
     ChunkProviderHell.java:303 and :358 set fallInstantly around populate -->

## Behaviour

Falling sand moves straight down. Each tick it gains 0.04 blocks a tick of
downward speed, then loses 2% of its speed, so it approaches 2 blocks a tick.
Water does not slow it, and fire and lava do not harm it.
<!-- src: EntityFallingSand.java:37 onUpdate, which replaces Entity.onUpdate and
     never calls onEntityUpdate, where water movement is handled; fire damage
     (Entity.java:562 dealFireDamage)
     reaches Entity.java:746 attackEntityFrom, which does nothing -->

It falls through players and mobs, and lands as a block even in a space one of
them stands in.
<!-- src: Entity.java:558 getBoundingBox and :912 getCollisionBox are null for
     living entities, so World.java:959 getCollidingBoundingBoxes adds nothing
     for them; World.java:2101 skips the entity test when landing -->

On landing, it becomes the block again in the space it stopped in. If that
space already holds a block, such as a [[Torch|torch]] it fell onto or a
[[Stone Slab|slab]] it landed on, it drops as an item instead. Water, lava, fire
and [[Snow|snow]] layers do not count as blocks, and are replaced.
<!-- src: EntityFallingSand.java:57-:64; World.java:2096 canBlockBePlacedAt
     treats water, lava, fire and snow as empty; Block.java:501 -->

A block still falling after 100 ticks, about 117 blocks down, drops as an item
where it is.
<!-- src: EntityFallingSand.java:65 fallTime > 100; the distance is the motion
     of onUpdate summed over 101 ticks -->

The item is always the block itself. Gravel dropped this way never gives
[[Flint|flint]].
<!-- src: EntityFallingSand.java:63 and :66 dropItem(this.blockID, 1) -->

## Data values

- Entity network ID: {{id|FallingSand}}

The entity saves the id of the block it carries as `Tile`. The game names it
*FallingSand* whichever block it carries.
<!-- src: EntityFallingSand.java:74 writeEntityToNBT -->
