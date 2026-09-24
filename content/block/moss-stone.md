---
title: Moss Stone
description: A mossy cobblestone block found only on dungeon floors.
type: block
categories: [Blocks, Building blocks, Naturally generated]
---

**Moss Stone** is a mossy form of [[Cobblestone|cobblestone]] found in
[[Dungeon|dungeons]].

## Obtaining

### Breaking

Moss stone drops itself when [[Mining|mined]] with any pickaxe, and nothing
otherwise. A pickaxe breaks it fastest.
<!-- src: Block.java:640 Material.rock; Material.java:114 rock setNoHarvest;
     ItemPickaxe.java:18 canHarvestBlock; ItemPickaxe.java:41
     blocksEffectiveAgainst lists Block.cobblestoneMossy -->

### Natural generation

Moss stone generates only on the floor of a [[Dungeon|dungeon]], where it is 3
blocks in 4.
<!-- src: WorldGenDungeons.java:43-:44, nextInt(4) != 0 on the floor layer -->

## Data values

- Block ID: {{id|Moss Stone}}
- Translation key: `tile.stoneMoss`
