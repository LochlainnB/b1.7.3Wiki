---
title: Wooden Axe
description: The axe made from wooden planks, with a mining speed of 2, lasting 60 blocks.
type: item
categories: [Items, Tools]
---

**Wooden Axe** is the [[Mining#Tools|axe]] made from
[[Wooden Planks|wooden planks]].

## Obtaining

### Crafting

{{crafting|Wooden Axe}}

## Usage

A wooden axe has a [[Mining#Tools|mining speed]] of 2 on the blocks an axe is
effective against.
<!-- src: EnumToolMaterial.java:4 WOOD(0, 59, 2.0F, 0); ItemAxe.java:11 -->

It [[Mining#Tool wear|wears out]] after 60 blocks.
<!-- src: EnumToolMaterial.java:4 maxUses 59; ItemTool.java:34
     onBlockDestroyed; ItemStack.java:127 damageItem breaks the tool once
     damage exceeds 59 -->

## Data values

- Item ID: {{id|Wooden Axe}}
- Translation key: `item.hatchetWood`
