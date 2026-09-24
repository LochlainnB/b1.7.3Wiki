---
title: Seasonal Forest
description: A hot, lightly wooded biome of trees, yellow flowers and tall grass.
type: biome
categories: [Biomes]
infobox: {Map colour: '#9BE023'}
---

**Seasonal Forest** is a hot, lightly wooded [[Overworld]] biome.

## Terrain

Seasonal Forest [[World Generation#Biomes|generates]] where temperature is 0.97
or more, and rainfall × temperature is at least 0.45 and below 0.9.
<!-- src: BiomeGenBase.java:100 getBiome -->

The surface is [[Grass|grass]] over [[Dirt|dirt]].
<!-- src: BiomeGenBase.java:34 -->

[[Weather#Biomes|Rain]] falls, and lightning strikes during thunderstorms.
<!-- src: BiomeGenBase.java:41 enableRain; :150 canSpawnLightningBolt -->

## Vegetation

Each chunk gets `n` + 2 trees, where `n` is the
[[World Generation#Trees|tree noise]] value. One chunk in ten gets one more.
<!-- src: ChunkProviderGenerate.java:411 the noise, :413 the one-in-ten bonus,
     :425 the Seasonal Forest term -->

A tree is a big tree one time in ten, and an ordinary tree otherwise.
<!-- src: BiomeGenBase.java:70 getRandomWorldGenForTrees, which Seasonal Forest
     does not override -->

Each chunk gets 4 [[World Generation#Plants|patches]] of yellow
[[Flower|flowers]] and 2 of [[Tall Grass|tall grass]].
<!-- src: ChunkProviderGenerate.java:459, :489 -->

## Mobs

Seasonal Forest uses the shared
[[Mob Spawning#What spawns where|Overworld spawn lists]].
<!-- src: BiomeGenBase.java:42-:51; Seasonal Forest is a plain BiomeGenBase -->

## Data values

- Map colour: `#9BE023`

<!-- src: BiomeGenBase.java:11 setColor(10215459). The game stores the colour
     but never reads it. -->
