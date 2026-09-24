---
title: Cow
description: A passive mob that spawns on grass, drops leather and fills buckets with milk.
type: entity
categories: [Mobs, Passive mobs]
---

A **cow** is a passive mob that drops leather and gives milk.

## Spawning

Cows spawn [[Mob Spawning#Passive mobs|on grass in light above 8]] in every
[[Overworld]] biome, in packs of up to 4.
<!-- src: BiomeGenBase.java:50 spawnableCreatureList; EntityAnimal.java:20
     getCanSpawnHere; EntityLiving.java:842 getMaxSpawnedInChunk -->

## Drops

A cow drops 0–2 [[Leather|leather]] when it dies.
<!-- src: EntityCow.java:34 getDropItemId; EntityLiving.java:424
     dropFewItems, nextInt(3) of the item -->

## Behaviour

A cow attacks nothing, and does not flee when hurt.
<!-- src: EntityCreature.java:155 findPlayerToAttack returns null; neither
     EntityAnimal nor EntityCow overrides it or attackEntityFrom -->

It walks at 3.0 blocks per second, 70% of a player's walking speed.
<!-- src: EntityLiving.java:56 moveSpeed 0.7, which EntityCow keeps; see
     Zombie for how moveSpeed becomes blocks per second -->

Using an empty [[Bucket|bucket]] on a cow fills it with [[Milk|milk]]. A cow
can be milked any number of times.
<!-- src: EntityCow.java:38 interact, which keeps no count -->

It wanders, choosing [[Grass|grass]] and then brighter spaces.
<!-- src: EntityCreature.java:118 updateWanderPath takes the best of ten
     random spots by EntityAnimal.java:8 getBlockPathWeight, 10 above grass
     and brightness - 0.5 elsewhere -->

## Data values

- Entity network ID: {{id|Cow}}
