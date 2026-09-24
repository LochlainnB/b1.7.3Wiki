---
title: Wolf
description: A mob of forests and taigas that attacks sheep, turns on whoever hurts it, and can be tamed with bones.
type: entity
categories: [Mobs, Passive mobs]
---

A **wolf** is a mob that can be tamed with [[Bone|bones]] to follow and defend
a player.

## Spawning

Wolves spawn [[Mob Spawning#Passive mobs|on grass in light above 8]] in
[[Forest]] and [[Taiga]] biomes only, in packs of up to 8.
<!-- src: BiomeGenForest.java:7, BiomeGenTaiga.java:7; EntityAnimal.java:20
     getCanSpawnHere; EntityWolf.java:418 getMaxSpawnedInChunk -->

A tamed wolf never [[Mob Spawning#Despawning|despawns]].
<!-- src: EntityWolf.java:66 canDespawn -->

## Drops

A wolf drops nothing.
<!-- src: EntityWolf.java:92 getDropItemId returns -1 -->

## Behaviour

A wolf walks at 4.4 blocks per second, 102% of a player's walking speed.
<!-- src: EntityWolf.java:19 moveSpeed 1.1. After the 0.98 at
     EntityLiving.java:640 that input is still above 1, and Entity.java:614
     moveFlying scales any input above 1 down to 1, so it accelerates by 0.1 a
     tick against a walking player's 0.098; see Zombie for the rest -->

Between 2 and 6 blocks from its target, it leaps at it 1 tick in 10. Within 1.5
blocks it bites, for [[Damage#Mob attacks|2 damage]], or 4 when tamed. It can
bite a player on level ground only while airborne, as in a leap. Bites land at
most every 10 ticks, as often as the target's
[[Damage#The invulnerability window|invulnerability window]] allows.
<!-- src: EntityWolf.java:304 attackEntity, given the distance between
     positions (EntityCreature.java:27, Entity.java:678). A player's position
     is 1.62 above its feet (EntityPlayer.java:44) and a wolf's is at its feet,
     so on level ground the two are never within 1.5. The leap at :305 needs
     onGround; the bite at :314 tests no attackTime, unlike EntityMob.java:50,
     so only the target's window (EntityLiving.java:317) spaces the bites -->

Its bite is not scaled by [[Damage#Difficulty|difficulty]], and it bites on
Peaceful too.
<!-- src: EntityPlayer.java:366 scales only EntityMob and EntityArrow
     attackers; EntityWolf extends EntityAnimal, and nothing in it tests the
     difficulty -->

It takes half damage, rounded up, from a mob, a skeleton's arrow and a
creeper's blast included.
<!-- src: EntityWolf.java:256 (damage + 1) / 2 from any attacker but a player;
     EntityArrow.java:163 names the shooter as the attacker, Explosion.java:100
     the creeper -->

It makes no footstep sounds, and does not trample [[Farmland|farmland]] or
light [[Redstone Ore|redstone ore]] by walking on it.
<!-- src: EntityWolf.java:30 canTriggerWalking false skips the step sound and
     onEntityWalking at Entity.java:478; BlockFarmland.java:50,
     BlockRedstoneOre.java:26 -->

With no target it wanders, choosing [[Grass|grass]] and then brighter spaces.
<!-- src: EntityCreature.java:118 updateWanderPath takes the best of ten
     random spots by EntityAnimal.java:8 getBlockPathWeight, 10 above grass
     and brightness - 0.5 elsewhere -->

### Wild wolves

A wild wolf attacks no player until one hurts it. That wolf then becomes angry
and attacks the player, and so does every wild wolf within 16 blocks
horizontally and 4 vertically that has no target.
<!-- src: EntityWolf.java:254 attackEntityFrom; :263 the wolf hurt, :274 the
     others, in a box reaching 16 out and 4 up and down from the wolf's block -->

An angry wolf stays angry, and cannot be tamed. Once its target is dead, it
targets the nearest player within 16 blocks, even one it cannot see. Its anger
is saved with the world.
<!-- src: nothing calls setWolfAngry(false); EntityWolf.java:300
     findPlayerToAttack has no sight test; :44 writes "Angry"; :329 taming
     needs a wolf that is not angry -->

A mob that hurts a wild wolf is attacked by the same wolves, and none of them
becomes angry.
<!-- src: EntityWolf.java:273, which sets anger only for a player -->

1 tick in 100, a wild wolf with no target attacks a random [[Sheep|sheep]]
within the same range.
<!-- src: EntityWolf.java:108 updatePlayerActionState -->

### Taming

Using a [[Bone|bone]] on a wild wolf that is not angry uses up the bone, and
tames the wolf one time in three. Hearts appear when it is tamed, and smoke
when it is not.
<!-- src: EntityWolf.java:326 interact; :342 and :345 showHeartsOrSmokeFX -->

The player who tames it is its owner. Taming sets its health to 20 and makes it
sit.
<!-- src: EntityWolf.java:337-:341 -->

### Tamed wolves

A tamed wolf that is not sitting follows its owner once more than 5 blocks
away. If it finds no path and is more than 12 blocks away, it teleports to 2
blocks from its owner.
<!-- src: EntityWolf.java:98 updatePlayerActionState; :229
     getPathOrWalkableBlock searches 16 blocks for a path, then tries the ring
     of a 5 x 5 square around the owner for a solid block with two non-solid
     spaces above -->

Its owner makes it sit or stand by using it. Being hurt or entering water makes
it stand. A tamed wolf whose owner is not in its world sits.
<!-- src: EntityWolf.java:366 interact; :250 isMovementCeased; :255 and :115
     stand it up; :105 sits it when getPlayerEntityByName finds no owner -->

It attacks whatever hurts it, except its owner.
<!-- src: EntityWolf.java:288 -->

When its owner is hurt by a mob, every tamed wolf of that owner within 16
blocks horizontally and 4 vertically that has no target attacks the mob,
standing up if it was sitting. When the owner hits a mob that survives, those
wolves that are not sitting attack it too. Neither applies to a creeper, a
ghast, the owner's own wolves, or another player unless the server has PvP on.
<!-- src: EntityPlayer.java:389 and :507 call :402 alertWolves; :403 skips
     creepers and ghasts, :406 the owner's wolves, :411 players unless
     isPVPEnabled, which EntityPlayerMP.java:110 (server tree) reads from the
     server's pvp setting; :430 skips sitting wolves only on the owner's own
     attack -->

A tamed wolf below full health eats a raw or cooked
[[Raw Porkchop|porkchop]] from a player's hand, and
[[Food#Wolves|restores 3 health]] from either.
<!-- src: EntityWolf.java:353-:361 -->

Its tail sits lower the less health it has.
<!-- src: EntityWolf.java:410 setTailRotation, (0.55 - (20 - health) x 0.02)
     x pi for a tamed wolf, drawn at ModelWolf.java:136 -->

## Data values

- Entity network ID: {{id|Wolf}}
