---
title: Wood
description: The log block of tree trunks, in oak, spruce and birch, crafted into planks and smelted into charcoal.
type: block
categories: [Blocks, Building blocks, Naturally generated]
---

**Wood** is the log block that makes up tree trunks.

## Obtaining

### Natural generation

Wood forms the trunk of every [[World Generation#Trees|tree]]. Its kind depends
on the tree:

| Wood | Trees | Biomes |
|---|---|---|
| Oak | ordinary and big trees | every biome with trees but [[Taiga]] |
| Spruce | spruce and pine | [[Taiga]] |
| Birch | birch | [[Forest]] |

<!-- src: WorldGenTrees.java:65 and WorldGenBigTree.java:198 metadata 0,
     WorldGenTaiga1.java:70 and WorldGenTaiga2.java:82 metadata 1,
     WorldGenForest.java:65 metadata 2; BiomeGenBase.java:70,
     BiomeGenForest.java:11, BiomeGenTaiga.java:11 and BiomeGenRainforest.java:7
     choose the trees -->

A [[Sapling|sapling]] grows into a tree of its own kind.

### Breaking

Breaking wood drops it, of the same kind, whatever breaks it. An axe breaks it
fastest.
<!-- src: BlockLog.java:15 idDropped, :56 damageDropped; Material.java:113 wood
     needs no tool; ItemAxe.java:11 blocksEffectiveAgainst -->

The *Getting Wood* [[Achievements|achievement]] is for picking up a wood block.
<!-- src: EntityItem.java:114 -->

## Usage

### Crafting and smelting

{{used in|Wood}}

Wood burns as [[Smelting#Fuel|furnace fuel]].
<!-- src: TileEntityFurnace.java:190 getItemBurnTime, any block of Material.wood -->

## Behaviour

Removing wood marks the [[Leaves#Decay|leaves]] up to 4 blocks away for a decay
check.
<!-- src: BlockLog.java:23 onBlockRemoval -->

Wood [[Fire#Flammable blocks|burns]].

## Data values

- Block ID: {{id|Wood}}
- Metadata: 0 oak, 1 spruce, 2 birch
- Translation key: `tile.log`

The game names all three *Wood*.
