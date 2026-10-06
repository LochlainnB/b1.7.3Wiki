---
title: Multiplayer Bed Recall
description: How to carry a sleeping player away from a bed and return them using the stock multiplayer Leave Bed button.
type: guide
categories: [Guides]
---

**Multiplayer bed recall** returns a transported, sleeping player to their original [[Bed|bed]] through the **Leave Bed** button.
<!-- src: minecraft_server/EntityPlayer.java:592-607 wakeUpPlayer;
     EntityPlayerMP.java:248-257; GuiSleepMP.java:36-49 -->

## How it works

Entering a [[Bed|bed]] while riding a [[Minecart|minecart]] does not dismount the player. The cart can carry the sleeping player away without changing which bed they wake beside.

**The cart must be removed before waking.** Otherwise, the player remains attached to it and is pulled back to the cart's position after leaving the bed.
<!-- src: minecraft_server/EntityPlayer.java:512-570,592-607;
     Entity.java:910-911 updateRiderPosition;
     EntityPlayerMP.java:248-265 -->
<!-- test: 2026-10-06, b173harness 0.1.0, seed 1, two real clients,
     stock mouse/keyboard input, no T3 behaviour deviations: a detached sleeper
     returned about 63 blocks with unchanged health on both server and client.
     An intact-cart control stayed at the destination after Leave Bed.
     Longer routes and bed-chunk unloading were not runtime-tested.
     Evidence: https://ampcode.com/threads/T-01a10ea1-2780-7373-b4d3-70cf3a51b6bb -->

This is not a recall button for an awake player. The player stays asleep throughout the outward journey and cannot resume normal play at the destination while keeping the recall available.
<!-- src: Minecraft.java:972-979; GuiSleepMP.java:36-49;
     EntityClientPlayerMP.java:38-52 -->

## Using the recall

Having a helper ready to launch and destroy the player's [[Minecart|minecart]] is the simplest way to use this recall, particularly because another player must be connected to the server to prevent night being skipped.

1. Mount a minecart.
2. Right click a [[Bed|bed]] to sleep. **Leave Bed** must appear before departure.
3. Launch the minecart and wait for it to reach its destination.
4. Destroy the cart.
5. Click **Leave Bed** to return to beside the original bed.

<!-- src: minecraft_server/NetServerHandler.java:59-71,308-310,447-455;
     EntityPlayer.java:512-570;
     EntityMinecart.java:70-82 (cart destruction dismounts the rider);
     EntityPlayer.java:337-344 (damage wakes a sleeper);
     EntityPlayerMP.java:248-265; GuiSleepMP.java:36-49 -->

## Limits and failure conditions

| Condition | Effect or action |
|---|---|
| Everyone sleeps | The night skips and the player wakes. |
| Daylight arrives | The player wakes. |
| The player takes damage | The player wakes. |
| The original bed breaks or its chunk unloads | The bed can no longer provide the return position. |
| Leave Bed is pressed while still mounted | The player stays with the cart. |
| The server restarts or the player reconnects | The transported sleep state is lost. |
| Bed or launcher interactions fail near world spawn | Spawn protection can block the interaction. Build outside it or obtain operator permission. |

<!-- src: minecraft_server/EntityPlayer.java:63-68,288-298,337-344,592-625;
     World.java:1502-1515,2082-2099;
     NetServerHandler.java:295-310 -->
