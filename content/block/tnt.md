---
title: TNT
description: An explosive block, lit by redstone power, flint and steel, fire or another explosion, that blows up when its fuse runs out.
type: block
aliases: [Primed TNT, PrimedTnt]
categories: [Blocks, Redstone]
---

**TNT** is a block that, once lit, explodes when its fuse runs out.

## Obtaining

### Crafting

{{crafting|TNT}}

### Breaking

Breaking TNT drops it, unless the player is holding
[[Flint and Steel|flint and steel]], which lights it instead.
<!-- src: BlockTNT.java:35 quantityDropped 0; :45 onBlockDestroyedByPlayer drops
     it explicitly when metadata bit 1 is clear -->

## Usage

### Lighting

Lit TNT becomes an entity. Its fuse depends on what lit it:

| Lit by | Fuse |
|---|---|
| A player hitting it with {{sprite\|Flint and Steel\|text=flint and steel}} | 80 ticks (4 seconds) |
| [[Redstone Power\|Redstone power]] | 80 ticks |
| [[Fire#Burning\|Fire]] that catches it | 80 ticks |
| An [[Explosion\|explosion]] that reaches it | 10 to 29 ticks |

<!-- src: BlockTNT.java:58 onBlockClicked sets bit 1, and :50 primes it;
     BlockFire.java:131; BlockTNT.java:39 onBlockDestroyedByExplosion,
     nextInt(20) + 10; EntityTNTPrimed.java:21 fuse = 80 -->

Lighting TNT costs the flint and steel no durability.
<!-- src: ItemFlintAndSteel does not override Item.java:201 onBlockDestroyed -->

TNT lights when it is [[Redstone Power#Blocks that respond|powered]]. It checks
when it is placed, and when a [[Lever|lever]], [[Button|button]],
[[Pressure Plate|pressure plate]], [[Redstone Torch|redstone torch]],
[[Redstone Dust|redstone dust]] or [[Detector Rail|detector rail]] beside it
changes. A [[Redstone Repeater|repeater]] switching beside it goes unnoticed.
<!-- src: BlockTNT.java:18 onBlockAdded, :27 onNeighborBlockChange, which
     tests canProvidePower on the changed block. That returns true only for
     BlockLever, BlockButton, BlockPressurePlate, BlockRedstoneTorch,
     BlockRedstoneWire and BlockDetectorRail; BlockRedstoneRepeater.java:127
     returns false -->

## Behaviour

### Lit TNT

Lit TNT is thrown upward at 0.2 blocks a tick, with a push of 0.02 blocks a
tick to the north. It then falls, and slides to a stop on the ground. An
explosion throws lit TNT without destroying it.
<!-- src: EntityTNTPrimed.java:17-:20, where an angle in radians is read as
     degrees, so the push always points within 7 degrees of north (-z); :38
     onUpdate; it does not override Entity.java:746 attackEntityFrom, so
     Explosion.java:92-:103 only adds knockback -->

Lit TNT explodes with a size of 4. The [[Explosion#Sizes|explosion]] breaks
blocks with a blast resistance below 15.5, deals 65 damage at its centre, and
sets no fire.
<!-- src: EntityTNTPrimed.java:66 explode, createExplosion with no fire -->

## Data values

- Block ID: {{id|TNT}}
- Entity network ID: {{id|PrimedTnt}}
- Translation key: `tile.tnt`
