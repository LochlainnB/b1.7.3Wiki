---
title: Block Transmutation
description: Glitches that give a block a metadata value the game never assigns it, and the invalid wood, slab and sapling items they produce.
type: mechanic
categories: [Game mechanics]
aliases: [Transmutation, Metadata transmutation, Moving piston merge, Invalid data value]
---

**Block transmutation** is a set of glitches that give a block a metadata value
the game never assigns it.

{{hatnote|The investigation behind this page, with its evidence and open questions, is [[Block Data Corruption]].}}

## How it works

Replacing a block writes the new block's ID first, then runs the old block's
removal, and only then writes the new metadata. While the old block's removal
runs, its space holds the new block with the old block's metadata. A block
placed in the space during that time keeps its own ID, and then receives the
new metadata.
<!-- src: Chunk.java:236 setBlockIDWithMetadata writes the id at :245, calls the
     old block's onBlockRemoval at :247, and writes the metadata at :250 and
     :265; Chunk.java:275 setBlockID does the same, writing metadata 0 at :289 -->

Transmutation changes metadata only. It cannot turn one block into another, so
it cannot make [[Sponge|sponge]] or any other block the world does not already
contain.

## Moving piston merge

When a [[Piston|piston]] moves a block into a space that already holds a moving
block with different metadata, the two merge. The moving block already there
lands at once and takes the incoming block's metadata. The incoming block is
lost.
<!-- src: BlockPistonMoving.java:18 onBlockRemoval calls TileEntityPiston.java:93
     clearPistonTileEntity, which places the stored block at :99, between the
     id and metadata writes above -->

A piston cannot normally push into a moving block. It can when the space is
empty as it checks its line and fills while it moves: a piston breaks a fragile
block at the end of its line, which updates the blocks around it, before it
moves anything. A second piston that answers that update can fill the space
first.
<!-- src: BlockPistonBase.java:309 tryExtend: the first loop checks the line and
     breaks a mobility-1 block at :336-:337 with setBlockWithNotify; the second
     loop at :345 moves whatever is in the line then, unchecked -->

Pistons of one kind ignore every update while one of them is moving, so the two
pistons must be one sticky and one normal.
<!-- src: BlockPistonBase.java:7 ignoreUpdates is a field of the Block object,
     one for Block.pistonBase and one for Block.pistonStickyBase; :113 sets it
     for the whole of playBlock and :53 onNeighborBlockChange checks it. Tested:
     with two normal pistons the second never fired. -->

### The machine

This machine gives a block the metadata of a piece of [[Wool|wool]]. Wool's
metadata is its colour, so every value but 0 can be chosen.
<!-- Tested on a dedicated server, built with the player's own placement and
     lever code; see Block Data Corruption. -->

Positions are relative to the [[Redstone Torch|redstone torch]] at the centre,
with east as +x and south as +z. Everything stands on a solid floor.

| Position | Block |
|---|---|
| 0, 0, 0 | Redstone torch, standing on the floor |
| −1, 0, 0 | Wool of the colour to transfer |
| −2, 0, 0 | Piston, facing east |
| 0, 0, −1 | The block to transmute |
| 0, 0, −2 | [[Sticky Piston\|Sticky piston]], facing south |
| −2, 0, −2 and −2, 1, −2 | Two solid blocks, one on the other |
| −1, 1, −2 | [[Lever]] on the east face of the upper solid block |
| −2, 0, 1 | Lever on the floor |

1. Place everything, with the upper lever off.
2. Turn the upper lever on. It powers the sticky piston through the space above
   it without updating it, so the sticky piston stays retracted.
3. Turn the floor lever on.

The piston breaks the torch. A lit redstone torch's removal updates every block
two steps away from it, which fires the sticky piston, and the pushed block ends
up at the centre with the wool's metadata. The wool is used up, and the torch
drops as an item.
<!-- src: BlockRedstoneTorch.java:61 onBlockRemoval updates the neighbours of
     each neighbour, which reaches the sticky piston through the block in front
     of it; BlockLever.java:153 blockActivated updates the lever's neighbours and
     the block it is on, neither of which is the sticky piston -->

The space's metadata is always 0 when the merge happens, so white wool,
metadata 0, transfers nothing.
<!-- src: the torch's removal ends with Chunk.java:289 writing metadata 0 after
     the sticky piston has filled the space, and setBlockIDWithMetadata returns
     early at :240 when id and metadata both match. Tested: white wool left the
     wood at 17:0. -->

The block to transmute must be one a piston can push. [[Leaves]] and
[[Sapling|saplings]] break instead.
<!-- src: Material.java:118-:119 leaves and plants setNoPushMobility. Tested:
     both were broken and the wool landed in the centre as usual. -->

## Tree growth

A tree that grows over a lit redstone torch gives a sapling with damage value 3
a chance to drop.

An oak tree's two lowest leaf layers reach 2 blocks from its trunk, but the tree
checks only 1 block out at those heights for room to grow. Its leaves there
replace any non-solid block, torches included, without breaking them.
<!-- src: WorldGenTrees.java:14-:35 checks radius 1 below the top three layers;
     :45-:56 places leaves at radius 2 in the lowest two layers wherever
     opaqueCubeLookup is false -->

While the torch is being replaced, the new leaves carry the torch's metadata. A
torch on the south face of a block has metadata 3. The torch's removal fires a
piston two blocks away whose line runs through the torch's space. The piston
breaks the new leaves, and like any leaves they drop a sapling 1 time in 20,
with the leaves' metadata as its damage value.
<!-- src: BlockPistonBase.java:336 drops a fragile block with the metadata it
     holds at that moment; BlockLeaves.java:155 quantityDropped 1 in 20, :173
     damageDropped metadata & 3. A torch removed by a growing tree updates only
     the blocks two steps away (BlockRedstoneTorch.java:61); the tree places
     leaves without neighbour updates. -->

Positions are relative to the [[Sapling|sapling]], on dirt or grass:

| Position | Block |
|---|---|
| ±2, 2, −1 | Solid block |
| ±2, 2, 0 | Redstone torch on the south face of that block |
| ±3, 2, 0 | Any block a piston can push |
| ±4, 2, 0 | Piston facing the torch, powered without being updated |

{{viewer|sapling-transmutation}}
<!-- Scene: Block Data Corruption, Appendix C, E6 setup. Coordinates and
     metadata are the tested pre-growth fixture, including its powered levers. -->

Growing the sapling with [[Bone Meal|bone meal]] hits the torches when the tree
grows 4 or 5 blocks tall, two times in three, and never when it grows as a big
oak.
<!-- src: WorldGenTrees.java:7 height rand.nextInt(3) + 4; BlockSapling.java:46
     a big tree 1 time in 10. Tested: 60 trees with two torches each gave two
     saplings of damage 3 (6:3), at the torch's position. -->

## Results

Three blocks keep an invalid metadata value in what they drop:

| Block | Invalid values | Method | Drops |
|---|---|---|---|
| [[Wood]] | 3 to 15 | moving piston merge | wood with that damage value |
| [[Stone Slab]] and [[Double Stone Slab]] | 4 to 15 | moving piston merge | slabs with that damage value |
| [[Sapling]] | 3 | tree growth | a sapling with damage value 3 |

<!-- src: BlockLog.java:56 and BlockStep.java:68 damageDropped return the
     metadata, BlockSapling.java:57 and BlockLeaves.java:173 metadata & 3.
     Wool (BlockCloth.java:17) keeps its metadata too, but all 16 values are
     valid. Leaves with metadata 3 exist only while the torch is being removed,
     so shears never reach them. Tested: a player mined 17:5 and 44:9 and picked
     up items of the same damage values. -->

Each of these items places a block with its own damage value as metadata, and
stacks only with items of the same value.
<!-- src: ItemLog.java, ItemSlab.java and ItemSapling.java getPlacedBlockMetadata
     return the damage. Tested: 17:5 sat in its own slot beside 17:0; a placed
     44:9 slab came out 44:9. -->

Invalid wood looks like oak wood, and the damage-3 sapling looks and grows like
an oak sapling. Invalid slabs look like stone slabs, but show the smooth top
texture on every face.
<!-- src: BlockLog.java and BlockSapling.java getBlockTextureFromSideAndMetadata
     fall through to oak; BlockSapling.java:36 growTree treats metadata 3 as oak;
     BlockStep.java:19 returns the top texture, 6, on every side for metadata 4
     and above -->

Two invalid slabs of the same value stack into a double stone slab of that
value, which drops two of them.
<!-- src: BlockStep.java:43 onBlockAdded compares metadata only. Tested: two
     44:9 made 43:9, which dropped two 44:9. -->

Holding the pointer over an invalid slab in an inventory screen crashes the
game. The tooltip asks for a name the game does not have.
<!-- src: GuiContainer.java:66 asks for the hovered stack's name;
     ItemSlab.java:18 getItemNameIS indexes a 4-entry array by damage value.
     Reproduced by calling the client jar's ItemStack name lookup directly: it
     throws ArrayIndexOutOfBoundsException for damage 4 to 15. The crash screen
     itself was not observed in a running client. -->
