---
title: Tundra
description: A cold, flat, snow-covered biome with no trees.
type: biome
categories: [Biomes]
infobox: {Map colour: '#57EBF9'}
---

**Tundra** is a cold, snow-covered [[Overworld]] biome with no trees.

## Terrain

Tundra [[World Generation#Biomes|generates]] where temperature is below 0.1, or
below 0.5 where rainfall × temperature is also below 0.2.
<!-- src: BiomeGenBase.java:100 getBiome -->

The surface is [[Grass|grass]] over [[Dirt|dirt]]. Tundra, [[Desert]] and
[[Savanna]] have the [[World Generation#The noise fields|least relief]] of any
biome.
<!-- src: BiomeGenBase.java:34; ChunkProviderGenerate.java:229-:236 the
     1 - (1 - t*h)^4 factor on the stretch, lowest where rainfall × temperature
     is below 0.2 -->

The sea surface [[World Generation#Water, ice and bedrock|generates]] as
[[Ice|ice]]. The land [[World Generation#Snow|generates]] under a layer of
[[Snow|snow]].
<!-- src: ChunkProviderGenerate.java:82 ice at y=63 below temperature 0.5; :596
     snow where temperature less the height term is below 0.5. The biome lookup
     rounds temperature down to 1/63 steps (BiomeGenBase.java:94) while the ice
     and snow tests use the unrounded value, so a Tundra column can read up to
     0.508: a thin band at the biome's warm edge generates without ice at sea
     level, or snow on its lowest ground. -->

[[Weather#Biomes|Snow]] falls in place of rain, and there is no lightning. Snow
[[Weather#Snow and ice|settles]] on the ground, and still [[Water|water]]
freezes to ice.
<!-- src: BiomeGenBase.java:19 setEnableSnow; :150 canSpawnLightningBolt;
     World.java:1939 -->

## Vegetation

No [[World Generation#Trees|trees]], yellow [[Flower|flowers]] or
[[Tall Grass|tall grass]] generate.
<!-- src: ChunkProviderGenerate.java:437 the -20 tree term; Tundra has no flower
     or tall grass term at :454-:499 -->

## Mobs

Tundra uses the shared [[Mob Spawning#What spawns where|Overworld spawn lists]].
<!-- src: BiomeGenBase.java:42-:51; Tundra is a plain BiomeGenBase -->

## Data values

- Map colour: `#57EBF9`

<!-- src: BiomeGenBase.java:19 setColor(5762041). The game stores the colour but
     never reads it. -->
