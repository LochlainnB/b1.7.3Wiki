---
title: Smelting
description: The furnace, fuel, and every smelting recipe in Beta 1.7.3.
type: mechanic
categories: [Game mechanics]
---

**Smelting** converts one item into another using a [[Furnace]] and a fuel.
Unlike [[Crafting]], smelting takes time and consumes fuel as it runs.

## Using a furnace

A furnace has three slots: the item to smelt on top, the fuel below it, and the
result on the right. While it has both an input and burning fuel, the furnace
works through its input one item at a time and lights up.

Every smelt takes the same **200 ticks — 10 seconds** — whatever is being
smelted.
<!-- src: TileEntityFurnace.java:128 updateEntity -->

A furnace only draws a new piece of fuel when there is something it can smelt,
so an idle furnace never burns anything. Once a piece is alight, though, it
burns to the end regardless: taking the input out part-way through wastes
whatever is left of it.
<!-- src: TileEntityFurnace.java:113 updateEntity -->

Progress is not banked. If the fuel runs out mid-item, or the input is removed,
or the output slot fills up, the progress bar drops to empty and that item
starts again from the beginning.
<!-- src: TileEntityFurnace.java:134 updateEntity -->

## Fuel

| Fuel | Burns for | Items smelted |
|---|---|---|
| {{sprite\|Lava bucket}} | 20000 ticks (16m 40s) | 100 |
| {{sprite\|Coal}} or charcoal | 1600 ticks (1m 20s) | 8 |
| Any block made of wood | 300 ticks (15s) | 1.5 |
| {{sprite\|Stick}} or {{sprite\|Sapling}} | 100 ticks (5s) | 0.5 |

<!-- src: TileEntityFurnace.java:185 getItemBurnTime -->

Nothing else burns. An item that is not on this list leaves the furnace unlit.

A lava bucket is consumed whole, [[Bucket|bucket]] and all — the furnace
decrements the fuel stack and returns nothing, so burning one costs the
container as well as the lava.
<!-- src: TileEntityFurnace.java:118 updateEntity; the furnace never calls
     getContainerItem, which only applies to crafting -->

Charcoal is the same item as coal and burns for exactly as long.

The blocks that count as wood are [[Wooden Planks]], [[Wood]] logs,
[[Wooden Stairs]], [[Fence]], [[Trapdoor]], [[Crafting Table]], [[Chest]],
[[Bookshelf]], [[Jukebox]], [[Note Block]] and the wooden [[Pressure Plate]].
Each burns for the same 300 ticks no matter what it cost to make, so what a
piece of wood is worth as fuel depends entirely on how it is cut. One [[Wood]]
log crafts into four [[Wooden Planks]], which quadruples its fuel value from 300
ticks to 1200. Going any further loses: four planks make one
[[Crafting Table]], turning 1200 ticks of fuel into 300.

Sticks are worse still. Two planks yield four sticks, trading 600 ticks for 400,
and the six sticks a [[Fence]] costs would have burned for exactly as long as
the two fences they make.

Wooden doors and signs are the exception: the furnace tests the item's id
against the block list, and both exist only as items once they are in an
inventory, so neither burns.
<!-- src: TileEntityFurnace.java:190 getItemBurnTime, the var2 < 256 test -->

## Smelting recipes

{{recipe list|type=smelting}}

## See also

- [[Crafting]]
- [[Furnace]]
- [[Coal]]
