---
title: Shrubland
description: A warm biome of bare grass with almost no trees.
type: biome
categories: [Biomes]
infobox: {Colour: '#A1AD20'}
---

**Shrubland** is a warm [[Overworld]] biome of bare, almost treeless grassland.

## Terrain

Shrubland [[World Generation#Biomes|generates]] where temperature is at least
0.5 and below 0.97, and rainfall × temperature is at least 0.2 and below 0.35.
<!-- src: BiomeGenBase.java:100 getBiome -->

The surface is [[Grass|grass]] over [[Dirt|dirt]].
<!-- src: BiomeGenBase.java:34 -->

[[Weather#Biomes|Rain]] falls, and lightning strikes during thunderstorms.
<!-- src: BiomeGenBase.java:41 enableRain; :150 canSpawnLightningBolt -->

## Vegetation

One chunk in ten gets a single [[World Generation#Trees|tree]]. A tree is a big
tree one time in ten, and an ordinary tree otherwise.
<!-- src: ChunkProviderGenerate.java:413 the one-in-ten bonus, with no
     Shrubland term after it; BiomeGenBase.java:70 getRandomWorldGenForTrees -->

No yellow [[Flower|flowers]] or [[Tall Grass|tall grass]] generate.
<!-- src: Shrubland has no flower or tall grass term at
     ChunkProviderGenerate.java:454-:499 -->

## Mobs

Shrubland uses the shared
[[Mob Spawning#What spawns where|Overworld spawn lists]].
<!-- src: BiomeGenBase.java:42-:51; Shrubland is a plain BiomeGenBase -->

## Data values

- Colour: `#A1AD20`

<!-- src: BiomeGenBase.java:14 setColor(10595616). The game stores the colour
     but never reads it. -->
