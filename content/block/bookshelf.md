---
title: Bookshelf
description: A wooden block crafted from planks and books, which drops nothing when broken.
type: block
categories: [Blocks, Building blocks]
---

**Bookshelf** is a block crafted from [[Wooden Planks|wooden planks]] and
[[Book|books]].

## Obtaining

### Crafting

{{crafting|Bookshelf}}

### Breaking

A bookshelf [[Mining#What blocks drop|drops nothing]] when broken, whatever
breaks it. [[Mining#What each tool is effective against|Axes]] break it
fastest.
<!-- src: BlockBookshelf.java:14 quantityDropped 0; ItemAxe.java:11
     blocksEffectiveAgainst -->

## Usage

A placed bookshelf has no function beyond building.
<!-- src: BlockBookshelf.java overrides only getBlockTextureFromSide and
     quantityDropped -->

### Fuel

A bookshelf burns in a [[Smelting#Fuel|furnace]] for 300 ticks (15 seconds),
long enough to smelt one and a half items.
<!-- src: TileEntityFurnace.java:190 getItemBurnTime, Material.wood;
     BlockBookshelf.java:7 -->

## Behaviour

Bookshelves [[Fire#Flammable blocks|catch fire]] and burn away.
<!-- src: BlockFire.java:20 setBurnRate(bookShelf, 30, 20) -->

## Data values

- Block ID: {{id|Bookshelf}}
- Translation key: `tile.bookshelf`
