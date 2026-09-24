---
title: Compass
description: An item crafted from iron and redstone, whose needle points to the world spawn point.
type: item
categories: [Items, Tools]
---

**Compass** is an item whose needle points to the
[[World Generation#The world spawn point|world spawn point]].

## Obtaining

### Crafting

{{crafting|Compass}}

## Usage

### Finding spawn

The needle points toward the world spawn point from wherever the player stands
and whichever way they face. A [[Bed|bed]] does not change where it points.
<!-- src: TextureCompassFX.java:53-:56, the angle from the player's position
     and rotationYaw to World.java:2286 getSpawnPoint, which reads the world's
     spawn and never the player's own -->

Every compass shows the same needle, drawn for the player looking at it, whether
it is held, in a chest or on the ground.
<!-- src: TextureCompassFX.java:15, one animated icon for Item.compass, drawn
     from mc.thePlayer -->

In the [[Nether#Light and weather|Nether]], the needle spins at random.
<!-- src: TextureCompassFX.java:57 -->

On a server, a compass points to x=8, z=8 once the player has died or changed
dimension, until the player rejoins.
<!-- src: NetClientHandler.java:467 handleRespawn calls Minecraft.java:1447
     setSpawnLocation, which WorldClient.java:69 sets to (8, 64, 8), as does a
     new WorldClient (:18) on a change of dimension; the server sends the real
     spawn only at login, minecraft_server NetLoginHandler.java:91
     Packet6SpawnPosition -->

### Crafting ingredient

{{used in|Compass}}

## Data values

- Item ID: {{id|Compass}}
- Translation key: `item.compass`
