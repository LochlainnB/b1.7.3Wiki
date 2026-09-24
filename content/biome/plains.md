---
title: Plains
description: A hot, treeless biome of grass, tall grass and yellow flowers.
type: biome
categories: [Biomes]
infobox: {Map colour: '#FFD910'}
---

**Plains** is a hot, treeless [[Overworld]] biome of grassland.

## Terrain

Plains [[World Generation#Biomes|generates]] where temperature is 0.97 or more,
and rainfall × temperature is at least 0.2 and below 0.45.
<!-- src: BiomeGenBase.java:100 getBiome -->

The surface is [[Grass|grass]] over [[Dirt|dirt]].
<!-- src: BiomeGenBase.java:34; Plains is a BiomeGenDesert, but only Desert and
     Ice Desert have their surface changed to sand (:66) -->

[[Weather#Biomes|Rain]] falls, and lightning strikes during thunderstorms.
<!-- src: BiomeGenBase.java:41 enableRain; :150 canSpawnLightningBolt -->

## Vegetation

No [[World Generation#Trees|trees]] generate. Each chunk gets 3
[[World Generation#Plants|patches]] of yellow [[Flower|flowers]] and 10 of
[[Tall Grass|tall grass]].
<!-- src: ChunkProviderGenerate.java:441 the -20 tree term; :467 flowers; :497
     tall grass -->

## Mobs

Plains uses the shared [[Mob Spawning#What spawns where|Overworld spawn lists]].
<!-- src: BiomeGenBase.java:42-:51; BiomeGenDesert adds nothing -->

## Data values

- Map colour: `#FFD910`

<!-- src: BiomeGenBase.java:17 setColor(16767248). The game stores the colour
     but never reads it. -->
