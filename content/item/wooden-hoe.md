---
title: Wooden Hoe
description: The hoe made from wooden planks, which tills grass and dirt into farmland.
type: item
categories: [Items, Tools]
---

**Wooden Hoe** is the hoe made from [[Wooden Planks|wooden planks]].

## Obtaining

### Crafting

{{crafting|Wooden Hoe}}

The *Time to Farm!* [[Achievements|achievement]] is for crafting a wooden hoe.
<!-- src: SlotCrafting.java:25 onPickupFromSlot; AchievementList.java:39
     buildHoe; the name is achievement.buildHoe in lang/stats_US.lang -->

## Usage

A wooden hoe tills [[Grass|grass]] and [[Dirt|dirt]] into
[[Farmland#Obtaining|farmland]]. Each block tilled costs it 1
[[Durability|durability]].
<!-- src: ItemHoe.java:13 onItemUse, :22 damageItem(1) -->

It has a [[Mining#Tools|mining speed]] of 1, the same as a bare hand.
[[Mining#Tool wear|Mining]] costs it no durability.
<!-- src: ItemHoe.java overrides neither getStrVsBlock nor onBlockDestroyed -->

## Data values

- Item ID: {{id|Wooden Hoe}}
- Translation key: `item.hoeWood`
