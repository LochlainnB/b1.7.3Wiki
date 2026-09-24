---
title: Map
description: An item that draws the land around the player holding it, seen from above, in a 1024-block square centred where it was crafted.
type: item
categories: [Items, Tools]
---

**Map** is an item that draws the land around the player holding it, seen from
above.

## Obtaining

### Crafting

{{crafting|Map}}

Each map crafted is a new, blank map with the next number, starting from 0. It
is centred on the block where the crafter stands, in the crafter's dimension.
<!-- src: ItemMap.java:228 onCreated: getUniqueDataId("map") (MapStorage.java:133),
     xCenter and zCenter the floor of posX and posZ, dimension the world's
     worldType -->

Taking a map from the [[Crafting Table|crafting table]] with shift-click gives
map 0, the first map made in the world, instead of a new one.
<!-- src: ContainerWorkbench.java:71 mergeItemStack puts a copy of the result,
     still at damage 0, into the inventory (Container.java:236); :90
     onPickupFromSlot then runs onCreated on the original, which is discarded.
     The server does the same: minecraft_server ContainerWorkbench.java:71-:90 -->

## Usage

### Drawing

A map is 128 × 128 pixels, and each pixel covers 8 × 8 blocks.
<!-- src: MapData.java:13 colors, 128 x 128; ItemMap.java:235 scale 3, and
     :44 1 << scale blocks a pixel -->

A map fills in only while it is held, and only in the dimension it was made in.
It redraws everything within 128 blocks of the holder every 16
[[Game Tick|ticks]]. Areas never drawn stay blank.
<!-- src: InventoryPlayer.java:113 passes currentItem == slot, and
     ItemMap.java:221 draws only then; :41 the dimension test; :49 a radius of
     128 / 8 = 16 pixels; :57 (x & 15) == (step & 15); MapItemRenderer.java:27
     draws colour 0 clear -->

### What a map shows

Each pixel shows the most common top block in its 8 × 8 area, in the colour of
what that block is made of:

| Colour | Blocks |
|---|---|
| Light green | [[Grass]] |
| Dark green | [[Leaves]], [[Cactus]], [[Pumpkin\|pumpkins]], [[Jack 'o' Lantern\|jack 'o' lanterns]] and every other plant |
| Pale yellow | [[Sand]], [[Gravel]], [[Soul Sand]] |
| Brown | [[Dirt]], [[Farmland]] |
| Dark brown | [[Wood]], [[Wooden Planks]] and every other wooden block but the slab |
| Grey | [[Stone]], [[Cobblestone]], [[Moss Stone]], [[Bedrock]], [[Obsidian]], [[Bricks]], [[Sandstone]], [[Netherrack]], [[Glowstone]], the ores, [[Lapis Lazuli Block]], every [[Stone Slab\|slab]], [[Stone Stairs]], [[Furnace\|furnaces]], [[Dispenser\|dispensers]], [[Monster Spawner\|monster spawners]], the stone [[Pressure Plate\|pressure plate]] and [[Piston\|pistons]] |
| Light grey | [[Wool]], [[Bed\|beds]], [[Sponge]], [[Cobweb]], [[Iron Door\|iron doors]] and the blocks of [[Block of Iron\|iron]], [[Block of Gold\|gold]] and [[Block of Diamond\|diamond]] |
| Blue-grey | [[Clay]] |
| White | [[Snow]] |
| Pale blue | [[Ice]] |
| Blue | [[Water]] |
| Red | [[Lava]], [[TNT]] |

<!-- src: ItemMap.java:96-:155 counts the top block of each column in the 8 x 8
     area and keeps the most common; :169 its material's materialMapColor.
     MapColor.java:6-:18 grass 7FB238, foliage 007C00, sand F7E9A3, dirt B76A2F,
     wood 685332, stone 707070, cloth and iron A7A7A7, clay A4A8B8, snow FFFFFF,
     ice A0A0FF, water 4040FF, tnt FF0000. Material.java:110-:137 gives each
     material its colour; Block.java:592-:688 and the Block classes give each
     block its material. Glowstone is Material.rock (Block.java:681); every
     BlockStep, the wooden slab included, is rock (BlockStep.java:10). -->

Glass, torches, [[Redstone Dust|redstone]], [[Redstone Repeater|repeaters]],
rails, ladders, levers, buttons, fire, portals and cake are not drawn. The map
shows the block beneath them.
<!-- src: ItemMap.java:106-:116 passes over blocks whose material's colour is
     MapColor.airColor: glass, circuits, fire, portal and cakeMaterial
     (Material.java:122-:135) -->

A pixel is drawn lighter where its ground is higher than in the pixel above it
on the map, and darker where it is lower. [[Water]] is shaded by depth instead,
and deep water is darker.
<!-- src: ItemMap.java:157-:165 compares the area's average height with the
     previous row's (var15): lighter above +0.6, darker below -0.6, with a
     +-0.2 checkerboard; :170-:180 water uses the count of liquid blocks under
     the surface. The top of the map is -z: MapItemRenderer.java:99 writes the
     name upright at pixel (0, 0). -->

### Markers

A white marker shows where the player carrying the map stands and which way
they face. It disappears while that player is outside the map's area or in
another dimension.
<!-- src: MapData.java:71 updateVisiblePlayers: players whose inventory holds
     the map (:82), within 64 map pixels of the centre (:87), in the map's
     dimension (:97); facing in 16 steps of rotationYaw (:91);
     MapItemRenderer.java:73 icon 0 of misc/mapicons.png -->

The map's name, such as `map_0`, is written in its top left corner.
<!-- src: MapItemRenderer.java:99 drawString(mapName), the "map_" + number of
     ItemMap.java:24 -->

### In the Nether

A map made in the [[Nether]] draws a fixed pattern of brown and grey that does
not follow the terrain, and only within 64 blocks of the holder. Its marker
points in random directions.
<!-- src: ItemMap.java:50 halves the radius where hasNoSky; :82-:94 picks dirt
     or stone from a hash of the pixel's coordinates; MapData.java:92 random
     rotation where the dimension is below 0 -->

## Data values

- Item ID: {{id|Map}}
- Translation key: `item.map`

A map's number is its damage value. Its picture is saved in the world folder as
`data/map_<number>.dat`.
<!-- src: ItemMap.java:24 "map_" + getItemDamage(); SaveHandler.java:23 the data
     folder, :167 getMapFile -->
