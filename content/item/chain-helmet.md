---
title: Chain Helmet
description: The helmet made from fire, unobtainable in singleplayer.
type: item
categories: [Items, Armour]
---

**Chain Helmet** is the [[Damage#Armour|helmet]] made from
[[Fire|fire]].

## Obtaining

A chain helmet cannot be obtained in singleplayer. Its recipe calls for
[[Fire|fire]], which cannot be collected. No mob drops a chain helmet, and no
chest holds one.
<!-- src: RecipesArmor.java:8 gives chain Block.fire as its material;
     BlockFire.java:47 quantityDropped returns 0; helmetChain is named only at
     Item.java:320 and RecipesArmor.java:8, so no drop or loot names it -->

On a server, an operator's `give` command can hand a player a chain helmet, or
fire to craft one from.
<!-- src: minecraft_server ConsoleCommandHandler.java:133 give takes a player and
     any id in Item.itemsList, and Block.java:646 gives fire an
     ItemBlock; NetServerHandler.java:428 runs an operator's slash command -->

### Crafting

{{crafting|Chain Helmet}}

## Usage

A chain helmet is worn in the top armour slot. It gives 3
[[Damage#Armour|armour points]].
<!-- src: Item.java:320 armorType 0; ItemArmor.java:4 damageReduceAmountArray
     {3, 8, 6, 3}; ContainerPlayer.java:28 puts armour slot n at y = 8 + n * 18,
     and SlotArmor.java:19 accepts only the matching armorType there -->

## Data values

- Item ID: {{id|Chain Helmet}}
- Translation key: `item.helmetChain`
