---
title: Diamond Sword
description: The sword made from diamonds, lasting 1562 hits.
type: item
categories: [Items, Weapons]
---

**Diamond Sword** is the [[Damage#Weapons|sword]] made from
[[Diamond|diamonds]].

## Obtaining

### Crafting

{{crafting|Diamond Sword}}

## Usage

A diamond sword has a [[Mining#Tools|mining speed]] of 1.5 on every block, and
15 on [[Cobweb|cobweb]]. It [[Mining#Drops|harvests]] cobweb.
<!-- src: ItemSword.java:13 getStrVsBlock; ItemSword.java:35 canHarvestBlock -->

It wears out after 1562 [[Damage#Weapons|hits]], or 781
[[Mining#Tool wear|blocks mined]].
<!-- src: ItemSword.java:17 hitEntity damageItem(1); ItemSword.java:22
     onBlockDestroyed damageItem(2); EnumToolMaterial.java:7 maxUses 1561;
     ItemStack.java:127 damageItem breaks the sword once damage exceeds 1561 -->

## Data values

- Item ID: {{id|Diamond Sword}}
- Translation key: `item.swordDiamond`
