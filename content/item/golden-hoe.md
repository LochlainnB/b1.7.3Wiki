---
title: Golden Hoe
description: The hoe made from gold ingots, which tills grass and dirt into farmland, lasting 33 blocks, the fewest of any hoe.
type: item
categories: [Items, Tools]
---

**Golden Hoe** is the hoe made from [[Gold Ingot|gold ingots]].

## Obtaining

### Crafting

{{crafting|Golden Hoe}}

## Usage

Using a golden hoe on [[Grass|grass]] or [[Dirt|dirt]] turns it into
[[Farmland|farmland]]. Grass must have air above it, and cannot be tilled from
below. Dirt can be tilled from any side, even with a block on top.
<!-- src: ItemHoe.java:13 onItemUse; var7 is the face used, 0 the underside,
     and var9 the block above. The grass tests do not apply to dirt. -->

It has a [[Mining#Tools|mining speed]] of 1, the same as a bare hand.
[[Mining#Tool wear|Mining]] costs it no durability.
<!-- src: ItemHoe.java overrides neither getStrVsBlock nor onBlockDestroyed -->

It wears out after tilling 33 blocks, the fewest of any hoe.
<!-- src: ItemHoe.java:22 damageItem(1) per block tilled;
     EnumToolMaterial.java:8 maxUses 32; ItemStack.java:127 damageItem breaks
     the tool once damage exceeds 32 -->

## Data values

- Item ID: {{id|Golden Hoe}}
- Translation key: `item.hoeGold`
