---
title: Iron Hoe
description: The hoe made from iron ingots, which tills grass and dirt into farmland.
type: item
categories: [Items, Tools]
---

**Iron Hoe** is the hoe made from [[Iron Ingot|iron ingots]].

## Obtaining

### Crafting

{{crafting|Iron Hoe}}

## Usage

An iron hoe tills [[Grass|grass]] and [[Dirt|dirt]] into
[[Farmland#Obtaining|farmland]]. Each block tilled costs it 1
[[Durability|durability]].
<!-- src: ItemHoe.java:13 onItemUse, :22 damageItem(1) -->

It has a [[Mining#Tools|mining speed]] of 1, the same as a bare hand.
[[Mining#Tool wear|Mining]] costs it no durability.
<!-- src: ItemHoe.java overrides neither getStrVsBlock nor onBlockDestroyed -->

## Data values

- Item ID: {{id|Iron Hoe}}
- Translation key: `item.hoeIron`
