---
title: Pressure Plate
description: A stone or wooden plate placed on a block, which gives redstone power while something stands on it.
type: block
subject: {Stone: Pressure Plate, Wooden: block 72}
aliases: [Stone Pressure Plate, Wooden Pressure Plate]
categories: [Blocks, Redstone]
---

**Pressure Plate** is a plate of stone or wood that gives
[[Redstone Power|redstone power]] while something is on it.

## Obtaining

### Crafting

{{crafting|Pressure Plate}}

### Breaking

A stone pressure plate drops itself only when
[[Mining#Drops|mined with a pickaxe]]. A wooden one drops whatever breaks it.
<!-- src: Block.java:662 pressurePlateStone is Material.rock, :664
     pressurePlatePlanks Material.wood; Material.java:114 rock setNoHarvest;
     ItemPickaxe.java:18 canHarvestBlock accepts any rock -->

## Usage

### Placing

A pressure plate is placed on top of a full, solid block. It drops as an item
when that block goes.
<!-- src: BlockPressurePlate.java:33 canPlaceBlockAt, :40
     onNeighborBlockChange -->

### Crafting ingredient

{{used in|Pressure Plate}}

### Fuel

A wooden pressure plate burns in a [[Smelting#Fuel|furnace]] for 300 ticks
(15 seconds), long enough to smelt 1.5 items.
<!-- src: TileEntityFurnace.java:190 getItemBurnTime, any Material.wood block -->

## Behaviour

### Power

| Plate | Pressed by |
|---|---|
| Stone | players and mobs |
| Wooden | any entity, including [[Dropped Item\|dropped items]], [[Arrow\|arrows]], [[Minecart\|minecarts]] and [[Boat\|boats]] |

<!-- src: Block.java:662 EnumMobType.mobs, :664 EnumMobType.everything;
     BlockPressurePlate.java:74-:84, mobs meaning any EntityLiving -->

While pressed, a pressure plate [[Redstone Power#Power sources|powers]] every
block beside it, and [[Redstone Power#Powered blocks|strongly powers]] the
block beneath it. It checks every 20 ticks (1 second) whether anything is still
on it, and releases at the first check that finds nothing. A
[[Game Tick#Skipping a delay|random tick]] can release it sooner.
<!-- src: BlockPressurePlate.java:133 isPoweringTo, :137 isIndirectlyPoweringTo;
     :17 tickRate 20, rescheduled at :107 while occupied; :12
     setTickOnLoad(true) and :53 updateTick -->

## Data values

- Block ID: {{id|Pressure Plate}} stone, {{id|block 72}} wooden
- Translation key: `tile.pressurePlate`
