---
title: Minecart with Furnace
description: A minecart carrying a furnace, which drives itself along rails while it has coal to burn.
type: item
aliases: [Powered Minecart, Furnace Minecart]
categories: [Items, Transportation]
---

A **minecart with furnace** is a [[Minecart|minecart]] that drives itself along
rails by burning [[Coal|coal]].

## Obtaining

### Crafting

{{crafting|Minecart with Furnace}}

## Usage

### Fuel

Using a minecart with furnace while holding [[Coal|coal]] or
[[Charcoal|charcoal]] uses one up and adds fuel. Each piece lasts 4 minutes of
running on average.
<!-- src: EntityMinecart.java:778 interact adds 1200 fuel for any Item.coal;
     :485 burns one unit, 1 tick in 4, while it drives itself: 4800 ticks -->

Using it, with or without coal, points it away from the player. It drives
itself that way while it has fuel.
<!-- src: EntityMinecart.java:786 sets its push away from the player; :337
     pushes while the push is set, and :487 clears it once fuel is below
     zero -->

Fuel for more than 27 pieces of coal is lost when the minecart is saved. The
total turns negative, and the minecart does not run until enough coal brings it
back above zero.
<!-- src: EntityMinecart.java:603 writes fuel as (short), so anything above
     32,767 wraps; 27 × 1200 = 32,400. :487 clears the push whenever fuel is
     below zero -->

## Behaviour

A minecart with furnace is placed, and moves, as a [[Minecart|minecart]] does,
but drives itself while it has fuel. It cannot be ridden, and picks up no mobs.
<!-- src: EntityMinecart.java:776 interact never mounts; :649 picks up mobs
     only for type 0 -->

Under its own power it reaches 3.3 blocks per second on flat track. Without
fuel, it loses 13.6% of its speed every tick, against a minecart's 4%.
<!-- src: EntityMinecart.java:336-:357: speed × 0.8 + 0.04, then × 0.96,
     which settles at 0.1655 blocks per tick; × 0.9 × 0.96 with no push -->

<!-- check: whether it pushes other minecarts along. EntityMinecart.java:684
     gives the other minecart its speed and keeps 70% of its own, but
     :673-:680 can return before that; see the check on Minecart -->

When it [[Damage#Other entities|breaks]], it drops a minecart and a
[[Furnace|furnace]].
<!-- src: EntityMinecart.java:84-:115 attackEntityFrom -->

## Data values

- Item ID: {{id|Minecart with Furnace}}
- Entity network ID: {{id|entity 40}}
- Translation key: `item.minecartFurnace`

It is the minecart entity, saved with a `Type` of 2.
<!-- src: EntityMinecart.java:599 writeEntityToNBT; Item.java:361
     ItemMinecart(87, 2) -->
