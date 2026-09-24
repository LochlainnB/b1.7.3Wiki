---
title: Tall Grass
description: The grass plant that covers plains and forests, and drops seeds one time in eight.
type: block
categories: [Blocks, Plants, Naturally generated]
---

**Tall Grass** is a grass plant that drops [[Seeds|seeds]] when broken.

## Obtaining

### Natural generation

Tall grass generates only in [[Plains]], [[Rainforest]], [[Forest]],
[[Seasonal Forest]] and [[Taiga]], in [[World Generation#Plants|patches]]: 10
per chunk in Plains and Rainforest, 2 in Forest and Seasonal Forest, and 1 in
Taiga. Two Rainforest patches in three are [[Fern|ferns]] instead.
<!-- src: ChunkProviderGenerate.java:480-:513 populate; WorldGenTallGrass.java:19 -->

[[Bone Meal|Bone meal]] used on [[Grass|grass]] also grows tall grass.
<!-- src: ItemDye.java:62-:63, metadata 1 -->

### Breaking

Breaking tall grass drops [[Seeds|seeds]] one time in eight, and nothing
otherwise, whatever breaks it.
<!-- src: BlockTallGrass.java:39 idDropped; it has no harvestBlock of its own,
     so shears change nothing -->

## Behaviour

Tall grass stands on [[Grass|grass]], [[Dirt|dirt]] or
[[Farmland|farmland]], and needs [[Light|light]] 8 or more, or open sky, to
stay.
<!-- src: BlockTallGrass extends BlockFlower; BlockFlower.java:18
     canThisPlantGrowOnThisBlockID, :39 canBlockStay -->

Tall grass that cannot stay breaks when a block beside it changes, or on its
next [[Game Tick#Random ticks|random tick]].
<!-- src: BlockFlower.java:22 onNeighborBlockChange, :27 updateTick, :31
     checkFlowerChange -->

Tall grass [[Fire#Flammable blocks|burns]].
[[Fluid#What stops flow|Flowing water]] breaks it, and flowing [[Lava|lava]]
destroys it.

Tall grass is tinted by the temperature and rainfall of a point up to 31 blocks
away along +x and +z, picked by its position. Its colour can differ from the
[[Grass|grass]] beneath it.
<!-- src: BlockTallGrass.java:22 colorMultiplier; :27-:31 hash the position into
     offsets of 0 to 31 on x and z before :32 reads the climate there -->

## Data values

- Block ID: {{id|Tall Grass}}
- Metadata: 0 dead shrub, 1 tall grass, 2 [[Fern|fern]]
- Translation key: `tile.tallgrass`

The game has no name for block 31 or any of its three plants.

The dead shrub at metadata 0 looks like a [[Dead Bush|dead bush]], but stands
and drops as tall grass does. Nothing generates it. An item of block 31 places a
dead shrub, whatever its damage value.
<!-- src: BlockTallGrass.java:18 texture 39 + 16, the dead bush's 55
     (Block.java:624), and :24-:25 no tint for metadata 0. Only
     ChunkProviderGenerate.java:512 (metadata 1 or 2) and ItemDye.java:63
     (metadata 1) place block 31. Block 31's item is a plain ItemBlock
     (Block.java:697), which keeps Item.java:171 getPlacedBlockMetadata
     returning 0. -->
