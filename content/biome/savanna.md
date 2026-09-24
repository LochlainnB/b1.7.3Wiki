---
title: Savanna
description: A warm, dry biome of bare grass with almost no trees.
type: biome
categories: [Biomes]
infobox: {Map colour: '#D9E023'}
---

**Savanna** is a warm, dry [[Overworld]] biome of bare, almost treeless
grassland.

## Terrain

Savanna [[World Generation#Biomes|generates]] where temperature is at least 0.5
and below 0.95, and rainfall × temperature is below 0.2.
<!-- src: BiomeGenBase.java:100 getBiome -->

The surface is [[Grass|grass]] over [[Dirt|dirt]]. Savanna, [[Desert]] and
[[Tundra]] have the [[World Generation#The noise fields|least relief]] of any
biome.
<!-- src: BiomeGenBase.java:34; Savanna is a BiomeGenDesert, but only Desert and
     Ice Desert have their surface changed to sand (:66).
     ChunkProviderGenerate.java:229-:236 the 1 - (1 - t*h)^4 factor on the
     stretch, lowest where rainfall × temperature is below 0.2 -->

[[Weather#Biomes|Rain]] falls, and lightning strikes during thunderstorms.
<!-- src: BiomeGenBase.java:41 enableRain; :150 canSpawnLightningBolt -->

## Vegetation

One chunk in ten gets a single [[World Generation#Trees|tree]]. A tree is a big
tree one time in ten, and an ordinary tree otherwise.
<!-- src: ChunkProviderGenerate.java:413 the one-in-ten bonus, with no Savanna
     term after it; BiomeGenBase.java:70 getRandomWorldGenForTrees -->

No yellow [[Flower|flowers]] or [[Tall Grass|tall grass]] generate.
<!-- src: Savanna has no flower or tall grass term at
     ChunkProviderGenerate.java:454-:499 -->

## Mobs

Savanna uses the shared [[Mob Spawning#What spawns where|Overworld spawn lists]].
<!-- src: BiomeGenBase.java:42-:51; BiomeGenDesert adds nothing -->

## Data values

- Map colour: `#D9E023`

<!-- src: BiomeGenBase.java:13 setColor(14278691). The game stores the colour
     but never reads it. -->
