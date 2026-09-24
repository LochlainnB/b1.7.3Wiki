---
title: Bone Meal
description: The white dye, crafted from bones, which grows saplings and crops at once and plants tall grass and flowers on grass.
type: item
categories: [Items]
---

**Bone meal** is the white [[Dye|dye]], crafted from [[Bone|bones]].

## Obtaining

### Crafting

{{crafting|Bone Meal}}

## Usage

### Growing plants

Using bone meal on a [[Sapling|sapling]], [[Crops|crops]] or [[Grass|grass]]
uses up one, whether or not anything grows.
<!-- src: ItemDye.java:21-:74 onItemUse; each branch decrements the stack
     before, and regardless of, the outcome -->

A sapling grows into a tree at once. Where the tree cannot grow, the sapling
stays.
<!-- src: ItemDye.java:24-:28 growTree; BlockSapling.java:51-:53 puts the
     sapling back when the tree generator fails -->

Crops grow fully at once.
<!-- src: ItemDye.java:33-:38; BlockCrops.java:33 fertilize sets metadata 7,
     with no test of the current stage -->

Saplings and crops grow this way in any light.
<!-- src: the light >= 9 tests are in BlockSapling.java:15 and
     BlockCrops.java:20 updateTick, which bone meal does not go through -->

On grass, bone meal makes 128 tries at planting around the clicked block. Each
try follows a random path of up to 7 steps across the tops of grass blocks, and
plants where it ends if that space is empty: [[Tall Grass|tall grass]] 9 times
in 10, otherwise a [[Flower|flower]] 2 times in 3 or a [[Rose|rose]] 1 time in
3.
<!-- src: ItemDye.java:42-:70; try n takes n / 16 steps, each of up to 1 block
     in x and z and sometimes 1 in y, and is abandoned on a step that is not
     above grass or is inside a solid block -->

### Dyeing

Used on a [[Sheep|sheep]], bone meal [[Dye|dyes]] its wool white.
<!-- src: ItemDye.java:80 saddleEntity; ItemDye.java:4 dyeColorNames[15] is
     "white" -->

### Crafting ingredient

{{used in|Bone Meal}}

## Data values

- Item ID: {{id|Bone Meal}}
- Translation key: `item.dyePowder.white`
