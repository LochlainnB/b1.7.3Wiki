---
title: Monster
description: A hostile mob with a player's appearance, which nothing in the game spawns.
type: entity
categories: [Mobs, Hostile mobs]
---

A **monster** is a hostile mob with a player's appearance, which nothing in the
game spawns.

## Spawning

A monster never spawns. No biome's [[Mob Spawning#What spawns where|spawn list]]
includes it, and no [[Monster Spawner|monster spawner]] generates with it. It
exists only in a world edited to hold one.
<!-- src: BiomeGenBase.java:42-:46, BiomeGenHell.java:8, BiomeGenSky.java:5
     leave it out; WorldGenDungeons.java:134 pickMobSpawner; EntityList.java:88
     registers EntityMob itself as "Monster" -->

On Peaceful a monster is removed from the world.
<!-- src: EntityMob.java:20 onUpdate -->

## Drops

A monster drops nothing.
<!-- src: EntityMob does not override getDropItemId, which returns 0
     (EntityLiving.java:436) -->

Killing one earns the *Monster Hunter* [[Achievements|achievement]].
<!-- src: EntityPlayer.java:797 onKillEntity, for any EntityMob -->

## Behaviour

A monster is 0.6 blocks wide and 1.8 tall, and wears the player's default skin.
<!-- src: Entity.java:86-:87, the default size, which EntityMob keeps;
     EntityLiving.java:16 texture /mob/char.png; RenderManager.java:41 draws
     every EntityLiving without a renderer of its own with the player-shaped
     ModelBiped -->

It targets the nearest player within 16 blocks, if it can see them, and walks
towards them. It also attacks any mob or player that hurts it.
<!-- src: EntityMob.java:28 findPlayerToAttack, :33 attackEntityFrom sets the
     attacker as the target; EntityCreature.java:16 updatePlayerActionState -->

It walks at 3.0 blocks per second, 70% of a [[Player#Movement|player's]]
walking speed.
<!-- src: EntityLiving.java:56 moveSpeed 0.7, which EntityMob keeps; see Zombie
     for how moveSpeed becomes blocks per second -->

It hits for [[Damage#Mob attacks|2 damage]].
<!-- src: EntityMob.java:4 attackStrength 2, :49 attackEntity -->

Unlike a [[Zombie|zombie]], it does not burn in daylight. With no target it
wanders, choosing darker spaces.
<!-- src: only EntityZombie.java:11 and EntitySkeleton.java:24 add the
     daylight burning; EntityCreature.java:118 updateWanderPath takes the best
     of ten random spots by EntityMob.java:57 getBlockPathWeight,
     0.5 - brightness -->

## Data values

- Entity network ID: {{id|Monster}}
