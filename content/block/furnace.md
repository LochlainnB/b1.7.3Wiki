---
title: Furnace
description: A cobblestone block that smelts items with fuel, and gives off light while fuel burns in it.
type: block
subject: {Unlit: block 61, Lit: block 62}
categories: [Blocks, Utility blocks]
---

**Furnace** is a cobblestone block that [[Smelting|smelts]] items using fuel.

## Obtaining

### Crafting

{{crafting|Furnace}}

The *Hot Topic* [[Achievements|achievement]] is for crafting a furnace.
<!-- src: SlotCrafting.java:23; AchievementList.java:37 buildFurnace -->

### Breaking

A furnace drops itself only when [[Mining|mined]] with a pickaxe. Mined with
anything else, it drops nothing. A pickaxe is not
[[Mining#What each tool is effective against|effective against]] it. A lit
furnace drops an unlit one.
<!-- src: BlockFurnace.java:11 Material.rock; Material.java:114 rock
     setNoHarvest; ItemPickaxe.java:18 canHarvestBlock; ItemPickaxe.java:41
     has no furnace; BlockFurnace.java:16 idDropped returns the unlit id -->

## Usage

A furnace is placed with its front facing the player. Using it opens its three
slots; see [[Smelting#Using a furnace]].
<!-- src: BlockFurnace.java:132 onBlockPlacedBy; :102 blockActivated -->

A furnace is lit while a piece of [[Smelting#Fuel|fuel]] burns in it. A lit
furnace gives off [[Light#Block light|light]], and shows flames and smoke at its
front.
<!-- src: TileEntityFurnace.java:137 switches the block with
     BlockFurnace.java:112 updateFurnaceBlockState whenever furnaceBurnTime
     crosses zero; Block.java:654 sets light on the lit id only;
     BlockFurnace.java:67 randomDisplayTick -->

Breaking a furnace drops its contents.
<!-- src: BlockFurnace.java:152 onBlockRemoval, skipped only while the block
     swaps between lit and unlit -->

### Crafting ingredient

{{used in|Furnace}}

## Behaviour

A [[Piston|piston]] cannot push a furnace, except in the tick the furnace
lights or goes out. A piston that answers the neighbour update the furnace sends
then can. The pushed furnace loses its contents and stays lit for good, and
the piston's head takes its old place.
<!-- src: BlockPistonBase.java:268 canPushBlock refuses any block with a tile
     entity. BlockFurnace.java:112 updateFurnaceBlockState swaps the block from
     inside the block entity pass, where World.java:1624 only marks the old
     block entity removed, so Chunk.java:415 reports none; the new block's
     onBlockAdded updates the neighbours at BlockFurnace.java:48. Tested: see
     Block Data Corruption. -->

Each time a furnace lights or goes out, one spare block entity is left ticking
with nothing in the world pointing at it.
<!-- src: the new block's onBlockAdded adds a fresh TileEntityFurnace, which
     BlockFurnace.java:125 then replaces in the chunk with the old one; the
     fresh one stays in World.loadedTileEntityList. Tested: one orphan per
     change, see Block Data Corruption. -->

## Data values

- Block ID: {{id|block 61}}, {{id|block 62}} lit
- Translation key: `tile.furnace`
