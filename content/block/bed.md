---
title: Bed
description: A two-block bed that a player sleeps in to skip the night, and that sets the player's spawn point.
type: block
categories: [Blocks, Utility blocks]
---

**Bed** is a two-block piece of furniture that a player sleeps in to skip the
night.

## Obtaining

### Crafting

{{crafting|Bed}}

Any colour of [[Wool|wool]] can be used.
<!-- src: CraftingManager.java:80; :115 wraps a block ingredient with damage
     -1, which ShapedRecipes.java:62 matches against any damage -->

### Breaking

Breaking either half removes the whole bed and drops one bed.
<!-- src: BlockBed.java:121 onNeighborBlockChange removes a half whose partner
     is gone; :137 idDropped and :194 give the item for one half only -->

## Usage

### Placing

A bed is placed on top of a block, and fills the space above it and the next
space in the direction the player faces. Both spaces must be empty, each above
a full, opaque block.
<!-- src: ItemBed.java:9 top face only; :33 isAirBlock and isBlockNormalCube
     for both spaces -->

### Sleeping

Using either half of a bed puts the player to sleep in it. This works only:

- at night, or during a [[Weather#Thunderstorms|thunderstorm]];
- within 3 blocks of the bed horizontally and 2 vertically;
- when no other player is asleep in it.

<!-- src: BlockBed.java:14 blockActivated, :48 the occupied test;
     EntityPlayer.java:537 sleepInBedAt, :545 isDaytime, :549 the distance,
     measured from the player's position to the corner of the half further
     from where the player stood when placing it -->

Once every player in the world has been asleep for 100 ticks (5 seconds), the
[[Game Tick#The world clock|clock]] moves on to the next morning and every
player wakes. Sleeping through a daytime thunderstorm skips the rest of that day
as well. Sleeping through ends rain and thunder; see [[Weather#The cycle]].
<!-- src: EntityPlayer.java:691 isPlayerFullyAsleep, sleepTimer >= 100;
     World.java:1748-:1757 sets the time to the next multiple of 24000 and calls
     wakeUpAllPlayers -->

On any difficulty but Peaceful, a monster may appear beside the bed and wake
the player instead; see [[Mob Spawning#Other ways mobs appear]].

A sleeping player also wakes when hurt, or when the bed is broken. In
multiplayer only, a button on the sleeping screen gets the player up.
<!-- src: EntityPlayer.java:357 attackEntityFrom, :67 isInBed;
     Minecraft.java:975 shows GuiSleepMP only in a multiplayer world;
     GuiSleepMP.java:48 sends Packet19EntityAction state 3 -->

### Spawn point

Waking in the morning sets the player's spawn point at the bed. In multiplayer,
getting up with the button sets it too.
<!-- src: EntityPlayer.java:617 wakeUpPlayer sets it at :644 only when its third
     argument is true: World.java:2402 wakeUpAllPlayers and EntityPlayer.java:70,
     day arriving, pass true, as does minecraft_server NetServerHandler.java:453
     for the button; EntityPlayer.java:68, :363 and SpawnerAnimals.java:241 pass
     false -->

A player who dies respawns in a free space beside the bed: a full, opaque block
with two empty spaces above it. If the bed is gone, or no space around it is
free, the player respawns at the
[[World Generation#The world spawn point|world spawn point]] instead, and the
bed stops being the spawn point.
<!-- src: Minecraft.java:1427 respawn; EntityPlayer.java:653 func_25060_a;
     BlockBed.java:168 getNearestEmptyChunkCoordinates searches the 3 x 3 around
     each half; Minecraft.java:1460 keeps the spawn point only when it was used.
     A server does the same: minecraft_server
     ServerConfigurationManager.java:144 -->

### In the Nether

Using a bed in the [[Nether]] destroys it and sets off an
[[Explosion|explosion]] that starts fires.
<!-- src: BlockBed.java:30 canRespawnHere, :45 newExplosion with the fire flag
     set -->

## Behaviour

A [[Piston|piston]] breaks a bed, which drops. [[Fire]] does not burn it.
<!-- src: BlockBed.java:201 getMobilityFlag 1, which BlockPistonBase.java:336
     breaks and drops; BlockFire.java:14 initializeBlock gives it no burn rate -->

## Data values

- Block ID: {{id|Bed}}
- Item ID: {{id|item 355}}
- Translation key: `tile.bed`, `item.bed`
