---
title: Wandering
description: How a mob picks where to walk when it has nowhere to be — ten random spaces scored by light level or grass, with solid ground always scoring as dark.
type: mechanic
categories: [Game mechanics]
---

**Wandering** is a mob walking to a space it picks at random.

## Choosing a space

A mob picks 10 spaces at random, up to 6 blocks away in x and z and 3 up or
down, and walks towards the one that scores best. Where several tie, the first
picked wins, so each is equally likely. The spaces are not checked: one can be
in mid-air, underwater or inside a solid block.
<!-- src: EntityCreature.java:118 updateWanderPath; :126-:128 offsets
     nextInt(13) - 6, nextInt(7) - 3, nextInt(13) - 6 from the mob's position;
     :130 keeps a later spot only if it scores strictly higher -->

| Mob | Best space |
|---|---|
| [[Zombie]], [[Skeleton]], [[Spider]], [[Creeper]], [[Pig Zombie]], [[Monster]] | lowest light level |
| [[Giant]] | highest light level |
| [[Pig]], [[Cow]], [[Sheep]], [[Chicken]], [[Wolf]] | directly above a [[Grass\|grass]] block; otherwise highest light level |

<!-- src: EntityMob.java:57 getBlockPathWeight 0.5 - brightness;
     EntityGiantZombie.java:14 brightness - 0.5; EntityAnimal.java:8 10 when
     the block below is grass, else brightness - 0.5. World.java:696
     getLightBrightness looks the light level up in a table that rises with
     it (WorldProvider.java:19), so only the order of light levels matters -->

A space above grass beats any light level. Light is read as it stands at that
moment, so open sky reads 4 at [[Light#Day and night|night]].
<!-- src: World.java:545 getBlockLightValue_do subtracts skylightSubtracted -->

[[Squid]], [[Slime|slimes]] and [[Ghast|ghasts]] do not wander this way.
<!-- src: EntitySquid.java:131 replaces updatePlayerActionState without calling
     EntityCreature's; EntitySlime extends EntityLiving and EntityGhast extends
     EntityFlying, neither of which has updateWanderPath -->

### Solid ground reads as dark

The inside of a full opaque block has light level 0 unless the block gives off
light. Torchlight in the space above does not reach it.
<!-- src: MetadataChunkBlock.java:85 stores 0 in a block of opacity 15 or more
     that gives off no light; Chunk.java:111 generateSkylightMap never sets sky
     light in one; World.java:548 reads neighbours only for slabs, stairs and
     farmland -->

To a hostile mob, a space in the ground is the darkest there can be. On flat
ground, 3 of the 7 heights it picks from are below its feet, so one of its 10
spaces lands in the ground more than 99% of the time, and it picks among those
at random. Torches on a floor of full blocks do not steer it. Light decides only
between open spaces: over [[Stone Slab|slabs]], [[Wooden Stairs|stairs]],
[[Farmland|farmland]] and blocks [[Light#What stops light|light passes through]],
which read as bright as the air beside them.
<!-- src: 1 - (4/7)^10 = 0.996. World.java:548 gives stairSingle,
     tilledField, stairCompactCobblestone and stairCompactPlanks the brightest
     neighbour's light -->

To an animal, a space in the ground scores worst.

## Walking there

If the mob cannot reach the space it picked, it walks to the reachable space
closest to it. A space picked inside flat ground brings the mob to the surface
directly above. If nothing reachable is closer than where the mob stands, it
stays put.
<!-- src: EntityCreature.java:140 getEntityPathToXYZ with range 10;
     Pathfinder.java:45 keeps the explored point closest to the target, :69
     returns no path when that point is the start -->

## When a mob wanders

| Mob | Chance of a new pick each tick |
|---|---|
| Standing, with no path | about 1 in 40 |
| Walking a path | 1 in 80; the new path replaces the old |
| With a target, and no path | none; it paths to the target |
| With a target, on a path | 1 in 80, on the 19 ticks in 20 it does not path to the target |

<!-- src: EntityCreature.java:35-:41. With no path it rolls nextInt(80) twice,
     159 in 6,400; with a path once. A target and a path re-path to the target
     when nextInt(20) is 0 -->

A walking mob also has a 1 in 100 chance each tick to drop its path and stop.
<!-- src: EntityCreature.java:47 nextInt(100), :114 clears the path -->

There is no new pick while a [[Skeleton|skeleton]] can see its target within
10 blocks, while a [[Creeper|creeper]] swells, or while a [[Wolf|wolf]] sits
or shakes itself dry.
<!-- src: EntityCreature.java:36 skips updateWanderPath while hasAttacked;
     :17 sets it from isMovementCeased, EntityWolf.java:250 sitting or
     field_25052_g, set at :143 while shaking; EntitySkeleton.java:50 in
     attackEntity within 10 blocks, called only for a target it can see
     (EntityCreature.java:28); EntityCreeper.java:109 while swelling -->

## Standing

A mob with no path stands still and turns at random. Each tick it has a 1 in
50 chance to look at the nearest player within 8 blocks, for 11 to 30 ticks.
<!-- src: EntityCreature.java:113 falls back to EntityLiving.java:689
     updatePlayerActionState; :693-:694 zero movement, :696 2% chance, :697
     8 blocks, :700 10 + nextInt(20), faced until :708 counts past 0 -->
