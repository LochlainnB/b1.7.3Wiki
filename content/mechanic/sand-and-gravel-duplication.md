---
title: Sand and Gravel Duplication
description: A piston timing glitch that preserves a sand or gravel block while its falling entity produces another copy.
type: mechanic
categories: [Game mechanics]
aliases: [Sand Duplication, Gravel Duplication, Sand Duplicator, Gravel Duplicator]
---

**Sand and gravel duplication** is a timing glitch that creates extra
[[Sand|sand]] or [[Gravel|gravel]] by separating a falling block's entity from
its original block.

## How it works

Unsupported sand and gravel create a [[Falling Sand|falling sand entity]] when
their scheduled fall check runs. Creating the entity does not immediately
remove the original block. During each of its updates, the entity removes a
block of the same kind at its current position, after moving. A missing
original block does not cancel the entity.
<!-- src: BlockSand.java:24-:29 tryToFall spawns the entity without removing
     the block; EntityFallingSand.java:37-:55 onUpdate moves, then removes a
     matching block without cancelling the entity when none is found;
     BlockGravel.java:5 extends BlockSand -->

A [[Piston|piston]] can move the original block before the entity removes it.
The moved block survives, while the entity remains a separate copy. A
[[Sticky Piston|sticky piston]] can pull the original back onto a support.
If the falling copy later passes through the preserved block, it removes that
block too.
<!-- src: BlockPistonBase.java:153-:161 playBlock pulls a stored block into a
     moving piston; :345-:356 tryExtend stores pushed blocks separately from
     entities; TileEntityPiston.java:105-:112 restores the stored block;
     EntityFallingSand.java:53 checks the current position on every update -->

The falling copy lands as a block or drops as an item under the ordinary
[[Falling Sand#Behaviour|landing rules]]. The original can be used again.
Duplicated gravel that drops this way gives gravel, not [[Flint|flint]].
<!-- src: EntityFallingSand.java:57-:66 landing and dropItem(this.blockID, 1),
     without calling BlockGravel.idDropped -->

## Timing

Sand and gravel schedule a fall check 3 [[Game Tick|game ticks]] after placement
or a neighbour update. The block below must allow falling when the check runs.
<!-- src: BlockSand.java:12-:21 schedules tickRate(), :45-:60 gives 3 ticks and
     tests the block below -->

The piston must separate the original block and the entity after the entity
appears, but before its next update removes the original. Moving the block
before the fall check prevents that check from creating an entity at the old
position. Moving it after the entity has removed it preserves no original.
<!-- src: World.java:1986-:1988 TickUpdates checks that the scheduled block ID
     still occupies the position; EntityFallingSand.java:53-:55 removes it on
     the entity's update -->

Scheduled checks due together run in the order they were scheduled. Piston
movements triggered by those checks happen immediately. Their order matters
when the fall check and the piston movement occur in the same tick.
<!-- src: NextTickListEntry.java:38 comparer orders by time then tickEntryID;
     World.java:1967 TickUpdates; :2369-:2372 playNoteAt calls playBlock directly;
     BlockPistonBase.java:66-:78 updatePistonState -->
