---
title: Cake
description: A food crafted from milk, sugar, an egg and wheat, placed as a block and eaten where it stands, a slice at a time.
type: block
categories: [Blocks, Food]
---

**Cake** is a [[Food|food]] placed as a block and eaten where it stands, a
slice at a time.

## Obtaining

### Crafting

{{crafting|Cake}}

Crafting a cake leaves its [[Milk|milk]] buckets in the crafting grid, empty.
<!-- src: SlotCrafting.java:41-:42 puts back an item's container item;
     Item.java:353 gives milk the empty bucket as its container -->

The [[Achievements|achievement]] *The Lie* is for crafting a cake.
<!-- src: SlotCrafting.java:29 onPickupFromSlot; AchievementList.java:41
     bakeCake -->

## Usage

### Placing

A cake can be placed only where the block beneath it is solid. Glass, slabs,
fences, leaves and other cakes all count.
<!-- src: Item.java:372 an ItemReed placing block 92; BlockCake.java:90
     canPlaceBlockAt and :102 canBlockStay test only Material.isSolid() below,
     which Material.java:135 cakeMaterial passes -->

### Eating

Using or hitting a cake [[Food#Foods|eats]] one slice of it, if the player is
below full health. Eating the last slice removes the cake.
<!-- src: BlockCake.java:67 blockActivated and :72 onBlockClicked call :76
     eatCakeSlice; :80 removes it once metadata would reach 6 -->

## Behaviour

A cake breaks when the block beneath it is removed. It drops nothing when it
breaks, whatever breaks it. A [[Piston#Pushing|piston]] breaks a cake rather
than moving it.
<!-- src: BlockCake.java:94 onNeighborBlockChange, :102 canBlockStay; :106
     quantityDropped 0, :110 idDropped 0; Material.java:135 setNoPushMobility,
     which BlockPistonBase.java:336 breaks and drops -->

## Data values

- Block ID: {{id|Cake}}
- Item ID: {{id|item 354}}
- Metadata: slices eaten, 0 to 5
- Translation key: `tile.cake`, `item.cake`
