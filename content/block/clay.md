---
title: Clay
description: A grey block found in sand near water, broken for clay balls.
type: block
categories: [Blocks, Naturally generated]
---

{{hatnote|This page is about the block. For the item it drops, see [[Clay Ball]].}}

**Clay** is a grey block that generates in [[Sand|sand]] near [[Water|water]].

## Obtaining

### Natural generation

Ten clay blobs are attempted per chunk, each at a random point in the chunk. An
attempt is abandoned unless that point is [[Water|water]]. A blob replaces only
[[Sand|sand]], and takes the shape of an [[World Generation#Ores|ore vein]] at
size 32.
<!-- src: WorldGenClay.java:14-58 generate, ChunkProviderGenerate.java:347-352 -->

### Crafting

{{crafting|Clay}}

## Usage

### Breaking

Breaking clay drops four [[Clay Ball|clay balls]], whatever breaks it. The block
never drops itself. A shovel breaks it fastest.
<!-- src: BlockClay.java:10-16 idDropped, quantityDropped;
     ItemSpade.java:19 blocksEffectiveAgainst -->

## Data values

- Block ID: {{id|Clay}}
- Translation key: `tile.clay`

The game names both this block and the item it drops *Clay*.
<!-- The wiki names the item Clay Ball (data/name-overrides.json) so the two can
     have separate pages and recipes. -->
