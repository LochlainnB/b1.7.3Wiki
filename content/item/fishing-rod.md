---
title: Fishing Rod
description: A rod crafted from sticks and string, cast into water to catch raw fish, or at a mob to hook it and pull it in.
type: item
categories: [Items, Tools]
aliases: [Fishing, Bobber, Fishing Bobber]
---

A **fishing rod** is a tool cast into water to catch [[Raw Fish|raw fish]].

## Obtaining

### Crafting

{{crafting|Fishing Rod}}

## Usage

### Casting

Using a fishing rod casts a bobber. Using it again reels the bobber in.
<!-- src: ItemFishingRod.java:18 onItemRightClick; :26 spawns an EntityFish
     when the player has none out, otherwise :20 catchFish -->

The bobber disappears if the player stops holding a fishing rod, moves more
than 32 blocks from it, or dies. A bobber that lands on a block disappears
after 1200 ticks (1 minute) there.
<!-- src: EntityFish.java:146 the held item, the distance squared against 1024
     and the angler's death; :172 ticksInGround == 1200 -->

### Fishing

While the bobber floats in [[Water|water]], a fish bites with a chance of 1 in
500 each tick, or 1 in 300 when [[Weather#Rain|rain]] falls on the space above
it. That is a bite every 25 seconds on average, or 15 in the rain. The bobber
dips, and the bite lasts 10 to 39 ticks.
<!-- src: EntityFish.java:263-:272 any water in the bobber's box, still or
     flowing; :273 no new bite while one lasts; :276-:281 the 500 or 300, with
     canBlockBeRainedOn one space above the bobber; :282 ticksCatchable
     nextInt(30) + 10; :283 and :306 pull the bobber down -->

Reeling in during a bite catches one [[Raw Fish|raw fish]], which flies
towards the player.
<!-- src: EntityFish.java:361-:371 catchFish, the item's motion aimed at the
     angler -->

### Hooking

A bobber that hits a mob, a player or a vehicle hooks it, and stays on it.
Reeling in pulls a hooked entity towards the player.
<!-- src: EntityFish.java:225-:226 sets bobber when attackEntityFrom succeeds;
     :152-:157 rides along on it; :348-:360 catchFish adds motion towards the
     angler. A mob inside its invulnerability window refuses a 0 hit
     (EntityLiving.java:317), so the bobber passes on without hooking it -->

The hit deals no [[Damage|damage]], but counts as an attack by the player. It:

- knocks a mob or player back;
- angers a [[Pig Zombie|pig zombie]] or a wild [[Wolf|wolf]];
- breaks a [[Painting|painting]], which drops;
- sends a [[Ghast|ghast]]'s [[Fireball|fireball]] off the way the player is
  looking.

<!-- src: EntityFish.java:225 attackEntityFrom(angler, 0); EntityLiving.java:337
     knocks back from the attacker; EntityPigZombie.java:49; EntityWolf.java:254;
     EntityPainting.java:204; EntityFireball.java:202 takes the attacker's
     getLookVec -->

### Durability

Reeling in costs the rod [[Durability|durability]]: 1 for a fish, 2 with the
bobber on a block, 3 with an entity hooked, and nothing otherwise.
<!-- src: ItemFishingRod.java:21 damageItem(catchFish()); EntityFish.java:346
     catchFish returns 3 for a hooked entity, 1 for a fish, then 2 whenever the
     bobber is in the ground -->

## Data values

- Item ID: {{id|Fishing Rod}}
- Translation key: `item.fishingRod`

The bobber has no entity network ID, and is not saved with the world.
<!-- src: EntityList.java:83-:106 registers no EntityFish, and Entity.java:780
     addEntityID saves only entities it names. A server spawns the bobber on
     clients as object type 90 of Packet23VehicleSpawn
     (NetClientHandler.java:80) -->
