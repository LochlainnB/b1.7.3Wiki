---
title: Iron Axe
description: The axe made from iron ingots, with a mining speed of 6, lasting 251 blocks.
type: item
categories: [Items, Tools]
---

**Iron Axe** is the [[Mining#Tools|axe]] made from
[[Iron Ingot|iron ingots]].

## Obtaining

### Crafting

{{crafting|Iron Axe}}

## Usage

An iron axe has a [[Mining#Tools|mining speed]] of 6 on the blocks an axe is
effective against.
<!-- src: EnumToolMaterial.java:6 IRON(2, 250, 6.0F, 2); ItemAxe.java:11 -->

It [[Mining#Tool wear|wears out]] after 251 blocks.
<!-- src: EnumToolMaterial.java:6 maxUses 250; ItemTool.java:34
     onBlockDestroyed; ItemStack.java:127 damageItem breaks the tool once
     damage exceeds 250 -->

## Data values

- Item ID: {{id|Iron Axe}}
- Translation key: `item.hatchetIron`
