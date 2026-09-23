---
title: Wooden Hoe
description: The hoe made from wooden planks, which tills grass and dirt into farmland, lasting 60 blocks.
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

Using a wooden hoe on [[Grass|grass]] or [[Dirt|dirt]] turns it into
[[Farmland|farmland]]. Grass must have air above it, and cannot be tilled from
below. Dirt can be tilled from any side, even with a block on top.
<!-- src: ItemHoe.java:13 onItemUse; var7 is the face used, 0 the underside,
     and var9 the block above. The grass tests do not apply to dirt. -->

It has a [[Mining#Tools|mining speed]] of 1, the same as a bare hand.
[[Mining#Tool wear|Mining]] costs it no durability.
<!-- src: ItemHoe.java overrides neither getStrVsBlock nor onBlockDestroyed -->

It wears out after tilling 60 blocks.
<!-- src: ItemHoe.java:22 damageItem(1) per block tilled;
     EnumToolMaterial.java:4 maxUses 59; ItemStack.java:127 damageItem breaks
     the tool once damage exceeds 59 -->

## Data values

- Item ID: {{id|Wooden Hoe}}
- Translation key: `item.hoeWood`
