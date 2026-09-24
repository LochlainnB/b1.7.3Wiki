---
title: Lapis Lazuli
description: The blue dye dropped by lapis lazuli ore.
type: item
categories: [Items]
---

**Lapis Lazuli** is the blue [[Dye|dye]] dropped by
[[Lapis Lazuli Ore|lapis lazuli ore]].

## Obtaining

### Breaking

[[Lapis Lazuli Ore|Lapis lazuli ore]] drops four to eight lapis lazuli when
[[Mining#Harvest levels|mined]] with a stone, iron or diamond pickaxe.
<!-- src: BlockOre.java:10-26 idDropped, quantityDropped 4 + nextInt(5),
     damageDropped 4; ItemPickaxe.java:16 canHarvestBlock -->

### Crafting

{{crafting|Lapis Lazuli}}

## Usage

### Dyeing

Used on a [[Sheep|sheep]], lapis lazuli [[Dye|dyes]] its wool blue.
<!-- src: ItemDye.java:80 saddleEntity; ItemDye.java:4 dyeColorNames[4] is
     "blue" -->

### Crafting ingredient

{{used in|Lapis Lazuli}}

## Data values

- Item ID: {{id|Lapis Lazuli}}
- Translation key: `item.dyePowder.blue`
