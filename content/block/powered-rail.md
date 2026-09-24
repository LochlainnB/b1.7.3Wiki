---
title: Powered Rail
description: A rail that speeds up minecarts while it is powered, and brakes them while it is not.
type: block
aliases: [Golden Rail]
categories: [Blocks, Transportation, Redstone]
---

**Powered Rail** is a [[Rail|rail]] that speeds up [[Minecart|minecarts]] while
it is powered, and brakes them while it is not.

## Obtaining

### Crafting

{{crafting|Powered Rail}}

## Usage

### Placing

A powered rail is placed, and joins other rails, as a [[Rail#Joining|rail]]
does, but never curves.
<!-- src: Block.java:619 registers it as a BlockRail with
     isPowered true; RailLogic.java:248 skips the curves for it -->

## Behaviour

### Power

A powered rail is on while it or the block above it is
[[Redstone Power#Blocks that respond|powered]]. It passes power along a
straight or sloped line of powered rails, up to 8 rails beyond the one that is
powered.
<!-- src: BlockRail.java:117-:127 onNeighborBlockChange; :148
     isNeighborRailPowered gives up at a depth of 8; :222 isRailPassingPower
     accepts only a powered rail lying along the same axis -->

### Minecarts

While on, a powered rail speeds up a minecart moving along it. The speed can
build past the minecart's [[Minecart#Movement|top speed]].
<!-- src: EntityMinecart.java:396-:401 adds 0.06 blocks per tick to the
     minecart's speed every tick, with no cap on the stored speed -->

A minecart standing still on a flat powered rail that is on is pushed away from
a full, solid block at one end of the rail. With no such block, it stays still.
<!-- src: EntityMinecart.java:402-:414, for metadata 0 and 1 only -->

While off, a powered rail halves the speed of a minecart on it every tick, and
brings it to a stop.
<!-- src: EntityMinecart.java:262-:273, zeroing speed below 0.03 blocks per
     tick -->

## Data values

- Block ID: {{id|Powered Rail}}
- Translation key: `tile.goldenRail`
