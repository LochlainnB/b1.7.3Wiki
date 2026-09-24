---
title: Boat
description: A wooden vehicle that floats on water and carries a player, and breaks into planks and sticks when it crashes.
type: item
categories: [Items, Transportation]
---

A **boat** is a wooden vehicle that floats on [[Water|water]] and carries a
player.

## Obtaining

### Crafting

{{crafting|Boat}}

## Usage

### Placing

Using a boat places it on top of the block or water the player is pointing at,
up to 5 blocks away.
<!-- src: ItemBoat.java:28 the 5-block trace, which stops at liquids; :41
     spawns the boat on top of the block hit -->

### Riding

Using a boat gets in, and using it again gets out. A boat another player is
riding cannot be entered.
<!-- src: EntityBoat.java:336 interact; Entity.java:982 mountEntity dismounts
     a player already riding -->

The rider steers the boat with the movement keys.
<!-- src: EntityBoat.java:195 adds a fifth of the rider's own motion each
     tick -->

A rider takes the boat's [[Damage#Environmental damage|fall damage]].
<!-- src: Entity.java:570 fall passes the distance to riddenByEntity -->

## Behaviour

### Movement

A boat floats at the surface of water. On land, it loses half its speed every
tick.
<!-- src: EntityBoat.java:136-:193 measures how much of the boat is under
     water and lifts it toward the surface; :217-:221 onGround -->

<!-- check: the boat's top speed with a rider. Speed is capped at 0.4 blocks
     per tick along each axis (EntityBoat.java:200-:215), but the rider adds
     only a fifth of their own motion each tick (:195) against 1% loss (:260),
     which may settle below the cap -->

A boat breaks [[Snow|snow]] layers it passes over.
<!-- src: EntityBoat.java:302-:308 -->

### Breaking

A boat breaks when it runs into a block while still moving faster than 3
blocks per second along the block's face. Running straight into a block stops
it without breaking it.
<!-- src: EntityBoat.java:224 measures speed after :223 moveEntity, which
     zeroes the blocked axis (Entity.java:461-:471); :246 breaks above 0.15
     blocks per tick -->

A boat also [[Damage#Other entities|breaks]] when damaged enough. Either way,
it drops three [[Wooden Planks|wooden planks]] and two [[Stick|sticks]], never
a boat. Its rider is let out.
<!-- src: EntityBoat.java:63-:83 attackEntityFrom, :246-:258 onUpdate -->

## Data values

- Item ID: {{id|Boat}}
- Entity network ID: {{id|entity 41}}
- Translation key: `item.boat`
