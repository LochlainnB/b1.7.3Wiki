---
title: Relog Teleportation
description: The multiplayer login collision correction that can lift a player through terrain, including invisible overlaps caused by wall-contact rounding.
type: mechanic
categories: [Game mechanics]
aliases: [Relog Elevator, Multiplayer Relog Elevator, Logout Teleportation]
---

**Relog teleportation** is a multiplayer glitch that moves a [[Player|player]] upward out of collisions when they disconnect and reconnect.

## How it works

Disconnecting saves the [[Player|player]]'s position. Reconnecting restores it, then checks the player's full collision box. An overlapping player moves upward in one-block steps until the box is clear. X and Z stay unchanged.
<!-- src: minecraft_server/ServerConfigurationManager.java:74-99
     readPlayerDataFromFile, playerLoggedIn, playerLoggedOut;
     minecraft_server/NetLoginHandler.java:81-98 doLogin;
     minecraft_server/Entity.java:746-776 readFromNBT -->

The check uses block and entity collision shapes, not visible block outlines or [[Damage|suffocation]]. Any positive overlap counts. Touching a collision face exactly does not.
<!-- src: World.java:959-996 getCollidingBoundingBoxes;
     Block.java:273-283 getCollidingBoundingBoxes, getCollisionBoundingBoxFromPool;
     AxisAlignedBB.java:185-195 intersectsWith;
     Entity.java:892-905 isEntityInsideOpaqueBlock uses separate eye-level samples -->

## Wall-contact rounding

The glitch can occur while the [[Player|player]] stands in air on a cave floor beside a wall. Burial and suffocation are not required.
<!-- test: real-client wall-contact experiment below; both the cave-floor
     position and the client's entire collision box were clear before logout -->

Movement shifts the edges of the client's collision box separately. The reported horizontal position is the centre of that box. The server rebuilds a fixed-width box around that position. Floating-point rounding can make the server's box extend slightly into a wall even when the client's box ends exactly at its face.
<!-- src: Entity.java:347-372,453-455 moveEntity;
     AxisAlignedBB.java:197-204 offset;
     EntityClientPlayerMP.java:55-75 sendMotionUpdates;
     minecraft_server/NetServerHandler.java:132-135,190 handleFlying;
     minecraft_server/Entity.java:142-149 setPosition -->

Ordinary server movement checks a box inset by 1/16 of a block on every face. A rounding overlap fits within that margin. Login checks the full box without the margin and starts the upward correction.
<!-- src: minecraft_server/NetServerHandler.java:171-193 handleFlying;
     minecraft_server/AxisAlignedBB.java:226-233 getInsetBoundingBox;
     minecraft_server/ServerConfigurationManager.java:83-85 playerLoggedIn -->

Wall contact does not always leave an overlap. Different approach positions can produce exact contact, a tiny gap or a tiny overlap. Only the overlap starts the lift. There is no fixed success probability or random chance in the login correction.
<!-- src: Entity.java:163-169 setPosition, :453-455 moveEntity;
     minecraft_server/ServerConfigurationManager.java:78-89 playerLoggedIn;
     test: approach-dependent wall contact below.
     A reported success rate of about two-thirds is not a measured game rule.
     This establishes an air-standing wall variant, not every unexplained
     cave-floor relog report or a trigger away from all collision shapes. -->

<!-- test: 2026-10-07, b173harness 0.1.0, JDK 17.0.19+10, vanilla generator,
     seed 1, spawn (0,100,0), no T3 deviations, real multiplayer client Walker.
     Normal difficulty; mobs disabled; view-distance 5; renderDistance 1;
     guiScale 2; 854x480 window. Python b173.server with s.client("Walker").
     Fixture supplied by notifying world writes: stone (0,39,0)..(10,100,10),
     cave air (1,40,1)..(9,42,9), landing air (0,101,0)..(10,105,10).
     Waited for client/server block agreement, not a fixed loading delay.
     Initial positioning used server teleports. Walking and GUI Disconnect /
     reconnect used virtual keyboard/mouse through stock input handling.
     After teleporting to (4.848127557889951,40,5.5), yaw 90, waited 3 ticks,
     held forward for 28 ticks, released, waited 3 ticks. Client box minX=1.0;
     maxX=1.600000023841857; reported centre X=1.3000000119209285.
     Server box minX=0.9999999999999996: overlap 4.440892098500626e-16.
     Player stood on ground at feet Y=40 in air, without health loss.
     Reconnect lifted to Y=101. Repeating the same approach reproduced it.
     Starting at X=1.872986182830961 instead gave exact server contact at
     minX=1.0 and no lift. The cave-centre control also stayed at Y=40.
     After the overlapping wall approach, holding back for 4 ticks, releasing
     and waiting 8 ticks cleared the overlap; reconnect stayed at Y=40.
     Removing stone (0,60,4)..(2,61,6) stopped the wall-contact ascent at Y=60.
     Read-only playerLoggedIn entry/exit traces verified restored Y=40,
     corrected destinations and unchanged X/Z in all six cases.
     Evidence: https://ampcode.com/threads/T-01a11104-f82f-761b-95c7-ed6616e10833 -->

## Destination

The lift stops at the first collision-free position it tests, not necessarily the surface. The [[Player|player]]'s box is 0.6 blocks wide and 1.8 blocks high. A two-block-high cavity can stop an ascent underground. A one-block-high gap cannot contain the whole body.
<!-- src: minecraft_server/ServerConfigurationManager.java:83-85;
     Entity.java:86-87,163-169 width, height, setPosition;
     minecraft_server/EntityPlayerMP.java:41 yOffset=0 -->

A slight side-wall overlap can carry the player upward while their centre remains in air. The lift continues only while every tested position intersects a collision shape. Solid terrain above a cave does not start the lift when the saved position is clear.
<!-- src: minecraft_server/ServerConfigurationManager.java:83-85;
     World.java:959-996; AxisAlignedBB.java:185-195 -->

The destination is not checked for hazards. [[Water|Water]] and [[Lava|lava]] have no collision box and do not stop the lift. The player is not sent to their [[Bed|bed]] or world spawn.
<!-- src: BlockFluid.java:82-83 getCollisionBoundingBoxFromPool returns null;
     minecraft_server/ServerConfigurationManager.java:78-89 playerLoggedIn -->
<!-- test: 2026-10-06, same harness/JDK/seed and no T3 deviations.
     Stone (0,39,0)..(4,100,4), air (1,41,1)..(3,42,3), pit air (2,40,2),
     landing air Y=101..105. Real-client placement buried the player in two
     sand or gravel blocks. Both materials twice gave Y=40 to Y=101;
     empty pit stayed Y=40, one sand stopped Y=41. One-high gap at Y=60
     was bypassed; two-high gap Y=60..61 stopped at Y=60. X/Z unchanged.
     Evidence: https://ampcode.com/threads/T-01a11104-f82f-761b-95c7-ed6616e10833 -->

## Singleplayer

Saving and reopening a singleplayer world does not apply this login correction. The saved [[Player|player]] position is restored without the server's upward collision check.
<!-- src: minecraft/net/minecraft/client/Minecraft.java:1282-1299,1325 changeWorld;
     World.java:256-271 spawnPlayerWithLoadedChunks;
     test: 2026-10-06, singleplayer save/reload negative control left a buried
     player at Y=40, using the same sand fixture and stock save/quit UI.
     Evidence: https://ampcode.com/threads/T-01a11104-f82f-761b-95c7-ed6616e10833 -->
