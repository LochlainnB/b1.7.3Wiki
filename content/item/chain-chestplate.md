---
title: Chain Chestplate
description: The chestplate made from fire, unobtainable in singleplayer.
type: item
categories: [Items, Armour]
---

**Chain Chestplate** is the [[Damage#Armour|chestplate]] made from
[[Fire|fire]].

## Obtaining

A chain chestplate cannot be obtained in singleplayer. Its recipe calls for
[[Fire|fire]], which cannot be collected. No mob drops a chain chestplate, and
no chest holds one.
<!-- src: RecipesArmor.java:8 gives chain Block.fire as its material;
     BlockFire.java:47 quantityDropped returns 0; plateChain is named only at
     Item.java:321 and RecipesArmor.java:8, so no drop or loot names it -->

On a server, an operator's `give` command can hand a player a chain chestplate,
or fire to craft one from.
<!-- src: minecraft_server ConsoleCommandHandler.java:133 give takes a player and
     any id in Item.itemsList, and Block.java:646 gives fire an
     ItemBlock; NetServerHandler.java:428 runs an operator's slash command -->

### Crafting

{{crafting|Chain Chestplate}}

## Usage

A chain chestplate is worn in the second armour slot. It gives 8
[[Damage#Armour|armour points]].
<!-- src: Item.java:321 armorType 1; ItemArmor.java:4 damageReduceAmountArray
     {3, 8, 6, 3}; ContainerPlayer.java:28 puts armour slot n at y = 8 + n * 18,
     and SlotArmor.java:19 accepts only the matching armorType there -->

## Data values

- Item ID: {{id|Chain Chestplate}}
- Translation key: `item.chestplateChain`
