---
title: Rose
description: A small red plant that grows in every biome, and crafts into rose red dye.
type: block
categories: [Blocks, Plants, Naturally generated]
---

**Rose** is a small red plant that crafts into [[Rose Red|rose red]] dye.

## Obtaining

### Natural generation

Roses generate in every biome. One chunk in two gets a
[[World Generation#Plants|patch]].
<!-- src: ChunkProviderGenerate.java:527-:532 populate, with no biome test;
     WorldGenFlowers.java:13 -->

[[Bone Meal|Bone meal]] used on [[Grass|grass]] also grows roses.
<!-- src: ItemDye.java:66-:67 -->

### Breaking

Breaking a rose drops it, whatever breaks it.
<!-- src: BlockFlower keeps Block's idDropped and quantityDropped; hardness 0 -->

## Usage

### Crafting ingredient

{{used in|Rose}}

## Behaviour

A rose stands on [[Grass|grass]], [[Dirt|dirt]] or [[Farmland|farmland]], and
needs [[Light|light]] 8 or more, or open sky, to stay. Placing one checks only
the block beneath.
<!-- src: Block.java:630 plantRed is a BlockFlower; BlockFlower.java:14
     canPlaceBlockAt, :18 canThisPlantGrowOnThisBlockID, :39 canBlockStay -->

A rose that cannot stay breaks when a block beside it changes, or on its next
[[Game Tick#Random ticks|random tick]].
<!-- src: BlockFlower.java:22 onNeighborBlockChange, :27 updateTick, :31
     checkFlowerChange -->

[[Fluid#What stops flow|Flowing water]] breaks a rose, and flowing
[[Lava|lava]] destroys it.

## Data values

- Block ID: {{id|Rose}}
- Translation key: `tile.rose`
