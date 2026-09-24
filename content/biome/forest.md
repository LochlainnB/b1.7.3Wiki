---
title: Forest
description: A warm, wooded biome with birch among its trees, and one of two biomes where wolves spawn.
type: biome
categories: [Biomes]
infobox: {Map colour: '#056621'}
---

**Forest** is a warm, wooded [[Overworld]] biome.

## Terrain

Forest [[World Generation#Biomes|generates]] where temperature is at least 0.5
and below 0.97, and rainfall × temperature is 0.35 or more. Where temperature
is below 0.7 and rainfall × temperature above 0.5, [[Swampland]] generates
instead.
<!-- src: BiomeGenBase.java:100 getBiome -->

The surface is [[Grass|grass]] over [[Dirt|dirt]].
<!-- src: BiomeGenBase.java:34 -->

[[Weather#Biomes|Rain]] falls, and lightning strikes during thunderstorms.
<!-- src: BiomeGenBase.java:41 enableRain; :150 canSpawnLightningBolt -->

## Vegetation

Each chunk gets `n` + 5 trees, where `n` is the
[[World Generation#Trees|tree noise]] value. One chunk in ten gets one more.
<!-- src: ChunkProviderGenerate.java:411 the noise, :413 the one-in-ten bonus,
     :417 the Forest term -->

One tree in five is a birch. Of the rest, one in three is a big tree and the
others are ordinary trees.
<!-- src: BiomeGenForest.java:10 getRandomWorldGenForTrees -->

Each chunk gets 2 [[World Generation#Plants|patches]] of yellow
[[Flower|flowers]] and 2 of [[Tall Grass|tall grass]].
<!-- src: ChunkProviderGenerate.java:455, :481 -->

## Mobs

Forest uses the shared [[Mob Spawning#What spawns where|Overworld spawn lists]],
with the [[Wolf|wolf]] added to the creature list at weight 2. Forest and
[[Taiga]] are the only biomes where wolves spawn.
<!-- src: BiomeGenForest.java:7 -->

## Data values

- Map colour: `#056621`

<!-- src: BiomeGenBase.java:12 setColor(353825). The game stores the colour but
     never reads it. -->
