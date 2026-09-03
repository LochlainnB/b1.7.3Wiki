---
title: Mushroom
description: A small plant that survives only in darkness and slowly spreads to nearby blocks.
type: block
categories: [Blocks, Plants, Naturally generated]
---

**Mushroom** is a small plant that survives only in darkness. Two kinds exist,
brown and red. The game gives both the same name and runs both through the same
code, so they behave identically; they differ in appearance, in how often they
generate, and in that the brown one gives off a faint light where the red one
gives off none.

## Obtaining

### Natural generation

Mushrooms are placed during world generation, at a random height anywhere in the
chunk column rather than on the surface. Each attempt picks one point in the
chunk, then makes 64 tries to place a mushroom scattered up to eight blocks
horizontally and four vertically around it, taking only the spots already legal
for a mushroom to stand in. Because the starting height is drawn from the whole
column and mushrooms need darkness, nearly all of them end up underground.
<!-- src: WorldGenFlowers.java:12-23 generate -->

In the Overworld a chunk gets one brown attempt in four and one red attempt in
eight, and the Sky dimension uses the same rates. In the Nether both kinds run
in every chunk, which is why [[Netherrack]] caverns are thick with them.
<!-- src: ChunkProviderGenerate.java:534-546, ChunkProviderSky.java:428-440, ChunkProviderHell.java:344-357 -->

### Breaking

Breaking a mushroom drops it as an item, whatever it is broken with. A mushroom
also drops itself if the block beneath it is removed or replaced with something
it cannot stand on.

## Usage

### Crafting ingredient

{{used in|Mushroom}}

## Behaviour

### Where a mushroom can stand

Three things must be true of a space before a mushroom can occupy it: the space
is air, and so not water, not [[Tall Grass]] and not a snow layer; the block
directly below fills its whole cube and blocks light; and the light in the space
is 12 or less.

The ground rule is unusually broad. Other small plants accept only [[Grass]],
[[Dirt]] and [[Farmland]], but a mushroom asks a different question of the block
below it — whether it is a full opaque cube. Nearly every solid block passes,
[[Stone]] and ores and wool and planks alike, and so do [[Leaves]] and the
[[Double Stone Slab]]. Blocks that do not fill their cube all fail, among them
the [[Stone Slab]], stairs, fences, [[Glass]] and [[Ice]] — and [[Farmland]],
which every other plant accepts and a mushroom refuses.
<!-- src: BlockMushroom.java:29-31 canThisPlantGrowOnThisBlockID, Block.java:151 -->

The light test ignores the time of day. It reads the sky light stored for the
block without the reduction that nightfall applies to it, so a space open to the
sky counts as fully lit at midnight exactly as at noon. Mushrooms therefore
belong to overhangs, cave mouths, deep forest floor and everything below ground.
<!-- src: BlockMushroom.java:33-39 canBlockStay, World.java:529 getFullBlockLightValue -->

### Spreading

A mushroom spreads by copying itself into a space nearby. Each time it receives
a random tick there is a 1 in 100 chance that it tries, and a try considers
exactly one candidate: a single block drawn from the 3×3×3 cube centred on the
mushroom itself. The two horizontal offsets are even — one block either way, or
none — but the vertical one is not, and staying on the same level is twice as
likely as rising or dropping a block. The candidate is taken only if it meets
the three conditions above, and one try in eighteen draws the mushroom's own
space and is wasted.
<!-- src: BlockMushroom.java:13-27 updateTick -->

Random ticks set the pace, and they are scarce. A chunk receives eighty of them
per game tick, spread across the 32768 blocks of its column, so any one mushroom
is ticked about once every 410 ticks and tries to spread about once every 41000
— a little over half a try per in-game day, most of which fail. Only chunks
within nine of a player are ticked at all, so a patch grows only while someone is
nearby.
<!-- src: World.java:1879 chunk radius, World.java:1952-1961 updateBlocksAndPlayCaveSounds -->

Nothing caps how many mushrooms may stand together, so a patch left alone in a
large dark space keeps spreading until it runs out of ground.

### Staying put

A mushroom checks whether it is still in a legal spot only when a block directly
beside it changes. It never checks during a random tick, unlike the flowers it
shares its code with, so a mushroom standing somewhere too bright stays there
indefinitely.
<!-- src: BlockMushroom.java:13 updateTick replaces BlockFlower.checkFlowerChange, BlockFlower.java:22-37 -->

Placing one by hand does not test the light either, only that the space is clear
and that the block below will hold it. A mushroom can therefore be planted in
full daylight and left there, where it sits unbothered and never spreads. It
drops the moment anything beside it is built or broken.
<!-- src: BlockFlower.java:14-16 canPlaceBlockAt -->

## Data values

- Block ID: `39`, `40`
- Translation key: `tile.mushroom`
