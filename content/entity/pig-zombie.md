---
title: Pig Zombie
description: A mob of the Nether that leaves players alone until one of them hurts a pig zombie, and then attacks with every pig zombie nearby.
type: entity
subject: PigZombie
aliases: [PigZombie]
categories: [Mobs, Hostile mobs]
---

A **pig zombie** is a mob of the [[Nether]] that leaves players alone until one
of them hurts a pig zombie.

## Spawning

Pig zombies spawn only in the [[Nether]], at any
[[Mob Spawning#Hostile mobs|light level]], in packs of up to 4.
<!-- src: BiomeGenHell.java:9; EntityPigZombie.java:27 getCanSpawnHere;
     EntityLiving.java:842 getMaxSpawnedInChunk -->

A [[Pig|pig]] struck by [[Weather#Lightning|lightning]] becomes a pig zombie.
<!-- src: EntityPig.java:62 onStruckByLightning -->

On Peaceful no pig zombie spawns, and any in the world is removed.
<!-- src: Minecraft.java:1164 setAllowedMobSpawns; EntityMob.java:20 onUpdate -->

## Drops

A pig zombie drops 0–2 [[Cooked Porkchop|cooked porkchops]] when it dies.
<!-- src: EntityPigZombie.java:85 getDropItemId; EntityLiving.java:424
     dropFewItems, nextInt(3) of the item -->

Killing one earns the *Monster Hunter* [[Achievements|achievement]].
<!-- src: EntityPlayer.java:797 onKillEntity, for any EntityMob -->

## Behaviour

A pig zombie attacks no player until a player hurts a pig zombie. The one hurt,
and every pig zombie within 32 blocks of it on each axis, then attack that
player.
<!-- src: EntityPigZombie.java:41 findPlayerToAttack, :49 attackEntityFrom,
     the 32-block box at :51, :67 becomeAngryAt -->

An angered pig zombie stays angry. Once its target is dead, it targets the
nearest player within 16 blocks that it can see. Its anger is saved with the
world.
<!-- src: nothing lowers angerLevel once becomeAngryAt (EntityPigZombie.java:67)
     sets it, in either source tree, so :41 keeps handing on to
     EntityMob.java:28; :33 writes it as "Anger" -->

It also attacks any mob that hurts it.
<!-- src: EntityMob.java:33 attackEntityFrom sets any attacker as the target -->

It walks at 2.2 blocks per second, 50% of a player's walking speed. While it has
a target it walks at 4.1 blocks per second, 95% of a player's walking speed.
<!-- src: EntityPigZombie.java:19 moveSpeed 0.95 with a target, 0.5 without;
     see Zombie for how moveSpeed becomes blocks per second -->

It hits for [[Damage#Mob attacks|5 damage]].

[[Damage#Catching fire|Fire, lava and lightning]] do it no damage. In the
[[Overworld]] it catches fire by day as a [[Zombie|zombie]] does, and takes no
harm from it.
<!-- src: EntityPigZombie.java:15 isImmuneToFire; it extends EntityZombie and
     so runs EntityZombie.java:11 onLivingUpdate -->

With no target it wanders, choosing darker spaces.
<!-- src: EntityCreature.java:118 updateWanderPath takes the best of ten
     random spots by EntityMob.java:57 getBlockPathWeight, 0.5 - brightness -->

## Data values

- Entity network ID: {{id|PigZombie}}
