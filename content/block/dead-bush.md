---
title: Dead Bush
description: A dry shrub that grows on the sand of deserts, and drops nothing when broken.
type: block
categories: [Blocks, Plants, Naturally generated]
---

**Dead Bush** is a dry shrub that grows on [[Sand|sand]] in
[[Desert|deserts]].

## Obtaining

### Natural generation

Dead bushes generate only in [[Desert]], in 2
[[World Generation#Plants|patches]] per chunk.
<!-- src: ChunkProviderGenerate.java:515-:525 populate; WorldGenDeadBush.java:17 -->

### Breaking

Breaking a dead bush drops nothing, whatever breaks it.
<!-- src: BlockDeadBush.java:20 idDropped returns -1 -->

## Behaviour

A dead bush stands only on [[Sand|sand]], and needs [[Light|light]] 8 or more,
or open sky, to stay.
<!-- src: BlockDeadBush.java:12 canThisPlantGrowOnThisBlockID; BlockFlower.java:39
     canBlockStay -->

A dead bush that cannot stay breaks when a block beside it changes, or on its
next [[Game Tick#Random ticks|random tick]].
<!-- src: BlockFlower.java:22 onNeighborBlockChange, :27 updateTick, :31
     checkFlowerChange -->

[[Fluid#What stops flow|Flowing water]] breaks a dead bush, and flowing
[[Lava|lava]] destroys it.

## Data values

- Block ID: {{id|Dead Bush}}
- Translation key: `tile.deadbush`

The game has no name for the dead bush.
<!-- lang/en_US.lang has no tile.deadbush.name; the wiki's name comes from
     data/name-overrides.json -->
