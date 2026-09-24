---
title: Rail
description: A track laid on a solid block, which joins the rails beside it into straight lines, curves and slopes for minecarts to run along.
type: block
categories: [Blocks, Transportation, Redstone]
---

**Rail** is a track that [[Minecart|minecarts]] run along.

## Obtaining

### Crafting

{{crafting|Rail}}

## Usage

### Placing

A rail is placed on top of a full, solid block. It drops as an item when that
block goes.
<!-- src: BlockRail.java:74 canPlaceBlockAt, :94 onNeighborBlockChange -->

A sloped rail also drops when the block it rises against goes.
<!-- src: BlockRail.java:98-:112, the block level with the rail on its rising
     side, for metadata 2 to 5 -->

### Joining

A rail joins the rails on its four sides, including rails one block higher or
lower. It joins a rail that is already joined to it or has a free end, and
leaves alone a rail joined at both ends to others. Placing a rail bends a
neighbour with a free end to meet it.
<!-- src: RailLogic.java:93 getMinecartTrackLogic looks level, one up and one
     down; :146 handleKeyPress; :345-:352 reshapes each neighbour it joins
     through :159 func_788_d. The same rules serve all three rail blocks
     (BlockRail.java:8 isRailBlockAt) -->

| Joins | Shape |
|---|---|
| nothing | straight, north to south |
| one rail, or two on opposite sides | straight, toward them |
| two rails on adjacent sides | curved between them |

<!-- src: RailLogic.java:234 refreshTrackShape, :240-:264; :332 falls back to
     metadata 0, north to south -->

A straight rail slopes up to meet a rail one block higher at either end. A
curve never slopes.
<!-- src: RailLogic.java:312-:330 -->

Only a plain rail curves. A [[Powered Rail|powered rail]] or
[[Detector Rail|detector rail]] between rails on two axes lies east to west.
<!-- src: RailLogic.java:25 isPoweredRail, true for both; :248 skips the
     curves for them, and :266-:273 settles on east to west whenever a rail
     lies east or west -->

### Junctions

A rail between three rails curves.
[[Redstone Power#Blocks that respond|Redstone power]] decides which way:

| Rails beside it | Unpowered | Powered |
|---|---|---|
| north, south and east | south to east | north to east |
| north, south and west | south to west | north to west |
| east, west and south | south to east | south to west |
| east, west and north | north to east | north to west |

<!-- src: RailLogic.java:275-:308, where the last curve tested wins; the
     unpowered order puts south and east last, the powered order north and
     west -->

It switches when a power source beside it changes.
<!-- src: BlockRail.java:135 onNeighborBlockChange, gated on canProvidePower
     and on getNAdjacentTracks == 3 -->

A rail between four rails takes its curve when placed, south to east or, if
powered, north to west. It does not switch.
<!-- src: BlockRail.java:78 onBlockAdded passes the power state to
     refreshTrackShape; :135 switches only with exactly three rails beside it -->

## Data values

- Block ID: {{id|Rail}}
- Translation key: `tile.rail`
