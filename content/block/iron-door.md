---
title: Iron Door
description: A two-block-tall iron door that only redstone power opens.
type: block
categories: [Blocks, Redstone]
---

**Iron Door** is a two-block-tall door that only
[[Redstone Power|redstone power]] opens.

## Obtaining

### Crafting

{{crafting|Iron Door}}

### Breaking

An iron door drops itself only when [[Mining#Drops|mined with a pickaxe]],
unless its top half is broken. The lower half then breaks and drops the door,
whatever broke the top.
<!-- src: Block.java:663 Material.iron; BlockDoor.java:171 idDropped gives
     nothing for the top half; :146 the lower half removes itself and calls
     dropBlockAsItem, which skips the harvest check -->

## Usage

### Placing

An iron door is placed, and hinged, like a [[Wooden Door#Placing|wooden door]].
One hinged on the right opens when unpowered and closes when powered.
<!-- src: ItemDoor.java, shared by both doors -->

## Behaviour

### Power

A door opens when either half is
[[Redstone Power#Blocks that respond|powered]], and closes when neither is. It
checks only when a power source beside it changes, so a
[[Redstone Repeater|repeater]] switching beside it goes unnoticed.
<!-- src: BlockDoor.java:134 onNeighborBlockChange, the canProvidePower test at
     :163; :164 reads both halves -->

A player cannot open an iron door by hand.
<!-- src: BlockDoor.java:90 blockActivated returns at once for Material.iron -->

## Data values

- Block ID: {{id|Iron Door}}
- Item ID: {{id|item 330}}
- Translation key: `tile.doorIron`, `item.doorIron`
