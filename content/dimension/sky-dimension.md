---
title: Sky Dimension
description: A third dimension the game can generate but never creates.
type: dimension
categories: [Dimensions]
---

{{hatnote|This page is about the dimension. For the biome of the same name, see [[Sky]].}}

**Sky Dimension** is a third dimension the game can build but never creates.

## Reaching it

There is no way in. A world is opened by dimension number, and only 0 and -1 are
ever asked for. Single-player builds the [[Overworld]] and the [[Nether]], and a
[[Portal|portal]] switches between the two. A server holds an array of two worlds
and sends a travelling player to whichever one it is not in.
<!-- src: World.java:185 asks only for -1 or 0; Minecraft.java:1213 usePortal
     toggles between them; MinecraftServer.java:138 sizes worldMngr at 2, and
     :404 getWorldManager maps everything but -1 onto slot 0.
     WorldProvider.java:106 answers a 1 with WorldProviderSky, and nothing
     passes it a 1. -->

## Terrain

Terrain comes from the same kind of density field as the Overworld's, but only
[[Stone|stone]] is placed. No [[Water|water]] fills the space below sea level and
no [[Bedrock|bedrock]] closes off the bottom of the world.
<!-- src: ChunkProviderSky.java:80, which writes stone where the density is above
     zero and leaves air everywhere else -->

The field is biased downwards by a constant, then blended towards a large
negative value within 8 blocks of y=0 and again from y=8 up to the top of the
world. Stone is confined to the lower part of the world and never reaches the
top of it.
<!-- src: ChunkProviderSky.java:242 the -8 bias, :247 and :253 the two blends
     towards -30 -->

The surface is [[Grass|grass]] over [[Dirt|dirt]], and caves are cut by the same
generator the Overworld uses.
<!-- src: ChunkProviderSky.java:103 replaceBlocksForBiome, :20 MapGenCaves -->

Population is the Overworld's, run with the biome always [[Sky]]: the same ores,
[[Clay|clay]], lakes, [[Dungeon|dungeons]] and springs, the same flowers,
[[Mushroom|mushrooms]], [[Sugar cane]] and [[Pumpkin|pumpkins]], and one tree in
one chunk in ten. No [[Tall Grass|tall grass]], [[Dead Bush|dead bushes]] or
[[Cactus|cacti]] generate at all. Temperature is fixed at 0.5, so [[Snow|snow]]
settles on any surface above y=64.
<!-- src: ChunkProviderSky.java:269 populate, whose biome-gated branches never
     match; WorldChunkManagerHell.java:33 getTemperatures returns the provider's
     0.5 -->

## Light and weather

The sun never moves, and sky light is never reduced. A block under open sky reads
light 15 at every point of the clock.
<!-- src: WorldProviderSky.java:13 calculateCelestialAngle returns 0, which is
     noon, and World.java:999 calculateSkylightSubtracted returns 0 for it -->

Clouds sit at y=8, below the terrain rather than above it. There is no sunrise
or sunset colour, and the sky beneath the world is drawn in the same colour as
the sky over it.
<!-- src: WorldProviderSky.java:45 getCloudHeight, :17 calcSunriseSunsetColors
     returns null, :41 func_28112_c drops the darkened void colour -->

Rain and thunderstorms run as they do in the Overworld. Rain lays no
[[Snow|snow]] and never brings lightning: the [[Sky]] biome has neither snow nor
rain enabled.
<!-- src: WorldProviderSky leaves hasNoSky false, so World.java:1792
     updateWeather runs; World.java:1938 tests the biome's enableSnow;
     BiomeGenBase.java:150 canSpawnLightningBolt, against the flags set at :21 -->

## Mobs

{{main|Mob Spawning}}

[[Chicken|Chickens]] are the only mob on the Sky biome's spawn lists. No monster
and no water creature spawns.
<!-- src: BiomeGenSky.java:5 clears all three lists and adds the chicken alone -->

## Data values

- Dimension: `1`

The dimension has no save folder of its own. Only the Nether is given one, and
everything else is written into the world folder itself.
<!-- src: SaveHandler.java:71 getChunkLoader, which special-cases
     WorldProviderHell and nothing else -->
