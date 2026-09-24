---
title: Golden Apple
description: A food crafted from an apple and eight blocks of gold, which restores a player to full health.
type: item
categories: [Items, Food]
---

A **golden apple** is a [[Food|food]] crafted from an [[Apple|apple]] and eight
[[Block of Gold|blocks of gold]].

## Obtaining

### Crafting

{{crafting|Golden Apple}}

### Dungeon chests

A [[Dungeon#Chest loot|dungeon chest]] draw gives a golden apple 1 time in
1,100.
<!-- src: WorldGenDungeons.java:124 pickCheckLootItem, one in eleven and then
     one in a hundred -->

## Usage

A golden apple is [[Food#Eating|eaten]] to restore 42 health. A player has at
most 20, so one always restores full health.
<!-- src: Item.java:340 ItemFood(66, 42, false); EntityLiving.java:296 heal
     caps at 20 -->

## Data values

- Item ID: {{id|Golden Apple}}
- Translation key: `item.appleGold`
