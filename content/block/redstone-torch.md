---
title: Redstone Torch
description: A torch that gives redstone power unless the block it is attached to is powered, turning the signal around.
type: block
subject: {Off: block 75, On: block 76}
categories: [Blocks, Redstone]
---

**Redstone Torch** is a torch that gives [[Redstone Power|redstone power]]
while the block it is attached to is not powered.

## Obtaining

### Crafting

{{crafting|Redstone Torch}}

## Usage

### Placing

A redstone torch is placed on top of a full, solid block or a [[Fence|fence]],
or on the side of a full, solid block. It drops as an item when that block goes.
<!-- src: BlockRedstoneTorch extends BlockTorch; BlockTorch.java:27
     canPlaceTorchOn, :31 canPlaceBlockAt, :94 onNeighborBlockChange -->

### Crafting ingredient

{{used in|Redstone Torch}}

## Behaviour

### Power

A redstone torch is lit unless the block it is attached to is
[[Redstone Power#Powered blocks|powered]]. It switches 2 ticks after that block's
power changes. A [[Game Tick#Skipping a delay|random tick]] can switch it sooner. A
torch on a fence stays lit, as a fence is never powered.
<!-- src: BlockRedstoneTorch.java:92 isIndirectlyPowered reads the attached
     block through World.java:2167 isBlockIndirectlyProvidingPowerTo, which
     asks a fence (not a normal cube) for isPoweringTo, false by default;
     :41 tickRate 2, scheduled at :136; :38 setTickOnLoad(true) -->

A lit redstone torch [[Redstone Power#Power sources|powers]] every block beside
it except the one it is attached to, and
[[Redstone Power#Powered blocks|strongly powers]] the block above it.
<!-- src: BlockRedstoneTorch.java:73 isPoweringTo, :139 isIndirectlyPoweringTo -->

### Burning out

A redstone torch that turns off for the 8th time within 100 ticks burns out,
with a hiss and a puff of smoke. It stays off while 8 of its turn-offs lie
within the last 100 ticks, and relights at its next update after that: when a
block beside it changes, or on a random tick.
<!-- src: BlockRedstoneTorch.java:15 checkForBurnout, which counts entries for
     this position in a list shared by every torch; :110 drops entries older
     than 100 ticks; :117 the fizz and smoke on the 8th; :128 no relight while 8
     remain -->

## Data values

- Block ID: {{id|Redstone Torch}} unlit, {{id|block 76}} lit
- Translation key: `tile.notGate`

The item is the lit torch. Breaking either kind drops block 76.
<!-- src: BlockRedstoneTorch.java:143 idDropped -->
