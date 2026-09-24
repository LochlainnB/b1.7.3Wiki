---
title: Netherrack
description: The rock the Nether is made of, on which fire never burns out.
type: block
categories: [Blocks, Naturally generated]
---

**Netherrack** is the rock that the [[Nether]] is made of.

## Obtaining

### Breaking

Netherrack drops itself when [[Mining|mined]] with any pickaxe, and nothing
otherwise. A pickaxe breaks it fastest.
<!-- src: BlockNetherrack.java:5 Material.rock; Material.java:114 rock
     setNoHarvest; ItemPickaxe.java:18 canHarvestBlock; ItemPickaxe.java:41
     blocksEffectiveAgainst lists Block.netherrack -->

### Natural generation

Netherrack fills the Nether's [[World Generation#The Nether|terrain]] wherever it
is solid. [[Soul Sand|Soul sand]] and [[Gravel|gravel]] replace it at the surface
in places between y=60 and y=65.
<!-- src: ChunkProviderHell.java:38 generateNetherTerrain; :112-:150 -->

## Usage

[[Fire#Burning|Fire]] on netherrack never burns out, even in rain.
<!-- src: BlockFire.java:56, which skips the burn-out and rain tests for fire
     standing on netherrack -->

## Data values

- Block ID: {{id|Netherrack}}
- Translation key: `tile.hellrock`
