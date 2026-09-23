---
title: Cobblestone
description: The block stone drops when mined with a pickaxe, and the material of stone tools and the furnace.
type: block
categories: [Blocks, Building blocks, Naturally generated]
---

**Cobblestone** is the block dropped when [[Stone]] is mined with a pickaxe.

## Obtaining

### Breaking

[[Stone]] and cobblestone each drop one cobblestone when [[Mining|mined]] with
any pickaxe. Mined with anything else, they drop nothing.
<!-- src: BlockStone.java:10 idDropped; Material.java:114 sets rock as needing a
     tool; ItemPickaxe.java:10 canHarvestBlock accepts any pickaxe on either -->

### Natural generation

[[Dungeon]] walls are cobblestone, as is one floor block in four.
<!-- src: WorldGenDungeons.java:43-46 -->

### Lava and water

Cobblestone [[Fluid#Lava and water|forms]] where [[Water|water]] touches flowing
[[Lava|lava]].
<!-- src: BlockFluid.java:247 checkForHarden, which turns lava with metadata 1 to
     4 into cobblestone when water is beside or above it -->

## Usage

### Crafting ingredient

{{used in|Cobblestone}}

### Smelting

{{smelting|Stone}}

## Data values

- Block ID: {{id|Cobblestone}}
- Translation key: `tile.stonebrick`
