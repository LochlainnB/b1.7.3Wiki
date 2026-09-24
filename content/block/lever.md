---
title: Lever
description: A switch placed on a block, which gives redstone power from when a player switches it on until they switch it off.
type: block
categories: [Blocks, Redstone]
---

**Lever** is a switch that gives [[Redstone Power|redstone power]] while it is
on.

## Obtaining

### Crafting

{{crafting|Lever}}

## Usage

### Placing

A lever is placed on top of a full, solid block, or on its side. It drops as an
item when that block goes.
<!-- src: BlockLever.java:24 canPlaceBlockOnSide, which has no case for the
     underside (side 0); :85 onNeighborBlockChange drops it -->

### Switching

A player switches a lever on or off by right-clicking or hitting it.
<!-- src: BlockLever.java:149 onBlockClicked calls :153 blockActivated -->

## Behaviour

### Power

While on, a lever [[Redstone Power#Power sources|powers]] every block beside
it, and [[Redstone Power#Powered blocks|strongly powers]] the block it is
attached to. It stays on until it is switched off.
<!-- src: BlockLever.java:201 isPoweringTo, :205 isIndirectlyPoweringTo -->

## Data values

- Block ID: {{id|Lever}}
- Translation key: `tile.lever`
