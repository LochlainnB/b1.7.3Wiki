---
title: Weather
description: Rain, snow and thunderstorms — how long each lasts, which biomes get which, what rain puts out, where lightning strikes and when water freezes.
type: mechanic
categories: [Game mechanics]
aliases: [Rain, Snowfall, Thunderstorm, Thunder, Lightning]
---

**Weather** is the rain, snow and thunderstorms of the [[Overworld]].

## The cycle

Rain and thunder each run on a countdown of their own. When a countdown ends,
the state flips and a new countdown starts:

| State | Lasts (ticks) |
|---|---|
| Raining | 12,000 to 24,000 |
| Not raining | 12,000 to 180,000 |
| Thundering | 3,600 to 15,600 |
| Not thundering | 12,000 to 180,000 |

<!-- src: World.java:1792 updateWeather; nextInt(12000) + 12000,
     nextInt(168000) + 12000, nextInt(12000) + 3600 -->

A thunderstorm is thunder while it rains. Thunder without rain does nothing.
<!-- src: World.java:2428 getWeightedThunderStrength multiplies thunder by rain;
     :2441 getIsThundering needs the product above 0.9 -->

Rain fades in and out over 100 ticks. Its effects begin 20 ticks into the fade
in and end 20 ticks before the fade out finishes.
<!-- src: World.java:1828 steps rainingStrength by 0.01 a tick; :2445 isRaining
     needs it above 0.2 -->

The weather is the same across the whole world, and is saved with it. The
[[Nether]] has none.
<!-- src: WorldInfo.java:99-:102 rainTime, raining, thunderTime, thundering;
     World.java:1793 updateWeather does nothing where the provider has no sky -->

Sleeping through the night in a [[Bed|bed]] ends rain and thunder, and starts
both clear countdowns afresh.
<!-- src: World.java:1757 wakeUpAllPlayers, :2406 stopPrecipitation zeroes both
     countdowns with both states off -->

## Biomes

The biome under each column decides what falls there:

| Biome | Weather |
|---|---|
| [[Rainforest]], [[Swampland]], [[Seasonal Forest]], [[Forest]], [[Savanna]], [[Shrubland]], [[Plains]] | rain and lightning |
| [[Taiga]], [[Tundra]], [[Ice Desert]] | snow |
| [[Desert]] | none |

<!-- src: BiomeGenBase.java:15-:21 setEnableSnow and setDisableRain; :150
     canSpawnLightningBolt; EntityRenderer.java:673 draws snow where the biome
     has snow -->

## Rain

A space is rained on while it rains, when it is open to the [[Light#Sky
light|sky]], nothing solid or liquid is above it, and its biome gets rain.
Snow does not count as rain.
<!-- src: World.java:2448 canBlockBeRainedOn; findTopSolidBlock (:1122) stops at
     any solid or liquid material; a biome with snow returns false -->

| What | Effect |
|---|---|
| [[Fire]] | goes out when it or a space beside it is rained on, unless it burns on [[Netherrack\|netherrack]]; does not spread into a rained-on space |
| A burning entity | goes out, and does not catch fire; see [[Damage#Catching fire]] |
| [[Farmland]] | becomes fully wet, as it does beside water |
| [[Fishing Rod\|Fishing]] | a bite comes 1 tick in 300, rather than 1 in 500 |
| Sky light | darkened to 12 by day; see [[Light#Day and night]] |

<!-- src: BlockFire.java:61, :97, :119; Entity.java:577 isWet;
     BlockFarmland.java:36; EntityFish.java:276 -->

## Thunderstorms

A thunderstorm darkens the daytime sky to [[Light#Day and night|light 10]].
The game stops counting it as day, so a player can sleep in a bed, and
[[Zombie|zombies]] and [[Skeleton|skeletons]] do not catch fire.
<!-- src: World.java:999 calculateSkylightSubtracted gives 5 at full rain and
     thunder; World.java:700 isDaytime needs less than 4; EntityPlayer.java:545;
     EntityZombie.java:12, EntitySkeleton.java:24 -->

[[Mob Spawning#Hostile mobs|Hostile mobs spawn]] as though the sky's darkness
were 10, by day or night, which puts a space open to the sky at light 5.
<!-- src: EntityMob.java:77 -->

### Lightning

{{main|Lightning Bolt}}

During a thunderstorm, each chunk within 9 chunks of a player has a 1 in
100,000 chance each tick of a strike. A lone player in a rainy biome sees about
one strike every 14 seconds.
<!-- src: World.java:1917; the chunks are the 19 x 19 square of
     updateBlocksAndPlayCaveSounds (:1880), 361 in all -->

The strike takes a random column of the chunk. It lands in the space above the
highest solid or liquid block, and only if that space is rained on. Nothing
strikes a snowy biome or a desert.
<!-- src: World.java:1919-:1924 -->

A strike sets fires, and damages, burns or transforms the entities around the
space it lands in.

## Snow and ice

In a biome with snow, each chunk within 9 chunks of a player picks one random
column 1 tick in 16. Where the block light above that column's highest solid or
liquid block is below 10:

- while it snows, a [[Snow|snow]] layer settles on that block, if it is a full,
  solid block other than [[Ice|ice]];
- if that block is a still [[Water|water]] source, it freezes to ice, whatever
  the weather.

<!-- src: World.java:1932 the one-in-sixteen draw; :1939 the biome and block
     light test; :1942 the snow, needing isRaining; :1946 the ice, with no
     weather test; BlockSnow.java:31 canPlaceBlockAt wants an opaque cube -->

Snow placed when a world is generated follows temperature instead; see
[[World Generation#Snow]].
