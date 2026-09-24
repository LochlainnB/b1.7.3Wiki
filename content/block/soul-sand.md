---
title: Soul Sand
description: A Nether block that slows anything moving across it.
type: block
categories: [Blocks, Naturally generated]
---

**Soul Sand** is a [[Nether]] block that slows anything moving across it.

## Obtaining

### Breaking

Breaking soul sand drops it, whatever breaks it. No tool is
[[Mining#What each tool is effective against|effective against]] it, and a sword
breaks it fastest.
<!-- src: BlockSoulSand.java:5 Material.sand, which needs no tool
     (Material.java:123); ItemSpade.java:19 does not list Block.slowSand;
     ItemSword.java:13 getStrVsBlock is 1.5 against every block -->

### Natural generation

In the [[Nether]], about half of columns whose surface lies between y=60 and
y=65 take soul sand as their top block and filler. See
[[World Generation#The Nether]].
<!-- src: ChunkProviderHell.java:112 the soul sand roll, :143-:150 -->

## Behaviour

An entity standing on soul sand sinks an eighth of a block into it. On every
tick it touches the block, its horizontal speed is multiplied by 0.4. Players,
mobs and dropped items are all slowed.
<!-- src: BlockSoulSand.java:8 getCollisionBoundingBoxFromPool, 0.125 short of
     the top; :13 onEntityCollidedWithBlock, called from Entity.java:514
     moveEntity for every block the entity's box overlaps -->

Soul sand does not fall.
<!-- src: BlockSoulSand extends Block, not BlockSand -->

## Data values

- Block ID: {{id|Soul Sand}}
- Translation key: `tile.hellsand`
