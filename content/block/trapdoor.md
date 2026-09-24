---
title: Trapdoor
description: A wooden hatch hung on the side of a block, opened by a player's click or by redstone power.
type: block
categories: [Blocks, Redstone]
---

**Trapdoor** is a wooden hatch that a player or
[[Redstone Power|redstone power]] opens.

## Obtaining

### Crafting

{{crafting|Trapdoor}}

## Usage

### Placing

A trapdoor is placed against the side of a full, solid block, and lies flat
along the bottom of its space. It opens by swinging up against that block. It
drops as an item when that block goes.
<!-- src: BlockTrapDoor.java:154 canPlaceBlockOnSide refuses the top and
     bottom faces; :47 setBlockBoundsForBlockRender; :94 onNeighborBlockChange -->

### Opening

A player opens or closes a trapdoor by right-clicking or hitting it.
<!-- src: BlockTrapDoor.java:70 onBlockClicked calls :74 blockActivated -->

### Fuel

A trapdoor burns in a [[Smelting#Fuel|furnace]] for 300 ticks (15 seconds),
long enough to smelt 1.5 items.
<!-- src: TileEntityFurnace.java:190 getItemBurnTime, any Material.wood block -->

## Behaviour

### Power

A trapdoor opens when it is [[Redstone Power#Blocks that respond|powered]], and
closes when it is not. It checks only when a power source beside it changes, so
a [[Redstone Repeater|repeater]] switching beside it goes unnoticed.
<!-- src: BlockTrapDoor.java:120 the canProvidePower test, :85
     onPoweredBlockChange -->

## Data values

- Block ID: {{id|Trapdoor}}
- Translation key: `tile.trapdoor`
