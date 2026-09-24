---
title: Iron Ore
description: The ore block smelted into iron ingots, mined with a stone pickaxe or better.
type: block
categories: [Blocks, Naturally generated, Ores]
---

**Iron Ore** is the ore block smelted into [[Iron Ingot|iron ingots]].

## Obtaining

### Natural generation

Iron ore generates in [[World Generation#Ores|veins]] of size 8, 20 per chunk,
from y=0 to y=63.
<!-- src: ChunkProviderGenerate.java:375-379 populate -->

### Breaking

Iron ore drops itself when [[Mining#Harvest levels|mined]] with a stone, iron or
diamond pickaxe. Mined with anything else, it drops nothing.
<!-- src: BlockOre.java:16 idDropped returns the block's own id;
     Material.java:114; ItemPickaxe.java:15 canHarvestBlock, harvest level 1
     or more -->

## Usage

### Smelting

{{used in|Iron Ore}}

## Data values

- Block ID: {{id|Iron Ore}}
- Translation key: `tile.oreIron`
