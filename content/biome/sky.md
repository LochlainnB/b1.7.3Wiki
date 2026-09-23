---
title: Sky
description: The only biome of the Sky dimension.
type: biome
categories: [Biomes]
infobox: {Map colour: '#8080FF'}
---

{{hatnote|This page is about the biome. For the dimension it belongs to, see [[Sky Dimension]].}}

**Sky** is the only biome of the [[Sky Dimension|Sky dimension]], and never
generates in the [[Overworld]].
<!-- src: WorldProviderSky.java:5 hands the dimension a WorldChunkManagerHell
     fixed to this biome; BiomeGenBase.java:100 getBiome never returns it -->

## Terrain

The surface is [[Grass|grass]] over [[Dirt|dirt]]. Temperature is fixed at 0.5
and rainfall at 0 across the whole dimension.
<!-- src: BiomeGenBase.java:34 the default top and filler blocks;
     WorldProviderSky.java:5 passes 0.5 and 0.0 to WorldChunkManagerHell -->

The sky is a fixed pale blue. Rain is disabled, so there is no lightning.
<!-- src: BiomeGenSky.java:11 getSkyColorByTemp returns a constant;
     BiomeGenBase.java:21 setDisableRain, read by :150
     canSpawnLightningBolt -->

## Vegetation

A tree is a big tree one time in ten, and an ordinary tree otherwise. Which
plants generate, and how many, is set by the
[[Sky Dimension#Terrain|dimension's generator]], not the biome.
<!-- src: BiomeGenBase.java:70 getRandomWorldGenForTrees, which BiomeGenSky does
     not override -->

## Mobs

[[Chicken|Chickens]] are the only mob on the biome's spawn lists, at weight 10.
The monster and water creature lists are empty.
<!-- src: BiomeGenSky.java:5 -->

## Data values

- Map colour: `#8080FF`
