---
title: Nether
description: A second dimension reached through an obsidian portal, where one block covers eight in the Overworld.
type: dimension
categories: [Dimensions]
---

**Nether** is a second dimension, reached from the [[Overworld]] through a
[[Portal|portal]] built of [[Obsidian|obsidian]].

## Reaching it

A portal is a frame of obsidian around a space 2 blocks wide and 3 tall, with
[[Fire|fire]] set on the obsidian floor inside it. The frame's four corners are
never checked, so ten blocks of obsidian are enough.
<!-- src: BlockPortal.java:37 tryToCreatePortal, whose loop skips the corner
     positions; BlockFire.java:192 onBlockAdded starts the check whenever the
     block below the new fire is obsidian -->

Standing in the portal for 80 ticks — 4 seconds — moves the player. Stepping out
drains that progress four times faster than it builds. After a trip the player
must stay clear of a portal for 10 ticks before another will take them.
<!-- src: EntityPlayerSP.java:53, adding 0.0125 a tick and subtracting 0.05;
     EntityPlayer.java:811 setInPortal holds timeUntilPortal at 10 for as long
     as the player stands in one -->

Only players travel. A mob, a dropped item or a [[Minecart|minecart]] standing in
a portal is not moved, and a player riding a [[Boat|boat]] or minecart is
dismounted first.
<!-- src: Entity.java:1038 setInPortal is empty and only EntityPlayer overrides
     it; BlockPortal.java:150 ignores an entity that is riding or ridden -->

The player's x and z are divided by 8 on the way in and multiplied by 8 on the
way out, and the y is unchanged. One block walked in the Nether covers eight in
the Overworld.
<!-- src: Minecraft.java:1225 usePortal -->

At the far end the game looks for a portal block within 128 blocks in x and z at
any height, and puts the player at the closest one. Finding none, it searches 16
blocks for a spot on solid ground with a clear space 3 wide, 4 long and 4 tall,
and builds a portal there. Failing that as well, it carves one out at a height
clamped to between y=70 and y=118.
<!-- src: Teleporter.java:15 func_4106_b the search, :78 func_4108_c the build -->

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
