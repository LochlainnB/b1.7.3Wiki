---
title: Mob Spawning
description: How mobs appear in Beta 1.7.3 — the spawn cycle, light and block conditions, biome lists, monster spawners and despawning.
type: mechanic
categories: [Game mechanics]
---

**Mob spawning** is the game placing mobs into the world at random near a
player. A [[Monster Spawner]] block spawns mobs by its own rules.

## The spawn cycle

The cycle runs once per tick. Every chunk within 8 chunks of a player is
eligible, a 17×17 square — 289 chunks for a single player, and fewer per player
where two squares overlap.
<!-- src: SpawnerAnimals.java:27 performSpawning -->

Mobs fall into three categories, each with its own population cap and its own
material to stand in:

| Category | Mobs | Cap per 256 chunks | Spawns in |
|---|---|---|---|
| Monster | [[Zombie]], [[Skeleton]], [[Spider]], [[Creeper]], [[Slime]], [[Ghast]], [[Pig Zombie]] | 70 | air |
| Creature | [[Sheep]], [[Pig]], [[Cow]], [[Chicken]], [[Wolf]] | 15 | air |
| Water creature | [[Squid]] | 5 | [[Water|water]] |

<!-- src: EnumCreatureType.java:4 -->

The cap scales with how much world is loaded, at `cap × eligible chunks ÷ 256`,
and is counted against every mob of that category in loaded chunks. One player
alone supports 79 monsters, 16 animals and 5 squid.
<!-- src: SpawnerAnimals.java:48; World.java:2064 countEntities walks
     loadedEntityList -->

That count is taken once per category per tick, before the pass over the
eligible chunks, and nothing rechecks it during the pass. A tick that starts
under the cap runs the whole pass, so a category can finish the tick well over
its cap. Spawning then stops until despawning brings the count back down.
<!-- src: SpawnerAnimals.java:48, the single countEntities call guarding the
     entire chunk loop -->

For each eligible chunk the game draws one mob from the biome's list for that
category, then picks a starting point: a random x and z inside the chunk, and a
y from 0 to 127 chosen with no regard for the terrain. The chunk is abandoned
unless that point is non-solid and made of the category's material, which is why
most attempts end in [[Stone|stone]].
<!-- src: SpawnerAnimals.java:12 getRandomSpawningPointInChunk, :92 -->

From that point the game runs three groups of four spawn attempts. Each attempt
moves up to 5 blocks in x and z from the previous one. The y never changes, so a
whole group lands on one level.
<!-- src: SpawnerAnimals.java:101; the y offset is nextInt(1) - nextInt(1),
     which is always zero -->

An attempt needs all of:

- a solid block below,
- a non-solid, non-liquid block at the spot,
- a non-solid block above,
- no player within 24 blocks,
- 24 blocks or more from the world spawn point,
- whatever the mob itself requires.

A water creature instead needs a liquid at the spot and a non-solid block above.
<!-- src: SpawnerAnimals.java:153 canCreatureTypeSpawnAtLocation, :115 -->

Every mob a chunk produces in one tick is the same type, which is what makes
packs. A chunk stops at 4 mobs, or 8 for wolves and 1 for ghasts. Each eligible
chunk gets its own group of attempts in the same tick, so one pass places far
more than one pack.
<!-- src: SpawnerAnimals.java:134; EntityLiving.java:842 getMaxSpawnedInChunk -->

A spawned spider carries a skeleton rider one time in a hundred. A spawned sheep
takes a random fleece colour.
<!-- src: SpawnerAnimals.java:161 creatureSpecificInit -->

## Hostile mobs

A hostile mob tests light twice, and both tests are random.

The stored sky light at the spot is compared against a random number from 0 to
31, and the spawn fails if the light is larger. An enclosed spot has a sky light
of 0 and always passes; a spot under open sky has 15 and fails just under half
the time. That value is stored per block and does not track the time of day, so
the test rejects surface spawns at midnight as often as at noon.

The current light level is then compared against a random number from 0 to 7,
and the spawn fails if the light is larger. Light 0 always passes, light 7 passes
one time in eight, and light 8 or brighter never passes.
<!-- src: EntityMob.java:69 getCanSpawnHere -->

During a thunderstorm the second test subtracts 10 from sky light whatever the
time of day, putting an open surface at light 5 and letting hostile mobs spawn
outdoors in daylight.

On Peaceful no monster spawns at all, and any [[Zombie|zombie]],
[[Skeleton|skeleton]], [[Spider|spider]], [[Creeper|creeper]], [[Giant|giant]],
[[Ghast|ghast]] or [[Pig Zombie|pig zombie]] already in the world is removed on
its next tick. [[Slime|Slimes]] are not removed.
<!-- src: Minecraft.java:1164 setAllowedMobSpawns; EntityMob.java:20 onUpdate;
     EntityGhast.java:30 onUpdate. EntitySlime extends EntityLiving, not
     EntityMob, so it has no such check. -->

Ghasts and pig zombies skip the light tests entirely and need only a difficulty
above Peaceful and a clear space. A ghast additionally succeeds one attempt in
twenty.
<!-- src: EntityGhast.java:151, EntityPigZombie.java:27 getCanSpawnHere -->

Slimes ignore light as well. A slime must be below y=16, in a chunk where a hash
of the world seed and the chunk coordinates comes out zero — about one chunk in
ten — and then succeeds one attempt in ten. A slime above the smallest size also
needs a difficulty above Peaceful. The clear-space test is skipped, so a slime
can appear partly inside blocks.
<!-- src: EntitySlime.java:134 getCanSpawnHere, via
     Chunk.getRandomWithSeed(987234911L) -->

## Passive mobs

An animal needs a [[Grass]] block directly beneath it and a light level above 8.
The level used is the higher of the block's stored sky light and its block light,
with no subtraction for the time of day. Torchlight therefore counts towards it.
A spot under open sky reads 15 at midnight, so animals spawn at night as readily
as by day.
<!-- src: EntityAnimal.java:20 getCanSpawnHere; World.java:529
     getFullBlockLightValue passes 0 as the sky subtraction to
     Chunk.java:341 getBlockLightValue, which returns max(sky, block) -->

[[Squid]] need [[Water|water]] and a clear space, with no light condition and no
depth limit. The chunk's starting point must be water, but the attempts that
follow accept any liquid.
<!-- src: EntityWaterMob.java:20 getCanSpawnHere -->

Animals spawn continuously on the same cycle as monsters. They are not placed
once when a chunk generates, so an area cleared of [[Cow|cows]] fills up again.

## What spawns where

Every [[Overworld]] biome shares one set of lists. The number is a weight within
its own list, not a chance:

| Category | Entries |
|---|---|
| Monster | [[Spider]] 10, [[Zombie]] 10, [[Skeleton]] 10, [[Creeper]] 10, [[Slime]] 10 |
| Creature | [[Sheep]] 12, [[Pig]] 10, [[Chicken]] 10, [[Cow]] 8 |
| Water creature | [[Squid]] 10 |

[[Forest]] and [[Taiga]] add [[Wolf]] at weight 2 to the creature list.
[[Hell]], the [[Nether]]'s only biome, replaces all three lists with [[Ghast]] 10
and [[Pig Zombie]] 10 as monsters. [[Sky]] carries Chicken 10 alone.
<!-- src: BiomeGenBase.java:42; BiomeGenForest.java:7; BiomeGenTaiga.java:7;
     BiomeGenHell.java:5; BiomeGenSky.java:5 -->

The draw only decides which mob is attempted. A slime is one monster pick in
five, and almost always fails its own conditions.

The [[Giant|giant]] appears on no list and never spawns naturally.

## Monster spawners

A [[Monster Spawner|monster spawner]] holds the name of one mob and runs only
while a player is within 16 blocks. Out of range it does nothing at all, down to
the smoke and flame particles.
<!-- src: TileEntityMobSpawner.java:67 anyPlayerInRange, :71 updateEntity -->

The spawner counts down a delay. At zero it makes four attempts, each of which:

- abandons the round if six or more of that mob are already within 8 blocks
  horizontally and 4 vertically;
- picks a point up to 4 blocks away in x and z and 1 block in y, biased towards
  the spawner;
- creates the mob there and applies the mob's own conditions, exactly as a
  natural spawn does.

A successful attempt sets the delay to 200 ticks plus a random 0 to 599 — 10 to
about 40 seconds. A round in which nothing spawns leaves the delay at zero, and
the spawner tries again on the next tick.
<!-- src: TileEntityMobSpawner.java:94, :135 updateDelay -->

Because the mob's own conditions still apply, lighting the room to level 8 stops
a [[Zombie|zombie]], [[Skeleton|skeleton]] or [[Spider|spider]] spawner outright.

Spawners generate only in [[Dungeon|dungeons]], one per dungeon, set to Zombie
half the time and to Skeleton or Spider a quarter each.
<!-- src: WorldGenDungeons.java:96, :131 pickMobSpawner -->

## Despawning

A mob more than 128 blocks from the nearest player is removed at once.
<!-- src: EntityLiving.java:667 despawnEntity -->

A mob older than 600 ticks has a 1 in 800 chance each tick of a second check:
beyond 32 blocks from the nearest player it is removed, and within them its age
resets to zero.

Both checks run only on ticks where the mob has no path to follow, plus one tick
in a hundred where it does.
<!-- src: EntityCreature.java:113, which reaches
     EntityLiving.updatePlayerActionState only on that branch -->

A hostile mob standing in light level 12 or brighter ages an extra 2 ticks per
tick, reaching the 600-tick threshold three times faster.
<!-- src: EntityMob.java:11 onLivingUpdate; brightness 0.5 is light 12 in
     WorldProvider.generateLightBrightnessTable -->

Animals despawn on the same rules. A tamed [[Wolf|wolf]] is the only mob that
never despawns.
<!-- src: EntityWolf.java:66 canDespawn -->

## Other ways mobs appear

A thrown [[Egg]] spawns a [[Chicken|chicken]] one time in eight, and four
chickens in one of every 32 of those.
<!-- src: EntityEgg.java:156 -->

A [[Pig|pig]] struck by lightning becomes a [[Pig Zombie|pig zombie]].
<!-- src: EntityPig.java:62 onStruckByLightning -->

When every player in the world is asleep and the difficulty is above Peaceful,
the game makes 20 attempts to spawn a [[Spider|spider]], [[Zombie|zombie]] or
[[Skeleton|skeleton]] within 32 blocks horizontally and 16 vertically of a
sleeper. The mob must be able to path to within 1.5 blocks of the player. If it
can, it is placed in a free space beside the [[Bed]], the player is woken, and
the night does not pass.
<!-- src: SpawnerAnimals.java:173 performSleepSpawning; World.java:1748 tick -->
