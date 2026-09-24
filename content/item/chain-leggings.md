---
title: Chain Leggings
description: The leggings made from fire, unobtainable in singleplayer.
type: item
categories: [Items, Armour]
---

**Chain Leggings** are the [[Damage#Armour|leggings]] made from
[[Fire|fire]].

## Obtaining

Chain leggings cannot be obtained in singleplayer. Their recipe calls for
[[Fire|fire]], which cannot be collected. No mob drops chain leggings, and no
chest holds them.
<!-- src: RecipesArmor.java:8 gives chain Block.fire as its material;
     BlockFire.java:47 quantityDropped returns 0; legsChain is named only at
     Item.java:322 and RecipesArmor.java:8, so no drop or loot names it -->

On a server, an operator's `give` command can hand a player chain leggings, or
fire to craft them from.
<!-- src: minecraft_server ConsoleCommandHandler.java:133 give takes a player and
     any id in Item.itemsList, and Block.java:646 gives fire an
     ItemBlock; NetServerHandler.java:428 runs an operator's slash command -->

### Crafting

{{crafting|Chain Leggings}}

## Usage

Chain leggings are worn in the third armour slot. They give 6
[[Damage#Armour|armour points]].
<!-- src: Item.java:322 armorType 2; ItemArmor.java:4 damageReduceAmountArray
     {3, 8, 6, 3}; ContainerPlayer.java:28 puts armour slot n at y = 8 + n * 18,
     and SlotArmor.java:19 accepts only the matching armorType there -->

## Data values

- Item ID: {{id|Chain Leggings}}
- Translation key: `item.leggingsChain`
