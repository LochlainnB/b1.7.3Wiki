---
title: Dye
description: An item in sixteen colours, crafted from flowers and other dyes or smelted from cactus, that colours wool and sheep.
type: item
sprite: Rose Red
categories: [Items]
---

**Dye** is an item in sixteen colours, used to colour [[Wool|wool]] and
[[Sheep|sheep]].

## Obtaining

Four dyes come from sources of their own:

- [[Ink Sac|Ink sacs]], the black dye, drop from [[Squid|squid]].
- [[Cocoa Beans|Cocoa beans]], the brown dye, are found in
  [[Dungeon|dungeon]] chests.
- [[Lapis Lazuli|Lapis lazuli]], the blue dye, drops from
  [[Lapis Lazuli Ore|lapis lazuli ore]].
- [[Bone Meal|Bone meal]], the white dye, is crafted from [[Bone|bones]].

The other twelve are crafted or smelted.

### Crafting

{{crafting|Dye}}

### Smelting

{{smelting|Dye}}

## Usage

### Dyeing sheep

Using a dye on an unsheared [[Sheep|sheep]] turns its fleece the dye's colour,
and uses up the dye. On a sheared sheep, or one already that colour, a dye does
nothing and is not used up.
<!-- src: ItemDye.java:80-:88 saddleEntity, reached through
     EntityPlayer.java:456 useCurrentItemOnEntity because EntitySheep.java:34
     interact returns false; BlockCloth.java:21 getBlockFromDye -->

### Dyeing wool

A dye crafted with a block of white [[Wool|wool]] makes one wool of the dye's
colour. Wool of any other colour cannot be dyed.
<!-- src: RecipesDyes.java:6, whose wool ingredient is damage 0;
     ShapelessRecipes.java:32 compares the damage -->

### Crafting ingredient

{{used in|Dye}}

## Data values

- Item ID: {{id|Rose Red}} rose red, {{id|Cactus Green}} cactus green,
  {{id|Purple Dye}} purple, {{id|Cyan Dye}} cyan, {{id|Light Gray Dye}} light
  gray, {{id|Gray Dye}} gray, {{id|Pink Dye}} pink, {{id|Lime Dye}} lime,
  {{id|Dandelion Yellow}} dandelion yellow, {{id|Light Blue Dye}} light blue,
  {{id|Magenta Dye}} magenta, {{id|Orange Dye}} orange
- Translation key: `item.dyePowder.red`, `item.dyePowder.green`,
  `item.dyePowder.purple`, `item.dyePowder.cyan`, `item.dyePowder.silver`,
  `item.dyePowder.gray`, `item.dyePowder.pink`, `item.dyePowder.lime`,
  `item.dyePowder.yellow`, `item.dyePowder.lightBlue`,
  `item.dyePowder.magenta`, `item.dyePowder.orange`

The game names each colour, and has no name for the item as a whole.
<!-- src: lang/en_US.lang in the client jar has item.dyePowder.<colour>.name
     for all sixteen and no item.dyePowder.name; ItemDye.java:17
     getItemNameIS always appends the colour -->
