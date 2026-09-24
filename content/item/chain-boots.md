---
title: Chain Boots
description: The boots made from fire, unobtainable in singleplayer.
type: item
categories: [Items, Armour]
---

**Chain Boots** are the [[Damage#Armour|boots]] made from
[[Fire|fire]].

## Obtaining

Chain boots cannot be obtained in singleplayer. Their recipe calls for
[[Fire|fire]], which cannot be collected. No mob drops chain boots, and no
chest holds them.
<!-- src: RecipesArmor.java:8 gives chain Block.fire as its material;
     BlockFire.java:47 quantityDropped returns 0; bootsChain is named only at
     Item.java:323 and RecipesArmor.java:8, so no drop or loot names it -->

On a server, an operator's `give` command can hand a player chain boots, or
fire to craft them from.
<!-- src: minecraft_server ConsoleCommandHandler.java:133 give takes a player and
     any id in Item.itemsList, and Block.java:646 gives fire an
     ItemBlock; NetServerHandler.java:428 runs an operator's slash command -->

### Crafting

{{crafting|Chain Boots}}

## Usage

Chain boots are worn in the bottom armour slot. They give 3
[[Damage#Armour|armour points]].
<!-- src: Item.java:323 armorType 3; ItemArmor.java:4 damageReduceAmountArray
     {3, 8, 6, 3}; ContainerPlayer.java:28 puts armour slot n at y = 8 + n * 18,
     and SlotArmor.java:19 accepts only the matching armorType there -->

## Data values

- Item ID: {{id|Chain Boots}}
- Translation key: `item.bootsChain`
