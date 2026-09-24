---
title: Flower
description: A small yellow plant that grows in plains and forests, and crafts into dandelion yellow dye.
type: block
categories: [Blocks, Plants, Naturally generated]
---

**Flower** is a small yellow plant that crafts into
[[Dandelion Yellow|dandelion yellow]] dye.

## Obtaining

### Natural generation

Flowers generate only in [[Seasonal Forest]], [[Plains]], [[Forest]] and
[[Taiga]], in [[World Generation#Plants|patches]]: 4 per chunk in Seasonal
Forest, 3 in Plains and 2 in the other two.
<!-- src: ChunkProviderGenerate.java:454-:478 populate; WorldGenFlowers.java:13 -->

[[Bone Meal|Bone meal]] used on [[Grass|grass]] also grows flowers.
<!-- src: ItemDye.java:64-:65 -->

### Breaking

Breaking a flower drops it, whatever breaks it.
<!-- src: BlockFlower keeps Block's idDropped and quantityDropped; hardness 0 -->

## Usage

### Crafting ingredient

{{used in|Flower}}

## Behaviour

A flower stands on [[Grass|grass]], [[Dirt|dirt]] or [[Farmland|farmland]], and
needs [[Light|light]] 8 or more, or open sky, to stay. Placing one checks only
the block beneath.
<!-- src: BlockFlower.java:14 canPlaceBlockAt, :18
     canThisPlantGrowOnThisBlockID, :39 canBlockStay -->

A flower that cannot stay breaks when a block beside it changes, or on its next
[[Game Tick#Random ticks|random tick]].
<!-- src: BlockFlower.java:22 onNeighborBlockChange, :27 updateTick, :31
     checkFlowerChange -->

[[Fluid#What stops flow|Flowing water]] breaks a flower, and flowing
[[Lava|lava]] destroys it.

## Data values

- Block ID: {{id|Flower}}
- Translation key: `tile.flower`
