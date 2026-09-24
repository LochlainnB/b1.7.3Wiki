---
title: Minecart
description: A cart placed on rails that carries a player or a mob, and rolls along the track.
type: item
categories: [Items, Transportation]
---

A **minecart** is a cart that runs along [[Rail|rails]], carrying a player or a
mob.

## Obtaining

### Crafting

{{crafting|Minecart}}

## Usage

### Placing

A minecart is placed by using it on a [[Rail|rail]],
[[Powered Rail|powered rail]] or [[Detector Rail|detector rail]]. It cannot be
placed anywhere else.
<!-- src: ItemMinecart.java:12 onItemUse, BlockRail.java:13 isRailBlock -->

### Riding

Using a minecart gets in, and using it again gets out. A minecart another
player is riding cannot be entered. Using one that carries a mob puts the
player in the mob's place.
<!-- src: EntityMinecart.java:763 interact; Entity.java:982 mountEntity
     dismounts a player already riding, and :1001 unseats any other rider -->

The rider cannot move or steer the minecart.
<!-- src: Entity.java:916 updateRidden zeroes the rider's motion, and
     EntityMinecart.onUpdate reads nothing from its rider -->

A minecart with no rider, moving faster than 2 blocks per second, picks up any
mob that touches it. It never picks up a player.
<!-- src: EntityMinecart.java:649 applyEntityCollision, speed squared above
     0.01 blocks per tick; reached from EntityLiving.java:647 -->

A rider takes the minecart's [[Damage#Environmental damage|fall damage]]. The
*On A Rail* [[Achievements|achievement]] is for riding a minecart to a point
1000 blocks from where the player got in.
<!-- src: Entity.java:570 fall passes the distance to riddenByEntity;
     EntityPlayer.java:774 -->

### Crafting ingredient

{{used in|Minecart}}

## Behaviour

### Movement

A minecart's top speed along a straight rail is 8 blocks per second (0.4 blocks
per [[Game Tick|tick]]).
<!-- src: EntityMinecart.java:308-:324 clamps each axis of the move to 0.4.
     With a rider, the move is 0.75 of the stored speed before the clamp
     (:303) -->

A minecart with no rider loses 4% of its speed every tick. One carrying a
player or mob loses 0.3%.
<!-- src: EntityMinecart.java:331-:358 -->

A minecart can gather speed beyond its top speed, from
[[Powered Rail|powered rails]] or slopes. It moves no faster for it, but keeps
top speed for longer before it slows.
<!-- src: EntityMinecart.java:259 and :400 change the stored speed, and
     nothing but the clamp on the move at :308 limits it -->

A minecart rolls down a sloped rail, and slows going up one.
<!-- src: EntityMinecart.java:232-:246, 0.0078125 blocks per tick downhill
     every tick; :360-:370 trades height for speed -->

A player or mob walking into a minecart pushes it.
<!-- src: EntityLiving.java:647 calls EntityMinecart.java:646
     applyEntityCollision, :707 -->

Off the rails, a minecart on the ground loses half its speed every tick.
<!-- src: EntityMinecart.java:433-:437 -->

<!-- check: two minecarts meeting on a rail. applyEntityCollision at
     EntityMinecart.java:673-:680 returns before any push when
     (dx * other.motionZ + dz * other.prevPosX)^2 > 5. That reads a position
     where a velocity belongs, and would stop minecarts on a north-south track
     away from x = 0 from pushing each other at all. Needs testing in game -->

### Breaking

A minecart [[Damage#Other entities|breaks]] when damaged enough, and drops as an
item. Its rider is let out.
<!-- src: EntityMinecart.java:73-:85 attackEntityFrom -->

## Data values

- Item ID: {{id|Minecart}}
- Entity network ID: {{id|entity 40}}
- Translation key: `item.minecart`
