---
title: Dungeon
description: A small underground cobblestone room with a monster spawner at its centre and up to two chests of loot.
type: structure
categories: [Structures]
aliases: [Dungeons, Monster room]
---

A **dungeon** is a small underground room of [[Cobblestone|cobblestone]] with a
[[Monster Spawner|monster spawner]] at its centre and up to two
[[Chest|chests]].

## Generation

Eight dungeons are attempted in every [[Overworld]] chunk, each at a random
point anywhere from y=0 to y=127.
<!-- src: ChunkProviderGenerate.java:340-:344 -->

The room inside is 5 or 7 blocks long in each direction, chosen separately, and
4 blocks tall. A dungeon is built only where:

- the whole floor layer and the whole ceiling layer are solid;
- the walls have between one and five openings, an opening being a wall space
  at floor level with air in it and above it.

A sealed room is rejected, so every dungeon opens onto some open space, such as
a cave.
<!-- src: WorldGenDungeons.java:6-:36 -->

## Contents

| Part | Made of |
|---|---|
| Walls | {{sprite\|Cobblestone}}, where the rock was solid; openings stay open |
| Floor | {{sprite\|Moss Stone}} 3 times in 4, {{sprite\|Cobblestone}} otherwise |
| Ceiling | the rock that was already there |
| Centre of the floor | a {{sprite\|Monster Spawner}}: [[Zombie]] half the time, [[Skeleton]] or [[Spider]] a quarter each |

<!-- src: WorldGenDungeons.java:34-:50, :98-:100, :134 pickMobSpawner -->

Any wall or floor block with nothing solid beneath it is left out.
<!-- src: WorldGenDungeons.java:40 -->

Two chests are attempted. Each takes up to three tries at a random floor space
against exactly one wall, so a chest never stands in a corner or in the open. A
dungeon holds none, one or two.
<!-- src: WorldGenDungeons.java:53-:96, the var15 == 1 test at :76 -->

### Chest loot

Each chest is filled by eight draws, each put into a random slot. A later draw
can replace an earlier one. Each draw gives one of:

| Item | Amount | Chance per draw |
|---|---|---|
| {{sprite\|Saddle}} | 1 | 1 in 11 |
| {{sprite\|Iron Ingot}} | 1–4 | 1 in 11 |
| {{sprite\|Bread}} | 1 | 1 in 11 |
| {{sprite\|Wheat}} | 1–4 | 1 in 11 |
| {{sprite\|Gunpowder}} | 1–4 | 1 in 11 |
| {{sprite\|String}} | 1–4 | 1 in 11 |
| {{sprite\|Bucket}} | 1 | 1 in 11 |
| {{sprite\|Cocoa Beans}} | 1 | 1 in 11 |
| {{sprite\|Redstone Dust\|text=Redstone}} | 1–4 | 1 in 22 |
| {{sprite\|Music Disc}}, either of the two | 1 | 1 in 110 |
| {{sprite\|Golden Apple}} | 1 | 1 in 1,100 |

A draw gives nothing otherwise.
<!-- src: WorldGenDungeons.java:80-:91 the eight draws, :107
     pickCheckLootItem; the rarer items need a second roll after drawing their
     one in eleven -->

## Usage

A dungeon's floor is the only place [[Moss Stone|moss stone]] generates.
<!-- src: Block.cobblestoneMossy is placed by WorldGenDungeons.java:44 and by no
     other generator, and no recipe in data/recipes.json makes it -->
