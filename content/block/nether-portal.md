---
title: Nether Portal
description: The block that fills a lit obsidian frame and carries a player between the Overworld and the Nether.
type: block
subject: Portal
aliases: [Portal]
categories: [Blocks]
---

**Nether Portal** is the block that fills a lit [[Obsidian|obsidian]] frame and
carries a player between the [[Overworld]] and the [[Nether]].

## Obtaining

The block has no item form and cannot be mined or crafted. It appears when a
frame is lit, and when the game builds a portal for an arriving player.

### Building a portal

The frame is obsidian around an upright space 2 blocks wide and 3 tall. Ten
blocks of obsidian are enough, because the corners are not needed. The frame
must run along one horizontal axis. Fire with obsidian beside it along both
axes lights nothing.
<!-- src: BlockPortal.java:37 tryToCreatePortal, whose loop skips the corner
     positions and whose first test rejects a block with obsidian on both axes -->

Setting [[Fire|fire]] on the obsidian floor inside the frame fills it with portal
blocks. [[Flint and Steel]] places the fire.
<!-- src: BlockFire.java:191 onBlockAdded, which runs the frame check whenever a
     fire block appears with obsidian below it -->

No other size works. A portal block survives only in a column exactly 3 tall
closed by obsidian above and below, paired side by side with one other such
column. Breaking any part of the frame removes the whole portal.
<!-- src: BlockPortal.java:87 onNeighborBlockChange -->

## Usage

### Travelling

Standing in a portal for 80 ticks — 4 seconds — moves the player. Stepping out
drains that progress four times faster than it builds, emptying in 20 ticks.
After a trip the player must stay clear of a portal for 10 ticks before another
will take them. The view warps and a purple overlay fades in as the progress
builds.
<!-- src: EntityPlayerSP.java:53 and EntityPlayerMP.java:161, both adding 0.0125
     a tick and subtracting 0.05; EntityRenderer.java:289, GuiIngame.java:43;
     EntityPlayer.java:811 setInPortal holds timeUntilPortal at 10 for as long as
     the player stands in one -->

The player's x and z are divided by 8 on the way into the Nether and multiplied
by 8 on the way out. The y is unchanged.
<!-- src: Minecraft.java:1213 usePortal;
     ServerConfigurationManager.java:171 sendPlayerToOtherDimension -->

Only players travel. A mob or a dropped item standing in a portal is not moved,
and neither is a player riding a [[Boat|boat]] or [[Minecart|minecart]].
<!-- src: Entity.java:1038 setInPortal is empty and only EntityPlayer overrides
     it; BlockPortal.java:150 onEntityCollidedWithBlock -->

On a server, setting `allow-nether` to false stops portals working.
<!-- src: EntityPlayerMP.java:153 -->

### Arriving

At the far end the game looks for a portal block within 128 blocks in x and z at
any height, and puts the player at the closest one.
<!-- src: Teleporter.java:15 func_4106_b -->

Finding none, it builds one. It looks within 16 blocks for solid ground under a
clear space 3 wide, 4 long and 4 tall, then for a space 1 wide, and builds at
the closest spot found. Failing both, it carves out a platform at a height
clamped to between y=70 and y=118. A portal the game builds has the full frame,
corners included.
<!-- src: Teleporter.java:78 func_4108_c -->

## Behaviour

Players and mobs walk through the block.
<!-- src: BlockPortal.java:10 getCollisionBoundingBoxFromPool returns null -->

No tool breaks the block, and it drops nothing. An explosion destroys it, and
the rest of the portal with it.
<!-- src: BlockPortal.java:142 quantityDropped, Block.java:682 setHardness(-1.0F)
     leaving the blast resistance at 0; Explosion.java:61 -->

The block gives off purple particles and plays an ambient sound at random.
<!-- src: BlockPortal.java:157 randomDisplayTick -->

## Data values

- Block ID: {{id|Portal}}
- Translation key: `tile.portal`

The game names the block *Portal*.
