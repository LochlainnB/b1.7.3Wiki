---
title: Slime
description: A hostile mob found below y=16 in one chunk in ten, which hops towards players and splits into smaller slimes when it dies.
type: entity
categories: [Mobs, Hostile mobs]
---

A **slime** is a hostile mob that hops towards players and splits into smaller
slimes when it dies.

## Spawning

Slimes spawn in every [[Overworld]] biome, in packs of up to 4, at any light
level. They spawn only below y=16, and only in about one chunk in ten, fixed by
the [[Mob Spawning#Hostile mobs|world seed]].
<!-- src: BiomeGenBase.java:46 spawnableMonsterList; EntityLiving.java:842
     getMaxSpawnedInChunk; EntitySlime.java:134 getCanSpawnHere -->

On Peaceful no slime spawns, but slimes already in the world stay.
<!-- src: Minecraft.java:1164 setAllowedMobSpawns skips the whole monster
     category on Peaceful. EntitySlime extends EntityLiving, not EntityMob, so
     EntityMob.java:20 does not remove it. EntitySlime.java:136 would also let
     a size 1 slime pass on Peaceful, which the skipped category makes moot. -->

A slime [[Mob Spawning#Despawning|despawns]] only when it is more than 128
blocks from every player. The chance of despawning beyond 32 blocks never
applies to it.
<!-- src: EntitySlime.java:68 updatePlayerActionState calls despawnEntity every
     tick but never counts entityAge up, which only EntityLiving.java:690 and
     EntityMob.java:14 do, so the age test at EntityLiving.java:678 never
     passes -->

## Drops

Only a slime of size 1 drops anything: 0–2 [[Slimeball|slimeballs]].
<!-- src: EntitySlime.java:130 getDropItemId; EntityLiving.java:424
     dropFewItems, nextInt(3) of the item -->

## Behaviour

A slime is size 1, 2 or 4, at even odds:

| Size | Width and height (blocks) | Health | Damage |
|---|---|---|---|
| 1 | 0.6 | 1 | 0 |
| 2 | 1.2 | 4 | 2 |
| 4 | 2.4 | 16 | 4 |

<!-- src: EntitySlime.java:11 1 << nextInt(3); :22 setSlimeSize sets width and
     height to 0.6 x size and health to size squared; :116 onCollideWithPlayer
     deals the size, above size 1. data/ carries no health for Slime because
     it depends on the size. -->

A slime moves only by jumping. It turns to face the nearest player within 16
blocks, and jumps every 10 to 29 ticks, or every 3 to 9 while a player is that
close.
<!-- src: EntitySlime.java:68 updatePlayerActionState; :75 slimeJumpDelay,
     divided by 3 with a player in range -->

It [[Damage#Mob attacks|damages]] only players, by touching one it can see.
<!-- src: EntitySlime.java:114 onCollideWithPlayer -->
<!-- check: the touch must bring the two positions within 0.6 x size of each
     other. A player's position is 1.62 above its feet (EntityPlayer.java:44)
     and a slime's is at its feet, so a size 2 slime (reach 1.2) may reach a
     player standing level with it only in mid-jump. Needs testing in game. -->

When a slime of size 2 or 4 dies, it splits into four slimes of half its size.
It splits only if the damage that kills it brings its health to exactly 0. More
damage than that kills it without a split.
<!-- src: EntitySlime.java:98 setEntityDead, the health == 0 test, run when the
     body is removed 20 ticks after death; EntityLiving.java:372 damageEntity
     lets health fall below 0. The server tree has the same test. -->

## Data values

- Entity network ID: {{id|Slime}}
