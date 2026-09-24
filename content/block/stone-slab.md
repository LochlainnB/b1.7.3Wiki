---
title: Stone Slab
description: A half-height block in four kinds, stone, sandstone, wooden and cobblestone, two of which stack into a double slab.
type: block
categories: [Blocks, Building blocks]
aliases: [Cobblestone Slab, Slab]
---

**Stone Slab** is a half-height block made in four kinds: stone,
[[Sandstone|sandstone]], wooden and [[Cobblestone|cobblestone]].
<!-- src: BlockStep.java:6 the four kinds, by metadata; :13 half height -->

## Obtaining

### Breaking

Every kind, the wooden slab included, drops itself when [[Mining|mined]] with
any pickaxe, and nothing otherwise. A pickaxe breaks every kind fastest.
<!-- src: BlockStep.java:10 Material.rock for all four; :60-:70 idDropped,
     quantityDropped 1, damageDropped keeps the kind; Material.java:114 rock
     setNoHarvest; ItemPickaxe.java:18 canHarvestBlock; ItemPickaxe.java:41
     blocksEffectiveAgainst lists stairSingle -->

### Crafting

{{crafting|Stone Slab}}

## Usage

A slab fills the lower half of its space. Players and mobs walk up onto a slab
without jumping.
<!-- src: BlockStep.java:13 setBlockBounds 0.5 high; EntityLiving.java:67
     stepHeight 0.5 -->

A slab placed directly on top of a slab of the same kind joins it into a
[[Double Stone Slab|double stone slab]].
<!-- src: BlockStep.java:43 onBlockAdded, which compares the two metadata
     values; the placed metadata is already set when it runs (ItemBlock.java
     onItemUse, Chunk.java setBlockIDWithMetadata) -->

## Behaviour

Slabs stop [[Light#What stops light|light]], although they fill only half their
space.
<!-- src: BlockStep.java:16 setLightOpacity(255) -->

Mobs do not [[Mob Spawning#The spawn cycle|spawn naturally]] on slabs, and
[[Torch|torches]] cannot be placed on them.
<!-- src: SpawnerAnimals.java:157 canCreatureTypeSpawnAtLocation and
     BlockTorch.java:27-:41 canPlaceBlockAt both need isBlockNormalCube, which
     (World.java:1644) needs renderAsNormalBlock, false for a single slab at
     BlockStep.java:72 -->

The wooden slab does not [[Fire#Flammable blocks|burn]], and is not
[[Smelting#Fuel|furnace fuel]].
<!-- src: BlockFire.java:14 initializeBlock has no entry for block 44;
     TileEntityFurnace.java:190 getItemBurnTime counts only Material.wood, and
     every slab is Material.rock (BlockStep.java:10) -->

## Data values

- Block ID: {{id|Stone Slab}} stone, {{id|Sandstone Slab}} sandstone,
  {{id|Wooden Slab}} wooden, `44:3` cobblestone
- Translation key: `tile.stoneSlab.stone`, `tile.stoneSlab.sand`,
  `tile.stoneSlab.wood`, `tile.stoneSlab.cobble`

<!-- 44:3 is typed: data/ has no variant name for it, since en_US.lang names it
     Stone Slab like damage 0, so no {{id}} resolves to it. -->

The game names the cobblestone slab *Stone Slab*, the same as the stone one.
<!-- src: en_US.lang tile.stoneSlab.cobble.name=Stone Slab; ItemSlab.java:18
     getItemNameIS -->
