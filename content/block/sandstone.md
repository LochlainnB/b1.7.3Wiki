---
title: Sandstone
description: A block found under the sand of deserts and beaches, and crafted from four sand.
type: block
categories: [Blocks, Building blocks, Naturally generated]
---

**Sandstone** is a block found under [[Sand|sand]], and crafted from it.

## Obtaining

### Breaking

Sandstone drops itself when [[Mining|mined]] with any pickaxe, and nothing
otherwise. A pickaxe breaks it fastest.
<!-- src: Block.java:616 Material.rock via BlockSandStone.java:5;
     Material.java:114 rock setNoHarvest; ItemPickaxe.java:18 canHarvestBlock;
     ItemPickaxe.java:41 blocksEffectiveAgainst lists Block.sandStone -->

### Crafting

{{crafting|Sandstone}}

### Natural generation

Wherever the [[World Generation#Surface|surface pass]] lays sand as filler, in
the [[Desert]] and on beaches, 0 to 3 blocks of sandstone lie under the sand.
<!-- src: ChunkProviderGenerate.java:175-:178, nextInt(4) blocks once the sand
     filler runs out -->

## Usage

### Crafting ingredient

{{used in|Sandstone}}

## Data values

- Block ID: {{id|Sandstone}}
- Translation key: `tile.sandStone`
