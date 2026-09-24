---
title: Chest
description: A wooden block that stores 27 stacks of items, or 54 when two stand side by side as a large chest.
type: block
categories: [Blocks, Utility blocks, Naturally generated]
---

**Chest** is a wooden block that stores items.

## Obtaining

### Crafting

{{crafting|Chest}}

### Breaking

A chest drops itself when broken with anything, and breaks fastest with an
[[Mining#What each tool is effective against|axe]].
<!-- src: BlockChest.java:9 Material.wood, which needs no tool; ItemAxe.java:11
     blocksEffectiveAgainst includes Block.chest -->

### Natural generation

A [[Dungeon|dungeon]] holds up to two chests of loot.

## Usage

### Storage

A chest holds 27 stacks. Using it opens them.
<!-- src: TileEntityChest.java:6 getSizeInventory; BlockChest.java:185
     blockActivated -->

Two chests side by side form a large chest that holds 54. Each half keeps its
own 27. A chest cannot be placed beside two chests, or beside a chest that is
already half of a large chest.
<!-- src: BlockChest.java:198-:211 joins a neighbouring chest into an
     InventoryLargeChest, whose size is the sum of both (InventoryLargeChest.java:14);
     :110 canPlaceBlockAt -->

A chest does not open while a full, opaque block is on top of it, or on top of
the other half of a large chest.
<!-- src: BlockChest.java:187-:196, isBlockNormalCube above each half; glass,
     leaves and other see-through blocks do not count (World.java:1644) -->

Breaking a chest drops its contents. Breaking one half of a large chest drops
only that half's.
<!-- src: BlockChest.java:155 onBlockRemoval empties only its own
     TileEntityChest -->

### Fuel

A chest burns in a [[Smelting#Fuel|furnace]] for 300 ticks (15 seconds).
<!-- src: TileEntityFurnace.java:190 getItemBurnTime, 300 for any block made
     of Material.wood -->

### Crafting ingredient

{{used in|Chest}}

## Behaviour

A [[Piston|piston]] cannot push a chest. [[Fire]] does not burn it.
<!-- src: BlockPistonBase.java:268 canPushBlock refuses any block with a tile
     entity; BlockFire.java:14 initializeBlock gives chests no burn rate -->

## Data values

- Block ID: {{id|Chest}}
- Translation key: `tile.chest`
