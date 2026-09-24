---
title: Wooden Stairs
description: A stair block crafted from wooden planks, which drops a block of planks rather than itself when broken.
type: block
categories: [Blocks, Building blocks]
---

**Wooden Stairs** are a stair block crafted from [[Wooden Planks|wooden planks]].

## Obtaining

### Breaking

Wooden stairs drop one block of [[Wooden Planks|wooden planks]] when broken,
whatever breaks them. They never drop themselves.
<!-- src: BlockStairs.java:93-:99 idDropped and quantityDropped, and :146
     dropBlockAsItemWithChance, all handed to the planks (Block.java:645
     new BlockStairs(53, planks)); BlockStairs.java:10 takes the planks'
     Material.wood, which needs no tool -->

An axe is not [[Mining#What each tool is effective against|effective against]]
wooden stairs, and takes 3 seconds to break them, as a bare hand does.
<!-- src: ItemAxe.java:11 blocksEffectiveAgainst has no stairCompactPlanks;
     Block.java:327 blockStrength, hardness 2 × 30 = 60 ticks at speed 1 -->

### Crafting

{{crafting|Wooden Stairs}}

## Usage

Players and mobs walk up stairs without jumping.
<!-- src: EntityLiving.java:67 stepHeight 0.5; BlockStairs.java:42
     getCollidingBoundingBoxes, a half-height box on the low side and a
     full-height box on the high side -->

Stairs rise in the direction the player faces when placing them.
<!-- src: BlockStairs.java:166 onBlockPlacedBy sets the metadata from the
     player's yaw; :42 puts the full-height half on that side -->

### Fuel

Wooden stairs burn in a [[Smelting#Fuel|furnace]] for 300 ticks (15 seconds),
long enough to smelt 1.5 items.
<!-- src: TileEntityFurnace.java:190 getItemBurnTime, 300 for any block of
     Material.wood -->

## Behaviour

Wooden stairs stop [[Light#What stops light|light]], although they fill only
part of their space.
<!-- src: BlockStairs.java:15 setLightOpacity(255) -->

Mobs do not [[Mob Spawning#The spawn cycle|spawn naturally]] on stairs, and
[[Torch|torches]] cannot be placed on them.
<!-- src: SpawnerAnimals.java:157 canCreatureTypeSpawnAtLocation and
     BlockTorch.java:27-:41 canPlaceBlockAt both need isBlockNormalCube, which
     (World.java:1644) needs renderAsNormalBlock, false for stairs at
     BlockStairs.java:30 -->

Wooden stairs [[Fire#Flammable blocks|burn]], with an encouragement of 5 and a
flammability of 20.
<!-- src: BlockFire.java:17 setBurnRate(stairCompactPlanks, 5, 20) -->

## Data values

- Block ID: {{id|Wooden Stairs}}
- Translation key: `tile.stairsWood`
