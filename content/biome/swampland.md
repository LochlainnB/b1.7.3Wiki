---
title: Swampland
description: A warm, wet biome of bare grass with almost no trees.
type: biome
categories: [Biomes]
infobox: {Colour: '#07F9B2'}
---

**Swampland** is a warm, wet [[Overworld]] biome of bare, almost treeless
grassland.

## Terrain

Swampland [[World Generation#Biomes|generates]] where temperature is below 0.7
and rainfall × temperature is above 0.5.
<!-- src: BiomeGenBase.java:100 getBiome -->

The surface is [[Grass|grass]] over [[Dirt|dirt]].
<!-- src: BiomeGenBase.java:34; BiomeGenSwamp adds nothing to BiomeGenBase -->
<!-- No relief sentence here. The terrain factor at ChunkProviderGenerate.java:229
     is 1 - (1 - t*h)^4, which rainfall × temperature of 0.5 to 0.7 puts
     between 0.94 and 0.99. Forest and Seasonal Forest columns can exceed that,
     so Swampland does not have the most relief of any biome. -->

[[Weather#Biomes|Rain]] falls, and lightning strikes during thunderstorms.
<!-- src: BiomeGenBase.java:41 enableRain; :150 canSpawnLightningBolt -->

## Vegetation

One chunk in ten gets a single [[World Generation#Trees|tree]]. A tree is a big
tree one time in ten, and an ordinary tree otherwise.
<!-- src: ChunkProviderGenerate.java:413 the one-in-ten bonus, with no
     Swampland term after it; BiomeGenBase.java:70 getRandomWorldGenForTrees -->

No yellow [[Flower|flowers]] or [[Tall Grass|tall grass]] generate.
<!-- src: Swampland has no flower or tall grass term at
     ChunkProviderGenerate.java:454-:499 -->

## Mobs

Swampland uses the shared
[[Mob Spawning#What spawns where|Overworld spawn lists]].
<!-- src: BiomeGenBase.java:42-:51; BiomeGenSwamp adds nothing -->

## Data values

- Colour: `#07F9B2`

<!-- src: BiomeGenBase.java:10 setColor(522674). The game stores the colour but
     never reads it. -->
