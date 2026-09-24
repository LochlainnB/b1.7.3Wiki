---
title: Wooden Sword
description: The sword made from wooden planks, which deals the same damage as a golden sword.
type: item
categories: [Items, Weapons]
---

**Wooden Sword** is the [[Damage#Weapons|sword]] made from
[[Wooden Planks|wooden planks]].

## Obtaining

### Crafting

{{crafting|Wooden Sword}}

The *Time to Strike!* [[Achievements|achievement]] is for crafting a wooden
sword.
<!-- src: SlotCrafting.java:33 onPickupFromSlot; AchievementList.java:45
     buildSword; the name is achievement.buildSword in lang/stats_US.lang -->

## Usage

A wooden sword deals the same [[Damage#Weapons|damage]] as a
[[Golden Sword|golden sword]].
<!-- src: ItemSword.java:10 weaponDamage = 4 + material * 2;
     EnumToolMaterial.java:4 and :8 give WOOD and GOLD damageVsEntity 0 -->

It has a [[Mining#Tools|mining speed]] of 1.5 on every block, and 15 on
[[Cobweb|cobweb]]. It [[Mining#Drops|harvests]] cobweb.
<!-- src: ItemSword.java:13 getStrVsBlock; ItemSword.java:35 canHarvestBlock -->

## Data values

- Item ID: {{id|Wooden Sword}}
- Translation key: `item.swordWood`
