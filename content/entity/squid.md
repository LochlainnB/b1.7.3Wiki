---
title: Squid
description: A passive mob that swims in water in every Overworld biome and drops ink sacs.
type: entity
categories: [Mobs, Passive mobs]
---

A **squid** is a passive mob that swims in water and drops ink sacs.

## Spawning

Squid spawn [[Mob Spawning#Passive mobs|in water]], at any light level and
depth, in every [[Overworld]] biome, in packs of up to 4.
<!-- src: BiomeGenBase.java:51 spawnableWaterCreatureList;
     EntityWaterMob.java:20 getCanSpawnHere; EntityLiving.java:842
     getMaxSpawnedInChunk -->

A squid [[Mob Spawning#Despawning|despawns]] only when it is more than 128
blocks from every player. The chance of despawning beyond 32 blocks never
applies to it.
<!-- src: EntitySquid.java:131 updatePlayerActionState calls despawnEntity
     every tick but never counts entityAge up, which only EntityLiving.java:690
     and EntityMob.java:14 do, so the age test at EntityLiving.java:678 never
     passes -->

## Drops

A squid drops 1–3 [[Ink Sac|ink sacs]] when it dies.
<!-- src: EntitySquid.java:54 dropFewItems, nextInt(3) + 1 of dye 0 -->

## Behaviour

A squid attacks nothing, and makes no sound.
<!-- src: EntitySquid.java:131 updatePlayerActionState seeks no target;
     :34-:43 return no living, hurt or death sound -->

It swims in bursts, in a random direction that it changes 1 tick in 50.
<!-- src: EntitySquid.java:132 picks a new direction; :87-:100 set the burst
     speed from the tentacle cycle -->

Out of water it cannot move except to fall. It takes no damage there.
<!-- src: EntitySquid.java:113 zeroes horizontal motion out of water;
     EntityLiving.java:122 is the only breathing test, and it applies only
     under water -->

## Data values

- Entity network ID: {{id|Squid}}
