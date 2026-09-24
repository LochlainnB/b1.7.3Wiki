---
title: Crops
description: Wheat growing on farmland, planted from seeds, which grows through eight stages in the light and drops wheat and seeds.
type: block
categories: [Blocks, Plants]
---

**Crops** are wheat growing on [[Farmland|farmland]], planted from
[[Seeds|seeds]].

## Obtaining

### Planting

Crops are planted from [[Seeds#Usage|seeds]], at the first of eight stages.
<!-- src: ItemSeeds.java:18 places the crops at metadata 0 -->

### Breaking

Breaking crops makes three tries at dropping a [[Seeds|seed]]. Each succeeds
(stage + 1) times in 15, so 8 in 15 when fully grown. Fully grown crops, at
stage 7, also drop one [[Wheat|wheat]].
<!-- src: BlockCrops.java:89 dropBlockAsItemWithChance, three tries at
     nextInt(15) <= metadata; :107 idDropped, wheat at metadata 7 only;
     :111 quantityDropped 1 -->

Crops drop the same whether a player, [[Fluid#What stops flow|flowing water]],
a [[Piston#Pushing|piston]] or [[Farmland#Trampling|trampled farmland]] breaks
them. Flowing [[Lava|lava]] destroys them without drops.
<!-- src: every path ends in dropBlockAsItem (Block.java:335), which calls the
     override above; BlockFlowing.java:116 flowIntoBlock drops for water only;
     BlockPistonBase.java:336 -->

## Behaviour

### Where they stand

Crops stand only on [[Farmland|farmland]], and need [[Light|light]] 8 or
more, or open sky, to stay.
<!-- src: BlockCrops.java:14 canThisPlantGrowOnThisBlockID; BlockFlower.java:39
     canBlockStay -->

Crops that cannot stay break when a neighbouring block changes, or on their
next [[Game Tick#Random ticks|random tick]].
<!-- src: BlockFlower.java:22 onNeighborBlockChange, :27 updateTick, :31
     checkFlowerChange; BlockCrops.java:19 runs it before growing -->

### Growing

On each [[Game Tick#Random ticks|random tick]] with [[Light|light]] 9 or more in
the space above them, crops have a chance to advance one stage. Crops lit only
by the sky do not grow at [[Light#Day and night|night]].
<!-- src: BlockCrops.java:20 getBlockLightValue at y + 1, which subtracts the
     night's darkness; :22 stops at metadata 7 -->

The chance is 1 in (100 ÷ growth rate), rounded down. The growth rate starts at
1, and:

- the farmland under the crops adds 1, or 3 if it is wet;
- each of the eight farmland blocks around that one adds a quarter as much:
  0.25, or 0.75 if wet;
- the total is halved if other crops stand diagonally beside these, or beside
  them on two sides at right angles.

<!-- src: BlockCrops.java:24 nextInt((int)(100 / rate)); :37 getGrowthRate,
     :55-:58 farmland 1 or 3 when metadata > 0, :62-:63 a quarter for the
     neighbours, :70 halved when var16 (a diagonal) or var14 && var15 (crops
     along both x and z) -->

| Crops | Chance per random tick | Average time to grow fully |
|---|---|---|
| In a single row, with wet farmland all round | 1 in 10 | 24 minutes |
| In a field of wet farmland, with crops on every side | 1 in 20 | 48 minutes |
| On dry farmland, with no farmland round it | 1 in 50 | 2 hours |

<!-- src: rates 10, 5 and 2. Times are seven stages at 1 in N, with a block
     drawing a random tick about every 410 ticks (World.java:1952), in constant
     light -->

[[Bone Meal|Bone meal]] used on crops grows them fully at once.
<!-- src: ItemDye.java:33-:38; BlockCrops.java:33 fertilize sets metadata 7 -->

## Data values

- Block ID: {{id|Crops}}
- Metadata: the growth stage, 0 to 7
- Translation key: `tile.crops`
