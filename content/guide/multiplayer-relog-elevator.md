---
title: Multiplayer Relog Elevator
description: How to escape a cave by burying the player in sand or gravel and reconnecting, with the conditions that determine the destination.
type: guide
categories: [Guides]
aliases: [Relog Elevator, Logout Teleportation]
---

**Multiplayer relog elevator** is a glitch that moves a player upward out of blocks when they disconnect and reconnect to a server.
<!-- src: minecraft_server/ServerConfigurationManager.java:74-89,95-99 -->

**This method works in stock multiplayer, not singleplayer.** Saving and reopening a singleplayer world leaves the player at the saved position, even when buried.
<!-- src: Minecraft.java:1282-1299,1325;
     World.java:256-271 (saved position is restored after preparePlayerToSpawn) -->

## How it works

On login, a player overlapping a block's collision shape moves upward in one-block steps until their whole body fits. Their horizontal position stays unchanged. The check does not search for the surface or return the player to their [[Bed|bed]] or world spawn.
<!-- src: minecraft_server/ServerConfigurationManager.java:78-89;
     minecraft_server/Entity.java:142-149,746-776;
     World.java:959-996 getCollidingBoundingBoxes -->

The lift stops at the first clear position above the saved position. A two-block-high cave can stop it underground. A continuous column of solid terrain carries it to the surface. An unexplored column does not guarantee a surface exit.
<!-- src: minecraft_server/ServerConfigurationManager.java:83-85;
     minecraft_server/EntityPlayerMP.java:41;
     Entity.java:86-87,163-169 (standing collision box is 1.8 blocks high) -->

## Triggering the elevator

Bring two blocks of [[Sand|sand]] or [[Gravel|gravel]] and a tool for digging. This setup is for [[Overworld]] caves. Test away from valuable items: the setup causes [[Damage|suffocation]], and the destination may be unsafe. The multiplayer menu does not pause the server.
<!-- src: BlockGravel.java:5; BlockSand.java:24-39;
     EntityFallingSand.java:57-64; EntityLiving.java:113-115;
     Minecraft.java:610 -->

1. Find or mine a passage with a solid floor and exactly two air blocks between the floor and ceiling. Use a column of solid terrain overhead if the intended destination is the surface.
2. Dig a **one-block-wide, one-block-deep pit** in the floor. Leave its four side walls and bottom intact. There are now three air blocks between the pit bottom and ceiling.
3. Stand in the centre of the pit. Do not jump or climb out during the following steps.
4. Look straight up and place one sand or gravel block against the underside of the ceiling. Let it fall into the pit and settle around the player's feet.
5. Place the second block against the same ceiling. It falls onto the first and settles around the player's head.
6. **As soon as the second block settles, press Escape and click Disconnect.** Do not wait in the menu; suffocation continues until the player leaves the server.
7. Reconnect to the same server with the same player name. The player appears at the first position above the pit where their body fits.

<!-- src: ItemBlock.java:12-20,45-51; BlockSand.java:24-39;
     EntityFallingSand.java:57-64; World.java:2096-2112
     (falling blocks ignore entities when settling);
     EntityPlayerSP.java:198-249 (pit walls prevent horizontal push-out);
     GuiIngameMenu.java:11-14,27-34;
     minecraft_server/ServerConfigurationManager.java:74-99 -->
<!-- test: 2026-10-06, b173harness 0.1.0, JDK 17.0.19+10, seed 1,
     vanilla generator, no T3 deviations, real multiplayer client, Normal.
     Fixture built by notifying world writes: stone (0,39,0)..(4,100,4),
     cave air (1,41,1)..(3,42,3), pit air (2,40,2), clear landing y=101..105.
     Initial positioning/inventory supplied by harness; placement, Disconnect
     and reconnect use stock mouse/keyboard input. Sand and gravel each passed
     twice: server feet and client bounding-box bottom moved y=40 to y=101,
     x=z=2.5 unchanged. Empty-pit control stayed y=40; one sand stopped y=41.
     Gap y=60 stayed bypassed; gap y=60..61 stopped the player at y=60.
     Singleplayer control remained buried at y=40 after stock save/quit and
     reloading the same sand fixture through Minecraft.startWorld.
     Evidence: https://ampcode.com/threads/T-01a11104-f82f-761b-95c7-ed6616e10833 -->

The column immediately before disconnecting is:

```text
Solid ceiling and terrain above
Air — where each falling block was placed
Sand or gravel — player's head
Sand or gravel — player's feet, inside the pit
Solid pit bottom
```

**Both falling blocks are needed for this pit layout.** With only the lower block, the player moves up one block and fits below the ceiling. The second block prevents that stop and carries the collision check into the ceiling.
<!-- src: minecraft_server/ServerConfigurationManager.java:83-85;
     EntityFallingSand.java:57-64;
     test: empty/one-block/two-block controls described above -->

## Failure conditions

| Condition | Result or action |
|---|---|
| Disconnecting before the blocks settle | Falling blocks are not yet the required obstruction. Wait for the second block to settle. |
| Leaving room for the player to move out of the buried position | The saved position may be clear. Keep the pit walls intact and stay centred. |
| A higher cave has room for the player | The lift stops there instead of reaching the surface. |
| The pit has more than three air blocks below the ceiling | The player can fit above the two buried blocks and stop below the ceiling. Use the specified height. |
| The destination is [[Water\|water]], [[Lava\|lava]] or another hazard | The login check only tests collision; it does not choose a safe landing. |
| Singleplayer or a server with changed login handling | This stock-server method does not apply. |

<!-- src: BlockSand.java:24-39; EntityFallingSand.java:57-64;
     EntityPlayerSP.java:198-249;
     minecraft_server/ServerConfigurationManager.java:83-85;
     World.java:959-996; BlockFluid.java:82-83;
     Minecraft.java:1282-1299,1325; World.java:256-271 -->
