---
title: Desert
description: A hot, dry biome of sand, cacti and dead bushes, where no rain falls.
type: biome
categories: [Biomes]
infobox: {Colour: '#FA9418'}
---

**Desert** is a hot, dry [[Overworld]] biome covered in [[Sand|sand]].

## Terrain

Desert [[World Generation#Biomes|generates]] where temperature is 0.95 or more
and rainfall × temperature is below 0.2.
<!-- src: BiomeGenBase.java:100 getBiome -->

The surface is [[Sand|sand]] over sand, with [[Sandstone|sandstone]] below it.
Desert, [[Savanna]] and [[Tundra]] have the
[[World Generation#The noise fields|least relief]] of any biome.
<!-- src: BiomeGenBase.java:66 generateBiomeLookup sets both surface blocks to
     sand; ChunkProviderGenerate.java:176 the sandstone under sand filler;
     :229-:236 the 1 - (1 - t*h)^4 factor on the stretch, lowest where
     rainfall × temperature is below 0.2 -->

No [[Weather#Biomes|rain or snow]] falls, so there is no lightning.
<!-- src: BiomeGenBase.java:16 setDisableRain; :150 canSpawnLightningBolt -->

## Vegetation

No [[World Generation#Trees|trees]] generate. Each chunk gets 2
[[World Generation#Plants|patches]] of [[Dead Bush|dead bushes]] and 10 of
[[Cactus|cacti]].
<!-- src: ChunkProviderGenerate.java:433 the -20 tree term; :516 dead bushes;
     :563 cacti -->

## Mobs

Desert uses the shared [[Mob Spawning#What spawns where|Overworld spawn lists]].
[[Mob Spawning#Passive mobs|Animals]] spawn only on [[Grass|grass]], so none
spawn on Desert's sand.
<!-- src: BiomeGenDesert.java adds nothing to BiomeGenBase.java:42-:51;
     EntityAnimal.java:19 getCanSpawnHere -->

## Data values

- Colour: `#FA9418`

<!-- src: BiomeGenBase.java:16 setColor(16421912). The game stores the colour
     but never reads it. -->
