---
title: Sheep
description: A passive mob that spawns on grass in one of six fleece colours, and gives wool when sheared or killed.
type: entity
categories: [Mobs, Passive mobs]
---

A **sheep** is a passive mob that is sheared for [[Wool|wool]].

## Spawning

Sheep spawn [[Mob Spawning#Passive mobs|on grass in light above 8]] in every
[[Overworld]] biome, in packs of up to 4.
<!-- src: BiomeGenBase.java:47 spawnableCreatureList; EntityAnimal.java:20
     getCanSpawnHere; EntityLiving.java:842 getMaxSpawnedInChunk -->

A sheep spawns with a random fleece colour:

| Fleece | Chance |
|---|---|
| White | 81.836% |
| Black | 5% |
| Gray | 5% |
| Light gray | 5% |
| Brown | 3% |
| Pink | 0.164% |

<!-- src: SpawnerAnimals.java:167 creatureSpecificInit; EntitySheep.java:102
     getRandomFleeceColor: under 5 of 100 black (15), under 10 gray (7), under
     15 light gray (8), under 18 brown (12), then pink (6) one time in 500 and
     white (0) otherwise -->

## Drops

An unsheared sheep drops 1 [[Wool|wool]] of its fleece colour when it dies. A
sheared sheep drops nothing.
<!-- src: EntitySheep.java:23 dropFewItems -->

Using [[Shears|shears]] on an unsheared sheep drops 2–4 wool of its colour and
leaves it sheared. Each shearing costs the shears 1
[[Durability|durability]].
<!-- src: EntitySheep.java:34 interact, 2 + nextInt(3) wool; :49 damageItem(1) -->

## Behaviour

A sheep attacks nothing, and does not flee when hurt.
<!-- src: EntityCreature.java:155 findPlayerToAttack returns null; neither
     EntityAnimal nor EntitySheep overrides it, and EntitySheep.java:19
     attackEntityFrom only calls super -->

It walks at 3.0 blocks per second, 70% of a player's walking speed.
<!-- src: EntityLiving.java:56 moveSpeed 0.7, which EntitySheep keeps; see
     Zombie for how moveSpeed becomes blocks per second -->

A sheared sheep never regrows its fleece.
<!-- src: setSheared is called only by EntitySheep.java:38 interact, with true,
     and :63 readEntityFromNBT -->

Using a [[Dye|dye]] on an unsheared sheep turns its fleece that colour, and uses
one dye. [[Bone Meal|Bone meal]] turns it white. A sheared sheep cannot be dyed.
<!-- src: ItemDye.java:80 saddleEntity, reached from EntityPlayer.java:461
     because EntitySheep.java:52 interact returns false; BlockCloth.java:21
     getBlockFromDye maps bone meal, dye 15, to white wool, 0 -->

Wild [[Wolf|wolves]] attack sheep.
<!-- src: EntityWolf.java:108 updatePlayerActionState -->

It wanders, choosing [[Grass|grass]] and then brighter spaces.
<!-- src: EntityCreature.java:118 updateWanderPath takes the best of ten
     random spots by EntityAnimal.java:8 getBlockPathWeight, 10 above grass
     and brightness - 0.5 elsewhere -->

## Data values

- Entity network ID: {{id|Sheep}}
