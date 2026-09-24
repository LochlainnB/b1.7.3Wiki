---
title: Player
description: The entity a person controls, with its size, movement, health, air, inventory, death and respawning.
type: entity
categories: [Entities]
---

The **player** is the entity a person controls.

## Spawning

A player first appears at the
[[World Generation#The world spawn point|world spawn point]].
<!-- src: EntityPlayer.java:45 -->

A player who dies respawns beside the [[Bed#Spawn point|bed]] last slept in, or
at the world spawn point without one. A player who dies in the [[Nether]]
respawns in the [[Overworld]].
<!-- src: Minecraft.java:1418 respawn, :1419 leaves a dimension that
     WorldProviderHell.java:45 marks as unfit to respawn in; minecraft_server
     NetServerHandler.java:490 recreates the player in dimension 0 -->

On a server, a player placed at the world spawn point, on first joining or on
respawning, lands at a random spot up to 10 blocks from it along x and along z.
For 60 ticks (3 seconds) after joining or respawning, a player on a server
cannot be hurt.
<!-- src: minecraft_server EntityPlayerMP.java:27-:37, rand.nextInt(20) - 10 on
     each axis outside the Nether; ServerConfigurationManager.java:83 and :156
     raise the player until nothing collides; EntityPlayerMP.java:18
     ticksOfInvuln = 60, :68 counts it down, :90 refuses damage until then -->

## Behaviour

### Body

A player is 0.6 blocks wide and 1.8 tall, with eyes 1.62 blocks above the feet.
A player can [[Mining|mine]] or use a block up to 4 blocks from the eyes, and
hit an entity up to 3 blocks away.
<!-- src: EntityPlayer.java:151-:152; EntityRenderer.java:187-:189 puts the
     camera 1.62 above the feet; PlayerControllerSP.java:109 and
     PlayerControllerMP.java:118 getBlockReachDistance 4, measured from the
     camera (EntityRenderer.java:85); :94 caps the entity reach at 3 -->

A distance measured to a player, such as a mob's reach, runs to the eyes in
singleplayer and to the feet on a server.
<!-- src: EntityPlayer.java:44 yOffset 1.62 puts the position at eye level;
     minecraft_server EntityPlayerMP.java:41 yOffset 0 puts it at the feet;
     Entity.java:678 getDistanceToEntity measures between positions -->

### Health

A player has 20 [[Damage#Health|health]]. Eating [[Food|food]] restores it, and on
Peaceful it regenerates at 1 point a second.
<!-- src: EntityPlayer.java:47; :173 the Peaceful regeneration -->

A player catches alight only after 20 ticks in [[Fire|fire]]. A
[[Lightning Bolt|lightning]] strike does not set a player alight.
<!-- src: EntityPlayer.java:50 fireResistance 20. Entity.java:525-:527 counts up
     from -20 while in fire and sets 300 on reaching 0, and :531 puts it back
     to -20 out of fire; Entity.java:1087 adds only 1 to the same count -->

A hit that deals no damage, such as a [[Snowball|snowball]], an [[Egg|egg]] or a
[[Fishing Rod|fishing bobber]], does nothing to a player, knockback included.
<!-- src: EntityPlayer.java:380 returns before EntityLiving.attackEntityFrom
     when the damage is 0. A mob's hit on Peaceful is scaled to 0 at :367 and
     does nothing either -->

### Movement

| Movement | Blocks per second |
|---|---|
| Walking | 4.3 |
| Sneaking | 1.3, or 1.8 diagonally |
| In water | 2.0 |
| In lava | 0.8 |

Moving diagonally is no faster than moving straight, except while sneaking.

A jump rises 1.25 blocks. A player walks up a rise of half a block, such as a
[[Stone Slab|slab]], without jumping. In water, a player rises at 2 blocks per
second while holding jump, and sinks at 2 otherwise.

A sneaking player does not walk off the edge of a block.
<!-- src: EntityLiving.java:640 takes 0.98 of the input; on the ground :489
     accelerates by a tenth of that a tick and :534 keeps 0.546 of the speed,
     a steady 0.216 a tick; MovementInputFromOptions.java:71-:74 scales the
     sneaking input by 0.3; in water :458-:463 accelerate by 0.02 and keep 0.8,
     in lava :469-:474 keep 0.5. Entity.java:611 moveFlying scales an input
     above 1 down to 1, which a diagonal walk is and a diagonal sneak is not.
     :660 jump 0.42, then :532-:533 gravity and drag; :67 stepHeight 0.5;
     :631 adds 0.04 a tick while jumping in water, against the 0.02 of
     sinking at :463; Entity.java:317 the edge check while sneaking -->

### Air

A player has 300 ticks (15 seconds) of air with the head underwater, shown as
ten bubbles, and then [[Damage#Environmental damage|drowns]]. Air refills in
full as soon as the head leaves the water.
<!-- src: Entity.java:100 maxAir 300; EntityLiving.java:123 counts it down and
     :139 refills it at once; GuiIngame.java:122 draws ten bubbles. The head
     is tested 1.74 above the feet in singleplayer (the position plus
     EntityPlayer.java:349 getEyeHeight 0.12) and 1.62 on a server
     (minecraft_server EntityPlayerMP.java:62) -->

### Inventory

A player has 36 inventory slots, the bottom row of 9 being the hotbar, plus 4
[[Armour|armour]] slots and a 2×2 [[Crafting|crafting]] grid.
<!-- src: InventoryPlayer.java:4-:5, :16 getCurrentItem holds from slots 0-8
     only; ContainerPlayer.java:13 the grid, :27 the armour slots -->

The drop key, Q by default, throws one of the held item forward as a
[[Dropped Item|dropped item]].
<!-- src: GameSettings.java:34 key 16, Q; EntityPlayer.java:249
     dropCurrentItem, :270-:272 aimed the way the player faces -->

An open [[Chest|chest]], [[Furnace|furnace]], [[Dispenser|dispenser]] or
[[Crafting Table|crafting table]] screen closes when the player is more than 8
blocks from the block's centre, or the block is gone.
<!-- src: EntityPlayer.java:81; TileEntityChest.java:84,
     TileEntityFurnace.java:204, TileEntityDispenser.java:104 and
     ContainerWorkbench.java:56, each a distance squared of at most 64 -->

### Death

A player dies at 0 health, and drops everything in the inventory and armour
slots, scattered around the body. In singleplayer, a player with the username
Notch also drops an [[Apple|apple]].
<!-- src: EntityPlayer.java:227 dropAllItems (InventoryPlayer.java:321), each
     stack thrown in a random direction (EntityPlayer.java:263-:268); :223 the
     apple. A server's player replaces onDeath with dropAllItems alone
     (minecraft_server EntityPlayerMP.java:85), so there the apple never
     drops -->

The death screen offers *Respawn* and *Title menu*, and shows a score, which is
always 0.
<!-- src: GuiGameOver.java:8-:9, :41; EntityLiving.java:21 scoreValue 0 is the
     only amount addToPlayerScore is ever given -->

### In multiplayer

A server with PvP turned off stops players hurting each other, by hits or by
arrows. PvP is on by default.
<!-- src: minecraft_server EntityPlayerMP.java:93-:103; MinecraftServer.java:85
     reads "pvp" from server.properties, true by default -->

Other players see a player's name above the head from up to 64 blocks away,
through blocks. A sneaking player's name shows only within 32 blocks, and not
through blocks.
<!-- src: RenderPlayer.java:61-:68; RenderLiving.java:185 draws the label with
     the depth test off, which the sneaking branch at RenderPlayer.java:69
     leaves on -->

## Data values

The player has no entity network ID. Singleplayer saves the player in the
world's `level.dat`, and a server saves each player as `players/<name>.dat` in
the world folder.
<!-- src: EntityList.java:83-:106 registers no EntityPlayer; WorldInfo.java:104
     the Player tag; minecraft_server PlayerNBTManager.java:172. A server sends
     other players to a client with Packet20NamedEntitySpawn -->
