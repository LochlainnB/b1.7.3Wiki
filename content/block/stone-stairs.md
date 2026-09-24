---
title: Stone Stairs
description: A stair block crafted from cobblestone, which drops one cobblestone rather than itself when mined with a pickaxe.
type: block
categories: [Blocks, Building blocks]
---

**Stone Stairs** are a stair block crafted from [[Cobblestone|cobblestone]].

## Obtaining

### Breaking

Stone stairs drop one [[Cobblestone|cobblestone]] when [[Mining|mined]] with
any pickaxe, and nothing otherwise. They never drop themselves.
<!-- src: BlockStairs.java:93-:99 idDropped and quantityDropped, and :146
     dropBlockAsItemWithChance, all handed to the cobblestone (Block.java:659
     new BlockStairs(67, cobblestone)); BlockStairs.java:10 takes its
     Material.rock; Material.java:114 rock setNoHarvest; ItemPickaxe.java:18
     canHarvestBlock -->

A pickaxe is not [[Mining#What each tool is effective against|effective
against]] stone stairs, so every pickaxe takes 3 seconds to mine them.
<!-- src: ItemPickaxe.java:41 blocksEffectiveAgainst has no
     stairCompactCobblestone; Block.java:327 blockStrength, hardness 2 × 30 =
     60 ticks at speed 1 -->

### Crafting

{{crafting|Stone Stairs}}

## Usage

Players and mobs walk up stairs without jumping.
<!-- src: EntityLiving.java:67 stepHeight 0.5; BlockStairs.java:42
     getCollidingBoundingBoxes, a half-height box on the low side and a
     full-height box on the high side -->

Stairs rise in the direction the player faces when placing them.
<!-- src: BlockStairs.java:166 onBlockPlacedBy sets the metadata from the
     player's yaw; :42 puts the full-height half on that side -->

## Behaviour

Stone stairs stop [[Light#What stops light|light]], although they fill only
part of their space.
<!-- src: BlockStairs.java:15 setLightOpacity(255) -->

Mobs do not [[Mob Spawning#The spawn cycle|spawn naturally]] on stairs, and
[[Torch|torches]] cannot be placed on them.
<!-- src: SpawnerAnimals.java:157 canCreatureTypeSpawnAtLocation and
     BlockTorch.java:27-:41 canPlaceBlockAt both need isBlockNormalCube, which
     (World.java:1644) needs renderAsNormalBlock, false for stairs at
     BlockStairs.java:30 -->

## Data values

- Block ID: {{id|Stone Stairs}}
- Translation key: `tile.stairsStone`
