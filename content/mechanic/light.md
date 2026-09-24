---
title: Light
description: The light level every block space holds — sky light and block light, what stops it, how night dims it, and what each light-sensitive block and mob needs.
type: mechanic
categories: [Game mechanics]
aliases: [Light level, Sky light, Block light]
---

**Light** is a level from 0 to 15 held by every block space.

## Light level

Every space stores two values from 0 to 15:

- **Sky light**, which comes from the sky.
- **Block light**, which comes from blocks that give off light.

A space's light level is the higher of its block light and its sky light minus
the sky's [[Light#Day and night|darkness]].
<!-- src: Chunk.java:341 getBlockLightValue, max(sky - skylightSubtracted,
     block); World.java:545 getBlockLightValue_do passes skylightSubtracted -->

## Sky light

A space open to the sky has sky light 15, however far down it is. A space is
open to the sky when nothing above it is a full opaque block or one of the
blocks [[Light#What stops light|listed below]]. Any other space takes the brightest
sky light among its six neighbours, minus the [[Light#What stops light|light lost in its own block]].
<!-- src: Chunk.java:397 canBlockSeeTheSky, true at or above the column's
     height map; Chunk.java:67 the height map stops at the first block with
     non-zero opacity; MetadataChunkBlock.java:84 sets 15 where the sky is
     open, otherwise the brightest neighbour less max(opacity, 1) -->

The [[Nether]] has no sky light.
<!-- src: Chunk.java:106 generateSkylightMap skips the sky where hasNoSky;
     WorldProviderHell.java:8 -->

## Block light

The blocks below give off light. The space a source stands in has that much
block light. Any other space takes the brightest block light among its six
neighbours, less the light lost in its own block.
<!-- src: MetadataChunkBlock.java:79 lightValue of the block in the space,
     :88-:113 the brightest neighbour less max(opacity, 1), whichever is higher -->

{{list|light}}

A [[Furnace|furnace]] gives off light only while it burns, [[Redstone Ore|redstone
ore]] only while it glows, a [[Redstone Torch|redstone torch]] only while it is
on and a [[Redstone Repeater|repeater]] only while it is powered.
<!-- src: Block.java:654, :666, :668, :686 set light on the lit twin only -->

## What stops light

Light loses 1 for each block it passes through. A full, opaque block stops it.
Every other block loses 1, as air does, and leaves the space below it open to
the sky, except these:

{{list|opacity}}

<!-- src: Block.java:152 lightOpacity 255 for an opaque cube, 0 otherwise;
     MetadataChunkBlock.java:70 treats 0 as 1; Chunk.java:67 ends the open sky
     at any non-zero opacity. The listed blocks call setLightOpacity:
     Block.java:600-610, :622, :671; BlockStairs.java:15, BlockStep.java:16,
     BlockFarmland.java:11 -->

Slabs, stairs and [[Farmland|farmland]] stop light although they do not fill
their space. The game reads the light at one of them as the brightest of the
spaces above and beside it.
<!-- src: World.java:548, the stairSingle, tilledField and stair case in
     getBlockLightValue_do -->

## Day and night

The sky's darkness is subtracted from sky light when a light level is read. It is 
0 by day and 11 at night, so a space open to the sky reads 15 by day and 4 at
night:

| Time of day (ticks) | Sky light read |
|---|---|
| 0 to 12,040 | 15 |
| 12,040 to 13,670 | falls from 15 to 4 |
| 13,670 to 22,330 | 4 |
| 22,330 to 23,960 | rises from 4 to 15 |

<!-- src: World.java:999 calculateSkylightSubtracted, (int)(11 * darkness) from
     the celestial angle of WorldProvider.java:42; ticks worked out by
     evaluating both at every tick of a day -->

[[Weather|Rain]] darkens the daytime sky to 12, and a thunderstorm to 10.
Neither darkens the night.
<!-- src: World.java:1010-:1011, each scaling daylight by 1 - strength * 5/16 -->

The game counts it as day while the sky reads 12 or brighter.
<!-- src: World.java:700 isDaytime, skylightSubtracted < 4 -->

The stored sky light never changes with the time of day. Some checks read a
space's light without subtracting darkness, and see a space open to the sky
as 15 at midnight.
<!-- src: World.java:529 getFullBlockLightValue passes 0 for the darkness -->

A day is 24,000 ticks, kept by the [[Game Tick#The world clock|world clock]].

## What light affects

| What | Needs | Reads |
|---|---|---|
| [[Mob Spawning#Hostile mobs\|Hostile mob spawning]] | two random tests | stored sky light, then light level |
| [[Mob Spawning#Passive mobs\|Animal spawning]] | above 8 | light level, ignoring night |
| [[Crops]] and [[Sapling\|saplings]] growing | 9 or more, in the space above | light level |
| [[Grass]] spreading | 9 or more above the grass, 4 or more above the dirt | light level |
| [[Grass]] dying | below 4, under water, ice, lava, an opaque block, a slab, stairs or farmland | light level |
| [[Flower\|Flowers]], [[Rose\|roses]], [[Tall Grass\|tall grass]], [[Dead Bush\|dead bushes]], crops and saplings staying put | 8 or more, or open to the sky | light level, ignoring night |
| [[Mushroom\|Mushrooms]] spreading and staying put | 12 or less | light level, ignoring night |
| [[Ice]] melting | above 8 | block light alone |
| [[Snow]] layers melting | above 11 | block light alone |
| [[Zombie\|Zombies]], [[Skeleton\|skeletons]] and [[Pig Zombie\|pig zombies]] catching fire | 12 or more, open to the sky, by day: a chance each tick, from 1 in 120 at 12 to 1 in 25 at 15 | light level |
| [[Spider\|Spiders]] seeking a player | 11 or less | light level |
| Hostile mobs except slimes and ghasts ageing towards [[Mob Spawning#Despawning\|despawning]] | 12 or more, at three times the rate | light level |
| Hostile mobs except slimes, ghasts and giants wandering | prefer darker spaces | light level |
| [[Giant\|Giants]] wandering | prefer brighter spaces | light level |
| Animals wandering | prefer [[Grass\|grass]], then brighter spaces | light level |

<!-- src: EntityMob.java:69 getCanSpawnHere; EntityAnimal.java:24
     getCanSpawnHere; BlockCrops.java:20, BlockSapling.java:15, BlockGrass.java:32
     and :43 updateTick; BlockFlower.java:40 canBlockStay, which BlockCrops,
     BlockSapling, BlockTallGrass and BlockDeadBush inherit;
     BlockMushroom.java:35; BlockIce.java:34, 11 less its own opacity of 3;
     BlockSnow.java:72. BlockSnowBlock.java:19 tests the block light stored in
     its own space, which is 0 for an opaque block, so a snow block never
     melts. Grass dying: BlockGrass.java:32 tests lightOpacity above 2, which
     BlockStep.java:16, BlockStairs.java:15, BlockFarmland.java:11 and lava
     (Block.java:602-:603) all have. EntityZombie.java:11-:14 and
     EntitySkeleton.java:24 roll rand * 30 < (brightness - 0.4) * 2 each tick;
     EntityPigZombie extends EntityZombie and runs it too.
     EntitySpider.java:20 findPlayerToAttack; EntityMob.java:12 onLivingUpdate;
     EntityMob.java:57 and EntityAnimal.java:9 getBlockPathWeight;
     EntityGiantZombie.java:14 overrides it as brightness - 0.5, the reverse.
     Slimes and ghasts are not EntityMob. A mob's brightness is read at two thirds of its height
     (Entity.java:628), and a brightness above 0.5 is light 12 or more in the
     table WorldProvider.java:19 builds -->
