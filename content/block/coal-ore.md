---
title: Coal Ore
description: The ore block that drops coal, found in veins at every height.
type: block
categories: [Blocks, Naturally generated, Ores]
---

**Coal Ore** is the ore block that drops [[Coal|coal]].

## Obtaining

### Natural generation

Coal ore generates in [[World Generation#Ores|veins]] of size 16, 20 per
chunk, from y=0 to y=127.
<!-- src: ChunkProviderGenerate.java:368-372 populate -->

## Usage

### Breaking

Coal ore drops one [[Coal|coal]] when [[Mining#Harvest levels|mined]] with any
pickaxe. Mined with anything else, it drops nothing. It never drops itself.
<!-- src: BlockOre.java:10-22 idDropped, quantityDropped; Material.java:114 sets
     rock as needing a tool; ItemPickaxe.java:18 canHarvestBlock accepts any
     pickaxe on other rock -->

## Data values

- Block ID: {{id|Coal Ore}}
- Translation key: `tile.oreCoal`
