---
title: Shears
description: The iron tool that shears sheep and collects leaves and cobweb, lasting 239 uses.
type: item
categories: [Items, Tools]
---

**Shears** are a tool made from [[Iron Ingot|iron ingots]], used to shear
[[Sheep|sheep]].

## Obtaining

### Crafting

{{crafting|Shears}}

## Usage

Shears act on:

- [[Sheep]], which they shear
- [[Leaves]], which they break at a [[Mining#Tools|mining speed]] of 15 and
  collect
- [[Cobweb]], which they break at a mining speed of 15 and
  [[Mining#Drops|harvest]]
- [[Wool]], which they break at a mining speed of 5

<!-- src: EntitySheep.java:36 interact; BlockLeaves.java:164 harvestBlock;
     ItemShears.java:22 getStrVsBlock; ItemShears.java:18 canHarvestBlock -->

They [[Mining#Tool wear|wear out]] after 239 uses, counting each leaf block,
cobweb and sheep sheared. Breaking any other block costs them nothing.
<!-- src: ItemShears.java:7 setMaxDamage(238); ItemShears.java:10
     onBlockDestroyed damages only on leaves and web; EntitySheep.java:49
     damageItem(1) per shearing; ItemStack.java:127 damageItem breaks the
     shears once damage exceeds 238 -->

## Data values

- Item ID: {{id|Shears}}
- Translation key: `item.shears`
