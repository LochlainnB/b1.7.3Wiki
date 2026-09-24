---
title: Torch
description: A light-giving block made from coal or charcoal and a stick, placed on the top or side of a block.
type: block
categories: [Blocks]
---

**Torch** is a block that gives off [[Light#Block light|light]].
<!-- src: Block.java:642 setLightValue(0.9375F) -->

## Obtaining

### Crafting

{{crafting|Torch}}

### Breaking

A torch breaks at once with anything, and drops itself.
<!-- src: Block.java:642 setHardness(0.0F); BlockTorch.java:7 Material.circuits,
     which needs no tool -->

## Usage

### Placing

A torch stands on top of a full, opaque block or a [[Fence|fence]], or on the
side of a full, opaque block. It drops when that block is removed. [[Glass]],
[[Ice|ice]], [[Leaves|leaves]] and [[TNT]] cannot hold one.
<!-- src: BlockTorch.java:27 canPlaceTorchOn, :31 canPlaceBlockAt, :94
     onNeighborBlockChange; isBlockNormalCube (World.java:1644) is false for
     glass, ice, leaves and TNT (Material.java:118-:128 setIsTranslucent) -->

### Crafting ingredient

{{used in|Torch}}

## Behaviour

Entities pass through a torch. [[Fluid#What stops flow|Flowing water]] breaks a
torch, which drops. Flowing lava destroys it. A [[Piston|piston]] breaks a
torch, which drops.
<!-- src: BlockTorch.java:11 getCollisionBoundingBoxFromPool returns null;
     BlockFlowing.java:116 flowIntoBlock drops the block for water and not for
     lava; Material.java:124 circuits setNoPushMobility, which
     BlockPistonBase.java:336 breaks and drops -->

## Data values

- Block ID: {{id|Torch}}
- Translation key: `tile.torch`
