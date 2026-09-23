---
title: Iron Shovel
description: The shovel made from iron ingots, with a mining speed of 6, lasting 251 blocks.
type: item
categories: [Items, Tools]
---

**Iron Shovel** is the [[Mining#Tools|shovel]] made from
[[Iron Ingot|iron ingots]].

## Obtaining

### Crafting

{{crafting|Iron Shovel}}

## Usage

An iron shovel has a [[Mining#Tools|mining speed]] of 6 on the blocks a shovel
is effective against.
<!-- src: EnumToolMaterial.java:6 IRON(2, 250, 6.0F, 2); ItemSpade.java:19 -->

It [[Mining#Drops|harvests]] [[Snow|snow]], as a layer and as a block.
<!-- src: ItemSpade.java:10 canHarvestBlock -->

It [[Mining#Tool wear|wears out]] after 251 blocks.
<!-- src: EnumToolMaterial.java:6 maxUses 250; ItemTool.java:34
     onBlockDestroyed; ItemStack.java:127 damageItem breaks the tool once
     damage exceeds 250 -->

## Data values

- Item ID: {{id|Iron Shovel}}
- Translation key: `item.shovelIron`
