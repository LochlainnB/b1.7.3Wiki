---
title: Golden Pickaxe
description: The pickaxe made from gold ingots, the fastest and shortest-lived, which harvests coal ore but no other ore.
type: item
categories: [Items, Tools]
---

**Golden Pickaxe** is the [[Mining#Tools|pickaxe]] made from
[[Gold Ingot|gold ingots]].

## Obtaining

### Crafting

{{crafting|Golden Pickaxe}}

## Usage

A golden pickaxe has a [[Mining#Tools|mining speed]] of 12 on the blocks a
pickaxe is effective against, the fastest of any pickaxe.
<!-- src: EnumToolMaterial.java:8 GOLD(0, 32, 12.0F, 0) -->

It has [[Mining#Harvest levels|harvest level]] 0, the same as a
[[Wooden Pickaxe|wooden pickaxe]]. It harvests [[Coal Ore|coal ore]] but no
other ore. It cannot harvest [[Obsidian|obsidian]], or a
[[Block of Iron|block of iron]], [[Block of Gold|gold]],
[[Block of Diamond|diamond]] or [[Lapis Lazuli Block|lapis lazuli]].
<!-- src: ItemPickaxe.java:10 canHarvestBlock -->

## Data values

- Item ID: {{id|Golden Pickaxe}}
- Translation key: `item.pickaxeGold`
