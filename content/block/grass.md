---
title: Grass
description: The grass-topped dirt block on the surface of most biomes, which spreads to dirt in the light and dies back to dirt in the dark.
type: block
categories: [Blocks, Naturally generated]
---

**Grass** is a block of [[Dirt|dirt]] with a grass top, and the surface of most
[[Overworld]] biomes. Its top is coloured by the temperature and rainfall where
it stands.
<!-- src: BlockGrass.java:23 colorMultiplier reads the column's temperature and
     humidity and looks them up in ColorizerGrass -->

## Obtaining

### Breaking

Breaking grass drops [[Dirt|dirt]], whatever breaks it. A shovel breaks it
fastest.
<!-- src: BlockGrass.java:51 idDropped; Material.java:111 grassMaterial needs no
     tool; ItemSpade.java:19 blocksEffectiveAgainst -->

### Natural generation

Grass is the [[World Generation#Surface|top block]] of every biome except
[[Desert]] and [[Ice Desert]], on ground that reaches y=63. Lower ground lies
under water, and is topped with dirt.
<!-- src: BiomeGenBase.java:35 topBlock, :66-:67 the two deserts;
     ChunkProviderGenerate.java:168 places the top block only at y >= 63, the
     filler below that -->

Where a [[World Generation#Caves|cave]] cuts through grass, the dirt it
uncovers becomes grass. A [[World Generation#Lakes|lake]] turns the dirt of its
banks to grass where sky light reaches it.
<!-- src: MapGenCaves.java:129-:140; WorldGenLakes.java:78-:81, the air layers
     4 to 7 and the dirt beneath them -->

## Usage

Any hoe tills grass with air above it into [[Farmland#Obtaining|farmland]].
Tilling drops nothing.
<!-- src: ItemHoe.java:13 onItemUse, which drops no item -->

[[Mob Spawning#Passive mobs|Animals spawn]] only on grass, and prefer to walk on
it.
<!-- src: EntityAnimal.java:24 getCanSpawnHere, :9 getBlockPathWeight -->

[[Flower|Flowers]], [[Rose|roses]], [[Sapling|saplings]],
[[Tall Grass|tall grass]] and [[Sugar cane|sugar cane]] stand on grass. Sugar
cane needs [[Water|water]] beside the grass block.
<!-- src: BlockFlower.java:19 canThisPlantGrowOnThisBlockID, inherited by
     BlockSapling and BlockTallGrass; BlockReed.java:33 canPlaceBlockAt -->

[[Bone Meal|Bone meal]] used on grass grows tall grass and flowers around it.
<!-- src: ItemDye.java:42-:70 -->

## Behaviour

Grass is **covered** when the block on top of it is a full opaque block, a slab,
stairs, [[Farmland|farmland]], [[Water|water]], [[Ice|ice]] or [[Lava|lava]].
[[Leaves]], [[Glass|glass]] and every other block leave it uncovered.
<!-- src: BlockGrass.java:32 and :43 compare Block.lightOpacity of the block
     above against 2: 255 for opaque cubes (Block.java:152), slabs
     (BlockStep.java:16), stairs (BlockStairs.java:15), farmland
     (BlockFarmland.java:11) and lava (Block.java:602-:603); 3 for water and ice
     (Block.java:600-:601, :671); 1 for leaves and cobweb; 0 otherwise -->

### Spreading

On a [[Game Tick#Random ticks|random tick]], grass with [[Light|light]] 9 or
more above it picks one block within 1 block across, from 3 blocks below it to
1 above. That block becomes grass if it is uncovered [[Dirt|dirt]] with light 4
or more above it.
<!-- src: BlockGrass.java:38-:45 updateTick; nextInt(3) - 1 across and
     nextInt(5) - 3 up -->

### Dying

On a [[Game Tick#Random ticks|random tick]], covered grass turns to
[[Dirt|dirt]] 1 time in 4 if the [[Light|light]] in the covering block's space
is below 4. Under a full opaque block that gives off no light, it always is.
<!-- src: BlockGrass.java:32-:37; an opaque block's own space stores light 0
     unless it emits light (MetadataChunkBlock.java:79-:113) -->

## Data values

- Block ID: {{id|Grass}}
- Translation key: `tile.grass`
