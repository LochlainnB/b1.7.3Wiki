---
title: Durability
description: How much use a tool, weapon or piece of armour takes before it breaks, and why each lasts one use more than its durability.
type: mechanic
categories: [Game mechanics]
---

**Durability** is how much use an item can take before it breaks.

## Breaking

Each use costs an item durability. The item breaks once the total cost passes
its durability, not when it reaches it.
<!-- src: ItemStack.java:124 damageItem; the test at :127 is
     itemDamage > getMaxDamage(), so an item survives at exactly its maximum -->

An item costing 1 per use lasts one use more than its durability. A
[[Wooden Pickaxe|wooden pickaxe]] has a durability of 59 and breaks on the 60th
block.

An item costing more per use lasts its durability divided by the cost, rounded
down, plus one.

The use that breaks an item still takes effect. The block still breaks, the hit
still lands, and armour still reduces the damage that breaks it.
<!-- src: PlayerControllerSP.java:25 removes the block and :27 settles the
     drop before :29 wears the tool; EntityPlayer.java:495 attackEntityFrom
     before :498 hitEntity; EntityPlayer.java:440 works out the reduction
     before :442 damageArmor -->

A broken item disappears. Nothing repairs a worn one.
<!-- src: ItemStack.java:132 takes the item off the stack;
     EntityPlayer.java:501 destroyCurrentEquippedItem, InventoryPlayer.java:314
     for armour. No recipe in CraftingManager reads item damage. -->

## What costs durability

| Item | Cost |
|---|---|
| Pickaxe, axe, shovel | 1 per block [[Mining#Tool wear\|broken]], 2 per [[Damage#Weapons\|hit]] |
| Sword | 1 per hit, 2 per block broken |
| Hoe | 1 per block [[Farmland#Obtaining\|tilled]] |
| [[Shears]] | 1 per [[Leaves\|leaf block]] or [[Cobweb\|cobweb]] broken, 1 per [[Sheep\|sheep]] sheared |
| [[Flint and Steel\|Flint and steel]] | 1 per use |
| [[Fishing Rod\|Fishing rod]] | 1 for a fish, 2 with the bobber in a block, 3 with an entity hooked, 0 otherwise |
| Helmet, chestplate, leggings, boots | the damage taken, before [[Damage#Armour\|armour]] reduces it |

<!-- src: ItemTool.java:30 and :35; ItemSword.java:18 and :23; ItemHoe.java:22;
     ItemShears.java:10 and EntitySheep.java:49; ItemFlintAndSteel.java:41;
     ItemFishingRod.java:21 costs what EntityFish.java:345 catchFish returns;
     EntityPlayer.java:442 damageArmor -->
