---
title: Nether
description: A second dimension reached through an obsidian portal, where one block covers eight in the Overworld.
type: dimension
categories: [Dimensions]
---

**Nether** is a second dimension, reached from the [[Overworld]] through a
[[Portal|portal]] built of [[Obsidian|obsidian]].

## Nether Portals

{{main|Nether Portal}}

A portal is a frame of obsidian around an upright space 2 blocks wide and 3 tall,
lit with [[Fire|fire]]. Standing in it for 4 seconds moves the player.

Only players travel. A mob, a dropped item or a [[Minecart|minecart]] standing in
a portal is not moved.

A player's x and z are divided by 8 on the way in and multiplied by 8 on the way
out, and the y is unchanged. One block walked in the Nether covers eight in the
Overworld.

## Terrain

{{main|World Generation#The Nether}}

The Nether is built of [[Netherrack|netherrack]]. A sea of [[Lava|lava]] fills it
to y=32, and [[Bedrock|bedrock]] closes it off at y=0 and again at y=127.
Between y=60 and y=65 the top of a column is [[Gravel|gravel]] or
[[Soul Sand|soul sand]] instead of netherrack. [[Glowstone]] hangs from ceilings,
and [[Mushroom|mushrooms]] and [[Fire|fire]] are scattered over the floors.

There are no ores, no lakes, no [[Dungeon|dungeons]] and no trees. Caves are
seeded into one chunk in five rather than one in fifteen, and their tunnels are
twice as wide and half as tall as the Overworld's.

## Light and weather

Sky light is never calculated. Every block in the Nether has a sky light of 0,
and [[Torch|torches]], glowstone, lava and fire are the only light there is.
<!-- src: Chunk.java:106, which builds no skylight map where the provider has no
     sky -->

Full darkness in the Nether is twice as bright as full darkness in the Overworld.
<!-- src: WorldProviderHell.java:16 generateLightBrightnessTable, whose floor
     term is 0.1 against WorldProvider.java:20's 0.05 -->

There is no sun, no sky, no clouds and no weather. The fog is dark red and starts
at the player rather than a quarter of the way to the horizon.
<!-- src: RenderGlobal.java:600 renderSky, :725 renderClouds; World.java:1793
     updateWeather; WorldProviderHell.java:12; EntityRenderer.java:911 -->

A [[Compass|compass]] and a [[Clock|clock]] both spin at random.
<!-- src: TextureCompassFX.java:57, TextureWatchFX.java:38 -->

## Mobs

{{main|Mob Spawning}}

[[Ghast|Ghasts]] and [[Pig Zombie|pig zombies]] are the only mobs that spawn, and
the game draws between them evenly. Neither tests light, so both appear in any
clear space at any brightness, and both need a difficulty above Peaceful. A ghast
succeeds one attempt in twenty, and a chunk holds at most one.
<!-- src: BiomeGenHell.java:5; EntityGhast.java:151, EntityPigZombie.java:27
     getCanSpawnHere -->

## Behaviour

Dying in the Nether returns the player to the Overworld.
<!-- src: Minecraft.java:1418 respawn; ServerConfigurationManager.java:132
     recreatePlayerEntity, always called with dimension 0 -->

Using a [[Bed|bed]] in the Nether destroys it and sets off an explosion that
starts fires.
<!-- src: BlockBed.java:30, newExplosion at strength 5 with the fire flag set -->

A [[Water Bucket|water bucket]] cannot be emptied in the Nether. The water fizzes
away, and the bucket empties all the same.
<!-- src: ItemBucket.java:80 -->

Lava spreads as far as [[Water|water]] does — seven blocks from a source rather
than three.
<!-- src: BlockFlowing.java:24, which adds 1 to the flow decay per block in the
     Nether where it adds 2 elsewhere -->

## Data values

- Dimension: `-1`

Nether chunks are saved in a `DIM-1` folder inside the world folder.
<!-- src: SaveHandler.java:71 getChunkLoader -->
