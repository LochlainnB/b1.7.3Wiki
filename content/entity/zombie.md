---
title: Zombie
description: A hostile mob that spawns in the dark across the Overworld, chases players and burns in daylight.
type: entity
categories: [Mobs, Hostile mobs]
---

A **zombie** is a hostile mob that chases players and hits them in melee.

## Spawning

Zombies spawn [[Mob Spawning#Hostile mobs|in the dark]] in every [[Overworld]]
biome, in packs of up to 4.
<!-- src: BiomeGenBase.java:43 spawnableMonsterList; EntityLiving.java:842
     getMaxSpawnedInChunk -->

Half of the [[Monster Spawner|monster spawners]] in [[Dungeon|dungeons]] spawn
zombies. A zombie is one of the three mobs that can
[[Mob Spawning#Other ways mobs appear|spawn beside a sleeping player]].
<!-- src: WorldGenDungeons.java:134 pickMobSpawner; SpawnerAnimals.java:10
     nightSpawnEntities -->

On Peaceful no zombie spawns, and any in the world is removed.
<!-- src: Minecraft.java:1164 setAllowedMobSpawns; EntityMob.java:20 onUpdate -->

## Drops

A zombie drops 0–2 [[Feather|feathers]] when it dies.
<!-- src: EntityZombie.java:34 getDropItemId; EntityLiving.java:424
     dropFewItems, nextInt(3) of the item -->

Killing one earns the *Monster Hunter* [[Achievements|achievement]].
<!-- src: EntityPlayer.java:797 onKillEntity, for any EntityMob -->

## Behaviour

A zombie targets the nearest player within 16 blocks, if it can see them, and
walks towards them. It also attacks any mob or player that hurts it.
<!-- src: EntityMob.java:28 findPlayerToAttack, :33 attackEntityFrom sets the
     attacker as the target; EntityCreature.java:16 updatePlayerActionState -->

It walks at 2.2 blocks per second, 50% of a player's walking speed.
<!-- src: EntityZombie.java:7 moveSpeed 0.5. A mob on a path sets moveForward
     to moveSpeed (EntityCreature.java:69) where a walking player's input is 1,
     and both become speed alike: EntityLiving.java:640 scales it by 0.98, :489
     accelerates by 0.1 times that a tick, :492 applies ground friction 0.546,
     a steady 0.216 blocks per tick (4.3 per second) for an input of 1 -->

It hits for [[Damage#Mob attacks|5 damage]].

By day, a zombie standing in [[Light#What light affects|light 12 or more]], open
to the sky, catches fire. It does not burn during a
[[Weather#Thunderstorms|thunderstorm]].
<!-- src: EntityZombie.java:11 onLivingUpdate; isDaytime is false in a
     thunderstorm (World.java:700) -->

With no target it wanders, choosing darker spaces.
<!-- src: EntityCreature.java:118 updateWanderPath takes the best of ten
     random spots by EntityMob.java:57 getBlockPathWeight, 0.5 - brightness -->

## Data values

- Entity network ID: {{id|Zombie}}
