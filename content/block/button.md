---
title: Button
description: A stone button placed on the side of a block, which gives redstone power for 1 second when pressed.
type: block
categories: [Blocks, Redstone]
---

**Button** is a stone button that gives a pulse of
[[Redstone Power|redstone power]] when pressed.

## Obtaining

### Crafting

{{crafting|Button}}

## Usage

### Placing

A button is placed on the side of a full, solid block, never on top or
underneath. It drops as an item when that block goes.
<!-- src: BlockButton.java:27 canPlaceBlockOnSide accepts sides 2-5 only; :82
     onNeighborBlockChange drops it -->

### Pressing

A player presses a button by right-clicking or hitting it. Pressing a button
that is already pressed does nothing.
<!-- src: BlockButton.java:144 onBlockClicked calls :148 blockActivated, which
     returns at once when the pressed bit is set -->

## Behaviour

### Power

While pressed, a button [[Redstone Power#Power sources|powers]] every block
beside it, and [[Redstone Power#Powered blocks|strongly powers]] the block it
is attached to. It releases after 20 ticks (1 second). A
[[Game Tick#Skipping a delay|random tick]] can release it sooner.
<!-- src: BlockButton.java:197 isPoweringTo, :201 isIndirectlyPoweringTo;
     :15 tickRate 20, scheduled at :171; :8 setTickOnLoad(true) and :225
     updateTick -->

## Data values

- Block ID: {{id|Button}}
- Translation key: `tile.button`
