---
title: Fern
description: A plant of rainforests that shares its block id with tall grass, and drops seeds one time in eight.
type: block
categories: [Blocks, Plants, Naturally generated]
---

**Fern** is a plant of [[Rainforest|rainforests]] that shares its block id with
[[Tall Grass|tall grass]].

## Obtaining

### Natural generation

Ferns generate only in [[Rainforest]]. Two in three of its 10 tall grass
[[World Generation#Plants|patches]] per chunk are ferns.
<!-- src: ChunkProviderGenerate.java:505-:512 populate, metadata 2 instead of 1 -->

### Breaking

Breaking a fern drops [[Seeds|seeds]] one time in eight, and nothing otherwise,
whatever breaks it.
<!-- src: BlockTallGrass.java:39 idDropped, the same for every metadata -->

## Behaviour

A fern stands on [[Grass|grass]], [[Dirt|dirt]] or [[Farmland|farmland]], and
needs [[Light|light]] 8 or more, or open sky, to stay.
<!-- src: BlockTallGrass extends BlockFlower; BlockFlower.java:18
     canThisPlantGrowOnThisBlockID, :39 canBlockStay -->

A fern that cannot stay breaks when a block beside it changes, or on its next
[[Game Tick#Random ticks|random tick]].
<!-- src: BlockFlower.java:22 onNeighborBlockChange, :27 updateTick, :31
     checkFlowerChange -->

A fern [[Fire#Flammable blocks|burns]]. [[Fluid#What stops flow|Flowing water]]
breaks it, and flowing [[Lava|lava]] destroys it.

A fern is tinted as [[Tall Grass#Behaviour|tall grass]] is.
<!-- src: BlockTallGrass.java:22 colorMultiplier, the same for metadata 1 and 2 -->

## Data values

- Block ID: {{id|Fern}}
- Translation key: `tile.tallgrass`

The game has no name for the fern.
