---
title: Snowball
description: A throwable item broken out of snow, which deals no damage but knocks back a mob it hits, and crafts into snow blocks.
type: item
categories: [Items]
---

A **snowball** is a throwable item broken out of [[Snow|snow]].

## Obtaining

### Breaking snow

[[Snow]] broken with a [[Mining#Drops|shovel]] drops snowballs: one from a
layer, four from a block.
<!-- src: BlockSnow.java:50 harvestBlock; BlockSnowBlock.java:15
     quantityDropped 4; ItemSpade.java:10 canHarvestBlock -->

## Usage

### Throwing

Using a snowball throws it. It breaks on the first block or entity it hits, and
flies through water and lava.
<!-- src: ItemSnowball.java:10; EntitySnowball.java:119 rayTraceBlocks, which
     ignores liquids (World.java:704), :160 setEntityDead on any hit -->

A hit deals no [[Damage|damage]], but counts as an attack by the thrower. It
knocks a mob back, and angers a [[Pig Zombie|pig zombie]] or wild
[[Wolf|wolf]] as any attack would. It does nothing to a [[Player|player]].
<!-- src: EntitySnowball.java:153 attackEntityFrom(thrower, 0);
     EntityLiving.java:337 knocks back from the attacker;
     EntityPigZombie.java:49; EntityWolf.java:254; EntityPlayer.java:380
     returns before any of it when the damage is 0 -->

A [[Dispenser|dispenser]] fires snowballs. A dispensed snowball has no thrower,
and knocks nothing back.
<!-- src: BlockDispenser.java:117-:121; EntitySnowball.java:47 leaves the
     thrower null; EntityLiving.java:337 knocks back only from an attacker -->

### Crafting ingredient

{{used in|Snowball}}

## Data values

- Item ID: {{id|Snowball}}
- Entity network ID: {{id|entity 11}}
- Translation key: `item.snowball`
