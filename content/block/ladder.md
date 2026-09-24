---
title: Ladder
description: A block placed against a wall that players and mobs climb, and that stops fall damage.
type: block
categories: [Blocks, Utility blocks]
---

**Ladder** is a block placed against a wall for climbing.

## Obtaining

### Crafting

{{crafting|Ladder}}

### Breaking

A ladder drops itself when broken with anything. An axe is not
[[Mining#What each tool is effective against|effective against]] it.
<!-- src: BlockLadder.java:7 Material.circuits, which needs no tool;
     :126 quantityDropped 1; ItemAxe.java:11 blocksEffectiveAgainst has no
     ladder -->

## Usage

### Placing

A ladder is placed against the side of a full, opaque block, and drops when
that block is removed. [[Glass]], [[Ice|ice]], [[Leaves|leaves]] and [[TNT]]
cannot hold one.
<!-- src: BlockLadder.java:66 canPlaceBlockAt, :78 onBlockPlaced and :99
     onNeighborBlockChange all test isBlockNormalCube, which World.java:1644
     denies to glass, ice, leaves and TNT (Material.java:118-:128
     setIsTranslucent) -->

### Climbing

A player or mob in a ladder's space climbs it while moving against the ladder or
a wall. It climbs about 2.35 blocks a second, and slides down at most 3 blocks a
second. A player who sneaks on a ladder does not slide down.
<!-- src: EntityLiving.java:550 isOnLadder, the block at the feet; :528 sets
     motionY to 0.2 on a horizontal collision, which gravity and drag at
     :532-:533 bring to 0.1176 a tick; :518 caps the fall at 0.15 a tick; :522
     holds a sneaking entity. None of this applies in water or lava (:456,
     :467) -->

An entity on a ladder takes no [[Damage#Environmental damage|fall damage]].
<!-- src: EntityLiving.java:517 resets fallDistance -->

## Behaviour

A ladder stops [[Fluid#What stops flow|flowing water and lava]]. A
[[Piston|piston]] breaks a ladder, which drops. [[Fire]] does not burn it.
<!-- src: BlockFlowing.java:222 blockBlocksFlow names the ladder;
     Material.java:124 circuits setNoPushMobility, which
     BlockPistonBase.java:336 breaks and drops; BlockFire.java:14
     initializeBlock gives it no burn rate -->

## Data values

- Block ID: {{id|Ladder}}
- Translation key: `tile.ladder`
