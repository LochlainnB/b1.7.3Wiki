---
title: Stone Axe
description: The axe made from cobblestone, with a mining speed of 4, lasting 132 blocks.
type: item
categories: [Items, Tools]
---

**Stone Axe** is the [[Mining#Tools|axe]] made from
[[Cobblestone|cobblestone]].

## Obtaining

### Crafting

{{crafting|Stone Axe}}

## Usage

A stone axe has a [[Mining#Tools|mining speed]] of 4 on the blocks an axe is
effective against.
<!-- src: EnumToolMaterial.java:5 STONE(1, 131, 4.0F, 1); ItemAxe.java:11 -->

It [[Mining#Tool wear|wears out]] after 132 blocks.
<!-- src: EnumToolMaterial.java:5 maxUses 131; ItemTool.java:34
     onBlockDestroyed; ItemStack.java:127 damageItem breaks the tool once
     damage exceeds 131 -->

## Data values

- Item ID: {{id|Stone Axe}}
- Translation key: `item.hatchetStone`
