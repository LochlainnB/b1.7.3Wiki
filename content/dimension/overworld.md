---
title: Overworld
description: The dimension a world starts in, and the only one with a day cycle and weather.
type: dimension
categories: [Dimensions]
---

**Overworld** is the dimension a world starts in, and the only one with a day
cycle and weather.

## Reaching it

A new world begins in the Overworld, at a spawn point the game places on
[[Sand|sand]]. A [[Portal|portal]] built here leads to the [[Nether]], and the
same portal brings a player back. Dying in the Nether also returns the player to
the Overworld.
<!-- src: WorldProvider.java:37 canCoordinateBeSpawn tests against Block.sand;
     Minecraft.java:1418 respawn calls usePortal where canRespawnHere is false -->

The Overworld is the only dimension a player can sleep or set a spawn point in.
<!-- src: EntityPlayer.java:541 sleepInBedAt returns NOT_POSSIBLE_HERE for the
     Nether; WorldProviderHell.java:45 canRespawnHere -->

## Terrain

{{main|World Generation}}

The world is 128 blocks tall. Sea level is y=64, and y=0 is [[Bedrock|bedrock]]
everywhere. The world ends 32,000,000 blocks from the origin in x and z: past
that every block reads as air, and nothing can be placed.
<!-- src: World.java:312 getBlockId, :371 setBlockAndMetadata and every other
     block accessor guard on the same range -->

Ten of the thirteen biomes generate here. [[Ice Desert]] is defined but never
chosen, and [[Hell]] and [[Sky]] belong to the other two dimensions.
<!-- src: BiomeGenBase.java:100 getBiome -->

## Light and weather

A day is 24000 ticks — 20 minutes. Sky light is reduced by up to 11 as the sun
goes down, so a block under open sky reads light 15 at noon and light 4 at
midnight. Sleeping in a bed sets the clock to the start of the next day.
<!-- src: World.java:999 calculateSkylightSubtracted; World.java:1755 rounds
     worldTime up to the next multiple of 24000 -->

The Overworld has [[Weather|weather]]. Most biomes get rain and lightning,
[[Taiga]] and [[Tundra]] get snow, and [[Desert]] gets neither.
<!-- src: BiomeGenBase.java:15-:21 setEnableSnow and setDisableRain, :150
     canSpawnLightningBolt -->

## Mobs

{{main|Mob Spawning}}

Every mob but the [[Ghast|ghast]], the [[Pig Zombie|pig zombie]] and the
[[Giant|giant]] spawns in the Overworld. All ten biomes share one set of spawn
lists. Only the [[Wolf|wolf]] is restricted to particular biomes: it is added to
the [[Forest]] and [[Taiga]] lists.
<!-- src: BiomeGenBase.java:34 the shared lists; BiomeGenForest.java:7,
     BiomeGenTaiga.java:7 -->

## Data values

- Dimension: `0`

Overworld chunks are saved in the world folder itself. A player's current
dimension is stored in the `Dimension` tag of their entity data.
<!-- src: SaveHandler.java:71 getChunkLoader; EntityPlayer.java:329 writeToNBT -->
