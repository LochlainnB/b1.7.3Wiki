---
title: Saddle
description: An item found in dungeon chests, put on a pig so that a player can ride it.
type: item
categories: [Items, Transportation]
---

A **saddle** is an item put on a [[Pig|pig]] so that a player can ride it.

## Obtaining

### Dungeon chests

A [[Dungeon#Chest loot|dungeon chest]] draw gives a saddle 1 time in 11. A
saddle cannot be crafted.
<!-- src: WorldGenDungeons.java:107 pickCheckLootItem; no recipe in
     CraftingManager.java produces Item.saddle -->

## Usage

Using a saddle on a [[Pig|pig]], or hitting the pig with it, saddles it and uses
up the saddle. No other mob takes one.
<!-- src: ItemSaddle.java:9 saddleEntity acts on EntityPig alone; :20 hitEntity
     calls it too -->

## Data values

- Item ID: {{id|Saddle}}
- Translation key: `item.saddle`
