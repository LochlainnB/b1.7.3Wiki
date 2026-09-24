---
title: Bricks
description: A building block crafted from four brick items, which needs a pickaxe to drop.
type: block
categories: [Blocks, Building blocks]
---

**Bricks** are a building block crafted from four [[Brick|brick]] items.

## Obtaining

### Breaking

Bricks drop themselves when [[Mining|mined]] with any pickaxe, and nothing
otherwise.
<!-- src: Block.java:637 Material.rock; Material.java:114 rock setNoHarvest;
     ItemPickaxe.java:18 canHarvestBlock -->

A pickaxe is not [[Mining#What each tool is effective against|effective
against]] bricks, so every pickaxe takes 3 seconds to mine them.
<!-- src: ItemPickaxe.java:41 blocksEffectiveAgainst has no Block.brick;
     Block.java:327 blockStrength, hardness 2 × 30 = 60 ticks at speed 1 -->

### Crafting

{{crafting|Bricks}}

## Data values

- Block ID: {{id|Bricks}}
- Translation key: `tile.brick`
