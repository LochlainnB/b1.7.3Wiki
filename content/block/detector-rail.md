---
title: Detector Rail
description: A rail that gives redstone power while a minecart is on it.
type: block
categories: [Blocks, Transportation, Redstone]
---

**Detector Rail** is a [[Rail|rail]] that gives
[[Redstone Power|redstone power]] while a [[Minecart|minecart]] is on it.

## Obtaining

### Crafting

{{crafting|Detector Rail}}

## Usage

### Placing

A detector rail is placed, and joins other rails, as a [[Rail#Joining|rail]]
does, but never curves.
<!-- src: BlockDetectorRail.java:8 passes isPowered true to BlockRail;
     RailLogic.java:248 skips the curves for it -->

## Behaviour

### Power

A detector rail turns on when a minecart of any kind is on it, with or without
a rider. Players, mobs and items do not turn it on.
<!-- src: BlockDetectorRail.java:20 onEntityCollidedWithBlock, :54 looks for
     EntityMinecart alone, which the chest and furnace minecarts also are -->

While on, a detector rail [[Redstone Power#Power sources|powers]] every block
beside it, and [[Redstone Power#Powered blocks|strongly powers]] the block
beneath it. It checks every 20 ticks (1 second) whether a minecart is still on
it, and turns off at the first check that finds none. A
[[Game Tick#Skipping a delay|random tick]] can turn it off sooner.
<!-- src: BlockDetectorRail.java:38 isPoweringTo, :42 isIndirectlyPoweringTo;
     :12 tickRate 20, rescheduled at :74 while occupied; :9 setTickOnLoad(true)
     and :29 updateTick -->

## Data values

- Block ID: {{id|Detector Rail}}
- Translation key: `tile.detectorRail`
