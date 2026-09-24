---
title: Monster Spawner
description: The caged block at the centre of every dungeon, which spawns one kind of mob while a player is within 16 blocks.
type: block
categories: [Blocks, Naturally generated]
aliases: [Spawner, Mob spawner]
---

**Monster Spawner** is a caged block that spawns one kind of mob while a player
is near.

## Obtaining

A monster spawner drops nothing, whatever breaks it.
<!-- src: BlockMobSpawner.java:14 idDropped and :18 quantityDropped return 0 -->

### Natural generation

Every [[Dungeon|dungeon]] has one monster spawner, at the centre of its floor.
It spawns [[Zombie|zombies]] half the time, and [[Skeleton|skeletons]] or
[[Spider|spiders]] a quarter of the time each.
<!-- src: WorldGenDungeons.java:98, :134 pickMobSpawner -->

## Behaviour

A spawner runs only while a player is within 16 blocks of it. It counts down a
delay, and at zero makes four attempts to spawn its mob. Each attempt:

- ends the round if six or more of that mob are within 8 blocks horizontally
  and 4 vertically;
- picks a point up to 4 blocks away in x and z and 1 block in y, most often
  near the spawner;
- places the mob there only if it passes the mob's own
  [[Mob Spawning|spawn conditions]], light included.

<!-- src: TileEntityMobSpawner.java:21 anyPlayerInRange, 16 blocks;
     :25 updateEntity; the 8, 4, 8 expansion and the >= 6 test at :57; x and z are
     (nextDouble() - nextDouble()) * 4, a triangular spread; getCanSpawnHere -->

A successful attempt sets the delay to 200 to 799 ticks, and so does a round
ended by six of the mob nearby. A round with no success leaves it at zero, and
the spawner tries again on the next tick.
<!-- src: TileEntityMobSpawner.java:89 updateDelay, 200 + nextInt(600), which
     :57-:58 also calls before ending a crowded round -->

Zombies, skeletons and spiders need light 7 or less to spawn, so a spawner whose
surroundings are lit to 8 or more spawns nothing.
<!-- src: EntityMob.java:69 getCanSpawnHere, light <= nextInt(8) -->

A spawner placed from the inventory spawns [[Pig|pigs]].
<!-- src: TileEntityMobSpawner.java:5 mobID defaults to "Pig" -->

## Data values

- Block ID: {{id|Monster Spawner}}
- Translation key: `tile.mobSpawner`
