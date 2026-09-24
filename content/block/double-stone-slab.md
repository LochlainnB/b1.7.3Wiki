---
title: Double Stone Slab
description: The full block two slabs of the same kind form when one is placed on the other, which breaks back into two slabs.
type: block
categories: [Blocks, Building blocks]
---

**Double Stone Slab** is a full block made of two [[Stone Slab|slabs]].

## Obtaining

### Breaking

A double stone slab drops two slabs of its kind when [[Mining|mined]] with any
pickaxe, and nothing otherwise. It never drops itself. A pickaxe breaks it
fastest.
<!-- src: BlockStep.java:60-:70 idDropped stairSingle, quantityDropped 2,
     damageDropped keeps the kind; :10 Material.rock; Material.java:114 rock
     setNoHarvest; ItemPickaxe.java:18 canHarvestBlock; ItemPickaxe.java:41
     blocksEffectiveAgainst lists stairDouble -->

### Stacking slabs

A [[Stone Slab|slab]] placed directly on top of a slab of the same kind joins
it into a double stone slab of that kind: stone, sandstone, wooden or
cobblestone.
<!-- src: BlockStep.java:43 onBlockAdded, which compares the two metadata
     values and replaces the lower slab with block 43 -->

## Behaviour

The wooden double slab looks like [[Wooden Planks|wooden planks]], but does not
[[Fire#Flammable blocks|burn]].
<!-- src: BlockStep.java:28 texture 4, the planks' tile, on every face for
     metadata 2; BlockFire.java:14 initializeBlock has no entry for block 43 -->

## Data values

- Block ID: {{id|Double Stone Slab}}
- Metadata: `0` stone, `1` sandstone, `2` wooden, `3` cobblestone
- Translation key: `tile.stoneSlab`

The game gives this block no display name.
<!-- src: en_US.lang names only the four slab items, tile.stoneSlab.stone.name
     and the rest, and has no tile.stoneSlab.name; StringTranslate.java:33
     translateNamedKey returns "" for a missing key. The wiki's name comes
     from data/name-overrides.json. -->
