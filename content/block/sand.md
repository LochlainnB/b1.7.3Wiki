---
title: Sand
description: The block of deserts and beaches, which falls when nothing holds it up and smelts into glass.
type: block
categories: [Blocks, Naturally generated]
---

**Sand** is the block that covers [[Desert|deserts]] and beaches, and falls when
nothing holds it up.

## Obtaining

### Breaking

Breaking sand drops it, whatever breaks it. A shovel breaks it fastest.
<!-- src: Material.java:123 sand needs no tool; ItemSpade.java:19
     blocksEffectiveAgainst -->

### Natural generation

Sand is the top block and the [[World Generation#Surface|filler]] of the
[[Desert]] and the [[Ice Desert]]. Between y=60 and y=65, about half of columns
in every other biome take sand as both instead, which makes beaches.
[[Sandstone]] lies under the sand.
<!-- src: BiomeGenBase.java:66-:67; ChunkProviderGenerate.java:123 the sand
     roll, :143-:157 applied between y=60 and y=65; :177 sandstone -->

## Usage

### Crafting ingredient

{{used in|Sand}}

[[Cactus|Cacti]] and [[Dead Bush|dead bushes]] stand only on sand.
<!-- src: BlockCactus.java:83 canBlockStay; BlockDeadBush.java:13
     canThisPlantGrowOnThisBlockID -->

A new world's [[World Generation#The world spawn point|spawn point]] is always on
sand.
<!-- src: WorldProvider.java:37 canCoordinateBeSpawn -->

## Behaviour

Sand [[Falling Sand|falls]] when the block below it is air, [[Water|water]],
[[Lava|lava]] or [[Fire|fire]].
<!-- src: BlockSand.java:24 tryToFall, :49 canFallBelow -->

## Data values

- Block ID: {{id|Sand}}
- Translation key: `tile.sand`
