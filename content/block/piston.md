---
title: Piston
description: A block that pushes up to 12 blocks in front of it one space when powered, and breaks the fragile ones instead.
type: block
categories: [Blocks, Redstone]
---

**Piston** is a block that pushes the blocks in front of it one space when it
is powered.

## Obtaining

### Crafting

{{crafting|Piston}}

### Breaking

Breaking the head of an extended piston breaks the whole piston, which drops as
one item.
<!-- src: BlockPistonExtension.java:23 onBlockRemoval drops the powered base
     behind it, :74 quantityDropped 0; breaking the base instead removes the
     head at :145 onNeighborBlockChange -->

## Usage

### Placing

A piston faces the player who places it, in any of six directions. When placed
within 2 blocks of the player horizontally, it faces up if it is below the
player's feet, and down if it is above the player's head.
<!-- src: BlockPistonBase.java:224 determineOrientation -->

### Crafting ingredient

{{used in|Piston}}

## Behaviour

### Power

A piston extends when it is [[Redstone Power#Blocks that respond|powered]]
from any side but its front, or would be if it stood one block higher. It
retracts when that power goes. It moves in the same tick its power changes.
<!-- src: BlockPistonBase.java:84 isIndirectlyPowered; :52
     onNeighborBlockChange calls :66 updatePistonState, whose playNoteAt runs
     :112 playBlock at once (World.java:2369) -->

### Pushing

An extending piston pushes the blocks in front of it one space, up to 12 in a
line. It does not extend if the line is longer, or if anything would move into
y=0 or y=127. Moving blocks travel for 2 ticks and settle on the tick after.
Entities in the way of the head or the pushed blocks are pushed along.
<!-- src: BlockPistonBase.java:273 canExtend and :309 tryExtend, 13 positions
     and the y test at :281; TileEntityPiston.java:105 updateEntity, progress
     +0.5 per update and the block placed on the third; :68 moves entities only
     while extending -->

These blocks stop a piston from extending:

- [[Obsidian|obsidian]], [[Bedrock|bedrock]] and [[Nether Portal|portal]]
  blocks
- an extended piston
- blocks with a [[Game Tick#Block entities|block entity]]: [[Chest|chests]],
  [[Furnace|furnaces]], [[Dispenser|dispensers]], [[Note Block|note blocks]],
  [[Jukebox|jukeboxes]], [[Sign|signs]] and
  [[Monster Spawner|monster spawners]]

<!-- src: BlockPistonBase.java:248 canPushBlock: obsidian by id, hardness -1
     (bedrock), mobility 2 (Material.portal, Material.piston), an extended
     piston, any tile entity; the BlockContainer subclasses -->

A retracted piston can itself be pushed.

These blocks break instead of moving, and drop their items:

- plants: [[Sapling|saplings]], [[Flower|flowers]], [[Rose|roses]],
  [[Mushroom|mushrooms]], [[Tall Grass|tall grass]],
  [[Dead Bush|dead bushes]], [[Crops|crops]] and [[Sugar cane|sugar cane]]
- [[Cactus|cactus]], [[Pumpkin|pumpkins]], [[Jack 'o' Lantern|jack 'o' lanterns]],
  [[Leaves|leaves]], [[Cobweb|cobwebs]], [[Cake|cake]] and [[Snow|snow]] layers
- [[Torch|torches]], [[Redstone Torch|redstone torches]],
  [[Redstone Dust|redstone dust]], [[Redstone Repeater|repeaters]],
  [[Lever|levers]], [[Button|buttons]], [[Pressure Plate|pressure plates]],
  [[Wooden Door|doors]], [[Ladder|ladders]] and every kind of [[Rail|rail]]
- [[Water|water]], [[Lava|lava]] and [[Fire|fire]]

<!-- src: BlockPistonBase.java:336 dropBlockAsItem on mobility 1; Material.java
     setNoPushMobility on water, lava, leaves, plants, fire, circuits, cactus,
     pumpkin, cakeMaterial, web, snow; BlockDoor.java:200 and
     BlockPressurePlate.java:156 getMobilityFlag -->

## Data values

- Block ID: {{id|Piston}}, {{id|block 34}} head, {{id|block 36}} moving block
- Translation key: `tile.pistonBase`
