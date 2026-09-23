---
title: Iron Sword
description: The sword made from iron ingots, lasting 251 hits.
type: item
categories: [Items, Weapons]
---

**Iron Sword** is the [[Damage#Weapons|sword]] made from
[[Iron Ingot|iron ingots]].

## Obtaining

### Crafting

{{crafting|Iron Sword}}

## Usage

An iron sword has a [[Mining#Tools|mining speed]] of 1.5 on every block, and 15
on [[Cobweb|cobweb]]. It [[Mining#Drops|harvests]] cobweb.
<!-- src: ItemSword.java:13 getStrVsBlock; ItemSword.java:35 canHarvestBlock -->

It wears out after 251 [[Damage#Weapons|hits]], or 126
[[Mining#Tool wear|blocks mined]].
<!-- src: ItemSword.java:17 hitEntity damageItem(1); ItemSword.java:22
     onBlockDestroyed damageItem(2); EnumToolMaterial.java:6 maxUses 250;
     ItemStack.java:127 damageItem breaks the sword once damage exceeds 250,
     which two points a block first passes on the 126th -->

## Data values

- Item ID: {{id|Iron Sword}}
- Translation key: `item.swordIron`
