---
title: Ghast
description: A large floating hostile mob of the Nether that shoots exploding fireballs at players from up to 64 blocks away.
type: entity
categories: [Mobs, Hostile mobs]
---

A **ghast** is a large floating hostile mob of the [[Nether]] that shoots
fireballs at players.

## Spawning

Ghasts spawn only in the [[Nether]], at any light level. A
[[Mob Spawning#Hostile mobs|spawn attempt]] succeeds one time in twenty, and a
chunk spawns one ghast at a time.
<!-- src: BiomeGenHell.java:8; EntityGhast.java:151 getCanSpawnHere, :155
     getMaxSpawnedInChunk -->

A ghast is 4 blocks wide and 4 tall. It spawns only where the 5 × 5 blocks
around its spawn point, for 4 blocks up, hold no liquid and nothing it would
collide with.
<!-- src: EntityGhast.java:16 setSize(4.0F, 4.0F); centred on the middle of a
     block (SpawnerAnimals.java:112), it reaches 1.5 into the second column on
     each side; EntityLiving.java:781 getCanSpawnHere. World.java:1370
     getIsAnyLiquid also reads the layer just above the box. -->

On Peaceful no ghast spawns, and any in the world is removed.
<!-- src: Minecraft.java:1164 setAllowedMobSpawns; EntityGhast.java:32 -->

A ghast [[Mob Spawning#Despawning|despawns]] only when it is more than 128
blocks from every player. The chance of despawning beyond 32 blocks never
applies to it.
<!-- src: EntityGhast.java:31 updatePlayerActionState calls despawnEntity every
     tick but never counts entityAge up, which only EntityLiving.java:690 and
     EntityMob.java:14 do, so the age test at EntityLiving.java:678 never
     passes -->

## Drops

A ghast drops 0–2 [[Gunpowder|gunpowder]] when it dies.
<!-- src: EntityGhast.java:143 getDropItemId; EntityLiving.java:424
     dropFewItems, nextInt(3) of the item -->

## Behaviour

A ghast flies. It drifts towards a random point up to 16 blocks away on each
axis, and picks a new point when it arrives or when a block lies on the straight
line to it.
<!-- src: EntityGhast.java:38-:59; :115 isCourseTraversable -->

It targets the nearest player within 100 blocks, and looks again every 21 ticks.
<!-- src: EntityGhast.java:65, aggroCooldown set to 20 and tested before each
     decrement -->

While that player is within 64 blocks and in sight, it shoots a fireball every
60 ticks, the first 20 ticks after it sees them. A charging sound plays, and its
face changes, 9 ticks before each shot.
<!-- src: EntityGhast.java:72-:103, attackCounter climbing by 1 a tick to 20
     and reset to -40; the sound plays at 10, before that tick's increment;
     :105 the face shows while the counter is above 10 -->

[[Damage#Catching fire|Fire, lava and lightning]] do it no damage.
<!-- src: EntityGhast.java:17 isImmuneToFire -->

Its sounds carry 160 blocks, ten times as far as other mobs'.
<!-- src: EntityGhast.java:147 getSoundVolume 10; RenderGlobal.java:1263
     playSound reaches 16 blocks times any volume above 1 -->

### Fireballs

A fireball flies in a straight line towards the player, with some random
spread, and speeds up as it goes. It explodes when it hits a block or an entity,
in an [[Explosion#Sizes|explosion]] of size 1 that starts fires. The entity it
hits takes no damage from the impact itself.
<!-- src: EntityFireball.java:44, a gaussian spread added to the aim; :166
     accelerationX..Z; :122-:131 the hit and the blast -->

A player who hits a fireball, in melee or with an [[Arrow|arrow]], sends it off
in the direction they are looking. A fireball can hit the ghast that fired it
once it has flown for 25 ticks.
<!-- src: EntityFireball.java:202 attackEntityFrom takes the attacker's look
     vector, and an arrow names its shooter as the attacker
     (EntityArrow.java:163); :104 ticksInAir >= 25 -->

## Data values

- Entity network ID: {{id|Ghast}}
