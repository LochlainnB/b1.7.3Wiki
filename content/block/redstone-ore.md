---
title: Redstone Ore
description: The ore block that drops redstone, and glows for a while when touched.
type: block
subject: {Ore: block 73, Glowing: block 74}
categories: [Blocks, Naturally generated, Ores]
---

**Redstone Ore** is the ore block that drops [[Redstone Dust|redstone]].

## Obtaining

### Natural generation

Redstone ore generates in [[World Generation#Ores|veins]] of size 7, 8 per
chunk, from y=0 to y=15.
<!-- src: ChunkProviderGenerate.java:389-393 populate -->

## Usage

### Breaking

Redstone ore drops four or five [[Redstone Dust|redstone]] when
[[Mining#Harvest levels|mined]] with an iron or diamond pickaxe. Mined with
anything else, it drops nothing. It never drops itself.
<!-- src: BlockRedstoneOre.java:51-57 idDropped, quantityDropped 4 + nextInt(2),
     the same for both ids; Material.java:114; ItemPickaxe.java:17
     canHarvestBlock, harvest level 2 or more for both ids -->

No pickaxe gets a [[Mining#What each tool is effective against|speed bonus]]
on redstone ore.
<!-- src: ItemPickaxe.java:41 blocksEffectiveAgainst, which lists neither id -->

## Behaviour

### Glowing

Redstone ore starts to glow when a player hits it or right-clicks it, or when a
player or mob walks on it. Glowing ore gives off [[Light|light]] and red
particles.
<!-- src: BlockRedstoneOre.java:21-42 onBlockClicked, onEntityWalking,
     blockActivated, each swapping block 73 for 74; :59 randomDisplayTick
     sparkles only on 74; Block.java:666 setLightValue(0.625F) on 74 alone -->

A sneaking player does not set it glowing by walking on it, and neither does a
spider or a wolf.
<!-- src: Entity.java:317 and :478, onEntityWalking is skipped while sneaking
     on the ground, while riding, and for any entity whose canTriggerWalking is
     false; EntitySpider.java:15, EntityWolf.java:30 -->

Glowing ore goes dark on its next [[Game Tick#Random ticks|random tick]], about
20 seconds later on average. Touching it again while it glows does not keep it
glowing longer.
<!-- src: BlockRedstoneOre.java:44 updateTick; :11 setTickOnLoad on 74 only;
     :38 only block 73 is swapped, and nothing schedules a tick -->

## Data values

- Block ID: {{id|Redstone Ore}}, {{id|block 74}} glowing
- Translation key: `tile.oreRedstone`
