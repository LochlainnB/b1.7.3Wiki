---
title: Gold Ore
description: The ore block smelted into gold ingots, mined with an iron pickaxe or better.
type: block
categories: [Blocks, Naturally generated, Ores]
---

**Gold Ore** is the ore block smelted into [[Gold Ingot|gold ingots]].

## Obtaining

### Natural generation

Gold ore generates in [[World Generation#Ores|veins]] of size 8, 2 per chunk,
from y=0 to y=31.
<!-- src: ChunkProviderGenerate.java:382-386 populate -->

### Breaking

Gold ore drops itself when [[Mining#Harvest levels|mined]] with an iron or
diamond pickaxe. Mined with anything else, it drops nothing.
<!-- src: BlockOre.java:16 idDropped returns the block's own id;
     Material.java:114; ItemPickaxe.java:14 canHarvestBlock, harvest level 2
     or more -->

## Usage

### Smelting

{{used in|Gold Ore}}

## Data values

- Block ID: {{id|Gold Ore}}
- Translation key: `tile.oreGold`
