---
title: Leaves
description: The canopy blocks of trees, which drop saplings, are collected with shears, and decay once cut off from their wood.
type: block
categories: [Blocks, Plants, Naturally generated]
---

**Leaves** are the blocks of a tree's canopy, which decay once cut off from its
[[Wood|wood]].

## Obtaining

### Natural generation

Leaves form the canopy of every [[World Generation#Trees|tree]], of the same
kind as its [[Wood#Natural generation|wood]].
<!-- src: WorldGenTrees.java:56 and WorldGenBigTree.java:119 metadata 0,
     WorldGenForest.java:56 metadata 2, WorldGenTaiga1.java:55 and
     WorldGenTaiga2.java:60 metadata 1 -->

### Breaking

Broken with [[Shears|shears]], leaves drop themselves, of the same kind. Broken
any other way, they drop a [[Sapling|sapling]] of their kind one time in
twenty, and nothing otherwise.
<!-- src: BlockLeaves.java:163 harvestBlock; :155 quantityDropped, :159
     idDropped, :173 damageDropped -->

## Behaviour

### Decay

Leaves are marked for a decay check when:

- a block of [[Wood|wood]] up to 4 blocks away in each direction is removed;
- a leaf block beside them, diagonals included, is removed;
- a player places them.

<!-- src: BlockLog.java:23 onBlockRemoval, a 9×9×9 cube; BlockLeaves.java:37
     onBlockRemoval, a 3×3×3 cube; ItemLeaves.java:10 getPlacedBlockMetadata
     sets bit 8. Chunk.java:247 calls onBlockRemoval whenever a block is
     replaced, however it goes. -->

On a [[Game Tick#Random ticks|random tick]], a marked leaf block stays if a
chain of leaf blocks joined face to face, at most four long counting itself,
joins it to a block of wood of any kind. Its mark is then cleared. Otherwise it decays: it is
removed, and drops as if broken without shears.
<!-- src: BlockLeaves.java:56 updateTick; :122-:133 map the 9×9×9 cube around
     the leaf, wood 0 and leaves -2; :81-:119 spread 1 to 4 outwards from the
     wood through face-touching leaves only; :139-:144 keep and clear bit 8 if
     the leaf was reached, else :150 removeLeaves -->

A leaf block that decays marks those around it, so a canopy cut off from its
wood decays block by block. Leaves that are never marked never decay.

### Colour

Oak leaves take their colour from the temperature and rainfall where they
stand. Spruce and birch leaves have a fixed colour each.
<!-- src: BlockLeaves.java:23 colorMultiplier; ColorizerFoliage's pine and birch
     colours are constants -->

### Fire

Leaves [[Fire#Flammable blocks|burn]].

## Data values

- Block ID: {{id|Leaves}}
- Metadata: 0 oak, 1 spruce, 2 birch, plus 8 while marked for a decay check
- Translation key: `tile.leaves`

The game names all three *Leaves*.
