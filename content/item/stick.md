---
title: Stick
description: The item crafted from wooden planks, which forms the handle of every pickaxe, axe, shovel, hoe and sword.
type: item
categories: [Items, Materials]
---

**Stick** is an item crafted from [[Wooden Planks|wooden planks]].

## Obtaining

### Crafting

{{crafting|Stick}}

### Boats

A [[Boat|boat]] that breaks drops two sticks and three
[[Wooden Planks|wooden planks]].
<!-- src: EntityBoat.java:75-:81 attackEntityFrom, and :250-:257 onUpdate when
     it crashes -->

## Usage

### Crafting ingredient

{{used in|Stick}}

### Fuel

A stick burns in a [[Smelting#Fuel|furnace]] for 100 ticks (5 seconds), long
enough to smelt half an item.
<!-- src: TileEntityFurnace.java:192 getItemBurnTime -->

## Data values

- Item ID: {{id|Stick}}
- Translation key: `item.stick`
