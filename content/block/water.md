---
title: Water
description: The fluid that fills the sea, flows seven blocks from a source, puts out burning entities and drowns them.
type: block
categories: [Blocks, Naturally generated]
---

**Water** is a [[Fluid|fluid]] that fills the sea and flows out from a source.

## Obtaining

### Natural generation

Water fills the open space below y=64, which makes the sea. It also forms
[[World Generation#Lakes|lakes]], and [[World Generation#Springs|springs]] in
cave walls.
<!-- src: ChunkProviderGenerate.java:81 every non-stone space below y=64;
     :323-:327 water lakes, 1 chunk in 4; :574-:579 water springs, 50 a chunk -->

### Buckets

An empty [[Bucket|bucket]] takes a water source, and a
[[Water Bucket|water bucket]] places one.
<!-- src: ItemBucket.java:41, :87 -->

### Ice

[[Ice]] becomes a water source when it melts, and when a player breaks it above
a solid or liquid block.
<!-- src: BlockIce.java:33 updateTick, :20 harvestBlock -->

## Usage

Water is needed by:

- [[Farmland]], which stays wet with water within 4 blocks across, level with
  it or one above;
- [[Sugar cane]], which is placed only on grass or dirt with water beside that
  block;
- [[Fishing Rod|fishing]], which gets bites only with the bobber in water;
- [[Squid]], which spawn in water.

<!-- src: BlockFarmland.java:71 isWaterNearby; BlockReed.java:32
     canPlaceBlockAt; EntityFish.java:267-:276, a bite is rolled only while
     the bobber is in water; SpawnerAnimals.java:155 -->

## Behaviour

### Flow

Water [[Fluid|flows]] 7 blocks from a source on the flat, spreading one block
every 5 ticks.
<!-- src: BlockFlowing.java:23 a level of 1 lost per block; BlockFluid.java:187
     tickRate 5 -->

Flowing water between two sources, over a solid block,
[[Fluid#Infinite water|becomes a source]].
<!-- src: BlockFlowing.java:51 -->

Flowing water breaks the non-solid blocks it reaches, such as plants and
torches, into their drops. See [[Fluid#What stops flow]].
<!-- src: BlockFlowing.java:116 flowIntoBlock -->

Lava with water beside it or above it [[Fluid#Lava and water|hardens]] into
[[Obsidian|obsidian]] or [[Cobblestone|cobblestone]].
<!-- src: BlockFluid.java:247 checkForHarden -->

### Freezing

Still water sources [[Weather#Snow and ice|freeze]] into [[Ice|ice]] in snowy
biomes.
<!-- src: World.java:1946 -->

### Entities

An entity in water:

- is pushed the way the water flows;
- stops burning, and does not [[Damage#Catching fire|catch fire]];
- takes no fall damage from a fall that ends in it;
- [[Damage#Environmental damage|drowns]] with its head under, unless it is a
  [[Squid|squid]]: 2 damage 16 seconds after going under, and 2 more every
  second after that.

<!-- src: World.java:1426 handleMaterialAcceleration, called from Entity.java:585;
     Entity.java:231 fallDistance and :233 fire cleared in water;
     EntityLiving.java:122 air falls from 300 while the head is in water, and
     :134 deals 2 each time it reaches -20; EntityWaterMob.java:8
     canBreatheUnderwater -->

A player with their head underwater [[Mining#Water and falling|mines]] five
times slower.
<!-- src: EntityPlayer.java:293 getCurrentPlayerStrVsBlock -->

### Explosions

No [[Explosion|explosion]] breaks water, and one centred in water breaks no
blocks at all.
<!-- src: Block.java:600-:601 hardness 100, so a blast resistance of 100;
     Explosion.java:55-:61, whose first step is at the centre -->

## Data values

- Block ID: {{id|Water}} (flowing), {{id|block 9}} (still)
- Translation key: `tile.water`
