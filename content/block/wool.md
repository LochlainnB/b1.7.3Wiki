---
title: Wool
description: A block in sixteen colours, sheared from sheep or crafted from string, and coloured with dye.
type: block
categories: [Blocks, Building blocks]
---

**Wool** is a block in sixteen colours, sheared from [[Sheep|sheep]] or crafted
from [[String|string]].

## Obtaining

### Sheep

[[Sheep#Drops|Sheep]] give wool of their fleece colour when sheared, and when
killed unsheared.
<!-- src: EntitySheep.java:34 interact; :23 dropFewItems -->

### Crafting

{{crafting|Wool}}

Only white wool can be [[Dye#Dyeing wool|dyed]].
<!-- src: RecipesDyes.java:6, whose wool ingredient is damage 0;
     ShapelessRecipes.java:32 compares the damage -->

### Breaking

Wool drops itself, in its own colour, whatever breaks it. [[Shears]] break it
five times as fast as a hand.
<!-- src: BlockCloth.java:17 damageDropped; Material.java:121 cloth is not
     setNoHarvest; ItemShears.java:22 getStrVsBlock returns 5 for cloth -->

## Usage

### Crafting ingredient

{{used in|Wool}}

A [[Bed|bed]] or [[Painting|painting]] takes wool of any colour.
<!-- src: CraftingManager.java:115 gives a Block ingredient damage -1;
     ShapedRecipes.java:62 accepts any damage for -1 -->

## Behaviour

Wool [[Fire#Flammable blocks|burns]].
<!-- src: BlockFire.java:23 setBurnRate(cloth, 30, 60) -->

## Data values

- Block ID: {{id|Wool}}
- Metadata: 0 white, 1 orange, 2 magenta, 3 light blue, 4 yellow, 5 lime,
  6 pink, 7 gray, 8 light gray, 9 cyan, 10 purple, 11 blue, 12 brown, 13 green,
  14 red, 15 black
- Translation key: `tile.cloth`; by colour `tile.cloth.white`,
  `tile.cloth.orange`, `tile.cloth.magenta`, `tile.cloth.lightBlue`,
  `tile.cloth.yellow`, `tile.cloth.lime`, `tile.cloth.pink`, `tile.cloth.gray`,
  `tile.cloth.silver`, `tile.cloth.cyan`, `tile.cloth.purple`,
  `tile.cloth.blue`, `tile.cloth.brown`, `tile.cloth.green`, `tile.cloth.red`,
  `tile.cloth.black`

The game names white wool *Wool*.
<!-- src: lang/en_US.lang in the client jar, tile.cloth.white.name=Wool;
     ItemCloth.java:18 getItemNameIS -->
