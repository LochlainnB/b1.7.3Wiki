---
title: Diamond Hoe
description: The hoe made from diamonds, which tills grass and dirt into farmland, lasting 1562 blocks.
type: item
categories: [Items, Tools]
---

**Diamond Hoe** is the hoe made from [[Diamond|diamonds]].

## Obtaining

### Crafting

{{crafting|Diamond Hoe}}

## Usage

Using a diamond hoe on [[Grass|grass]] or [[Dirt|dirt]] turns it into
[[Farmland|farmland]]. Grass must have air above it, and cannot be tilled from
below. Dirt can be tilled from any side, even with a block on top.
<!-- src: ItemHoe.java:13 onItemUse; var7 is the face used, 0 the underside,
     and var9 the block above. The grass tests do not apply to dirt. -->

It has a [[Mining#Tools|mining speed]] of 1, the same as a bare hand.
[[Mining#Tool wear|Mining]] costs it no durability.
<!-- src: ItemHoe.java overrides neither getStrVsBlock nor onBlockDestroyed -->

It wears out after tilling 1562 blocks.
<!-- src: ItemHoe.java:22 damageItem(1) per block tilled;
     EnumToolMaterial.java:7 maxUses 1561; ItemStack.java:127 damageItem breaks
     the tool once damage exceeds 1561 -->

## Data values

- Item ID: {{id|Diamond Hoe}}
- Translation key: `item.hoeDiamond`
