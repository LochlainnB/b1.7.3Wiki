---
title: Wooden Planks
description: The block crafted from any wood log, and the material of sticks, wooden tools and most wooden blocks.
type: block
categories: [Blocks, Building blocks]
---

**Wooden Planks** are a block crafted from [[Wood|wood]].

## Obtaining

### Breaking

Wooden planks drop themselves when broken, whatever breaks them. An axe breaks
them fastest.
<!-- src: Block.java:597 Material.wood, which needs no tool; ItemAxe.java:11
     blocksEffectiveAgainst -->

### Crafting

Every kind of [[Wood|wood]] crafts into the same planks.
<!-- src: CraftingManager.java:47; a block in a recipe matches any metadata
     (CraftingManager.java:115 new ItemStack(block, 1, -1); ShapedRecipes.java:62) -->

{{crafting|Wooden Planks}}

### Boats

A [[Boat|boat]] that breaks drops three wooden planks and two
[[Stick|sticks]].
<!-- src: EntityBoat.java:75-:81 attackEntityFrom, and :250-:257 onUpdate when
     it crashes -->

## Usage

### Crafting ingredient

{{used in|Wooden Planks}}

### Fuel

Wooden planks burn in a [[Smelting#Fuel|furnace]] for 300 ticks (15 seconds),
long enough to smelt 1.5 items.
<!-- src: TileEntityFurnace.java:190 getItemBurnTime, 300 for any block of
     Material.wood -->

## Behaviour

Wooden planks [[Fire#Flammable blocks|burn]], with an encouragement of 5 and a
flammability of 20.
<!-- src: BlockFire.java:15 setBurnRate(planks, 5, 20) -->

## Data values

- Block ID: {{id|Wooden Planks}}
- Translation key: `tile.wood`
