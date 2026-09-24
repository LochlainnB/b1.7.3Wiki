---
title: Gravel
description: A block that falls when nothing holds it up, and drops flint one time in ten.
type: block
categories: [Blocks, Naturally generated]
---

**Gravel** is a block that falls when nothing holds it up, and the only source
of [[Flint|flint]].

## Obtaining

### Breaking

Breaking gravel drops [[Flint|flint]] one time in ten, and gravel otherwise,
whatever breaks it. A shovel breaks it fastest.
<!-- src: BlockGravel.java:10 idDropped; Material.java:123 sand needs no tool;
     ItemSpade.java:19 blocksEffectiveAgainst -->

### Natural generation

Gravel forms [[World Generation#Ores|veins]] in stone, as an ore does: 10 per
chunk, of size 32, from y=0 to y=127.
<!-- src: ChunkProviderGenerate.java:361-:366 WorldGenMinable(Block.gravel.blockID,
     32), 10 times at nextInt(128) -->

Between y=60 and y=65, rare stretches of the [[World Generation#Surface|surface]]
have gravel in place of the biome's filler, and water or air in place of its
top block.
<!-- src: ChunkProviderGenerate.java:124 the gravel roll, :143-:152; the empty
     top becomes water below y=64 (:162) and stays air at y=64 and y=65 -->

In the [[Nether]], gravel tops about half of columns whose surface lies between
y=60 and y=65, except where [[Soul Sand|soul sand]] takes them.
<!-- src: ChunkProviderHell.java:113 the gravel roll, :136-:150, soul sand
     applied after gravel -->

## Behaviour

Gravel [[Falling Sand|falls]] when the block below it is air, [[Water|water]],
[[Lava|lava]] or [[Fire|fire]].
<!-- src: BlockGravel extends BlockSand; BlockSand.java:24 tryToFall, :49
     canFallBelow -->

## Data values

- Block ID: {{id|Gravel}}
- Translation key: `tile.gravel`
