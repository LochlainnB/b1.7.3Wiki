---
title: Stone Hoe
description: The hoe made from cobblestone, which tills grass and dirt into farmland.
type: item
categories: [Items, Tools]
---

**Stone Hoe** is the hoe made from [[Cobblestone|cobblestone]].

## Obtaining

### Crafting

{{crafting|Stone Hoe}}

## Usage

A stone hoe tills [[Grass|grass]] and [[Dirt|dirt]] into
[[Farmland#Obtaining|farmland]]. Each block tilled costs it 1
[[Durability|durability]].
<!-- src: ItemHoe.java:13 onItemUse, :22 damageItem(1) -->

It has a [[Mining#Tools|mining speed]] of 1, the same as a bare hand.
[[Mining#Tool wear|Mining]] costs it no durability.
<!-- src: ItemHoe.java overrides neither getStrVsBlock nor onBlockDestroyed -->

## Data values

- Item ID: {{id|Stone Hoe}}
- Translation key: `item.hoeStone`
