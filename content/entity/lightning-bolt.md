---
title: Lightning Bolt
description: The entity a lightning strike makes, which flashes two to four times, starting fires and striking every entity near where it lands.
type: entity
categories: [Entities]
---

A **lightning bolt** is the entity a [[Weather#Lightning|lightning strike]] makes
where it lands.

## Spawning

Lightning strikes only during a thunderstorm. [[Weather#Lightning|Weather]]
gives how often, and which space it lands in. Nothing else makes a lightning
bolt.
<!-- src: World.java:1927 is the only place a bolt is made, besides a client
     copying one a server sent (NetClientHandler.java:143) -->

## Behaviour

### Flashes

A bolt flashes two to four times: once when it lands, then one to three more
times. Each flash lasts 2 ticks, and the next begins at most 9 ticks after the
last ends. The bolt is gone once its last flash ends.
<!-- src: EntityLightningBolt.java:13 lightningState 2, :15 boltLivingTime 1 to
     3 more flashes; :43 counts the state down a tick at a time, and once it is
     below 0, :47 starts the next flash with a chance of (ticks dark) in 10,
     certain by the tenth; :62 a flash is the two ticks the state is 1 and 0;
     :45 removes the bolt when no flash is left -->

The first tick sounds thunder and an explosion. The sky lights up on every tick
of a flash. A bolt breaks no blocks.
<!-- src: EntityLightningBolt.java:39-:40 ambient.weather.thunder and
     random.explode; :71 sets the sky flash that World.java:1058 draws; nothing
     in the class removes a block -->

In singleplayer the thunder is heard at any distance. On a server, only players
within 512 blocks of the bolt see or hear it.
<!-- src: EntityLightningBolt.java:39 volume 10000, which RenderGlobal.java:1263
     hears within 16 blocks per unit of volume; minecraft_server
     WorldServer.java:79 sends the bolt to players within 512 blocks, and a
     client makes its own copy from that packet -->

### Fire

On Normal and Hard, the first flash sets fire to the struck space, and makes
four tries at spaces up to 1 block from it in each direction. Every later flash
sets fire to the struck space, on any difficulty. Fire is placed only in an
empty space where [[Fire#Where fire can stand|fire can stand]].
<!-- src: EntityLightningBolt.java:16 difficultySetting >= 2 guards the first
     flash alone; :24-:31 the four tries in the 3 x 3 x 3 around; :51-:57 the
     later flashes test no difficulty. Every placement needs getBlockId == 0
     and BlockFire.canPlaceBlockAt -->

### Entities

A flash strikes every entity that touches a box 6 blocks square and 12 tall. The
box is centred on the corner of the struck space at its lowest x and z, and runs
from 3 blocks below the struck space to 9 above. It strikes on both ticks of the
flash.
<!-- src: EntityLightningBolt.java:62-:69; the bolt stands on the block
     coordinates World.java:1927 passes, with no half-block offset -->

| Entity | A strike |
|---|---|
| [[Player]] | deals 5 [[Damage#Environmental damage\|damage]] |
| Any other mob | deals 5 damage, and sets it alight for 300 ticks |
| [[Ghast]], [[Pig Zombie\|pig zombie]] | sets it alight, and deals no damage |
| [[Pig]] | turns it into a pig zombie |
| [[Creeper]] | deals 5 damage, sets it alight, and charges it |
| [[Dropped Item\|Dropped item]] | destroys it |
| [[Boat]], [[Minecart\|minecart]] | breaks it |
| [[Painting]] | breaks it, and it drops |
| Arrow, snowball, egg, lit TNT, falling sand, fireball | nothing |

<!-- src: Entity.java:1085 onStruckByLightning: dealFireDamage(5), then fire
     counted up by 1 and set to 300 if that reaches 0. It reaches 0 from the
     -1 a mob rests at (Entity.java:531 with fireResistance 1), but not from a
     player's -20 (EntityPlayer.java:50). Entity.java:562 dealFireDamage
     spares EntityGhast.java:17 and EntityPigZombie.java:15 isImmuneToFire;
     EntityPig.java:62; EntityCreeper.java:141; EntityItem.java:87 against its 5
     health; EntityBoat.java:67 and EntityMinecart.java:78 add 50 to a counter
     that breaks them above 40; EntityPainting.java:204. The rest keep
     Entity.java:746 attackEntityFrom, which does nothing, and
     EntityFireball.java:216 refuses a null attacker -->

[[Weather#Rain|Rain]] puts out a struck entity standing in the open at once; see
[[Damage#Catching fire]].
<!-- src: Entity.java:534, isWet includes being rained on -->

A mob or player struck on both ticks of a flash takes the damage once; see
[[Damage#The invulnerability window]]. A dropped item has no such protection.
Items dropped by whatever a flash breaks or kills are struck on its second tick,
and destroyed if they are still in range.
<!-- src: EntityLiving.java:317 ignores the second 5 inside the window;
     EntityItem.java:87 has no window. World.java:1181 updates the bolt before
     the tick's other entities, and the drops join the world at once
     (World.java:896 entityJoinedWorld) -->

## Data values

A lightning bolt has no entity network ID, and is not saved with the world.
<!-- src: EntityList.java:83-:106 registers no EntityLightningBolt;
     World.java:891 addWeatherEffect keeps it in a list of its own, outside the
     chunks that are saved. A server sends it to clients as Packet71Weather
     (minecraft_server WorldServer.java:79) -->
