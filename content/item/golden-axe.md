---
title: Golden Axe
description: The axe made from gold ingots, the fastest and shortest-lived, with a mining speed of 12, lasting 33 blocks.
type: item
categories: [Items, Tools]
---

**Golden Axe** is the [[Mining#Tools|axe]] made from
[[Gold Ingot|gold ingots]].

## Obtaining

### Crafting

{{crafting|Golden Axe}}

## Usage

A golden axe has a [[Mining#Tools|mining speed]] of 12 on the blocks an axe is
effective against, the fastest of any axe.
<!-- src: EnumToolMaterial.java:8 GOLD(0, 32, 12.0F, 0); ItemAxe.java:11 -->

It [[Mining#Tool wear|wears out]] after 33 blocks, the fewest of any axe.
<!-- src: EnumToolMaterial.java:8 maxUses 32; ItemTool.java:34
     onBlockDestroyed; ItemStack.java:127 damageItem breaks the tool once
     damage exceeds 32 -->

## Data values

- Item ID: {{id|Golden Axe}}
- Translation key: `item.hatchetGold`
