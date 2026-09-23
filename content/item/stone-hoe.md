---
title: Stone Hoe
description: The hoe made from cobblestone, which tills grass and dirt into farmland, lasting 132 blocks.
type: item
categories: [Items, Tools]
---

**Stone Hoe** is the hoe made from [[Cobblestone|cobblestone]].

## Obtaining

### Crafting

{{crafting|Stone Hoe}}

## Usage

Using a stone hoe on [[Grass|grass]] or [[Dirt|dirt]] turns it into
[[Farmland|farmland]]. Grass must have air above it, and cannot be tilled from
below. Dirt can be tilled from any side, even with a block on top.
<!-- src: ItemHoe.java:13 onItemUse; var7 is the face used, 0 the underside,
     and var9 the block above. The grass tests do not apply to dirt. -->

It has a [[Mining#Tools|mining speed]] of 1, the same as a bare hand.
[[Mining#Tool wear|Mining]] costs it no durability.
<!-- src: ItemHoe.java overrides neither getStrVsBlock nor onBlockDestroyed -->

It wears out after tilling 132 blocks.
<!-- src: ItemHoe.java:22 damageItem(1) per block tilled;
     EnumToolMaterial.java:5 maxUses 131; ItemStack.java:127 damageItem breaks
     the tool once damage exceeds 131 -->

## Data values

- Item ID: {{id|Stone Hoe}}
- Translation key: `item.hoeStone`
