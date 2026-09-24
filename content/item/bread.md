---
title: Bread
description: A food crafted from three wheat, which restores 5 health and is found in dungeon chests.
type: item
categories: [Items, Food]
---

**Bread** is a [[Food|food]] crafted from [[Wheat|wheat]].

## Obtaining

### Crafting

{{crafting|Bread}}

The *Bake Bread* [[Achievements|achievement]] is for crafting bread.
<!-- src: SlotCrafting.java:27 onPickupFromSlot; AchievementList.java:40
     makeBread -->

### Dungeon chests

A [[Dungeon#Chest loot|dungeon chest]] draw gives one bread 1 time in 11.
<!-- src: WorldGenDungeons.java:114 pickCheckLootItem -->

## Usage

Bread is [[Food#Eating|eaten]] to restore 5 health.
<!-- src: Item.java:315 ItemFood(41, 5, false) -->

## Data values

- Item ID: {{id|Bread}}
- Translation key: `item.bread`
