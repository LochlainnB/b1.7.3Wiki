---
title: Jukebox
description: A wooden block that plays a music disc once, heard up to 64 blocks away.
type: block
categories: [Blocks, Utility blocks]
---

**Jukebox** is a wooden block that plays [[Music Disc|music discs]].

## Obtaining

### Crafting

{{crafting|Jukebox}}

### Breaking

A jukebox drops itself when broken with anything. An axe is not
[[Mining#What each tool is effective against|effective against]] it.
<!-- src: BlockJukeBox.java:5 Material.wood, which needs no tool;
     ItemAxe.java:11 blocksEffectiveAgainst has no jukebox -->

## Usage

Using a music disc on an empty jukebox puts the disc in and plays its song once.
The song fades with distance, and is silent beyond 64 blocks.
<!-- src: ItemRecord.java:13 needs a jukebox with metadata 0, :17 ejectRecord
     stores the disc, :18 plays it; SoundManager.java:148 newStreamingSource
     with looping off and linear fall-off over 16 * 4 blocks -->

The disc stays in the jukebox after the song ends. Using the jukebox ejects the
disc and stops the song. Breaking the jukebox ejects it too.
<!-- src: BlockJukeBox.java:12 blockActivated, :30 pops the disc out above
     the jukebox and plays a null record; :51 onBlockRemoval -->

A player hears one disc at a time. A disc starting stops any other disc and the
background music.
<!-- src: SoundManager.java:136 stops the one "streaming" source, :143 stops
     "BgMusic" -->

### Fuel

A jukebox burns in a [[Smelting#Fuel|furnace]] for 300 ticks (15 seconds).
<!-- src: TileEntityFurnace.java:190 getItemBurnTime, 300 for any block made
     of Material.wood -->

## Behaviour

A [[Piston|piston]] cannot push a jukebox. [[Fire]] does not burn it.
<!-- src: BlockPistonBase.java:268 canPushBlock refuses any block with a tile
     entity; BlockFire.java:14 initializeBlock gives it no burn rate -->

## Data values

- Block ID: {{id|Jukebox}}
- Translation key: `tile.jukebox`
