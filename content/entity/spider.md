---
title: Spider
description: A hostile mob that climbs walls, leaps at players in the dark and leaves them alone in bright light.
type: entity
categories: [Mobs, Hostile mobs]
---

A **spider** is a hostile mob that climbs walls and attacks players in the dark.

## Spawning

Spiders spawn [[Mob Spawning#Hostile mobs|in the dark]] in every [[Overworld]]
biome, in packs of up to 4.
<!-- src: BiomeGenBase.java:42 spawnableMonsterList; EntityLiving.java:842
     getMaxSpawnedInChunk -->

A spider is 1.4 blocks wide. It spawns only where the eight spaces around its
spawn point, at the same level, hold no liquid and nothing it would collide
with.
<!-- src: EntitySpider.java:7 setSize(1.4F, 0.9F); the spawn point is the
     middle of a block (SpawnerAnimals.java:112), so the spider reaches 0.2
     into each neighbouring column, and 0.9 up; EntityLiving.java:781
     getCanSpawnHere wants no colliding box and no liquid inside it -->

A quarter of the [[Monster Spawner|monster spawners]] in [[Dungeon|dungeons]]
spawn spiders. A spider is one of the three mobs that can
[[Mob Spawning#Other ways mobs appear|spawn beside a sleeping player]].
<!-- src: WorldGenDungeons.java:134 pickMobSpawner; SpawnerAnimals.java:10
     nightSpawnEntities -->

One spider in a hundred spawns with a [[Skeleton|skeleton]] riding it, except
from a monster spawner.
<!-- src: SpawnerAnimals.java:161 creatureSpecificInit, called by natural and
     sleep spawning; TileEntityMobSpawner.java:25 updateEntity never calls it -->

On Peaceful no spider spawns, and any in the world is removed.
<!-- src: Minecraft.java:1164 setAllowedMobSpawns; EntityMob.java:20 onUpdate -->

## Drops

A spider drops 0–2 [[String|string]] when it dies.
<!-- src: EntitySpider.java:70 getDropItemId; EntityLiving.java:424
     dropFewItems, nextInt(3) of the item -->

Killing one earns the *Monster Hunter* [[Achievements|achievement]].
<!-- src: EntityPlayer.java:797 onKillEntity, for any EntityMob -->

## Behaviour

In [[Light#What light affects|light 11 or less]], a spider targets the nearest
player within 16 blocks, even one it cannot see. It also attacks any mob or
player that hurts it, in any light.
<!-- src: EntitySpider.java:19 findPlayerToAttack has no line-of-sight test;
     EntityMob.java:33 attackEntityFrom sets the attacker as the target -->

In light 12 or more it seeks no player. In that light, a spider already chasing
a target it can see loses it 1 tick in 100.
<!-- src: EntitySpider.java:41 attackEntity, which EntityCreature.java:28 calls
     only while the target is in sight; :42 drops the target only when
     brightness is above 0.5, which is light 12 or more -->

It walks at 3.5 blocks per second, 80% of a player's walking speed.
<!-- src: EntitySpider.java:8 moveSpeed 0.8; see Zombie for how moveSpeed
     becomes blocks per second -->

Between 2 and 6 blocks from its target, it leaps at it 1 tick in 10. Closer
in, it hits for [[Damage#Mob attacks|2 damage]].
<!-- src: EntitySpider.java:46, the leap needing onGround; otherwise
     EntityMob.java:49 attackEntity -->

It climbs any wall it walks into, as though on a [[Ladder|ladder]].
<!-- src: EntitySpider.java:74 isOnLadder returns isCollidedHorizontally;
     EntityLiving.java:528 -->

It makes no footstep sounds, and does not trample [[Farmland|farmland]] or light
[[Redstone Ore|redstone ore]] by walking on it.
<!-- src: EntitySpider.java:15 canTriggerWalking false skips the step sound and
     onEntityWalking at Entity.java:478; BlockFarmland.java:50,
     BlockRedstoneOre.java:26 -->

With no target it wanders, choosing darker spaces.
<!-- src: EntityCreature.java:118 updateWanderPath takes the best of ten
     random spots by EntityMob.java:57 getBlockPathWeight, 0.5 - brightness -->

## Data values

- Entity network ID: {{id|Spider}}
