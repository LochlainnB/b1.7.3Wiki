---
title: Stone
description: The rock the Overworld is made of underground, which drops cobblestone when mined with a pickaxe.
type: block
categories: [Blocks, Building blocks, Naturally generated]
---

**Stone** is the rock that most of the [[Overworld]] is made of.

## Obtaining

### Breaking

Stone drops [[Cobblestone|cobblestone]] when [[Mining|mined]] with any pickaxe,
and nothing otherwise. A pickaxe breaks it fastest.
<!-- src: BlockStone.java:10 idDropped; Material.java:114 rock setNoHarvest;
     ItemPickaxe.java:18 canHarvestBlock accepts any pickaxe on rock;
     ItemPickaxe.java:41 blocksEffectiveAgainst lists Block.stone -->

### Smelting

{{smelting|Stone}}

### Natural generation

Stone is placed wherever the Overworld's [[World Generation#Terrain|terrain]] is
solid, under each biome's [[World Generation#Surface|surface blocks]]. A
[[World Generation#Lakes|lava lake]] is lined with stone.
<!-- src: ChunkProviderGenerate.java:43 generateTerrain fills solid density
     with Block.stone; :113 replaceBlocksForBiome; WorldGenLakes.java:93 -->

## Usage

### Crafting ingredient

{{used in|Stone}}

## Data values

- Block ID: {{id|Stone}}
- Translation key: `tile.stone`
