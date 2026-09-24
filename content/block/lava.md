---
title: Lava
description: The glowing fluid that flows three blocks from a source, sets fires, and burns what enters it.
type: block
subject: {Still: block 11, Flowing: block 10}
categories: [Blocks, Naturally generated]
---

**Lava** is a glowing [[Fluid|fluid]] that burns entities and starts fires.

<!-- The stub's subject map read {Still: block 10, Flowing: block 11}, the
     wrong way round: Block.java:602 registers 10 as BlockFlowing and :603
     registers 11 as BlockStationary. -->

## Obtaining

### Natural generation

In the [[Overworld]], lava forms [[World Generation#Lakes|lakes]] and
[[World Generation#Springs|springs]], and fills caves carved below y=10. In the
[[Nether]] it fills the open space below y=32, and forms
[[World Generation#The Nether|springs]] in the netherrack.
<!-- src: ChunkProviderGenerate.java:330-:335 lava lakes, 1 chunk in 8;
     :581-:586 lava springs, 20 a chunk; MapGenCaves.java:133-:135;
     ChunkProviderHell.java:40 and :75 lava below y=32; :310-:315 Nether
     springs, 8 a chunk -->

### Buckets

An empty [[Bucket|bucket]] takes a lava source, and a
[[Lava bucket|lava bucket]] places one.
<!-- src: ItemBucket.java:46, :87 -->

## Behaviour

### Flow

Lava [[Fluid|flows]] 3 blocks from a source on the flat, spreading one block
every 30 ticks. In the [[Nether]] it [[Nether#Behaviour|flows 7 blocks]].
<!-- src: BlockFlowing.java:24 a level of 2 lost per block, 1 in the Nether;
     BlockFluid.java:187 tickRate 30 -->

Lava never makes new sources.
<!-- src: BlockFlowing.java:51 tests for water only -->

Flowing lava destroys the non-solid blocks it reaches, such as plants and
torches, and leaves no drops. See [[Fluid#What stops flow]].
<!-- src: BlockFlowing.java:116 flowIntoBlock -->

Lava with [[Water|water]] beside it or above it
[[Fluid#Lava and water|hardens]] into [[Obsidian|obsidian]] or
[[Cobblestone|cobblestone]].
<!-- src: BlockFluid.java:247 checkForHarden -->

### Fire

On [[Game Tick#Random ticks|random ticks]], still lava
[[Fire#Starting a fire|sets fire]] to air up to two blocks above it that is
beside a wooden block, leaves, wool or TNT.
<!-- src: BlockStationary.java:7-:10 keeps random ticks for lava only;
     :32 updateTick, 0 to 2 steps upwards, each up to 1 block across;
     :54 isFlammable reads Material.getBurning, set on wood, leaves, cloth and
     tnt (Material.java:113-:126) -->

### Entities

Lava deals 4 [[Damage#Environmental damage|damage]] to an entity in it, as
often as the invulnerability window allows, and sets it
[[Damage#Catching fire|alight]] for 600 ticks. [[Ghast|Ghasts]] and
[[Pig Zombie|pig zombies]] take no damage from it.
<!-- src: Entity.java:255 handleLavaMovement, :271 setOnFireFromLava, which
     tests isImmuneToFire; EntityGhast.java:17, EntityPigZombie.java:15 -->

A dropped item in lava is destroyed.
<!-- src: EntityItem.java:8 health 5; :86 attackEntityFrom takes the 4 from
     setOnFireFromLava every tick -->

Lava does not push entities.
<!-- src: Entity.java:607 handleLavaMovement only tests for lava -->

### Explosions

[[Explosion|Explosions]] destroy flowing lava. No explosion breaks still lava,
and one centred in still lava breaks no blocks at all.
<!-- src: Block.java:602 flowing lava has hardness 0, so a blast resistance
     of 0; :603 still lava 100; Explosion.java:55-:61 add every block a ray
     reaches with strength left, and :158 removes it -->

## Data values

- Block ID: {{id|Lava}} (flowing), {{id|block 11}} (still)
- Translation key: `tile.lava`
