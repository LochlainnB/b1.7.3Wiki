---
title: String
description: An item dropped by spiders and cobwebs, and found in dungeon chests, used to make bows, fishing rods and wool.
type: item
categories: [Items, Materials]
---

**String** is an item dropped by [[Spider|spiders]] and [[Cobweb|cobwebs]].

## Obtaining

### Mob drops

[[Spider#Drops|Spiders]] drop string when they die.
<!-- src: EntitySpider.java:70 getDropItemId -->

### Breaking

A [[Cobweb|cobweb]] broken with a sword or [[Shears|shears]] drops one string.
Broken any other way, it [[Mining#Drops|drops nothing]].
<!-- src: BlockWeb.java:30 idDropped; Material.java:136 web is setNoHarvest;
     ItemSword.java:36 and ItemShears.java:18 canHarvestBlock -->

### Dungeon chests

A [[Dungeon#Chest loot|dungeon chest]] draw gives 1–4 string 1 time in 11.
<!-- src: WorldGenDungeons.java:120 pickCheckLootItem -->

## Usage

### Crafting ingredient

{{used in|String}}

## Data values

- Item ID: {{id|String}}
- Translation key: `item.string`
