---
title: Redstone Dust
description: The dust redstone ore drops, laid on the ground as a wire that carries redstone power up to 15 blocks.
type: block
aliases: [Redstone]
categories: [Blocks, Redstone]
---

**Redstone Dust** is the dust [[Redstone Ore|redstone ore]] drops, laid on the
ground as a wire that carries [[Redstone Power|redstone power]].

## Obtaining

### Mining

[[Redstone Ore|Redstone ore]] drops four or five redstone when
[[Mining#Harvest levels|mined with an iron or diamond pickaxe]]. Placed dust
drops one when broken.
<!-- src: BlockRedstoneOre.java:55 quantityDropped; BlockRedstoneWire.java:283
     idDropped returns Item.redstone -->

### Dungeon loot

Redstone is found in [[Dungeon|dungeon]] chests.

## Usage

### Placing

Redstone is placed as dust on top of a full, solid block. It can take the place
of a [[Snow|snow]] layer. Dust drops as an item when the block beneath it goes.
<!-- src: ItemRedstone.java onItemUse, which skips the air test on snow;
     BlockRedstoneWire.java:41 canPlaceBlockAt; onNeighborBlockChange drops
     the dust when canPlaceBlockAt fails -->

### Crafting ingredient

{{used in|Redstone Dust}}

## Behaviour

### Power level

Dust holds a power level from 0 to 15, and is off at 0. Dust is at 15 when a
[[Redstone Power#Power sources|power source]] beside it powers it, or a
[[Redstone Power#Powered blocks|strongly powered]] block is beside it. Other
dust takes the highest level of the dust it connects to, less 1, so power runs
15 blocks along a line of dust.
<!-- src: BlockRedstoneWire.java:57 calculateCurrentChanges; :60-:67 reads
     isBlockIndirectlyGettingPowered with dust's own output switched off; :68-:105
     the highest connected level, less 1 -->

### Connections

Dust connects to dust beside it, and to dust one block up or down:

- up, when the block beside it is solid and the block above the dust is not;
- down, when the block beside it is not solid.

It also connects to a [[Lever|lever]], [[Button|button]],
[[Pressure Plate|pressure plate]], [[Detector Rail|detector rail]] or
[[Redstone Torch|redstone torch]] beside it, and to the front or back of a
[[Redstone Repeater|repeater]].
<!-- src: BlockRedstoneWire.java:92-:98 the steps up and down; :366
     isPowerProviderOrWire, which accepts dust, any block that canProvidePower,
     and a repeater only along its axis -->

### What it powers

Dust carrying power powers the block beneath it, and the blocks it points into:

| Shape | Points into |
|---|---|
| A dot, with no connections | all four blocks around it |
| A line, or the end of one | the block past each end |
| A corner, T or cross | nothing |

<!-- src: BlockRedstoneWire.java:291 isPoweringTo; side 1 is always powered, and a
     side is powered when the dust connects on the opposite side and not
     across it -->

A solid block powered by dust is only [[Redstone Power#Powered blocks|weakly
powered]], and passes no power to other dust.

## Data values

- Block ID: {{id|Redstone Dust}}
- Item ID: {{id|item 331}}
- Translation key: `tile.redstoneDust`, `item.redstone`

The game calls the block *Redstone Dust* and the item *Redstone*.
