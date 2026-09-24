---
title: Chicken
description: A passive mob that lays an egg every 5 to 10 minutes, drops feathers and falls slowly.
type: entity
categories: [Mobs, Passive mobs]
---

A **chicken** is a passive mob that lays eggs and drops feathers.

## Spawning

Chickens spawn [[Mob Spawning#Passive mobs|on grass in light above 8]] in every
[[Overworld]] biome and in the [[Sky]], in packs of up to 4.
<!-- src: BiomeGenBase.java:49 spawnableCreatureList; BiomeGenSky.java:8;
     EntityAnimal.java:20 getCanSpawnHere; EntityLiving.java:842
     getMaxSpawnedInChunk -->

A thrown [[Egg|egg]] [[Mob Spawning#Other ways mobs appear|hatches a chicken]]
one time in eight.
<!-- src: EntityEgg.java:156 -->

## Drops

A chicken drops 0–2 [[Feather|feathers]] when it dies.
<!-- src: EntityChicken.java:74 getDropItemId; EntityLiving.java:424
     dropFewItems, nextInt(3) of the item -->

## Behaviour

A chicken attacks nothing, and does not flee when hurt.
<!-- src: EntityCreature.java:155 findPlayerToAttack returns null; neither
     EntityAnimal nor EntityChicken overrides it or attackEntityFrom -->

It walks at 3.0 blocks per second, 70% of a player's walking speed.
<!-- src: EntityLiving.java:56 moveSpeed 0.7, which EntityChicken keeps; see
     Zombie for how moveSpeed becomes blocks per second -->

It lays an [[Egg|egg]] every 5 to 10 minutes, dropped on the ground as an item.
<!-- src: EntityChicken.java:43 onLivingUpdate; :17 and :46 set the timer to
     6000 + nextInt(6000) ticks -->

It falls no faster than 2.3 blocks per second, and takes no
[[Damage#Environmental damage|fall damage]].
<!-- src: EntityChicken.java:38 multiplies downward motion by 0.6 each tick in
     the air, after EntityLiving.java:532 subtracts 0.08 and scales by 0.98:
     a steady fall of 0.114 blocks per tick. EntityChicken.java:51 fall is
     empty -->

It wanders, choosing [[Grass|grass]] and then brighter spaces.
<!-- src: EntityCreature.java:118 updateWanderPath takes the best of ten
     random spots by EntityAnimal.java:8 getBlockPathWeight, 10 above grass
     and brightness - 0.5 elsewhere -->

## Data values

- Entity network ID: {{id|Chicken}}
