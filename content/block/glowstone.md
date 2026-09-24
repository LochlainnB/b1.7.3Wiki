---
title: Glowstone
description: A light-giving block that hangs from the Nether's ceilings and breaks into glowstone dust.
type: block
categories: [Blocks, Naturally generated]
---

**Glowstone** is a light-giving block that hangs from the ceilings of the
[[Nether]].

## Obtaining

### Breaking

Glowstone drops two to four [[Glowstone Dust|glowstone dust]] when
[[Mining|mined]] with any pickaxe, and nothing otherwise. It never drops itself.
<!-- src: BlockGlowStone.java:10 quantityDropped 2 + nextInt(3), :14 idDropped;
     Block.java:681 Material.rock; Material.java:114 rock setNoHarvest;
     ItemPickaxe.java:18 canHarvestBlock -->

A pickaxe is not [[Mining#What each tool is effective against|effective
against]] glowstone, and mines it at speed 1.
<!-- src: ItemPickaxe.java:41 has no Block.glowStone -->

### Crafting

{{crafting|Glowstone}}

### Natural generation

Glowstone generates in clusters hanging from [[Netherrack|netherrack]] ceilings
in the [[Nether]]. A chunk attempts 10 to 19 clusters. Each grows down from one
block under the netherrack, up to 11 blocks below it and 7 to each side. See
[[World Generation#The Nether]].
<!-- src: ChunkProviderHell.java:328-:342, nextInt(nextInt(10) + 1) clusters
     and then 10 more; WorldGenGlowStone1.java and WorldGenGlowStone2.java are
     identical: an air block with netherrack above, then 1500 tries at
     nextInt(8) - nextInt(8) across and nextInt(12) down -->

## Usage

Glowstone gives off [[Light#Block light|light]].
<!-- src: Block.java:681 setLightValue(1.0F) -->

## Data values

- Block ID: {{id|Glowstone}}
- Translation key: `tile.lightgem`
