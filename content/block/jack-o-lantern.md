---
title: Jack 'o' Lantern
description: A pumpkin crafted with a torch, which gives off light.
type: block
categories: [Blocks]
---

**Jack 'o' Lantern** is a [[Pumpkin|pumpkin]] with a [[Torch|torch]] inside,
which gives off [[Light#Block light|light]].
<!-- src: Block.java:683 setLightValue(1.0F) -->

## Obtaining

### Crafting

{{crafting|Jack 'o' Lantern}}

### Breaking

Breaking a jack 'o' lantern drops it, whatever breaks it.
<!-- src: BlockPumpkin keeps Block's idDropped and quantityDropped;
     Material.java:133 pumpkin needs no tool -->

## Behaviour

A jack 'o' lantern is [[Pumpkin#Placement|placed]] as a pumpkin is.
<!-- src: Block.java:678, :683 both are BlockPumpkin -->

It cannot be worn, as a pumpkin can.
<!-- src: SlotArmor.java:22 accepts Block.pumpkin's id only -->

## Data values

- Block ID: {{id|Jack 'o' Lantern}}
- Metadata: facing, 0 +z, 1 −x, 2 −z, 3 +x
- Translation key: `tile.litpumpkin`
