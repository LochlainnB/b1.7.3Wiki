---
title: Farmland
description: Dirt tilled with a hoe, the block crops grow on, which water or rain keeps wet and which turns back to dirt when it dries out or is trampled.
type: block
categories: [Blocks]
---

**Farmland** is [[Dirt|dirt]] tilled with a hoe, and the only block
[[Crops|crops]] grow on.

## Obtaining

### Tilling

Using any hoe on [[Grass|grass]] or [[Dirt|dirt]] turns it into farmland. Grass
must have air above it, and cannot be tilled from below. Dirt can be tilled from
any side, even with a block on top.
<!-- src: ItemHoe.java:13 onItemUse; var7 is the face used, 0 the underside,
     and var9 the block above. The grass tests do not apply to dirt. -->

### Breaking

Breaking farmland drops [[Dirt|dirt]], whatever breaks it. A shovel breaks it
fastest.
<!-- src: BlockFarmland.java:94 idDropped; Material.java:112 ground needs no
     tool; ItemSpade.java:19 blocksEffectiveAgainst -->

## Usage

[[Seeds]] are planted on farmland, and grow into [[Crops|crops]].
[[Crops#Growing|Crops grow faster]] on wet farmland.
<!-- src: ItemSeeds.java:17; BlockCrops.java:55-:58 -->

## Behaviour

### Moisture

Farmland has a moisture level from 0, dry, to 7. Wet farmland, above 0, is
darker on top. Newly tilled farmland is dry.
<!-- src: BlockFarmland.java:26 the wet texture for metadata above 0;
     ItemHoe.java:21 places metadata 0 -->

On a [[Game Tick#Random ticks|random tick]], 1 time in 5, farmland:

- becomes fully wet if any [[Water|water]] is within 4 blocks horizontally,
  level with it or one block up, or if [[Weather#Rain|rain]] falls on the space
  above it;
- otherwise dries by one level;
- if already dry, turns to [[Dirt|dirt]], unless crops stand on it.

<!-- src: BlockFarmland.java:34 updateTick, :35 nextInt(5); :36
     canBlockBeRainedOn one space up; :44 metadata 7; :39 dries by 1; :41 dirt;
     :71 isWaterNearby, a 9 x 9 square on its own layer and the one above,
     testing Material.water, so flowing water counts; :57 isCropsNearby looks
     only at the space directly above -->

### Trampling

Each footstep an entity takes on farmland turns it to [[Dirt|dirt]] 1 time
in 4. A sneaking player, a rider, a [[Spider|spider]] or a [[Wolf|wolf]] never
tramples it.
<!-- src: BlockFarmland.java:50 onEntityWalking; Entity.java:478 calls it for
     each step unless canTriggerWalking is false, the entity is sneaking on the
     ground (:317) or riding; EntitySpider.java:15, EntityWolf.java:30 -->

### Under a solid block

Farmland with a solid block above it turns to [[Dirt|dirt]] when a
neighbouring block changes. Placing a solid block on it does this at once.
Anything but air, a fluid, a ladder, sugar cane, or a block that
[[Fluid#What stops flow|fluid flows into]] counts as solid.
<!-- src: BlockFarmland.java:85 onNeighborBlockChange tests
     Material.isSolid() above; the non-solid materials are air, liquids,
     plants, circuits, snow, fire and portal (Material.java:110-:134,
     MaterialLogic.java, MaterialTransparent.java, MaterialPortal.java) -->

Dirt tilled under a solid block stays farmland until a neighbouring block
changes.

## Data values

- Block ID: {{id|Farmland}}
- Metadata: moisture, 0 dry to 7 wet
- Translation key: `tile.farmland`
