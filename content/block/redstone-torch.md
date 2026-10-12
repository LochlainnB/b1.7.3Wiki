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
within the last 100 ticks, and relights at its next
[[Game Tick#Block updates|block update]] or random tick after that.
<!-- src: BlockRedstoneTorch.java:15 checkForBurnout, which counts entries for
     this position in a list shared by every torch; :110 drops entries older
     than 100 ticks; :117 the fizz and smoke on the 8th; :128 no relight while 8
     remain -->

Every torch in the running game records its turn-offs in one list, shared by
every world and dimension loaded since the game started. A torch counts the
turn-offs recorded at its coordinates, whichever world made them.

Turn-offs are cleared from the oldest end of the list, against the clock of the
world the clearing torch is in. A turn-off dated later than a world's clock
cannot be cleared by that world's torches, and holds back every turn-off
recorded after it. While it stays, a torch in that world burns out at its 8th
turn-off in all, and does not relight. This happens:

- in a singleplayer world opened after one with a later time, without restarting
  the game;
- in a server's Nether once players sleep through a night, which moves the
  Overworld's clock on and not the Nether's. Each Overworld torch that turns off
  then holds back the Nether's turn-offs until a torch in the Overworld updates
  more than 100 ticks later;
- on a server, after `time set` to an earlier time.

<!-- src: BlockRedstoneTorch.java:9 torchUpdates is static; :24 compares x, y
     and z only; :110 stops at the first entry not more than 100 ticks older
     than this world's time. Singleplayer copies the world info on a dimension
     change (World.java:136), so its two dimensions share one clock; a server
     loads a WorldInfo per dimension (minecraft_server World.java:68) and
     sleeping moves one world's clock (minecraft_server World.java:1502).
     tested (harness): singleplayer world at time 50000 burnt a clock out, then
     a new world in the same session: a clock at the same coordinates burnt out
     at its 1st turn-off and one elsewhere at its 8th, and neither relit in 8000
     ticks, where a fresh session's clocks relit every 100-900 ticks. Server, a
     player in the Nether, another asleep in the Overworld (clocks then 24008
     and 13112): once the Overworld's only clock stopped, a Nether clock burnt
     out and stayed out for 5945 ticks; while that clock ran, it had relit every
     140-780 ticks. Server, time set from 51500 to 1000: one clock never relit
     and a new one burnt out at its 8th turn-off, for 5000 ticks -->

## Data values

- Block ID: {{id|Redstone Torch}} unlit, {{id|block 76}} lit
- Translation key: `tile.notGate`

The item is the lit torch. Breaking either kind drops block 76.
<!-- src: BlockRedstoneTorch.java:143 idDropped -->
