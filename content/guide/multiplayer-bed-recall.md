---
title: Multiplayer Bed Recall
description: How to carry a sleeping player away from a bed and return them using the stock multiplayer Leave Bed button.
type: guide
categories: [Guides]
---

**Multiplayer bed recall** returns a transported, sleeping player to their original [[Bed|bed]] through the stock **Leave Bed** button.
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

## Preparing a route

Place a [[Bed|bed]] in the [[Overworld]], close enough to a stopped, empty [[Minecart|minecart]] to be used while mounted. Leave clear ground beside the bed for the return.
<!-- src: minecraft_server/EntityPlayer.java:512-570,592-607 -->

Keep the cart stopped until the player is asleep. A switchable [[Powered Rail|powered rail]] with a solid backstop provides a launcher. Build a safe, lit track to the destination, with powered rails to keep the cart moving and unpowered powered rails to stop it. Leave room beside the arrival point for a helper to reach the cart.
<!-- src: minecraft_server/EntityMinecart.java:252-263,386-406 -->

An awake helper launches the cart and removes it at the destination. The original bed must remain intact and its [[Chunk|chunk]] must stay loaded. For a route that takes the helper away from the bed's loaded area, keep another awake player near the bed.
<!-- src: minecraft_server/World.java:1502-1515,2082-2099;
     EntityPlayer.java:63-68,624-625;
     ChunkProviderServer.java:84-90; PlayerManager.java:11-38 -->

## Using the recall

1. At night, the sleeper mounts the stopped [[Minecart|minecart]] beside the [[Bed|bed]]. Wait a moment for mounting to settle.
2. Still mounted, the sleeper right-clicks the bed. **Leave Bed** must appear before departure.
3. The helper launches the cart. The sleeper keeps the sleep screen open during the journey.
4. At the destination, stop the cart. The helper attacks the cart until it breaks. **Stop attacking immediately when the cart disappears; do not hit the sleeper.**
5. Once the cart is gone and the sleeper is no longer mounted, the sleeper clicks **Leave Bed** to return beside the original bed.
6. Replace the cart and reset the launcher before another journey. Each use requires entering the bed again.

<!-- src: minecraft_server/NetServerHandler.java:59-71,308-310,447-455;
     EntityPlayer.java:512-570;
     EntityMinecart.java:70-82 (cart destruction dismounts the rider);
     EntityPlayer.java:337-344 (damage wakes a sleeper);
     EntityPlayerMP.java:248-265; GuiSleepMP.java:36-49 -->

## Limits and failure conditions

| Condition | Effect or action |
|---|---|
| Everyone sleeps | The night skips and wakes the sleeper. Keep at least one other player awake. |
| Daylight arrives | The sleeper wakes before the planned recall. Complete the journey during the night. |
| The sleeper takes damage | The sleeper wakes early. Protect the route from mobs and other hazards. |
| The original bed breaks or its chunk unloads | The bed can no longer provide the return position. |
| Leave Bed is pressed while still mounted | The player stays with the cart instead of completing the return. |
| The server restarts or the sleeper reconnects | The transported sleep state is lost. Start a new journey. |
| Bed or launcher interactions fail near world spawn | Spawn protection can block the interaction. Build outside it or obtain operator permission. |

<!-- src: minecraft_server/EntityPlayer.java:63-68,288-298,337-344,592-625;
     World.java:1502-1515,2082-2099;
     NetServerHandler.java:295-310 -->
