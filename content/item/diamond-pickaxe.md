---
title: Diamond Pickaxe
description: The pickaxe made from diamonds, the only one that harvests obsidian.
type: item
categories: [Items, Tools]
---

**Diamond Pickaxe** is the [[Mining#Tools|pickaxe]] made from
[[Diamond|diamonds]].

## Obtaining

### Crafting

{{crafting|Diamond Pickaxe}}

## Usage

A diamond pickaxe has a [[Mining#Tools|mining speed]] of 8 on the blocks a
pickaxe is effective against.
<!-- src: EnumToolMaterial.java:7 EMERALD(3, 1561, 8.0F, 3) -->

It has [[Mining#Harvest levels|harvest level]] 3. It harvests every ore. It is
the only pickaxe that harvests [[Obsidian|obsidian]].
<!-- src: ItemPickaxe.java:11 canHarvestBlock, harvestLevel == 3 for obsidian -->

Obsidian is not among the blocks a pickaxe is effective against. A diamond
pickaxe mines it at speed 1, in 301 ticks, just over 15 seconds.
<!-- src: ItemPickaxe.java:41 blocksEffectiveAgainst has no Block.obsidian;
     Block.java:327 blockStrength, 1 / (10 * 30) per tick at hardness 10,
     which a float total of 300 steps leaves just short of 1
     (PlayerControllerSP.java:9) -->

## Data values

- Item ID: {{id|Diamond Pickaxe}}
- Translation key: `item.pickaxeDiamond`
