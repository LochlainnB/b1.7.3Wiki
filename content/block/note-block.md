---
title: Note Block
description: A wooden block that plays one of 25 pitches when hit, used or powered, with an instrument set by the block beneath it.
type: block
categories: [Blocks, Utility blocks, Redstone]
---

**Note Block** is a wooden block that plays a note.

## Obtaining

### Crafting

{{crafting|Note Block}}

### Breaking

A note block drops itself when broken with anything. An axe is not
[[Mining#What each tool is effective against|effective against]] it.
<!-- src: BlockNote.java:5 Material.wood, which needs no tool; ItemAxe.java:11
     blocksEffectiveAgainst has no note block -->

## Usage

### Playing

A note block plays its note when a player hits it or uses it. Using it raises
the pitch first.
<!-- src: BlockNote.java:38 onBlockClicked; :27 blockActivated calls
     changePitch before triggerNote -->

A note block also plays once each time it becomes a
[[Redstone Power#Powered blocks|powered block]], strongly or weakly. A powered
block beside it does not play it.
<!-- src: BlockNote.java:12 onNeighborBlockChange reads isBlockGettingPowered,
     the power a solid block in its place would receive, and plays on the
     change from unpowered to powered -->

It plays only when the space above it is empty. The note can be heard up to 48
blocks away.
<!-- src: TileEntityNote.java:31 triggerNote, Material.air above;
     BlockNote.java:68 volume 3.0, which RenderGlobal.java:1264 and
     SoundManager.java:163 turn into 16 * 3 blocks -->

### Pitch

A note block has 25 pitches, two octaves. Each use raises the pitch by a
semitone, and a use at the highest returns it to the lowest.
<!-- src: TileEntityNote.java:26 changePitch, (note + 1) % 25;
     BlockNote.java:50 pitch 2^((note - 12) / 12), from half to double speed -->

### Instrument

The block beneath a note block sets its instrument:

| Block beneath | Instrument |
|---|---|
| [[Stone\|stone]], [[Cobblestone\|cobblestone]] and every other [[Mining#Drops\|rock]] block | bass drum |
| [[Sand\|sand]], [[Gravel\|gravel]], [[Soul Sand\|soul sand]] | snare drum |
| [[Glass\|glass]] | hi-hat |
| [[Wooden Planks\|planks]], [[Wood\|wood]] and every other wooden block | bass |
| anything else | harp |

<!-- src: TileEntityNote.java:32-:48 reads the material beneath: rock, sand,
     glass and wood give instruments 1 to 4; BlockNote.java:49 playBlock maps
     them to note.bd, note.snare, note.hat and note.bassattack, and 0 to
     note.harp. Material.sand is BlockSand, BlockGravel and BlockSoulSand;
     Material.glass is glass alone -->

### Fuel

A note block burns in a [[Smelting#Fuel|furnace]] for 300 ticks (15 seconds).
<!-- src: TileEntityFurnace.java:190 getItemBurnTime, 300 for any block made
     of Material.wood -->

## Behaviour

A [[Piston|piston]] cannot push a note block. [[Fire]] does not burn it.
<!-- src: BlockPistonBase.java:268 canPushBlock refuses any block with a tile
     entity; BlockFire.java:14 initializeBlock gives it no burn rate -->

## Data values

- Block ID: {{id|Note Block}}
- Translation key: `tile.musicBlock`
