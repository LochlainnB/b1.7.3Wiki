---
title: Wooden Shovel
description: The shovel made from wooden planks, with a mining speed of 2, lasting 60 blocks.
type: item
categories: [Items, Tools]
---

**Wooden Shovel** is the [[Mining#Tools|shovel]] made from
[[Wooden Planks|wooden planks]].

## Obtaining

### Crafting

{{crafting|Wooden Shovel}}

## Usage

A wooden shovel has a [[Mining#Tools|mining speed]] of 2 on the blocks a
shovel is effective against.
<!-- src: EnumToolMaterial.java:4 WOOD(0, 59, 2.0F, 0); ItemSpade.java:19 -->

It [[Mining#Drops|harvests]] [[Snow|snow]], as a layer and as a block.
<!-- src: ItemSpade.java:10 canHarvestBlock -->

It [[Mining#Tool wear|wears out]] after 60 blocks.
<!-- src: EnumToolMaterial.java:4 maxUses 59; ItemTool.java:34
     onBlockDestroyed; ItemStack.java:127 damageItem breaks the tool once
     damage exceeds 59 -->

## Data values

- Item ID: {{id|Wooden Shovel}}
- Translation key: `item.shovelWood`
