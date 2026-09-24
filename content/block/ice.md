---
title: Ice
description: A slippery block that forms on still water in cold places, drops nothing, and melts in block light.
type: block
categories: [Blocks, Naturally generated]
---

**Ice** is a slippery, translucent block that forms on [[Water|water]] in cold
places.

## Obtaining

### Natural generation

Where the temperature is below 0.5, the sea at y=63
[[World Generation#Water, ice and bedrock|generates]] as ice.
<!-- src: ChunkProviderGenerate.java:81-:82 -->

### Freezing

In a snowy biome, a still [[Water|water]] source with nothing solid or liquid
above it [[Weather#Snow and ice|freezes]] into ice in block light below 10, rain
or not.
<!-- src: World.java:1939 the biome and block light test, :1946 the still
     source; findTopSolidBlock (:1122) stops at any solid or liquid -->

### Breaking

Ice drops nothing, whatever breaks it. A pickaxe breaks it fastest.
<!-- src: BlockIce.java:29 quantityDropped 0; ItemPickaxe.java:41
     blocksEffectiveAgainst -->

Broken by a player, ice leaves a [[Water|water]] source where the block below it
is solid or a liquid.
<!-- src: BlockIce.java:20 harvestBlock sets water, level 0, on a solid or
     liquid material; explosions skip harvestBlock and leave air -->

## Behaviour

Ice is slippery. A player who stops walking on ice slides about 1.7 blocks,
against a quarter of a block on other ground.
<!-- src: BlockIce.java:8 slipperiness 0.98 against Block.java:143's 0.6;
     EntityLiving.java:479-:497 keeps slipperiness x 0.91 of the horizontal
     speed each tick on the ground, 0.892 on ice against 0.546. Walking speed
     is 0.216 blocks a tick on other ground and 0.208 on ice; once the key is
     let go, speed x f / (1 - f) gives 0.26 and 1.71 blocks. Confirmed in game,
     reported 2026-09-25 -->

On a [[Game Tick#Random ticks|random tick]], ice in
[[Light#What light affects|block light]] above 8 melts into a still water
source. Sky light never melts it. The water does not flow until a block beside
it changes.
<!-- src: BlockIce.java:33 updateTick, block light over 11 less its opacity
     of 3; sets waterStill, which BlockStationary.java:15 turns to flowing only
     on a neighbour change -->

No mob [[Mob Spawning#The spawn cycle|spawns naturally]] on ice.
<!-- src: SpawnerAnimals.java:156 wants World.isBlockNormalCube (:1644)
     below, which needs Material.getIsTranslucent; Material.java:128 marks ice
     so that it returns false (:87). A monster spawner does not make this
     test -->

[[Snow]] never settles on ice.
<!-- src: World.java:1942; ChunkProviderGenerate.java:596; BlockSnow.java:31
     canPlaceBlockAt wants an opaque cube, which ice is not -->

## Data values

- Block ID: {{id|Ice}}
- Translation key: `tile.ice`
