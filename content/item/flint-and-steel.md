---
title: Flint and Steel
description: A tool that sets fire to the space it is used on, and lights Nether portals and TNT.
type: item
categories: [Items, Tools]
---

**Flint and Steel** is a tool that sets [[Fire|fire]].

## Obtaining

### Crafting

{{crafting|Flint and Steel}}

## Usage

Flint and steel lights:

- [[Fire]], in the space against the face of the block it is used on, if that
  space is air. Fire set where it [[Fire#Where fire can stand|cannot stand]]
  goes out at once.
- A [[Nether Portal#Building a portal|Nether portal]], when that fire is set on
  the [[Obsidian|obsidian]] floor of a finished frame.
- [[TNT]], when the TNT is hit with flint and steel in hand.

<!-- src: ItemFlintAndSteel.java:10-:39 onItemUse; BlockFire.java:191
     onBlockAdded, which tries the portal first and removes fire that cannot
     stand; BlockTNT.java:58 onBlockClicked marks TNT hit with flint and steel,
     and :45 onBlockDestroyedByPlayer primes marked TNT. TNT has hardness 0, so
     the same click breaks it (PlayerControllerSP.java:50) -->

Each use on a block costs 1 [[Durability|durability]], whether or not a fire is
lit. Lighting TNT by hitting it costs nothing.
<!-- src: ItemFlintAndSteel.java:41 damageItem(1), outside the air test;
     Item.java:201 onBlockDestroyed does not damage the item -->

## Data values

- Item ID: {{id|Flint and Steel}}
- Translation key: `item.flintAndSteel`
