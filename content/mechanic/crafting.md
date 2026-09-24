---
title: Crafting
description: How the crafting grid works in Beta 1.7.3, and every recipe in the game.
type: mechanic
categories: [Game mechanics]
---

**Crafting** turns items into other items by arranging them in a grid. Every
recipe on this page is read directly from the Beta 1.7.3 client, so the grids
below are exactly what the game accepts.

## The grid

Two grids are available:

- The **2×2 grid** in the player's inventory, always available.
- The **3×3 grid** of the [[Crafting Table]], which is needed for anything
  larger than 2×2.

A recipe is either *shaped* or *shapeless*. A shaped recipe cares where the
ingredients sit relative to one another, though not where the shape sits in the
grid: a 2×2 shape works in any corner of a 3×3 table. A shapeless recipe only
cares which items are present.

A block named as an ingredient matches every kind of it, so any colour of
[[Wool|wool]] makes a [[Bed|bed]] and any [[Wood|wood]] makes planks. A recipe
that names one kind takes that kind alone: [[Dye|dyeing]] wool takes white wool.
<!-- src: CraftingManager.java:115 new ItemStack(block, 1, -1), a damage of -1
     matching any in ShapedRecipes.java:62 and ShapelessRecipes.java:32;
     RecipesDyes.java:6 names wool at damage 0 -->

Closing either grid drops whatever is left in it.
<!-- src: ContainerPlayer.java:48 and ContainerWorkbench.java:43
     onCraftGuiClosed -->

## All recipes

{{recipe list}}

## See also

- [[Crafting Table]]
