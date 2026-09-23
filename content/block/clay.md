---
title: Clay
description: A soft grey block found in patches under shallow water, mined for clay balls.
type: block
categories: [Blocks, Naturally generated]
---

**Clay** is a soft grey block that generates in patches beneath shallow water.
Breaking one yields [[Clay Ball|clay balls]], which fire into [[Brick|bricks]].
The game gives the block and the item the same name; this page is the block.

## Obtaining

### Natural generation

Clay generates in blobs that replace [[Sand|sand]]. Ten attempts are made per chunk,
each starting from a random point anywhere in the column, and an attempt is
abandoned at once unless the block it starts on is [[Water|water]]. What survives is
therefore a patch of clay in the sand of a lake or sea floor, in the shallows
where sand reaches the surface.
<!-- src: WorldGenClay.java:14-58 generate, ChunkProviderGenerate.java:347-352 -->

The blob itself is a line of overlapping spheres running horizontally through
32 steps, the same shape the game uses for ore, which is why a patch is a
lens rather than a ball.
<!-- src: WorldGenClay.java:18-55 -->

### Crafting

{{crafting|Clay}}

## Usage

### Mining

A clay block drops four [[Clay Ball|clay balls]] and never itself. A shovel is
the effective tool, and nothing is required: the block is soft enough that bare
hands break it and drop the same four.
<!-- src: BlockClay.java:10-16, ItemSpade.java:19 blocksEffectiveAgainst -->

## Data values

- Block ID: {{id|Clay}}
- Translation key: `tile.clay`

The item it drops has its own id: see [[Clay Ball]].
