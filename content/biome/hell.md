---
title: Hell
description: The only biome of the Nether.
type: biome
categories: [Biomes]
infobox: {Map colour: '#FF0000'}
---

{{hatnote|This page is about the biome. For the dimension it belongs to, see [[Nether]].}}

**Hell** is the only biome of the [[Nether]], and never generates in the
[[Overworld]].
<!-- src: WorldProviderHell.java:5 hands the dimension a WorldChunkManagerHell
     fixed to this biome; BiomeGenBase.java:100 getBiome never returns it -->

## Terrain

The biome's own surface of [[Grass|grass]] over [[Dirt|dirt]] is never used.
The [[World Generation#The Nether|Nether's generator]] does not read the biome.
Temperature is fixed at 1 and rainfall at 0 across the whole dimension.
<!-- src: BiomeGenBase.java:34 the default top and filler blocks;
     ChunkProviderHell.java never refers to the biome; WorldProviderHell.java:5
     passes 1.0 and 0.0 to WorldChunkManagerHell -->

Rain is disabled, so there is no lightning.
<!-- src: BiomeGenBase.java:20 setDisableRain, read by :150
     canSpawnLightningBolt -->

## Vegetation

No trees, yellow [[Flower|flowers]] or [[Tall Grass|tall grass]] generate. The
Nether's [[Mushroom|mushroom]] patches are placed by the
[[World Generation#The Nether|dimension's generator]], not the biome.
<!-- src: ChunkProviderHell.java:302 populate, which places no trees and never
     reads the biome -->

## Mobs

[[Ghast|Ghasts]] and [[Pig Zombie|pig zombies]] are the only mobs on the
biome's spawn lists, both on the monster list at weight 10. The creature and
water creature lists are empty.
<!-- src: BiomeGenHell.java:4 -->

## Data values

- Map colour: `#FF0000`

<!-- src: BiomeGenBase.java:20 setColor(16711680). The game stores the colour
     but never reads it. -->
