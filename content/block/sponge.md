---
title: Sponge
description: A block that is never generated or crafted, and absorbs no water.
type: block
categories: [Blocks, Building blocks]
---

**Sponge** is a block that cannot be obtained in survival play.

## Obtaining

No world generator places sponge, and no recipe makes it. A server operator can
hand it out with the `give` command.
<!-- src: no generator references Block.sponge, and data/recipes.json has no
     recipe for block 19; minecraft_server ConsoleCommandHandler.java:133 give
     accepts any id with an item, and Block.java:699 gives every block one -->

### Breaking

Sponge drops itself, whatever breaks it.
<!-- src: Material.java:120 sponge is harvestable; Block.idDropped returns the
     block's own id -->

## Usage

Sponge absorbs no water.
<!-- src: BlockSponge.java:9 onBlockAdded looks for water in the 5 x 5 x 5
     cube around it and does nothing with what it finds; :23 onBlockRemoval
     only sends neighbour updates through the same cube -->

## Data values

- Block ID: {{id|Sponge}}
- Translation key: `tile.sponge`
