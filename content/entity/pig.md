---
title: Pig
description: A passive mob that spawns on grass, drops porkchops, and can be saddled and ridden.
type: entity
categories: [Mobs, Passive mobs]
---

A **pig** is a passive mob that drops porkchops and can be ridden once saddled.

## Spawning

Pigs spawn [[Mob Spawning#Passive mobs|on grass in light above 8]] in every
[[Overworld]] biome, in packs of up to 4.
<!-- src: BiomeGenBase.java:48 spawnableCreatureList; EntityAnimal.java:20
     getCanSpawnHere; EntityLiving.java:842 getMaxSpawnedInChunk -->

## Drops

A pig drops 0–2 [[Raw Porkchop|raw porkchops]] when it dies, or 0–2
[[Cooked Porkchop|cooked porkchops]] if it is on fire.
<!-- src: EntityPig.java:45 getDropItemId tests fire > 0; EntityLiving.java:424
     dropFewItems, nextInt(3) of the item -->

A saddled pig does not drop its saddle.
<!-- src: EntityPig overrides getDropItemId alone, not dropFewItems -->

## Behaviour

A pig attacks nothing, and does not flee when hurt.
<!-- src: EntityCreature.java:155 findPlayerToAttack returns null; neither
     EntityAnimal nor EntityPig overrides it or attackEntityFrom -->

It walks at 3.0 blocks per second, 70% of a player's walking speed.
<!-- src: EntityLiving.java:56 moveSpeed 0.7, which EntityPig keeps; see
     Zombie for how moveSpeed becomes blocks per second -->

Using a [[Saddle|saddle]] on a pig saddles it and uses up the saddle. Hitting
the pig with the saddle does the same. The saddle cannot be taken off.
<!-- src: ItemSaddle.java:9 saddleEntity, reached by using it
     (EntityPlayer.java:461) or hitting with it (ItemSaddle.java:20 hitEntity);
     nothing but EntityPig.java:21 readEntityFromNBT calls setSaddled -->

Using a saddled pig mounts it, and using it again dismounts. The rider cannot
steer.
<!-- src: EntityPig.java:36 interact; Entity.java:982 mountEntity dismounts a
     player already riding it; EntityPig has no movement of its own, and
     Entity.java:971 updateRiderPosition carries the rider along -->

A rider takes the same [[Damage#Environmental damage|fall damage]] as the pig.
The *When Pigs Fly* [[Achievements|achievement]] is for falling more than 5
blocks while riding a pig.
<!-- src: Entity.java:570 fall passes the distance to riddenByEntity;
     EntityPig.java:71 fall, over 5 with a player riding -->

[[Weather#Lightning|Lightning]] turns a pig into a [[Pig Zombie|pig zombie]].
<!-- src: EntityPig.java:62 onStruckByLightning -->

It wanders, choosing [[Grass|grass]] and then brighter spaces.
<!-- src: EntityCreature.java:118 updateWanderPath takes the best of ten
     random spots by EntityAnimal.java:8 getBlockPathWeight, 10 above grass
     and brightness - 0.5 elsewhere -->

## Data values

- Entity network ID: {{id|Pig}}
