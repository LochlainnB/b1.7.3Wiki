---
title: Bedrock
description: The unbreakable block at the bottom of the Overworld and at the floor and ceiling of the Nether.
type: block
categories: [Blocks, Naturally generated]
---

**Bedrock** is the unbreakable block at the bottom of the world.

## Obtaining

No tool [[Mining#Instant and unbreakable blocks|breaks]] bedrock, so it never
drops, and no recipe makes it.
<!-- src: Block.java:599 setBlockUnbreakable; Block.java:328 blockStrength
     returns 0 for negative hardness -->

### Natural generation

Bedrock fills y=0 in every column of the [[Overworld]], and is scattered from
y=1 to y=4, more thinly the higher it is. See
[[World Generation#Water, ice and bedrock]].
<!-- src: ChunkProviderGenerate.java:132 -->

The [[Nether]] has the same layers at its floor, from y=0 to y=4, and at its
ceiling, from y=127 down to y=123. See [[World Generation#The Nether]].
<!-- src: ChunkProviderHell.java:121 the ceiling, :123 the floor -->

## Behaviour

No [[Explosion|explosion]] breaks bedrock, and a [[Piston|piston]] cannot push
it.
<!-- src: Block.java:599 setResistance(6000000.0F); BlockPistonBase.java:253
     canPushBlock refuses a hardness of -1 -->

## Data values

- Block ID: {{id|Bedrock}}
- Translation key: `tile.bedrock`
