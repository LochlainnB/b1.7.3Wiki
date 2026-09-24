---
title: Coal
description: The fuel dropped by coal ore, and charcoal, the same item smelted from wood.
type: item
categories: [Items, Materials]
---

**Coal** is the fuel item dropped by [[Coal Ore|coal ore]].

## Obtaining

### Breaking

[[Coal Ore|Coal ore]] drops one coal when [[Mining#Harvest levels|mined]] with
any pickaxe.
<!-- src: BlockOre.java:10-22 idDropped, quantityDropped -->

### Smelting

Smelting [[Wood|wood]] gives charcoal, a second kind of coal. Charcoal looks the
same as coal, but the two do not stack together.
<!-- src: FurnaceRecipes.java:24, coal at damage 1; Item.java:147
     getIconFromDamage, which ItemCoal does not override; ItemCoal.java:6
     setHasSubtypes; InventoryPlayer.java:31 storeItemStack compares damage
     for items with subtypes -->

{{smelting|Coal}}

## Usage

### Fuel

Coal and charcoal each burn in a [[Smelting#Fuel|furnace]] for 1600 ticks
(80 seconds), long enough to smelt 8 items.
<!-- src: TileEntityFurnace.java:194 getItemBurnTime, which tests the item id
     alone -->

Using coal or charcoal on a [[Minecart with Furnace|minecart with furnace]]
consumes one and fuels the minecart.
<!-- src: EntityMinecart.java:778-783 interact, which tests the item id alone -->

### Crafting ingredient

{{used in|Coal}}

## Data values

- Item ID: {{id|Coal}}, {{id|Charcoal}} charcoal
- Translation key: `item.coal`, `item.charcoal`
