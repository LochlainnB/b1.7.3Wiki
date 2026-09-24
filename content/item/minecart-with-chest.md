---
title: Minecart with Chest
description: A minecart carrying a chest, which holds 27 stacks of items in place of a rider.
type: item
aliases: [Storage Minecart, Chest Minecart]
categories: [Items, Transportation]
---

A **minecart with chest** is a [[Minecart|minecart]] that carries items in
place of a rider.

## Obtaining

### Crafting

{{crafting|Minecart with Chest}}

## Usage

### Storage

Using a minecart with chest opens its inventory, which holds 27 stacks, as a
[[Chest|chest]] does.
<!-- src: EntityMinecart.java:772 interact, :716 getSizeInventory -->

## Behaviour

A minecart with chest is placed, and moves, as a [[Minecart|minecart]] does. It
cannot be ridden, and picks up no mobs.
<!-- src: EntityMinecart.java:772 interact never mounts; :649 picks up mobs
     only for type 0 -->

When it [[Damage#Other entities|breaks]], it drops a minecart, a
[[Chest|chest]] and everything it holds.
<!-- src: EntityMinecart.java:84-:113 attackEntityFrom; :136 setEntityDead
     spills the contents -->

## Data values

- Item ID: {{id|Minecart with Chest}}
- Entity network ID: {{id|entity 40}}
- Translation key: `item.minecartChest`

It is the minecart entity, saved with a `Type` of 1.
<!-- src: EntityMinecart.java:599 writeEntityToNBT; Item.java:360
     ItemMinecart(86, 1) -->
