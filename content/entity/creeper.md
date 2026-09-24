---
title: Creeper
description: A hostile mob that walks up to a player and explodes, with a larger blast once lightning has charged it.
type: entity
categories: [Mobs, Hostile mobs]
---

A **creeper** is a hostile mob that walks up to a player and explodes.

## Spawning

Creepers spawn [[Mob Spawning#Hostile mobs|in the dark]] in every
[[Overworld]] biome, in packs of up to 4.
<!-- src: BiomeGenBase.java:45 spawnableMonsterList; EntityLiving.java:842
     getMaxSpawnedInChunk -->

On Peaceful no creeper spawns, and any in the world is removed.
<!-- src: Minecraft.java:1164 setAllowedMobSpawns; EntityMob.java:20 onUpdate -->

## Drops

A creeper drops 0–2 [[Gunpowder|gunpowder]] when it dies. A creeper that
explodes drops nothing.
<!-- src: EntityCreeper.java:129 getDropItemId; EntityLiving.java:424
     dropFewItems, nextInt(3) of the item; the blast at EntityCreeper.java:106
     calls setEntityDead, not onDeath -->

A creeper killed by a [[Skeleton|skeleton's]] arrow also drops a
[[Music Disc|music disc]], "13" or "cat" at even odds.
<!-- src: EntityCreeper.java:81 onDeath; an arrow names its shooter as the
     attacker (EntityArrow.java:163); Item.java:378 record13 and recordCat,
     items 2256 and 2257 -->

Killing one earns the *Monster Hunter* [[Achievements|achievement]].
<!-- src: EntityPlayer.java:797 onKillEntity, for any EntityMob -->

## Behaviour

A creeper targets the nearest player within 16 blocks, if it can see them, and
walks towards them. It also attacks any mob or player that hurts it.
<!-- src: EntityMob.java:28 findPlayerToAttack, :33 attackEntityFrom sets the
     attacker as the target; EntityCreature.java:16 updatePlayerActionState -->

It walks at 3.0 blocks per second, 70% of a player's walking speed.
<!-- src: EntityLiving.java:56 moveSpeed 0.7, which EntityCreeper keeps; see
     Zombie for how moveSpeed becomes blocks per second -->

Within 3 blocks of a target it can see, it hisses and lights its fuse. It swells
and flashes white while the fuse burns. After 30 ticks it explodes and is
destroyed.
<!-- src: EntityCreeper.java:89 attackEntity, :99 the 30-tick fuse;
     RenderCreeper.java:12 and :30 scale and flash by setCreeperFlashTime -->

The fuse keeps burning while the target stays within 7 blocks and in sight.
Otherwise it burns back down at the same rate.
<!-- src: EntityCreeper.java:92 the 3 and 7 block tests, :110 counting down;
     :31 attackBlockedEntity counts down while the target is out of sight -->

Its blast is an [[Explosion#Sizes|explosion]] of size 3.
<!-- src: EntityCreeper.java:103 -->

A creeper struck by [[Weather#Lightning|lightning]] becomes charged, and its
blast is size 6. The charge is permanent.
<!-- src: EntityCreeper.java:141 onStruckByLightning, :101 the charged blast;
     :18 writeEntityToNBT saves it as "powered" -->

With no target it wanders, choosing darker spaces.
<!-- src: EntityCreature.java:118 updateWanderPath takes the best of ten
     random spots by EntityMob.java:57 getBlockPathWeight, 0.5 - brightness -->

## Data values

- Entity network ID: {{id|Creeper}}
