---
title: Cobweb
description: A block that slows whatever moves through it, broken quickly only by swords and shears, and dropping string.
type: block
categories: [Blocks]
---

A **cobweb** is a block that slows whatever moves through it.

## Obtaining

No cobweb generates in the world, and no recipe makes one. Breaking a cobweb
never drops the cobweb itself. A server operator's `give` command is the only
way to get one.
<!-- src: Block.web is placed by no WorldGen* class and is the output of no
     recipe in CraftingManager.java; BlockWeb.java:30 idDropped returns
     string; minecraft_server ConsoleCommandHandler.java:133 give, which takes
     any id in Item.itemsList, and minecraft_server Block.java:646-:647 gives
     every block an item -->

### Breaking

A sword or [[Shears|shears]] breaks a cobweb in 8 ticks, and
[[Mining#Drops|harvests]] it for one [[String|string]]. Anything else takes 401
ticks, just over 20 seconds, and gets nothing.
<!-- src: Block.java:327 blockStrength with hardness 4 (Block.java:622):
     ItemSword.java:14 and ItemShears.java:22 give speed 15, 15 / 4 / 30 =
     0.125 a tick; anything else cannot harvest Material.web (Material.java:136
     setNoHarvest), 1 / 4 / 100 a tick, which float addition in
     PlayerControllerSP.java:71 takes 401 ticks to bring to 1 -->

## Behaviour

A player in a cobweb walks at about 0.5 blocks per second, a ninth of walking
speed, and sinks at under 0.1 blocks per second. Mobs and dropped items are
slowed the same way.
<!-- src: BlockWeb.java:10 onEntityCollidedWithBlock; Entity.java:303-:310
     scales the next move by 0.25 across and 0.05 up and down, and zeroes the
     motion, so no speed carries from one tick to the next. A walking player
     adds 0.098 a tick (EntityLiving.java:489) and moves 0.0245; gravity adds
     0.0784 (:532-:533) and moves 0.0039 -->

A cobweb does not break a fall. An entity that falls into one takes
[[Damage#Environmental damage|fall damage]] for the whole drop when it lands.
<!-- src: Entity.java:303 leaves fallDistance alone, and :553 keeps adding to
     it; only water (:231) and ladders (EntityLiving.java:517) reset it -->

Arrows pass through a cobweb.
<!-- src: EntityArrow.java:128 traces blocks with its last argument true, and
     World.java:724 and :846 then skip a block with no collision box, which
     BlockWeb.java:18 returns -->

## Data values

- Block ID: {{id|Cobweb}}
- Translation key: `tile.web`
