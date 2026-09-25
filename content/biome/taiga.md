---
title: Taiga
description: A cold, snow-covered biome of spruce and pine, and one of two biomes where wolves spawn.
type: biome
categories: [Biomes]
infobox: {Colour: '#2EB153'}
---

**Taiga** is a cold, snow-covered [[Overworld]] biome of spruce forest.

## Terrain

Taiga [[World Generation#Biomes|generates]] where temperature is at least 0.1
and below 0.5, and rainfall × temperature is 0.2 or more.
<!-- src: BiomeGenBase.java:100 getBiome -->

The surface is [[Grass|grass]] over [[Dirt|dirt]].
<!-- src: BiomeGenBase.java:34 -->

The sea surface [[World Generation#Water, ice and bedrock|generates]] as
[[Ice|ice]]. The land [[World Generation#Snow|generates]] under a layer of
[[Snow|snow]].
<!-- src: ChunkProviderGenerate.java:82 ice at y=63 below
     temperature 0.5; :596 snow where temperature less the height term is below
     0.5. The biome lookup rounds temperature down to 1/63 steps
     (BiomeGenBase.java:94) while the ice and snow tests use the unrounded
     value, so a Taiga column can read up to 0.508: a thin band at the biome's
     warm edge generates without ice at sea level, or snow on its lowest
     ground. -->

[[Weather#Biomes|Snow]] falls in place of rain, and there is no lightning. Snow
[[Weather#Snow and ice|settles]] on the ground, and still [[Water|water]]
freezes to ice.
<!-- src: BiomeGenBase.java:15 setEnableSnow; :150 canSpawnLightningBolt;
     World.java:1939 -->

## Vegetation

Each chunk gets `n` + 5 trees, where `n` is the
[[World Generation#Trees|tree noise]] value. One chunk in ten gets one more.
<!-- src: ChunkProviderGenerate.java:411 the noise, :413 the one-in-ten bonus,
     :429 the Taiga term -->

One tree in three is a pine, and the others are spruces.
<!-- src: BiomeGenTaiga.java:10 getRandomWorldGenForTrees; WorldGenTaiga1 is
     the pine and WorldGenTaiga2 the spruce, both of spruce wood and leaves
     (metadata 1) -->

Each chunk gets 2 [[World Generation#Plants|patches]] of yellow
[[Flower|flowers]] and 1 of [[Tall Grass|tall grass]].
<!-- src: ChunkProviderGenerate.java:463, :493 -->

## Mobs

Taiga uses the shared [[Mob Spawning#What spawns where|Overworld spawn lists]],
with the [[Wolf|wolf]] added to the creature list at weight 2. Taiga and
[[Forest]] are the only biomes where wolves spawn.
<!-- src: BiomeGenTaiga.java:7 -->

## Data values

- Colour: `#2EB153`

<!-- src: BiomeGenBase.java:15 setColor(3060051). The game stores the colour but
     never reads it. -->
