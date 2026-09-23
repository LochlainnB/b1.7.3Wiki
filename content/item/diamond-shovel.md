---
title: Diamond Shovel
description: The shovel made from diamonds, with a mining speed of 8, lasting 1562 blocks.
type: item
categories: [Items, Tools]
---

**Diamond Shovel** is the [[Mining#Tools|shovel]] made from
[[Diamond|diamonds]].

## Obtaining

### Crafting

{{crafting|Diamond Shovel}}

## Usage

A diamond shovel has a [[Mining#Tools|mining speed]] of 8 on the blocks a
shovel is effective against.
<!-- src: EnumToolMaterial.java:7 EMERALD(3, 1561, 8.0F, 3); ItemSpade.java:19 -->

It [[Mining#Drops|harvests]] [[Snow|snow]], as a layer and as a block.
<!-- src: ItemSpade.java:10 canHarvestBlock -->

It [[Mining#Tool wear|wears out]] after 1562 blocks.
<!-- src: EnumToolMaterial.java:7 maxUses 1561; ItemTool.java:34
     onBlockDestroyed; ItemStack.java:127 damageItem breaks the tool once
     damage exceeds 1561 -->

## Data values

- Item ID: {{id|Diamond Shovel}}
- Translation key: `item.shovelDiamond`
