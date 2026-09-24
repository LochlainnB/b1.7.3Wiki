---
title: Crafting Table
description: A wooden block that opens the 3×3 crafting grid, needed for every recipe larger than 2×2.
type: block
categories: [Blocks, Utility blocks]
---

**Crafting Table** is a wooden block that gives a player the 3×3
[[Crafting|crafting]] grid.

## Obtaining

### Crafting

{{crafting|Crafting Table}}

The *Benchmarking* [[Achievements|achievement]] is for crafting a crafting
table.
<!-- src: SlotCrafting.java:19; AchievementList.java:35 buildWorkBench -->

### Breaking

A crafting table drops itself when broken with anything. An axe is not
[[Mining#What each tool is effective against|effective against]] it.
<!-- src: BlockWorkbench.java:5 Material.wood, which needs no tool;
     ItemAxe.java:11 blocksEffectiveAgainst has no Block.workbench -->

## Usage

Using a crafting table opens a 3×3 [[Crafting#The grid|crafting grid]].
<!-- src: BlockWorkbench.java:19 blockActivated; ContainerWorkbench.java:4 -->

### Fuel

A crafting table burns in a [[Smelting#Fuel|furnace]] for 300 ticks
(15 seconds).
<!-- src: TileEntityFurnace.java:190 getItemBurnTime, 300 for any block made
     of Material.wood -->

## Behaviour

[[Fire]] does not burn a crafting table.
<!-- src: BlockFire.java:14 initializeBlock gives it no burn rate -->

## Data values

- Block ID: {{id|Crafting Table}}
- Translation key: `tile.workbench`
