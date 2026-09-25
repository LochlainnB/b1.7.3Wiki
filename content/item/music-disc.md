---
title: Music Disc
description: The two discs a jukebox plays, "13" and "cat", found in dungeon chests and dropped by creepers that skeletons kill.
type: item
subject: {13: Music Disc, cat: item 2257}
sprite: {13: Music Disc, cat: item 2257}
categories: [Items]
---

**Music Disc** is an item that a [[Jukebox|jukebox]] plays. There are two:
"13" and "cat".

## Obtaining

### Dungeon loot

Music discs are found in [[Dungeon#Chest loot|dungeon chests]], "13" and "cat"
at even odds.
<!-- src: WorldGenDungeons.java:128, record13 + nextInt(2) -->

### Creeper drop

A [[Creeper|creeper]] killed by a [[Skeleton|skeleton]]'s arrow drops one music
disc, "13" or "cat" at even odds.
<!-- src: EntityCreeper.java:80 onDeath; the arrow names the skeleton as its
     attacker (EntityArrow.java:162 attackEntityFrom(this.owner, 4)) -->

## Usage

Using a disc on an empty [[Jukebox|jukebox]] plays its song. The screen shows
the title as it starts: *C418 - 13* or *C418 - cat*.
<!-- src: ItemRecord.java:12 onItemUse; Item.java:378-:379 the names "13" and
     "cat"; RenderGlobal.java:1257 and GuiIngame.java:399 print
     "Now playing: C418 - " and the name -->

## Data values

- Item ID: {{id|Music Disc}} "13", {{id|item 2257}} "cat"
- Translation key: `item.record`

Both discs are named *Music Disc* in the inventory.
