---
title: Achievements
description: The sixteen achievements, what earns each, and the order they must be earned in.
type: mechanic
categories: [Game mechanics]
aliases: [Achievement]
---

**Achievements** are sixteen milestones the game records for each player, such
as crafting a first pickaxe.

## Earning an achievement

An achievement is earned only once the achievement it requires is unlocked.
Doing the task before then records nothing, and the task must be done again.
<!-- src: EntityPlayerSP.java:176 addStat, which drops an achievement at :180
     unless its parent is already unlocked -->

Achievements belong to the player, not the world. They are saved in the `stats`
folder of the game directory, in a file named after the player, and count in
every world.
<!-- src: StatFileWriter.java:17 the stats folder; StatsSyncher.java:27-:28
     stats_<username>.dat -->

Achievements are earned in multiplayer too, and saved to the same file.
<!-- src: the server sends each one as a Packet200Statistic
     (EntityPlayerMP.java:359 addStat); NetClientHandler.java:620 hands it to
     EntityClientPlayerMP.java:157 incrementStat, which runs the same
     EntityPlayerSP.addStat -->

## List

| Achievement | In-game description | Earned by | Requires |
|---|---|---|---|
| Taking Inventory | Press 'E' to open your inventory. | Opening the inventory | — |
| Getting Wood | Attack a tree until a block of wood pops out | Picking up a [[Wood\|wood]] block from the ground | Taking Inventory |
| Benchmarking | Craft a workbench with four blocks of planks | Crafting a [[Crafting Table\|crafting table]] | Getting Wood |
| Time to Mine! | Use planks and sticks to make a pickaxe | Crafting a [[Wooden Pickaxe\|wooden pickaxe]] | Benchmarking |
| Hot Topic | Construct a furnace out of eight stone blocks | Crafting a [[Furnace\|furnace]] | Time to Mine! |
| Acquire Hardware | Smelt an iron ingot | Taking an [[Iron Ingot\|iron ingot]] out of a furnace | Hot Topic |
| Time to Farm! | Use planks and sticks to make a hoe | Crafting a [[Wooden Hoe\|wooden hoe]] | Benchmarking |
| Bake Bread | Turn wheat into bread | Crafting [[Bread\|bread]] | Time to Farm! |
| The Lie | Wheat, sugar, milk and eggs! | Crafting a [[Cake\|cake]] | Time to Farm! |
| Getting an Upgrade | Construct a better pickaxe | Crafting a [[Stone Pickaxe\|stone pickaxe]] | Time to Mine! |
| Delicious Fish | Catch and cook fish! | Taking [[Cooked Fish\|cooked fish]] out of a furnace | Hot Topic |
| On A Rail | Travel by minecart at least 1 km from where you started | Riding a [[Minecart\|minecart]] 1000 blocks, in a straight line, from where the player got in | Acquire Hardware |
| Time to Strike! | Use planks and sticks to make a sword | Crafting a [[Wooden Sword\|wooden sword]] | Benchmarking |
| Monster Hunter | Attack and destroy a monster | Killing a [[Zombie\|zombie]], [[Skeleton\|skeleton]], [[Spider\|spider]], [[Creeper\|creeper]], [[Pig Zombie\|pig zombie]] or [[Giant\|giant]] | Time to Strike! |
| Cow Tipper | Harvest some leather | Picking up [[Leather\|leather]] from the ground | Time to Strike! |
| When Pigs Fly | Fly a pig off a cliff | Falling more than 5 blocks while riding a [[Pig\|pig]] | Cow Tipper |

<!-- src: AchievementList.java:33-:48, the ids, parents and special flags;
     names and descriptions from lang/stats_US.lang in the client jar, where
     Taking Inventory's '%1$s' is the key bound to the inventory, E by default.
     Triggers: GuiInventory.java:12; EntityItem.java:115 and :119, on picking
     up the item entity; SlotCrafting.java:19-:35, on taking the result;
     SlotFurnace.java:18 and :22, on taking the output; EntityPlayer.java:774,
     whose getSqDistanceTo returns the true distance (ChunkCoordinates.java:48
     takes the square root) from where :773 recorded the start, cleared at :122
     whenever the player rides nothing; EntityPlayer.java:797 onKillEntity, for
     any EntityMob, which slimes and ghasts are not; EntityPig.java:72 fall,
     over 5 with a player riding -->

On A Rail and When Pigs Fly are special achievements, drawn with a different
frame on the achievements screen.
<!-- src: AchievementList.java:44 and :48 setSpecial; GuiAchievements.java:262 -->
