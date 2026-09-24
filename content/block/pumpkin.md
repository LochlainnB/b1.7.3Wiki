---
title: Pumpkin
description: A carved orange block found in patches on grass, crafted into a jack 'o' lantern and worn in the helmet slot.
type: block
categories: [Blocks, Plants, Naturally generated]
---

**Pumpkin** is an orange block with a carved face, found in patches on
[[Grass|grass]].

## Obtaining

### Natural generation

One chunk in 32 gets a [[World Generation#Population|patch]] of pumpkins, in
every biome. Pumpkins generate only on [[Grass|grass]], each facing a random
way.
<!-- src: ChunkProviderGenerate.java:555-:560 populate, with no biome test;
     WorldGenPumpkin.java:11 the grass test, :12 random metadata 0 to 3 -->

### Breaking

Breaking a pumpkin drops it, whatever breaks it.
<!-- src: BlockPumpkin keeps Block's idDropped and quantityDropped;
     Material.java:133 pumpkin needs no tool -->

## Usage

### Crafting ingredient

{{used in|Pumpkin}}

### Wearing

A pumpkin can be worn in the helmet slot. It gives no
[[Damage#Armour|armour]] points and takes no wear. In first-person view, a worn
pumpkin draws its carved face over the screen.
<!-- src: SlotArmor.java:22 isItemValid; InventoryPlayer.java:290
     getTotalArmorValue and :310 damageArmor count only ItemArmor;
     GuiIngame.java:39 renderPumpkinBlur -->

## Behaviour

### Placement

A pumpkin is placed with its face towards the player, and only on top of a
full, solid, opaque block. It stays where it is if that block is removed.
<!-- src: BlockPumpkin.java:55 onBlockPlacedBy; :50 canPlaceBlockAt tests
     World.isBlockNormalCube below; there is no onNeighborBlockChange -->

## Data values

- Block ID: {{id|Pumpkin}}
- Metadata: facing, 0 +z, 1 −x, 2 −z, 3 +x
- Translation key: `tile.pumpkin`

<!-- src: BlockPumpkin.java:24-:31, which side draws the face for each
     metadata -->
