---
title: Rainforest
description: A hot, wet biome dense with trees, tall grass and ferns, with the most relief of any biome.
type: biome
categories: [Biomes]
infobox: {Colour: '#08FA36'}
---

**Rainforest** is a hot, wet [[Overworld]] biome of dense forest.

## Terrain

Rainforest [[World Generation#Biomes|generates]] where temperature is 0.97 or
more and rainfall × temperature is 0.9 or more.
<!-- src: BiomeGenBase.java:100 getBiome -->

The surface is [[Grass|grass]] over [[Dirt|dirt]]. Rainforest has the
[[World Generation#The noise fields|most relief]] of any biome.
<!-- src: BiomeGenBase.java:34; ChunkProviderGenerate.java:229-:236 the
     1 - (1 - t*h)^4 factor on the stretch, above 0.9999 wherever rainfall ×
     temperature is 0.9 or more -->

[[Weather#Biomes|Rain]] falls, and lightning strikes during thunderstorms.
<!-- src: BiomeGenBase.java:41 enableRain; :150 canSpawnLightningBolt -->

## Vegetation

Each chunk gets `n` + 5 trees, where `n` is the
[[World Generation#Trees|tree noise]] value. One chunk in ten gets one more.
<!-- src: ChunkProviderGenerate.java:411 the noise, :413 the one-in-ten bonus,
     :421 the Rainforest term -->

One tree in three is a big tree, and the others are ordinary trees.
<!-- src: BiomeGenRainforest.java:6 getRandomWorldGenForTrees -->

Each chunk gets 10 [[World Generation#Plants|patches]] of
[[Tall Grass|tall grass]]. Two patches in three are [[Fern|ferns]] instead.
<!-- src: ChunkProviderGenerate.java:485, :505 -->

## Mobs

Rainforest uses the shared
[[Mob Spawning#What spawns where|Overworld spawn lists]].
<!-- src: BiomeGenBase.java:42-:51; BiomeGenRainforest adds nothing -->

## Data values

- Colour: `#08FA36`

<!-- src: BiomeGenBase.java:9 setColor(588342). The game stores the colour but
     never reads it. -->
