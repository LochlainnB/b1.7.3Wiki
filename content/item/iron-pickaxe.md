---
title: Iron Pickaxe
description: The pickaxe made from iron ingots, which harvests every ore but not obsidian.
type: item
categories: [Items, Tools]
---

**Iron Pickaxe** is the [[Mining#Tools|pickaxe]] made from
[[Iron Ingot|iron ingots]].

## Obtaining

### Crafting

{{crafting|Iron Pickaxe}}

## Usage

An iron pickaxe has a [[Mining#Tools|mining speed]] of 6 on the blocks a
pickaxe is effective against.
<!-- src: EnumToolMaterial.java:6 IRON(2, 250, 6.0F, 2) -->

It has [[Mining#Harvest levels|harvest level]] 2. It harvests every ore. It
cannot harvest [[Obsidian|obsidian]].
<!-- src: ItemPickaxe.java:10 canHarvestBlock -->

It [[Mining#Tool wear|wears out]] after 251 blocks.
<!-- src: EnumToolMaterial.java:6 maxUses 250; ItemTool.java:34
     onBlockDestroyed; ItemStack.java:127 damageItem breaks the tool once
     damage exceeds 250 -->

## Data values

- Item ID: {{id|Iron Pickaxe}}
- Translation key: `item.pickaxeIron`
