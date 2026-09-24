---
title: Sign
description: A wooden board that shows four lines of text, placed standing on a block or hanging on its side.
type: block
categories: [Blocks, Utility blocks]
---

**Sign** is a wooden board that shows four lines of text.

## Obtaining

### Crafting

{{crafting|Sign}}

### Breaking

A sign drops a sign when broken with anything. An axe is not
[[Mining#What each tool is effective against|effective against]] it.
<!-- src: BlockSign.java:10 Material.wood, which needs no tool; :76 idDropped
     returns Item.sign; ItemAxe.java:11 blocksEffectiveAgainst has no sign -->

## Usage

### Placing

A sign placed on top of a block stands on a post, turned towards the player in
one of 16 directions. A sign placed on the side of a block hangs flat against
it. A sign cannot be placed on the underside of a block.
<!-- src: ItemSign.java:10 refuses side 0; :39 the post, rotation from the
     player's yaw in sixteenths; :41 the wall sign -->

A sign needs a solid block to stand on or hang from, and drops when that block
is removed. [[Glass]], [[Leaves|leaves]] and [[Fence|fences]] count as solid.
[[Torch|Torches]], plants, [[Rail|rails]] and [[Snow|snow]] layers do not.
<!-- src: ItemSign.java:12 and BlockSign.java:80 onNeighborBlockChange test
     Material.isSolid, which is false only for air, liquids, plants, circuits,
     snow, fire and portal (Material.java, MaterialLogic.java,
     MaterialTransparent.java, MaterialLiquid.java) -->

### Writing

Placing a sign opens a screen to write on it: four lines of up to 15 characters
each. The text cannot be changed afterwards.
<!-- src: ItemSign.java:47 displayGUIEditSign; TileEntitySign.java:4 four
     lines; GuiEditSign.java:58 length < 15; BlockSign has no blockActivated -->

## Behaviour

Entities pass through a sign. A sign stops
[[Fluid#What stops flow|flowing water and lava]]. A [[Piston|piston]] cannot
push a sign. [[Fire]] does not burn it.
<!-- src: BlockSign.java:19 getCollisionBoundingBoxFromPool returns null;
     BlockFlowing.java:222 names the post, and the wall sign is Material.wood,
     which is solid; BlockPistonBase.java:268 canPushBlock refuses any block
     with a tile entity; BlockFire.java:14 initializeBlock gives signs no burn
     rate -->

## Data values

- Block ID: {{id|Sign}} standing, {{id|block 68}} on a wall
- Item ID: {{id|item 323}}
- Translation key: `tile.sign`, `item.sign`
