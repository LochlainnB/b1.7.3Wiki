---
title: Diamond Axe
description: The axe made from diamonds, with a mining speed of 8, lasting 1562 blocks.
type: item
categories: [Items, Tools]
---

**Diamond Axe** is the [[Mining#Tools|axe]] made from [[Diamond|diamonds]].

## Obtaining

### Crafting

{{crafting|Diamond Axe}}

## Usage

A diamond axe has a [[Mining#Tools|mining speed]] of 8 on the blocks an axe is
effective against.
<!-- src: EnumToolMaterial.java:7 EMERALD(3, 1561, 8.0F, 3); ItemAxe.java:11 -->

It [[Mining#Tool wear|wears out]] after 1562 blocks.
<!-- src: EnumToolMaterial.java:7 maxUses 1561; ItemTool.java:34
     onBlockDestroyed; ItemStack.java:127 damageItem breaks the tool once
     damage exceeds 1561 -->

## Data values

- Item ID: {{id|Diamond Axe}}
- Translation key: `item.hatchetDiamond`
