---
title: Fence
description: A wooden barrier crafted from sticks, which blocks movement 1.5 blocks high, above the height of a jump.
type: block
categories: [Blocks, Building blocks]
---

**Fence** is a wooden barrier block crafted from [[Stick|sticks]].

## Obtaining

### Breaking

A fence drops itself when broken, whatever breaks it.
<!-- src: BlockFence.java:5 Material.wood, which needs no tool -->

An axe is not [[Mining#What each tool is effective against|effective against]]
fences, and takes 3 seconds to break one, as a bare hand does.
<!-- src: ItemAxe.java:11 blocksEffectiveAgainst has no Block.fence;
     Block.java:327 blockStrength, hardness 2 × 30 = 60 ticks at speed 1 -->

### Crafting

{{crafting|Fence}}

## Usage

A fence blocks movement up to 1.5 blocks above its base, higher than a player
or mob can jump. It fills its whole block space, whether or not it joins a
neighbour.
<!-- src: BlockFence.java:16 getCollisionBoundingBoxFromPool, a full-width box
     1.5 high; a jump starts at 0.42 blocks a tick (EntityLiving.java:660) and
     loses 0.08 then 2% each tick (:532-:533), topping out near 1.25 blocks.
     Spiders still climb it, as they climb any wall (EntitySpider.java:74
     isOnLadder) -->

A fence joins only to fences beside it.
<!-- src: RenderBlocks.java:2455-:2466 renderBlockFence tests each neighbour
     for the fence's own id -->

A [[Torch|torch]] can be placed on top of a fence.
<!-- src: BlockTorch.java:27 canPlaceTorchOn accepts a fence below -->

### Fuel

A fence burns in a [[Smelting#Fuel|furnace]] for 300 ticks (15 seconds), long
enough to smelt 1.5 items.
<!-- src: TileEntityFurnace.java:190 getItemBurnTime, 300 for any block of
     Material.wood -->

## Behaviour

A fence can be placed only on a solid block or on another fence. It stays
where it is if the block beneath it is later removed.
<!-- src: BlockFence.java:8 canPlaceBlockAt, Material.isSolid on the block
     below; air, liquids, fire, plants, redstone parts, torches and snow layers
     are not solid (MaterialTransparent, MaterialLiquid, MaterialLogic).
     BlockFence overrides neither onNeighborBlockChange nor canBlockStay -->

Fences [[Fire#Flammable blocks|burn]], with an encouragement of 5 and a
flammability of 20.
<!-- src: BlockFire.java:16 setBurnRate(fence, 5, 20) -->

## Data values

- Block ID: {{id|Fence}}
- Translation key: `tile.fence`
