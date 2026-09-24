---
title: Skeleton
description: A hostile mob that spawns in the dark across the Overworld, shoots arrows at players and burns in daylight.
type: entity
categories: [Mobs, Hostile mobs]
---

A **skeleton** is a hostile mob that shoots [[Arrow|arrows]] at players.

## Spawning

Skeletons spawn [[Mob Spawning#Hostile mobs|in the dark]] in every
[[Overworld]] biome, in packs of up to 4.
<!-- src: BiomeGenBase.java:44 spawnableMonsterList; EntityLiving.java:842
     getMaxSpawnedInChunk -->

A quarter of the [[Monster Spawner|monster spawners]] in [[Dungeon|dungeons]]
spawn skeletons. A skeleton is one of the three mobs that can
[[Mob Spawning#Other ways mobs appear|spawn beside a sleeping player]].
<!-- src: WorldGenDungeons.java:134 pickMobSpawner; SpawnerAnimals.java:10
     nightSpawnEntities -->

One [[Spider|spider]] in a hundred spawns with a skeleton riding it.
<!-- src: SpawnerAnimals.java:161 creatureSpecificInit -->

On Peaceful no skeleton spawns, and any in the world is removed.
<!-- src: Minecraft.java:1164 setAllowedMobSpawns; EntityMob.java:20 onUpdate -->

## Drops

A skeleton drops 0–2 [[Arrow|arrows]] and 0–2 [[Bone|bones]] when it dies. It
holds a [[Bow|bow]], which it never drops.
<!-- src: EntitySkeleton.java:67 dropFewItems, nextInt(3) of each; :88
     defaultHeldItem is the bow, which dropFewItems leaves out -->

Killing one earns the *Monster Hunter* [[Achievements|achievement]].
<!-- src: EntityPlayer.java:797 onKillEntity, for any EntityMob -->

## Behaviour

A skeleton targets the nearest player within 16 blocks, if it can see them, and
walks towards them. It also attacks any mob or player that hurts it.
<!-- src: EntityMob.java:28 findPlayerToAttack, :33 attackEntityFrom sets the
     attacker as the target; EntityCreature.java:16 updatePlayerActionState -->

It walks at 3.0 blocks per second, 70% of a player's walking speed.
<!-- src: EntityLiving.java:56 moveSpeed 0.7, which EntitySkeleton keeps; see
     Zombie for how moveSpeed becomes blocks per second -->

It shoots an [[Arrow|arrow]] at a target it can see within 10 blocks, one every
30 ticks, for [[Damage#Mob attacks|4 damage]]. Its arrows cannot be picked up.
<!-- src: EntitySkeleton.java:34 attackEntity; EntityArrow.java:33 marks only
     a player's arrow as belonging to a player, and :259 onCollideWithPlayer
     gives back only those -->

By day, a skeleton standing in [[Light#What light affects|light 12 or more]],
open to the sky, catches fire. It does not burn during a
[[Weather#Thunderstorms|thunderstorm]].
<!-- src: EntitySkeleton.java:23 onLivingUpdate; isDaytime is false in a
     thunderstorm (World.java:700) -->

With no target it wanders, choosing darker spaces.
<!-- src: EntityCreature.java:118 updateWanderPath takes the best of ten
     random spots by EntityMob.java:57 getBlockPathWeight, 0.5 - brightness -->

## Data values

- Entity network ID: {{id|Skeleton}}
