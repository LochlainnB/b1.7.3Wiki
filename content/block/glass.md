---
title: Glass
description: A transparent block smelted from sand, which drops nothing when broken.
type: block
categories: [Blocks, Building blocks]
---

**Glass** is a transparent block smelted from [[Sand|sand]].

## Obtaining

### Breaking

Glass drops nothing when broken, whatever breaks it.
<!-- src: BlockGlass.java:10 quantityDropped 0 -->

### Smelting

{{smelting|Glass}}

## Behaviour

Light passes through glass as it does through air. The space beneath glass
stays [[Light#Sky light|open to the sky]]. [[Zombie|Zombies]] and
[[Skeleton|skeletons]] under glass burn in daylight.
<!-- src: glass is not an opaque cube (BlockBreakable.java:11), so
     Block.java:152 gives it opacity 0; Chunk.java:67 generateHeightMap passes
     blocks of opacity 0; EntityZombie.java:14 and EntitySkeleton.java:26 test
     canBlockSeeTheSky -->

Mobs do not [[Mob Spawning#The spawn cycle|spawn naturally]] on glass, and
[[Torch|torches]] cannot be placed on it.
<!-- src: SpawnerAnimals.java:157 canCreatureTypeSpawnAtLocation and
     BlockTorch.java:27-:41 canPlaceBlockAt both need isBlockNormalCube, which
     (World.java:1644) glass fails: Material.glass is setIsTranslucent
     (Material.java:125), so Material.java:87 getIsTranslucent is false -->

## Data values

- Block ID: {{id|Glass}}
- Translation key: `tile.glass`
