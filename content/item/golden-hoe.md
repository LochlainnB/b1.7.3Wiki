---
title: Golden Hoe
description: The hoe made from gold ingots, which tills grass and dirt into farmland.
type: item
categories: [Items, Tools]
---

**Golden Hoe** is the hoe made from [[Gold Ingot|gold ingots]].

## Obtaining

### Crafting

{{crafting|Golden Hoe}}

## Usage

A golden hoe tills [[Grass|grass]] and [[Dirt|dirt]] into
[[Farmland#Obtaining|farmland]]. Each block tilled costs it 1
[[Durability|durability]].
<!-- src: ItemHoe.java:13 onItemUse, :22 damageItem(1) -->

It has a [[Mining#Tools|mining speed]] of 1, the same as a bare hand.
[[Mining#Tool wear|Mining]] costs it no durability.
<!-- src: ItemHoe.java overrides neither getStrVsBlock nor onBlockDestroyed -->

## Data values

- Item ID: {{id|Golden Hoe}}
- Translation key: `item.hoeGold`
