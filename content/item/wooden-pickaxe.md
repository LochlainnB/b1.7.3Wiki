---
title: Wooden Pickaxe
description: The pickaxe made from wooden planks, which harvests coal ore but no other ore.
type: item
categories: [Items, Tools]
---

**Wooden Pickaxe** is the [[Mining#Tools|pickaxe]] made from
[[Wooden Planks|wooden planks]].

## Obtaining

### Crafting

{{crafting|Wooden Pickaxe}}

The *Time to Mine!* [[Achievements|achievement]] is for crafting a wooden
pickaxe.
<!-- src: SlotCrafting.java:21 onPickupFromSlot; AchievementList.java:36
     buildPickaxe; the name is achievement.buildPickaxe in lang/stats_US.lang -->

## Usage

A wooden pickaxe has a [[Mining#Tools|mining speed]] of 2 on the blocks a
pickaxe is effective against.
<!-- src: EnumToolMaterial.java:4 WOOD(0, 59, 2.0F, 0) -->

It has [[Mining#Harvest levels|harvest level]] 0, the same as a
[[Golden Pickaxe|golden pickaxe]]. It harvests [[Coal Ore|coal ore]] but no
other ore. It cannot harvest [[Obsidian|obsidian]], or a
[[Block of Iron|block of iron]], [[Block of Gold|gold]],
[[Block of Diamond|diamond]] or [[Lapis Lazuli Block|lapis lazuli]].
<!-- src: ItemPickaxe.java:10 canHarvestBlock -->

It [[Mining#Tool wear|wears out]] after 60 blocks.
<!-- src: EnumToolMaterial.java:4 maxUses 59; ItemTool.java:34
     onBlockDestroyed; ItemStack.java:127 damageItem breaks the tool once
     damage exceeds 59 -->

## Data values

- Item ID: {{id|Wooden Pickaxe}}
- Translation key: `item.pickaxeWood`
