---
title: Wooden Door
description: A two-block-tall wooden door, opened by a player's click or by redstone power.
type: block
categories: [Blocks, Redstone]
---

**Wooden Door** is a two-block-tall door that a player or
[[Redstone Power|redstone power]] opens.

## Obtaining

### Crafting

{{crafting|Wooden Door}}

## Usage

### Placing

A door is placed on top of a full, solid block, and needs two free spaces above
it. It drops as an item when that block goes.
<!-- src: ItemDoor.java:12 onItemUse, top face only; BlockDoor.java:188
     canPlaceBlockAt; :151 the lower half drops the door when the block beneath
     goes -->

A door hinges on the left of the player placing it. It hinges on the right
instead when the right has more full, solid blocks beside the door than the
left, or when a door of the same kind stands on its left and none on its right.
<!-- src: ItemDoor.java:27 var9 from the player's facing; :46-:55 counts the
     solid blocks beside both halves on each side, and looks for a door of the
     same block id -->

A door hinged on the right answers redstone the other way round: it opens when
unpowered and closes when powered.
<!-- src: ItemDoor.java:57-:60 places it as an open door turned a quarter
     (var9 - 1, plus the open bit 4); BlockDoor.java:113 onPoweredBlockChange
     sets the open bit to match the power -->

### Opening

A player opens or closes a wooden door by right-clicking or hitting either half.
<!-- src: BlockDoor.java:85 onBlockClicked calls :89 blockActivated -->

## Behaviour

### Power

A door opens when either half is
[[Redstone Power#Blocks that respond|powered]], and closes when neither is. It
checks only when a power source beside it changes, so a
[[Redstone Repeater|repeater]] switching beside it goes unnoticed.
<!-- src: BlockDoor.java:134 onNeighborBlockChange, the canProvidePower test at
     :163; :164 reads both halves -->

## Data values

- Block ID: {{id|Wooden Door}}
- Item ID: {{id|item 324}}
- Translation key: `tile.doorWood`, `item.doorWood`
