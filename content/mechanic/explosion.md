---
title: Explosion
description: How an explosion breaks blocks and hurts entities — rays, blast resistance, drops, damage and knockback, and the size of every explosion in the game.
type: mechanic
categories: [Game mechanics]
aliases: [Explosions, Blast, Blast resistance]
---

An **explosion** is a blast that breaks blocks and damages entities around a
point.

## Sizes

| Explosion | Size | Breaks blast resistance below | Damage at the centre | Sets fire |
|---|---|---|---|---|
| [[Ghast]] fireball | 1 | 2.5 | 17 | yes |
| [[Creeper]] | 3 | 11 | 49 | no |
| [[TNT]] | 4 | 15.5 | 65 | no |
| [[Bed]] used in the [[Nether]] | 5 | 19.9 | 81 | yes |
| Charged creeper | 6 | 24.2 | 97 | no |

<!-- src: EntityFireball.java:127, EntityCreeper.java:103 and :101 (charged),
     EntityTNTPrimed.java:67, BlockBed.java:45; the fire flag is the last
     argument of World.java:1522 newExplosion. The resistance column is the
     strongest block the strongest possible ray can break one block from the
     centre, (1.3 * size - 0.45) / 0.3 - 0.3, from the arithmetic under
     Breaking blocks -->

The blast resistance of every block is in its infobox, and in the
[[Mining#Block hardness|table of every block]].

## Breaking blocks

An explosion sends 1,352 rays out from its centre, spread evenly in every
direction. Each ray starts with a strength of 0.7 to 1.3 times the explosion's
size and moves out in steps of 0.3 blocks. Each step costs:

- 0.225 strength, always;
- 0.3 × (blast resistance + 0.3) more, when the step lands inside a block.

A ray breaks each block it reaches with strength to spare, and stops when its
strength runs out. Through open air a ray reaches at most 1.73 times the size in
blocks.
<!-- src: Explosion.java:29 doExplosionA; the rays start from the 1,352 surface
     points of a 16 x 16 x 16 grid; :55-:71 the step loop; Block.java:371
     getExplosionResistance, which is the figure data/ records as blast
     resistance -->

No explosion breaks [[Obsidian|obsidian]], [[Bedrock|bedrock]], [[Water|water]]
or still [[Lava|lava]]. An explosion centred in water breaks no blocks at all,
because every ray starts inside it.
<!-- src: blast resistance 100 for water and still lava against a strongest
     ray of 7.8 for size 6; the first step of every ray is taken at the centre
     (Explosion.java:55) -->

A broken block drops each item it would drop with a chance of 3 in 10.
[[TNT]] drops nothing, and is lit instead with a short fuse.
<!-- src: Explosion.java:158 dropBlockAsItemWithChance(..., 0.3F);
     BlockTNT.java:35 quantityDropped 0, :39 onBlockDestroyedByExplosion -->

A ghast fireball or a bed sets fire to one space in three of those it clears,
where the block beneath is opaque.
<!-- src: Explosion.java:110-:121 -->

## Entities

Every entity within twice the size, in blocks, of the centre is damaged and
thrown back. A creeper's blast leaves the creeper out.
<!-- src: Explosion.java:77 doubles explosionSize before the entity pass, :84
     getEntitiesWithinAABBExcludingEntity(exploder), :90 distance / size <= 1 -->

With *d* the distance from the centre and *exposure* the share of the entity's
body in clear line of the centre:

- *f* = (1 − *d* ÷ (2 × size)) × *exposure*
- damage = ⌊(*f*² + *f*) ÷ 2 × 16 × size + 1⌋
- knockback = *f*, directly away from the centre

<!-- src: Explosion.java:92-:103, where 8 * explosionSize is 16 * size once
     doubled; World.java:1530 getBlockDensity samples a grid
     of points through the entity's bounding box and counts the ones with no
     block between them and the centre -->

An entity in range takes at least 1 damage, however well it is covered.

For a player, [[Damage#Armour|armour]] reduces explosion damage and
[[Damage#Difficulty|difficulty]] scales a creeper's.

A dropped item has 5 health and a [[Painting|painting]] breaks at any damage,
so both are destroyed by almost any blast. Lit [[Primed TNT|TNT]] takes no
damage, and is only thrown.
<!-- src: EntityItem.java:8, :87; EntityPainting.java:204; EntityTNTPrimed
     does not override Entity.java:746 attackEntityFrom -->
