---
title: Egg
description: An item laid by chickens, thrown to hatch chickens or crafted into cake.
type: item
categories: [Items]
---

An **egg** is an item laid by [[Chicken|chickens]].

## Obtaining

### Chickens

[[Chicken|Chickens]] lay eggs, which drop on the ground as items.
<!-- src: EntityChicken.java:43-:46 onLivingUpdate -->

## Usage

### Throwing

Using an egg throws it. It breaks on the first block or entity it hits, and
flies through water and lava.
<!-- src: ItemEgg.java:9 onItemRightClick; EntityEgg.java:119 rayTraceBlocks,
     which ignores liquids (World.java:704), :173 setEntityDead on any hit -->

A hit deals no [[Damage|damage]], but counts as an attack by the thrower. It
knocks a mob back, and angers a [[Pig Zombie|pig zombie]] or wild
[[Wolf|wolf]] as any attack would. It does nothing to a [[Player|player]].
<!-- src: EntityEgg.java:153 attackEntityFrom(thrower, 0);
     EntityLiving.java:337 knocks back from the attacker;
     EntityPigZombie.java:49; EntityWolf.java:254; EntityPlayer.java:380
     returns before any of it when the damage is 0 -->

A thrown egg [[Mob Spawning#Other ways mobs appear|hatches a chicken]] one time
in eight when it breaks.
<!-- src: EntityEgg.java:156 -->

A [[Dispenser|dispenser]] fires eggs. A dispensed egg has no thrower, and
knocks nothing back.
<!-- src: BlockDispenser.java:112-:116; the EntityEgg constructor at
     EntityEgg.java:47 leaves the thrower null; EntityLiving.java:337 knocks
     back only from an attacker -->

### Crafting ingredient

{{used in|Egg}}

## Data values

- Item ID: {{id|Egg}}
- Translation key: `item.egg`

A thrown egg has no entity network ID, and is not saved with the world.
<!-- src: EntityList.java:83-:106 registers no EntityEgg, and Entity.java:780
     addEntityID saves only entities it names. A server spawns it on clients
     as object type 62 of Packet23VehicleSpawn (NetClientHandler.java:97) -->
