---
title: Apple
description: A food that only a player named Notch drops, and the ingredient of the golden apple.
type: item
categories: [Items, Food]
---

An **apple** is a [[Food|food]] and the ingredient of a
[[Golden Apple|golden apple]].

## Obtaining

A player with the username Notch drops one apple on each death, along with the
inventory. Nothing else in the game gives an apple, except a server operator's
`give` command.
<!-- src: EntityPlayer.java:223 onDeath tests username.equals("Notch"), in the
     server tree too (minecraft_server EntityPlayer.java:203). No block, mob,
     chest or recipe produces Item.appleRed: it appears only there and in the
     golden apple recipe (CraftingManager.java:67). The give command:
     minecraft_server ConsoleCommandHandler.java:133, open to operators through
     minecraft_server NetServerHandler.java:428 -->

## Usage

### Eating

An apple is [[Food#Eating|eaten]] to restore 4 health.
<!-- src: Item.java:278 ItemFood(4, 4, false) -->

### Crafting ingredient

{{used in|Apple}}

## Data values

- Item ID: {{id|Apple}}
- Translation key: `item.apple`
