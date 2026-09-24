---
title: Snow
description: The thin layer that covers cold ground, and the block crafted from four snowballs; a shovel breaks either into snowballs.
type: block
subject: {Layer: block 78, Block: block 80}
aliases: [Snow Layer, Snow Block]
categories: [Blocks, Naturally generated, Building blocks]
---

**Snow** is both the thin layer that covers cold ground and the full block
crafted from [[Snowball|snowballs]].

## Obtaining

### Natural generation

Snow layers [[World Generation#Snow|generate]] over cold ground. They also
[[Weather#Snow and ice|settle]] while it snows in a snowy biome, on a full,
solid block other than [[Ice|ice]], in block light below 10.
<!-- src: ChunkProviderGenerate.java:588-:597; World.java:1939-:1943 -->

### Crafting

{{crafting|Snow}}

### Breaking

Broken with a [[Mining#Drops|shovel]], a snow layer drops one
[[Snowball|snowball]] and a snow block four. Broken any other way, neither drops
anything. A shovel breaks both fastest.
<!-- src: BlockSnow.java:50 harvestBlock; BlockSnowBlock.java:15
     quantityDropped 4; Material.java:129-:130 setNoHarvest; ItemSpade.java:10
     canHarvestBlock, :19 blocksEffectiveAgainst -->

## Behaviour

A snow layer is an eighth of a block tall. Entities pass through it and stand
on the block below.
<!-- src: BlockSnow.java:8 and :25 bounds 2/16 tall at metadata 0, which is
     all the game ever places; :12 no collision box below metadata 3 -->

These remove a snow layer without a drop:

- removing the block beneath it;
- placing a block on it, which takes its space;
- flowing [[Water|water]] or [[Lava|lava]], which
  [[Fluid#What stops flow|flows into it]];
- a [[Boat|boat]] passing over it.

<!-- src: BlockSnow.java:36 onNeighborBlockChange, :31 canPlaceBlockAt wants
     an opaque, solid block below, :67 quantityDropped 0; ItemBlock.java:13;
     BlockFlowing.java:116 flowIntoBlock; EntityBoat.java:302-:307 -->

On a [[Game Tick#Random ticks|random tick]], a snow layer in
[[Light#What light affects|block light]] above 11 melts away, dropping nothing.
Sky light never melts it. A snow block never melts.
<!-- src: BlockSnow.java:71 updateTick. BlockSnowBlock.java:19 makes the same
     test, but reads the block light stored in its own space, and a snow block
     is opaque (Block.java:152 opacity 255), so MetadataChunkBlock
     always stores 0 there (:85) -->

## Data values

- Block ID: {{id|Snow}} (layer), {{id|block 80}} (block)
- Translation key: `tile.snow`

The game names both blocks *Snow*.
