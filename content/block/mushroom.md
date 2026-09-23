---
title: Mushroom
description: A small brown or red plant that stands on any opaque block and spreads slowly in dim light.
type: block
categories: [Blocks, Plants, Naturally generated]
subject: {Brown: Brown Mushroom, Red: Red Mushroom}
aliases: [Brown Mushroom, Red Mushroom]
---

**Mushroom** is a small plant, brown or red, that spreads slowly in dim light.

## Obtaining

### Natural generation

Mushrooms generate in [[World Generation#Plants|patches]] at a random height,
mostly underground. An [[Overworld]] chunk gets a brown patch one time in four
and a red patch one time in eight, and the [[Sky Dimension|Sky dimension]] uses
the same rates. A [[Nether]] chunk gets one patch of each.
<!-- src: WorldGenFlowers.java:12-23 generate, which places only where
     canBlockStay passes; ChunkProviderGenerate.java:534-546,
     ChunkProviderSky.java:428-440, ChunkProviderHell.java:344-357 -->

### Breaking

Breaking a mushroom drops it, whatever breaks it.

## Usage

### Crafting ingredient

{{used in|Brown Mushroom}}

## Behaviour

### Where a mushroom can stand

A mushroom stands on any full opaque block, [[Leaves|leaves]] and the
[[Double Stone Slab|double stone slab]] included. [[Glass]], [[Ice|ice]],
[[Farmland|farmland]], slabs, stairs and [[Fence|fences]] do not hold one.
<!-- src: BlockMushroom.java:29-31 canThisPlantGrowOnThisBlockID reads
     Block.opaqueCubeLookup, filled at Block.java:151 -->

Generating and spreading also need an air space with [[Light|light]] 12 or
less. The light is read without the time of day, so a space open to the sky
counts as light 15 at midnight.
<!-- src: BlockMushroom.java:18 isAirBlock, :33-39 canBlockStay;
     World.java:529 getFullBlockLightValue -->

### Spreading

On each [[Game Tick#Random ticks|random tick]] a mushroom has a 1 in 100 chance
to try to spread, about once every 41,000 ticks. A try picks one block in the
3×3×3 cube around the mushroom and places a mushroom there if the space
qualifies. The same level is twice as likely as the level above or below.
<!-- src: BlockMushroom.java:13-27 updateTick; a block draws a random tick about
     once every 410 ticks, World.java:1952 -->

Nothing limits how many mushrooms stand together.

### Staying put

A mushroom drops as an item when a block beside it changes and its spot no
longer qualifies. Random ticks never remove one, so a mushroom in bright light
stays until something beside it changes.
<!-- src: BlockMushroom.java:13 updateTick replaces BlockFlower's, which would
     call checkFlowerChange; BlockFlower.java:22-37 onNeighborBlockChange -->

Placing a mushroom by hand skips the light test. One planted in daylight stays
there and never spreads.
<!-- src: BlockFlower.java:14-16 canPlaceBlockAt tests only the block beneath -->

## Data values

- Block ID: {{id|Brown Mushroom}} brown, {{id|Red Mushroom}} red
- Translation key: `tile.mushroom`

The game names both *Mushroom*.
<!-- The wiki names them Brown Mushroom and Red Mushroom
     (data/name-overrides.json) so a recipe can say which one it wants. -->
