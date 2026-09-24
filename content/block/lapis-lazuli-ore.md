---
title: Lapis Lazuli Ore
description: The ore block that drops four to eight lapis lazuli, mined with a stone pickaxe or better.
type: block
categories: [Blocks, Naturally generated, Ores]
---

**Lapis Lazuli Ore** is the ore block that drops [[Lapis Lazuli|lapis lazuli]].

## Obtaining

### Natural generation

Lapis lazuli ore generates in [[World Generation#Ores|veins]] of size 6, 1 per
chunk, from y=0 to y=30. Veins are most common around y=15.
<!-- src: ChunkProviderGenerate.java:403-407 populate, whose y is
     nextInt(16) + nextInt(16) -->

## Usage

### Breaking

Lapis lazuli ore drops four to eight [[Lapis Lazuli|lapis lazuli]] when
[[Mining#Harvest levels|mined]] with a stone, iron or diamond pickaxe. Mined
with anything else, it drops nothing. It never drops itself.
<!-- src: BlockOre.java:10-26 idDropped, quantityDropped 4 + nextInt(5),
     damageDropped 4; Material.java:114; ItemPickaxe.java:16 canHarvestBlock,
     harvest level 1 or more -->

## Data values

- Block ID: {{id|Lapis Lazuli Ore}}
- Translation key: `tile.oreLapis`
