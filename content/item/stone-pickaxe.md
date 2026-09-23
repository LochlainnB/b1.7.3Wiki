---
title: Stone Pickaxe
description: The pickaxe made from cobblestone, which harvests coal, iron and lapis lazuli ore but no other ore.
type: item
categories: [Items, Tools]
---

**Stone Pickaxe** is the [[Mining#Tools|pickaxe]] made from
[[Cobblestone|cobblestone]].

## Obtaining

### Crafting

{{crafting|Stone Pickaxe}}

The *Getting an Upgrade* [[Achievements|achievement]] is for crafting a stone
pickaxe. No other pickaxe counts.
<!-- src: SlotCrafting.java:31 onPickupFromSlot tests pickaxeStone alone;
     AchievementList.java:42 buildBetterPickaxe; the name is
     achievement.buildBetterPickaxe in lang/stats_US.lang -->

## Usage

A stone pickaxe has a [[Mining#Tools|mining speed]] of 4 on the blocks a
pickaxe is effective against.
<!-- src: EnumToolMaterial.java:5 STONE(1, 131, 4.0F, 1) -->

It has [[Mining#Harvest levels|harvest level]] 1. It harvests
[[Coal Ore|coal]], [[Iron Ore|iron]] and [[Lapis Lazuli Ore|lapis lazuli]] ore,
but no other ore. It cannot harvest [[Obsidian|obsidian]], or a
[[Block of Gold|block of gold]] or [[Block of Diamond|diamond]].
<!-- src: ItemPickaxe.java:10 canHarvestBlock -->

It [[Mining#Tool wear|wears out]] after 132 blocks.
<!-- src: EnumToolMaterial.java:5 maxUses 131; ItemTool.java:34
     onBlockDestroyed; ItemStack.java:127 damageItem breaks the tool once
     damage exceeds 131 -->

## Data values

- Item ID: {{id|Stone Pickaxe}}
- Translation key: `item.pickaxeStone`
