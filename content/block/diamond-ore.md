---
title: Diamond Ore
description: The ore block that drops diamonds, found near the bottom of the world.
type: block
categories: [Blocks, Naturally generated, Ores]
---

**Diamond Ore** is the ore block that drops [[Diamond|diamonds]].

## Obtaining

### Natural generation

Diamond ore generates in [[World Generation#Ores|veins]] of size 7, 1 per
chunk, from y=0 to y=15.
<!-- src: ChunkProviderGenerate.java:396-400 populate -->

## Usage

### Breaking

Diamond ore drops one [[Diamond|diamond]] when [[Mining#Harvest levels|mined]]
with an iron or diamond pickaxe. Mined with anything else, it drops nothing. It
never drops itself.
<!-- src: BlockOre.java:10-22 idDropped, quantityDropped; Material.java:114;
     ItemPickaxe.java:13 canHarvestBlock, harvest level 2 or more -->

### Smelting

{{used in|Diamond Ore}}

## Data values

- Block ID: {{id|Diamond Ore}}
- Translation key: `tile.oreDiamond`
