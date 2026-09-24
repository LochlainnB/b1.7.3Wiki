---
title: Fireball
description: The projectile a ghast shoots, which speeds up in a straight line, explodes on impact, and can be sent back by hitting it.
type: entity
aliases: [Ghast Fireball]
categories: [Entities]
---

A **fireball** is the exploding projectile a [[Ghast|ghast]] shoots.

## Spawning

Only a [[Ghast#Behaviour|ghast]] makes a fireball, and fires it at the player
it targets. The fireball appears 4 blocks out from the ghast towards the player,
half a block above the ghast's centre.
<!-- src: EntityGhast.java:85-:91, the look vector scaled by 4 on x and z, and
     posY + height / 2 + 0.5; no other class constructs an EntityFireball -->

It flies in the direction from the ghast's centre to the middle of the player's
body, with a random error of about 0.4 blocks on each axis.
<!-- src: EntityGhast.java:73-:75 the aim, centre to centre;
     EntityFireball.java:52-:54 adds nextGaussian() * 0.4 to each axis of it
     before :55-:58 normalise it -->

## Behaviour

### Flight

A fireball flies in a straight line, and does not fall. It starts at rest and
speeds up each tick towards 1.9 blocks per tick, or 0.4 in water.
<!-- src: EntityFireball.java:51 motion 0; :166-:171 add a tenth of a block per
     tick along the aim, then keep 0.95 of the speed, or 0.8 in water
     (:157-:164): a top speed of 0.95 * 0.1 / 0.05 = 1.9, or 0.8 * 0.1 / 0.2 =
     0.4. Nothing applies gravity -->

It flies through water, lava and fire, and explodes on the first other block it
meets, [[Torch|torches]] and [[Tall Grass|tall grass]] included. It flies through
[[Dropped Item|dropped items]], [[Arrow|arrows]], [[Snowball|snowballs]],
[[Egg|eggs]] and [[Fishing Rod|fishing bobbers]], and explodes on the first other
entity.
<!-- src: EntityFireball.java:91 rayTraceBlocks passes false to World.java:712
     rayTraceBlocks_do_do, which then needs no collision box but skips
     BlockFluid.java:56 canCollideCheck and BlockFire.java:168 isCollidable;
     :104 canBeCollidedWith, true only for living entities, boats, minecarts,
     paintings, primed TNT, falling sand and fireballs -->

### Hitting

A hit sets off an [[Explosion#Sizes|explosion]] of size 1 that starts fires. The
blast is centred where the fireball was at the start of that tick, up to 1.9
blocks short of what it hit.
<!-- src: EntityFireball.java:127 newExplosion(null, posX, posY, posZ, 1.0F,
     true), before :133 moves it on; the hit was found along the tick's motion
     (:89-:120) -->

The entity it hits takes no damage from the impact itself. A mob it hits is
knocked back away from the [[Ghast|ghast]]. A player is not knocked back.
<!-- src: EntityFireball.java:124 attackEntityFrom(shootingEntity, 0);
     EntityLiving.java:337 knocks back from the attacker's position;
     EntityPlayer.java:380 returns before that when the damage is 0 -->

A fireball can hit the ghast that fired it once 25 ticks have passed since it
was fired, including after it has been sent back.
<!-- src: EntityFireball.java:104 ticksInAir >= 25, counted from launch and never
     reset; :202 attackEntityFrom leaves shootingEntity alone -->

### Sending it back

A fireball is 1 block across, and a player's crosshair picks it out up to 1
block beyond that.
<!-- src: EntityFireball.java:21 setSize(1.0F, 1.0F), :198
     getCollisionBorderSize 1.0, which EntityRenderer.java:111 adds to the box
     the crosshair tests -->

Any attack by a player or mob sends a fireball off in the direction the attacker
is looking, at 1 block per tick, speeding up again as before. A player can do
this with a melee hit, an [[Arrow|arrow]], a [[Snowball|snowball]], an
[[Egg|egg]] or a [[Fishing Rod|fishing bobber]].
<!-- src: EntityFireball.java:202 attackEntityFrom takes the attacker's
     getLookVec, which only EntityLiving.java:809 provides; motion becomes that
     unit vector and acceleration a tenth of it. Each projectile names its
     shooter as the attacker: EntityArrow.java:163, EntitySnowball.java:153,
     EntityEgg.java:153, EntityFish.java:225 -->

An arrow, snowball or egg fired by a [[Dispenser|dispenser]] has no shooter, and
does not turn a fireball.
<!-- src: BlockDispenser.java:107, :113 and :118 use the constructors that leave
     the shooter null; EntityFireball.java:216 returns false for a null
     attacker -->

### Lifetime

A fireball that hits nothing has no time limit. It flies until it reaches the
edge of the [[Game Tick#Entities|loaded area]], where it stops, and disappears
when its chunk unloads.
<!-- src: EntityFireball.java:72 removes it after 1200 ticks only when inGround,
     which nothing sets; World.java:1294 skips an entity near an unloaded chunk;
     Chunk.java:478 onChunkUnload removes the chunk's entities -->

## Data values

A fireball has no entity network ID, and is not saved with the world.
<!-- src: EntityList.java:83-:106 registers no EntityFireball, and Entity.java:780
     addEntityID saves only entities it names. A server spawns it on clients
     as object type 63 of Packet23VehicleSpawn (minecraft_server
     EntityTrackerEntry.java:245) -->
