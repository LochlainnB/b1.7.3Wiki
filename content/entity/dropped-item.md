---
title: Dropped Item
description: A stack of items lying loose in the world, which a player picks up by walking near it, and which disappears after five minutes.
type: entity
subject: Item
categories: [Entities]
---

A **dropped item** is a stack of items lying loose in the world.

## Spawning

A dropped item is made by each source below, and cannot be picked up until the
source's delay has passed. What a block gives is on [[Mining#Drops|Mining]], and
what a mob gives is on the mob's own page.

| Made by | Can be picked up after |
|---|---|
| A player dropping an item, or dying | 40 ticks (2 seconds) |
| A broken block, a mob's drop, a broken [[Boat\|boat]] or [[Minecart\|minecart]] | 10 ticks |
| The contents of a broken [[Chest\|chest]], [[Furnace\|furnace]], [[Dispenser\|dispenser]] or [[Minecart with Chest\|storage minecart]] | at once |
| A dispenser firing an item, a broken [[Painting\|painting]], a [[Fishing Rod\|fishing]] catch | at once |

<!-- src: EntityPlayer.java:260 dropPlayerItemWithRandomChoice sets 40;
     Block.java:362 dropBlockAsItem_do and Entity.java:883 entityDropItem set
     10, which mob drops, boats and minecarts use; BlockChest.java:172,
     BlockFurnace.java:170, BlockDispenser.java:123 and :198,
     EntityMinecart.java:103, EntityPainting.java:208 and EntityFish.java:362
     make the item with no delay -->

## Behaviour

### Movement

A dropped item is 0.25 blocks across. It falls, and slides to a stop on the
ground. It slides further on [[Ice|ice]], and [[Soul Sand|soul sand]] slows it.
<!-- src: EntityItem.java:13 setSize; :45 gravity; :55-:66 drag in the air and
     ground friction from the slipperiness of the block below;
     BlockSoulSand.java:13 -->

Water does not slow its fall, but carries it the way the water
[[Fluid#Entities|flows]].
<!-- src: EntityItem.java:79 handleWaterMovement only adds the flow
     (World.java:1426); nothing in EntityItem changes its motion in water -->

An item inside a full block moves out through the nearest face with open space
beyond it.
<!-- src: EntityItem.java:53; Entity.java:1096 pushOutOfBlocks -->

A dropped item presses a wooden [[Pressure Plate|pressure plate]].
<!-- src: BlockPressurePlate.java:74, EnumMobType.everything -->

### Picking up

A player picks up an item that comes within 1 block of the player's body
horizontally, level with it, once the item can be picked up. Only players pick
up items.
<!-- src: EntityPlayer.java:196-:197 expands a living player's box by 1
     horizontally and 0 vertically; EntityItem.java:110 onCollideWithPlayer,
     :113 the delay; only EntityPlayer calls it -->

The item tops up stacks of the same kind first, then fills the first empty slot,
hotbar first. Whatever does not fit stays on the ground. A damaged tool or piece
of armour needs an empty slot.
<!-- src: InventoryPlayer.java:132 addItemStackToInventory; :29 storeItemStack
     and :40 getFirstEmptyStack walk slots 0-35, of which 0-8 are the hotbar;
     :134 a damaged stack goes only to an empty slot -->

### What ends it

A dropped item disappears 6000 ticks (5 minutes) after it appeared. It does not
age outside the [[Game Tick#Entities|loaded area]], and its age is saved with it.
<!-- src: EntityItem.java:72-:75; :99 writes Age; World.java:1294 skips an
     entity near an unloaded chunk -->

A dropped item has 5 [[Damage#Other entities|health]]. It is destroyed by:

- [[Fire|fire]], [[Lava|lava]] or a [[Cactus|cactus]] it touches;
- a [[Lightning Bolt|lightning]] strike;
- an [[Explosion#Entities|explosion]] that deals it 5 or more;
- falling below y = −64.

<!-- src: EntityItem.java:8 health 5, :87 attackEntityFrom with no
     invulnerability window; Entity.java:523 1 a tick in fire or lava, :271 4
     more from lava; BlockCactus.java:87 1 a tick; Entity.java:1085 5 from
     lightning; Explosion.java:100; Entity.java:259 removes any entity below
     y = -64 -->

## Data values

- Entity network ID: {{id|Item}}

The game names the entity *Item*. It saves the stack it holds as `Item`, with
its `Age` and `Health`.
<!-- src: EntityList.java:85; EntityItem.java:97 writeEntityToNBT -->
