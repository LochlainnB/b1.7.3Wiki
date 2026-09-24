---
title: Obsidian
description: The block a lava source hardens into, harvested only with a diamond pickaxe and used to frame Nether portals.
type: block
categories: [Blocks, Building blocks]
---

**Obsidian** is the block a [[Lava|lava]] source hardens into when water reaches
it.

## Obtaining

### Breaking

Obsidian drops itself only when [[Mining|mined]] with a
[[Diamond Pickaxe|diamond pickaxe]]. Mined with anything else, it drops nothing.
<!-- src: BlockObsidian.java:14 idDropped; ItemPickaxe.java:11 canHarvestBlock,
     harvestLevel == 3 -->

A pickaxe is not [[Mining#What each tool is effective against|effective
against]] obsidian, so even a diamond pickaxe takes 15 seconds to mine it.
<!-- src: ItemPickaxe.java:41 has no Block.obsidian; Block.java:327
     blockStrength, 10 * 30 = 300 ticks at speed 1 -->

### Lava and water

A [[Lava|lava]] source with [[Water|water]] beside it or above it
[[Fluid#Lava and water|hardens]] into obsidian.
<!-- src: BlockFluid.java:247 checkForHarden -->

### Nether portals

A portal the game builds for an [[Nether Portal#Arriving|arriving player]] is
framed in obsidian. Where the game has to carve out space for it, the portal
also stands on an obsidian platform.
<!-- src: Teleporter.java:228 the platform, :243 the frame -->

## Usage

Obsidian is the frame of a [[Nether Portal#Building a portal|Nether portal]].

## Behaviour

No [[Explosion|explosion]] breaks obsidian, and a [[Piston|piston]] cannot push
it.
<!-- src: Block.java:641 setResistance(2000.0F); BlockPistonBase.java:249
     canPushBlock refuses obsidian by id -->

## Data values

- Block ID: {{id|Obsidian}}
- Translation key: `tile.obsidian`
