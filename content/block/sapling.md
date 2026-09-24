---
title: Sapling
description: A young tree that drops from leaves and grows into an oak, spruce or birch tree in the light.
type: block
categories: [Blocks, Plants]
---

**Sapling** is a young tree that grows into a tree of its own kind of
[[Wood|wood]].

## Obtaining

### Leaves

[[Leaves]] drop a sapling of their own kind one time in twenty, when broken
without [[Shears|shears]] and when they [[Leaves#Decay|decay]].
<!-- src: BlockLeaves.java:155 quantityDropped, :159 idDropped, :173
     damageDropped; :150 removeLeaves drops the same way -->

### Breaking

Breaking a sapling drops it, of the same kind, whatever breaks it.
<!-- src: BlockSapling.java:57 damageDropped; hardness 0 -->

## Usage

A sapling burns as [[Smelting#Fuel|furnace fuel]].
<!-- src: TileEntityFurnace.java:199 getItemBurnTime -->

## Behaviour

### Where it stands

A sapling stands on [[Grass|grass]], [[Dirt|dirt]] or [[Farmland|farmland]],
and needs [[Light|light]] 8 or more, or open sky, to stay. Placing one checks
only the block beneath.
<!-- src: BlockSapling extends BlockFlower; BlockFlower.java:14 canPlaceBlockAt,
     :18 canThisPlantGrowOnThisBlockID, :39 canBlockStay -->

A sapling that cannot stay breaks when a block beside it changes, or on its
next [[Game Tick#Random ticks|random tick]].
<!-- src: BlockSapling.java:14 runs BlockFlower's updateTick first;
     BlockFlower.java:22 onNeighborBlockChange, :31 checkFlowerChange -->

[[Fluid#What stops flow|Flowing water]] breaks a sapling, and flowing
[[Lava|lava]] destroys it.

### Growing

On each [[Game Tick#Random ticks|random tick]] with [[Light|light]] 9 or more
in the space above it, a sapling has a 1 in 30 chance to advance a stage. The
second advance grows the tree, about 20 minutes on average in constant light.
<!-- src: BlockSapling.java:15 the light test and nextInt(30), :17-:18 the
     stage bit, :20 growTree. Two successes at 1 in 30 average 60 random
     ticks, and a block draws one about every 410 ticks (World.java:1952). -->

| Sapling | Tree |
|---|---|
| Oak | an ordinary tree, or a big tree 1 time in 10 |
| Spruce | a spruce |
| Birch | a birch |

<!-- src: BlockSapling.java:40-:49 growTree: WorldGenTrees or 1 in 10
     WorldGenBigTree, WorldGenTaiga2, WorldGenForest -->

The tree needs [[Grass|grass]] or [[Dirt|dirt]] beneath it and room to grow,
as a [[World Generation#Trees|generated tree]] does. A sapling on farmland
never grows. One without room stays a sapling, back at its first stage.
<!-- src: WorldGenTrees.java:42, WorldGenForest.java:42, WorldGenTaiga2.java:43,
     WorldGenBigTree.java:305 test the block below for grass or dirt;
     BlockSapling.java:51-:53 puts the sapling back with metadata & 3 -->

A big tree grown from a sapling has leaf clusters four layers deep, against
five for one the world generates.
<!-- src: WorldGenBigTree.java:19 field_869_n = 4; only populate calls
     func_517_a (ChunkProviderGenerate.java:450), which raises it to 5 at :324;
     :160 func_520_a builds each cluster field_869_n layers tall -->

[[Bone Meal|Bone meal]] used on a sapling grows it into a tree at once.
<!-- src: ItemDye.java:24-:28 -->

## Data values

- Block ID: {{id|Sapling}}
- Metadata: 0 oak, 1 spruce, 2 birch, plus 8 at the second stage
- Translation key: `tile.sapling`

The game names all three *Sapling*.
