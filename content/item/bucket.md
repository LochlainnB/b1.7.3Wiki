---
title: Bucket
description: An iron container that picks up a source of water or lava, or milk from a cow, and empties it again.
type: item
categories: [Items, Tools]
---

A **bucket** is an iron container for [[Water|water]], [[Lava|lava]] and
[[Milk|milk]].

## Obtaining

### Crafting

{{crafting|Bucket}}

Crafting a [[Cake|cake]] leaves its [[Milk|milk]] buckets in the crafting grid,
empty.
<!-- src: SlotCrafting.java:41 puts back an item's container item;
     Item.java:353 gives milk the empty bucket as its container -->

### Dungeon chests

A [[Dungeon#Chest loot|dungeon chest]] draw gives a bucket 1 time in 11.
<!-- src: WorldGenDungeons.java:107 pickCheckLootItem -->

## Usage

### Filling

An empty bucket used on a [[Fluid|source]] of [[Water|water]] or
[[Lava|lava]] within 5 blocks takes the source, and becomes a
[[Water Bucket|water bucket]] or a [[Lava bucket|lava bucket]]. It reaches
through flowing water and lava, and never takes them.
<!-- src: ItemBucket.java:26 the 5-block trace, :28 stopping at liquid only
     where BlockFluid.java:56 canCollideCheck finds level 0; :41 water,
     :46 lava, either the still or the flowing id -->

Used on a [[Cow|cow]], an empty bucket becomes a bucket of [[Milk|milk]].
<!-- src: EntityCow.java:38 interact -->

### Emptying

A full bucket used on a block within 5 blocks empties into the space against
the face it points at, and becomes an empty bucket:

- A [[Water Bucket|water bucket]] places a water source. In the
  [[Nether#Behaviour|Nether]], the water fizzes away and places nothing.
- A [[Lava bucket|lava bucket]] places a lava source.
- A bucket of [[Milk|milk]] pours it away, and places nothing.

<!-- src: ItemBucket.java:55-:77 the space against the face hit; :80 the
     Nether; :87 places the flowing id at level 0; :51 milk (isFull -1,
     Item.java:353) returns an empty bucket from any block -->

The space must hold air, a fluid, a ladder, sugar cane, or one of the blocks
that [[Fluid#What stops flow|fluid flows into]]. A block there is replaced, and
drops nothing.
<!-- src: ItemBucket.java:79 isAirBlock or a material that is not solid:
     liquids, plants, circuits, snow, fire and portal (Material.java:108-:138,
     MaterialLogic.java, MaterialTransparent.java, MaterialPortal.java).
     Ladders are circuits and sugar cane plants; flow skips both by id
     (BlockFlowing.java:220), the bucket does not.
     World.setBlockAndMetadataWithNotify drops nothing -->

## Data values

- Item ID: {{id|Bucket}}
- Translation key: `item.bucket`
