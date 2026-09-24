---
title: Seeds
description: The item dropped by tall grass and crops, planted on farmland to grow wheat.
type: item
categories: [Items]
---

**Seeds** are the item planted on [[Farmland|farmland]] to grow
[[Crops|crops]].

## Obtaining

Breaking [[Tall Grass|tall grass]] drops seeds 1 time in 8.
<!-- src: BlockTallGrass.java:40 idDropped -->

Breaking [[Crops#Breaking|crops]] drops up to three seeds, more the further
they have grown.
<!-- src: BlockCrops.java:89 dropBlockAsItemWithChance -->

Tilling [[Grass|grass]] with a hoe drops nothing.
<!-- src: ItemHoe.java:10 onItemUse creates no item -->

## Usage

Seeds used on the top of [[Farmland|farmland]] with air above it plant
[[Crops|crops]] there, at their first stage. Planting uses up one seed.
<!-- src: ItemSeeds.java:12 onItemUse; :13 the top face only; :17 farmland
     with air above; :18 places crops at metadata 0; :19 -->

Planting does not test the light. Crops planted where they
[[Crops#Where they stand|cannot stay]] break on their first random tick, or
when a neighbouring block changes.
<!-- src: ItemSeeds.java:17 tests only the block and the air above, not
     BlockFlower.canPlaceBlockAt; BlockFlower.java:22 onNeighborBlockChange and
     :27 updateTick run checkFlowerChange -->

## Data values

- Item ID: {{id|Seeds}}
- Translation key: `item.seeds`
