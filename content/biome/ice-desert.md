---
title: Ice Desert
description: A snowy sand biome the game defines but never generates.
type: biome
categories: [Biomes]
infobox: {Map colour: '#FFED93'}
---

**Ice Desert** is a biome the game defines but never generates.
<!-- src: BiomeGenBase.java:100 getBiome, the only source of Overworld biomes,
     never returns it; WorldProviderHell.java:5 and WorldProviderSky.java:5
     fix the other two dimensions to Hell and Sky -->

## Terrain

Its surface is defined as [[Sand|sand]] over sand, as [[Desert|Desert's]] is.
<!-- src: BiomeGenBase.java:67 generateBiomeLookup -->

Its [[Weather#Biomes|weather]] is set to snow, with no rain and no lightning.
<!-- src: BiomeGenBase.java:18 setEnableSnow and setDisableRain; :150
     canSpawnLightningBolt -->

<!-- Vegetation and Mobs are left out: the biome never appears, so nothing it
     would hold is ever placed. Its spawn lists are the shared ones
     (BiomeGenDesert adds nothing), and no term in ChunkProviderGenerate.java
     populate names it. -->

## Data values

- Map colour: `#FFED93`

<!-- src: BiomeGenBase.java:18 setColor(16772499). The game stores the colour
     but never reads it. -->
