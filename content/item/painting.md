---
title: Painting
description: An item that hangs a randomly chosen picture, from 1×1 to 4×4 blocks, on the side of a block.
type: item
categories: [Items]
---

**Painting** is an item that hangs a picture on a wall.

## Obtaining

### Crafting

{{crafting|Painting}}

Any colour of [[Wool|wool]] can be used.
<!-- src: CraftingManager.java:66; :115 wraps a block ingredient with damage
     -1, which ShapedRecipes.java:62 matches against any damage -->

## Usage

### Hanging

A painting is hung on the side of a block. The game picks a picture at random
from those that fit there:

- every block behind the picture is solid;
- the space in front of it is clear;
- it overlaps no other painting.

If no picture fits, nothing is hung and the painting is not used up.
<!-- src: ItemPainting.java:9 refuses the top and bottom faces, :28 uses the
     item only when the choice fits; EntityPainting.java:22 collects every
     EnumArt that passes :145 onValidSurface and picks one with nextInt -->

### Pictures

| Size, in blocks | Pictures |
|---|---|
| 1 × 1 | Kebab, Aztec, Alban, Aztec2, Bomb, Plant, Wasteland |
| 2 × 1 | Pool, Courbet, Sea, Sunset, Creebet |
| 1 × 2 | Wanderer, Graham |
| 2 × 2 | Match, Bust, Stage, Void, SkullAndRoses |
| 4 × 2 | Fighters |
| 4 × 3 | Skeleton, DonkeyKong |
| 4 × 4 | Pointer, Pigscene, BurningSkull |

Sizes are width by height. The names are the ones the game saves; nothing in
the game shows them.
<!-- src: EnumArt.java:4-:28, sizes in pixels divided by 16;
     EntityPainting.java:216 writes the title as "Motive" -->

## Behaviour

A hung painting drops as an item when:

- it takes any damage, from a punch to an [[Explosion|explosion]];
- anything moves it, such as a [[Piston|piston]];
- a block behind it stops being solid, or a block is placed in front of it.

The last is checked about every 5 seconds.
<!-- src: EntityPainting.java:204 attackEntityFrom; :245 moveEntity and :253
     addVelocity; :134 onUpdate runs onValidSurface every 101 ticks;
     TileEntityPiston.java:84 moves entities in the piston's path -->

## Data values

- Item ID: {{id|Painting}}
- Entity network ID: {{id|entity 9}}
- Translation key: `item.painting`
