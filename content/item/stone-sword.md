---
title: Stone Sword
description: The sword made from cobblestone, lasting 132 hits.
type: item
categories: [Items, Weapons]
---

**Stone Sword** is the [[Damage#Weapons|sword]] made from
[[Cobblestone|cobblestone]].

## Obtaining

### Crafting

{{crafting|Stone Sword}}

## Usage

A stone sword has a [[Mining#Tools|mining speed]] of 1.5 on every block, and 15
on [[Cobweb|cobweb]]. It [[Mining#Drops|harvests]] cobweb.
<!-- src: ItemSword.java:13 getStrVsBlock; ItemSword.java:35 canHarvestBlock -->

It wears out after 132 [[Damage#Weapons|hits]], or 66
[[Mining#Tool wear|blocks mined]].
<!-- src: ItemSword.java:17 hitEntity damageItem(1); ItemSword.java:22
     onBlockDestroyed damageItem(2); EnumToolMaterial.java:5 maxUses 131;
     ItemStack.java:127 damageItem breaks the sword once damage exceeds 131 -->

## Data values

- Item ID: {{id|Stone Sword}}
- Translation key: `item.swordStone`
