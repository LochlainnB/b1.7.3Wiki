---
title: Sticky Piston
description: A piston that pulls the block in front of its head back one space when it retracts.
type: block
categories: [Blocks, Redstone]
---

**Sticky Piston** is a [[Piston|piston]] that pulls back the block in front of
it when it retracts.

## Obtaining

### Crafting

{{crafting|Sticky Piston}}

## Usage

### Placing

A sticky piston is placed like a [[Piston#Placing|piston]].
<!-- src: both are BlockPistonBase; Block.java:621, :625 -->

## Behaviour

### Power

A sticky piston extends and retracts on the same [[Piston#Power|power]] as a
piston, and [[Piston#Pushing|pushes]] the same blocks.

### Pulling

When it retracts, a sticky piston pulls back the one block touching its head,
if a piston could push that block without breaking it. A retracted piston can
be pulled.
<!-- src: BlockPistonBase.java:127-:162 playBlock; :147 canPushBlock with
     var5 false refuses mobility 1 as well; pistons are exempted from the
     mobility test -->

A sticky piston that retracts before the block it pushed has settled leaves
that block where it was pushed.
<!-- src: BlockPistonBase.java:134-:143, which finishes the moving block in
     place when it is still extending in the same direction. It settles on its
     third block-entity update (TileEntityPiston.java:105), so a push and a
     retraction both run by scheduled ticks leave it behind when they are 2
     ticks apart or less -->

## Data values

- Block ID: {{id|Sticky Piston}}, {{id|block 34}} head, {{id|block 36}} moving
  block
- Translation key: `tile.pistonStickyBase`
