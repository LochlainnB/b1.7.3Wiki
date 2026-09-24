---
title: Locked chest
description: A glowing block that looks like a chest, holds nothing, and vanishes on its own; no recipe or generator makes one.
type: block
categories: [Blocks]
---

**Locked chest** is a glowing block that looks like a [[Chest|chest]] and
vanishes on its own.

## Obtaining

No recipe makes a locked chest, and the world generator never places one. A
server operator's `give` command is the only way to get one.
<!-- src: Block.lockedChest is read nowhere outside Block.java:687; no recipe in
     data/recipes.json makes it; minecraft_server ConsoleCommandHandler.java:144
     give accepts any id in Item.itemsList, and minecraft_server Block.java:647
     gives every block an item -->

### Breaking

A locked chest breaks at once and drops itself.
<!-- src: Block.java:687 setHardness(0.0F); BlockLockedChest.java:7
     Material.wood, which needs no tool; Block.idDropped returns its own id -->

## Usage

A locked chest holds nothing, and using it does nothing. It gives off
[[Light#Block light|light]].
<!-- src: BlockLockedChest extends Block, not BlockContainer, and has no
     blockActivated; Block.java:687 setLightValue(1.0F) -->

### Fuel

A locked chest burns in a [[Smelting#Fuel|furnace]] for 300 ticks
(15 seconds).
<!-- src: TileEntityFurnace.java:190 getItemBurnTime, 300 for any block made
     of Material.wood -->

## Behaviour

A locked chest disappears the first time a
[[Game Tick#Random ticks|random tick]] picks it.
<!-- src: Block.java:687 setTickOnLoad(true); BlockLockedChest.java:56
     updateTick sets it to air -->

## Data values

- Block ID: {{id|Locked chest}}
- Translation key: `tile.lockedchest`
