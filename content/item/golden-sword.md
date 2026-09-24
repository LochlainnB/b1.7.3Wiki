---
title: Golden Sword
description: The sword made from gold ingots, which deals the same damage as a wooden sword.
type: item
categories: [Items, Weapons]
---

**Golden Sword** is the [[Damage#Weapons|sword]] made from
[[Gold Ingot|gold ingots]]. [[Pig Zombie|Pig zombies]] carry one, but never
drop it.
<!-- src: EntityPigZombie.java:89 getHeldItem returns the golden sword set at
     :94; EntityPigZombie.java:85 getDropItemId returns the cooked porkchop -->

## Obtaining

### Crafting

{{crafting|Golden Sword}}

## Usage

A golden sword deals the same [[Damage#Weapons|damage]] as a
[[Wooden Sword|wooden sword]].
<!-- src: ItemSword.java:10 weaponDamage = 4 + material * 2;
     EnumToolMaterial.java:4 and :8 give WOOD and GOLD damageVsEntity 0 -->

It has a [[Mining#Tools|mining speed]] of 1.5 on every block, and 15 on
[[Cobweb|cobweb]]. It [[Mining#Drops|harvests]] cobweb.
<!-- src: ItemSword.java:13 getStrVsBlock; ItemSword.java:35 canHarvestBlock -->

## Data values

- Item ID: {{id|Golden Sword}}
- Translation key: `item.swordGold`
