---
title: Raw Porkchop
description: The meat a pig drops, eaten raw or cooked in a furnace, and fed to tamed wolves.
type: item
categories: [Items, Food]
---

A **raw porkchop** is the meat a [[Pig|pig]] drops.

## Obtaining

A [[Pig|pig]] drops 0–2 raw porkchops when it dies, unless it is on fire.
<!-- src: EntityPig.java:45 getDropItemId tests fire > 0; EntityLiving.java:424
     dropFewItems, nextInt(3) of the item -->

## Usage

### Eating

A raw porkchop is [[Food#Eating|eaten]] to restore 3 health.
<!-- src: Item.java:337 ItemFood(63, 3, true) -->

### Smelting

{{used in|Raw Porkchop}}

### Feeding wolves

Using a raw porkchop on a tamed [[Wolf|wolf]] below full health
[[Food#Wolves|feeds it]].
<!-- src: EntityWolf.java:353-:361; Item.java:337 marks it as the wolf's meat -->

## Data values

- Item ID: {{id|Raw Porkchop}}
- Translation key: `item.porkchopRaw`
