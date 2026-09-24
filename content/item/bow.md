---
title: Bow
description: A weapon crafted from sticks and string that fires arrows from the player's inventory, and never breaks.
type: item
categories: [Items, Weapons]
---

A **bow** is a weapon that fires [[Arrow|arrows]].

## Obtaining

A bow can only be crafted. [[Skeleton|Skeletons]] hold bows, but never drop
them.
<!-- src: EntitySkeleton.java:88 defaultHeldItem; :67 dropFewItems drops only
     arrows and bones; no dungeon loot or other drop names Item.bow -->

### Crafting

{{crafting|Bow}}

## Usage

### Firing

Using a bow fires an [[Arrow|arrow]] from the player's inventory, and uses up
the arrow. With no arrows, nothing happens.
<!-- src: ItemBow.java:10 consumeInventoryItem, which gates the shot -->

A bow is not drawn back. It fires the moment it is used, and every arrow
leaves at the same speed.
<!-- src: ItemBow.java:9 onItemRightClick spawns the arrow at once;
     EntityArrow.java:44 setArrowHeading with a fixed speed of 1.5 -->

Holding the use button fires an arrow every 5 ticks, 4 a second. Each fresh
click fires one at once.
<!-- src: Minecraft.java:1017 repeats clickMouse(1) while the button is held,
     every ticksPerSecond / 4 ticks against a 20-tick timer (:114); :1117
     runs it on each press -->

Each arrow deals [[Damage#Mob attacks|4 damage]].
<!-- src: EntityArrow.java:163 attackEntityFrom(owner, 4) -->

A bow has no [[Durability|durability]], and never breaks.
<!-- src: Item.java:279 registers it without setMaxDamage; Item.java:116
     maxDamage defaults to 0, so :194 isDamageable is false -->

### Crafting ingredient

{{used in|Bow}}

## Data values

- Item ID: {{id|Bow}}
- Translation key: `item.bow`
