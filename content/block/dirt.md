---
title: Dirt
description: The block beneath grass in most biomes, which grass spreads onto and a hoe tills into farmland.
type: block
categories: [Blocks, Naturally generated]
---

**Dirt** is the block that lies under [[Grass|grass]] in most biomes.

## Obtaining

### Breaking

Breaking dirt drops it, whatever breaks it. [[Grass]] and
[[Farmland|farmland]] drop dirt too. A shovel breaks it fastest.
<!-- src: Material.java:112 ground needs no tool; BlockGrass.java:51 and
     BlockFarmland.java:94 idDropped; ItemSpade.java:19 blocksEffectiveAgainst -->

### Natural generation

Dirt is the [[World Generation#Surface|filler]] under the top block of every
biome except [[Desert]] and [[Ice Desert]], and the top block itself where the
ground lies under water.
<!-- src: BiomeGenBase.java:36 fillerBlock, :66-:67 the two deserts;
     ChunkProviderGenerate.java:168 places the filler as the top below y=63 -->

Dirt also forms [[World Generation#Ores|veins]] in stone, as an ore does: 20 per
chunk, of size 32, from y=0 to y=127.
<!-- src: ChunkProviderGenerate.java:354-:358 WorldGenMinable(Block.dirt.blockID,
     32), 20 times at nextInt(128) -->

## Usage

Any hoe tills dirt into [[Farmland#Obtaining|farmland]].
<!-- src: ItemHoe.java:13 onItemUse -->

[[Grass#Spreading|Grass spreads]] onto dirt.

[[Flower|Flowers]], [[Rose|roses]], [[Sapling|saplings]],
[[Tall Grass|tall grass]] and [[Sugar cane|sugar cane]] stand on dirt. Sugar
cane needs [[Water|water]] beside the dirt block.
<!-- src: BlockFlower.java:19 canThisPlantGrowOnThisBlockID, inherited by
     BlockSapling and BlockTallGrass; BlockReed.java:33 canPlaceBlockAt -->

## Data values

- Block ID: {{id|Dirt}}
- Translation key: `tile.dirt`
