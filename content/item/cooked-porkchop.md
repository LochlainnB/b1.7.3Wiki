---
title: Cooked Porkchop
description: A raw porkchop cooked in a furnace, also dropped by pig zombies and by pigs that die on fire.
type: item
categories: [Items, Food]
---

A **cooked porkchop** is a [[Raw Porkchop|raw porkchop]] cooked in a
[[Furnace|furnace]].

## Obtaining

### Smelting

{{smelting|Cooked Porkchop}}

### Mob drops

A [[Pig|pig]] that dies on fire drops 0–2 cooked porkchops instead of raw ones.
A [[Pig Zombie|pig zombie]] drops 0–2 when it dies.
<!-- src: EntityPig.java:45 getDropItemId tests fire > 0; EntityPigZombie.java:85
     getDropItemId; EntityLiving.java:424 dropFewItems, nextInt(3) of the
     item -->

## Usage

### Eating

A cooked porkchop is [[Food#Eating|eaten]] to restore 8 health.
<!-- src: Item.java:338 ItemFood(64, 8, true) -->

### Feeding wolves

Using a cooked porkchop on a tamed [[Wolf|wolf]] below full health
[[Food#Wolves|feeds it]].
<!-- src: EntityWolf.java:353-:361; Item.java:338 marks it as the wolf's meat -->

## Data values

- Item ID: {{id|Cooked Porkchop}}
- Translation key: `item.porkchopCooked`
