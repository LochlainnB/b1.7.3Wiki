---
title: Dispenser
description: A block holding nine slots of items, which fires or drops one of them each time it is powered.
type: block
categories: [Blocks, Redstone]
---

**Dispenser** is a block that holds items and fires one out when powered.

## Obtaining

### Crafting

{{crafting|Dispenser}}

### Breaking

A dispenser drops itself only when [[Mining#Drops|mined with a pickaxe]]. Its
contents drop whatever breaks it.
<!-- src: BlockDispenser.java:9 Material.rock; :181 onBlockRemoval spills the
     slots -->

## Usage

### Placing

A dispenser is placed with its front facing the player.
<!-- src: BlockDispenser.java:161 onBlockPlacedBy -->

### Loading

Right-clicking a dispenser opens its 9 slots.
<!-- src: BlockDispenser.java:74 blockActivated; TileEntityDispenser.java:9 -->

## Behaviour

### Power

A dispenser fires 4 ticks after it, or the block above it, is
[[Redstone Power#Blocks that respond|powered]], and only if it is still powered
then. It checks only when a power source beside it changes, so a
[[Redstone Repeater|repeater]] switching beside it goes unnoticed, and so does
power reaching only the block above it.
<!-- src: BlockDispenser.java:140 onNeighborBlockChange, the canProvidePower
     test on the changed block; :13 tickRate 4; :150 updateTick checks power
     again -->

While it stays powered, a dispenser fires again each time a power source beside
it changes, even one that has nothing to do with it.
<!-- src: BlockDispenser.java:140 schedules whenever it is powered at a check,
     and keeps no record of its last state.
     tested (harness, server): a dispenser held on by one lever fired once more
     at each of four toggles of a second lever beside it, on and off alike; with
     a lever beside the block above it, it did not fire until a torch was placed
     beside it -->

### Firing

Each shot takes one item from a random occupied slot, every slot equally
likely:

| Item | Leaves the front as |
|---|---|
| {{sprite\|Arrow}} | an arrow in flight, which a player can pick up |
| {{sprite\|Egg}} | a thrown egg |
| {{sprite\|Snowball}} | a thrown snowball |
| Anything else | a [[Dropped Item\|dropped item]] |

An empty dispenser clicks instead.
<!-- src: TileEntityDispenser.java:39 getRandomStackFromInventory;
     BlockDispenser.java:84 dispenseItem, :109 doesArrowBelongToPlayer = true
     (minecraft_server BlockDispenser.java:98 too), :104 the click -->

## Data values

- Block ID: {{id|Dispenser}}
- Translation key: `tile.dispenser`
