---
title: Giant
description: A hostile mob built as a zombie six times normal size, which nothing in the game spawns.
type: entity
categories: [Mobs, Hostile mobs]
---

A **giant** is a hostile mob, a [[Zombie|zombie]] six times normal size, that
nothing in the game spawns.

## Spawning

A giant never spawns. No biome's [[Mob Spawning#What spawns where|spawn list]]
includes it, and no [[Monster Spawner|monster spawner]] generates with it. It
exists only in a world edited to hold one.
<!-- src: BiomeGenBase.java:42-:46, BiomeGenHell.java:8, BiomeGenSky.java:5
     leave it out; WorldGenDungeons.java:134 pickMobSpawner; EntityList.java:92
     registers it as "Giant" -->

On Peaceful a giant is removed from the world.
<!-- src: EntityMob.java:20 onUpdate -->

## Drops

A giant drops nothing.
<!-- src: EntityGiantZombie extends EntityMob and does not override
     getDropItemId, which returns 0 (EntityLiving.java:436) -->

## Behaviour

A giant is 3.6 blocks wide and 10.8 tall, and wears the zombie's skin.
<!-- src: EntityGiantZombie.java:6 texture, :11 setSize six times the default
     0.6 by 1.8 -->

It targets the nearest player within 16 blocks, if it can see them, and walks
towards them. It also attacks any mob or player that hurts it.
<!-- src: EntityMob.java:28 findPlayerToAttack, :33 attackEntityFrom sets the
     attacker as the target; EntityCreature.java:16 updatePlayerActionState -->

It walks at 2.2 blocks per second, 50% of a player's walking speed.
<!-- src: EntityGiantZombie.java:7 moveSpeed 0.5; see Zombie for how moveSpeed
     becomes blocks per second -->

It hits for [[Damage#Mob attacks|50 damage]], but only within 2 blocks of its
centre. That is inside its own body, so a player has to walk into it to be hit.
<!-- src: EntityMob.java:50 attackEntity needs getDistanceToEntity below 2,
     measured between positions. The giant's is at its feet, in the middle of a
     body 1.8 wide on each side; a player's is 1.62 above its feet
     (EntityPlayer.java:44), so on level ground the two must be within 1.17
     horizontally -->

Unlike a zombie, it does not burn in daylight. With no target it wanders,
choosing brighter spaces.
<!-- src: EntityGiantZombie extends EntityMob, not EntityZombie, so has no
     EntityZombie.java:11 onLivingUpdate; EntityGiantZombie.java:14
     getBlockPathWeight is brightness - 0.5, the reverse of EntityMob.java:57 -->

## Data values

- Entity network ID: {{id|Giant}}
