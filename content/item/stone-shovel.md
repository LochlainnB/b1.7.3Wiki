---
title: Stone Shovel
description: The shovel made from cobblestone, with a mining speed of 4, lasting 132 blocks.
type: item
categories: [Items, Tools]
---

**Stone Shovel** is the [[Mining#Tools|shovel]] made from
[[Cobblestone|cobblestone]].

## Obtaining

### Crafting

{{crafting|Stone Shovel}}

## Usage

A stone shovel has a [[Mining#Tools|mining speed]] of 4 on the blocks a shovel
is effective against.
<!-- src: EnumToolMaterial.java:5 STONE(1, 131, 4.0F, 1); ItemSpade.java:19 -->

It [[Mining#Drops|harvests]] [[Snow|snow]], as a layer and as a block.
<!-- src: ItemSpade.java:10 canHarvestBlock -->

It [[Mining#Tool wear|wears out]] after 132 blocks.
<!-- src: EnumToolMaterial.java:5 maxUses 131; ItemTool.java:34
     onBlockDestroyed; ItemStack.java:127 damageItem breaks the tool once
     damage exceeds 131 -->

## Data values

- Item ID: {{id|Stone Shovel}}
- Translation key: `item.shovelStone`
