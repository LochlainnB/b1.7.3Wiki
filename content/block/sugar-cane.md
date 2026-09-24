---
title: Sugar cane
description: A tall plant that grows on grass or dirt beside water, and the item it drops, crafted into sugar and paper.
type: block
aliases: [Sugar Canes]
sprite: {Item: Sugar cane, Placed: block 83}
categories: [Blocks, Plants, Naturally generated]
---

**Sugar cane** is a tall plant that grows beside [[Water|water]], and the item
it drops.

## Obtaining

### Natural generation

Sugar cane generates in every biome, on [[Grass|grass]] or [[Dirt|dirt]]
beside [[Water|water]]. Each chunk gets ten [[World Generation#Plants|runs]] of
20 attempts, and a stalk is 2 to 4 blocks tall.
<!-- src: ChunkProviderGenerate.java:548-:553 populate, with no biome test;
     WorldGenReed.java:7 the attempts, :12 the height -->

### Breaking

Breaking sugar cane drops one sugar cane, whatever breaks it. Every block of
the stalk above it breaks too.
<!-- src: BlockReed.java:70 idDropped; :54 checkBlockCoordValid, run from
     onNeighborBlockChange, breaks a block with air beneath it -->

## Usage

### Placing

Sugar cane is placed on [[Grass|grass]] or [[Dirt|dirt]] with [[Water|water]]
beside that block on one of its four sides, or on top of other sugar cane. It
never stands on [[Sand|sand]].
<!-- src: ItemReed.java:11 onItemUse; BlockReed.java:33 canPlaceBlockAt,
     testing Material.water, so flowing water counts -->

### Crafting ingredient

{{used in|Sugar cane}}

## Behaviour

### Growing

The top block of sugar cane less than 3 blocks tall, with air above it,
advances one of 16 stages on each [[Game Tick#Random ticks|random tick]], and
grows a new block above it on the sixteenth. That is about 5½ minutes a block
on average, in any light.
<!-- src: BlockReed.java:14 updateTick: air above, fewer than 3 blocks in the
     column, metadata 0 to 15. 16 random ticks at about 410 ticks each
     (World.java:1952). -->

### Staying put

Sugar cane that could no longer be placed where it stands breaks when a block
beside it changes. Random ticks never break it. Sugar cane whose water is
removed stands until a block beside it changes.
<!-- src: BlockReed.java:50 onNeighborBlockChange, :62 canBlockStay is
     canPlaceBlockAt; updateTick never tests it. The water sits diagonally below
     the sugar cane, so its removal notifies only the block beneath
     (World.java:506 notifyBlocksOfNeighborChange). -->

Sugar cane stops [[Fluid#What stops flow|water and lava]] flowing into its
space.
<!-- src: BlockFlowing.java:222 blockBlocksFlow -->

## Data values

- Block ID: {{id|Sugar cane}}
- Item ID: {{id|item 338}}
- Translation key: `tile.reeds`, `item.reeds`

The game calls the block *Sugar cane* and the item *Sugar Canes*.
