---
title: Mining
description: How blocks are broken in Beta 1.7.3 — breaking speed, tools, harvest levels and what drops.
type: mechanic
categories: [Game mechanics]
---

**Mining** is breaking a block in the world by holding the attack button on it.
Two questions decide what happens, and the game answers them separately: how
long the block takes to come apart, and whether it leaves anything behind. A
block can break quickly and drop nothing, or take half a minute and drop
nothing, depending on what is in the player's hand.

## Breaking a block

Damage to a block is measured in *strength* — a fraction added once per tick,
with the block breaking on the tick the running total reaches 1. Strength comes
from one of two formulas, and which one applies turns entirely on whether the
player can harvest the block at all:

- **Harvestable** — `speed ÷ (hardness × 30)` per tick, where *speed* is the
  held item's multiplier against that particular block, and 1 for a bare hand or
  anything with no opinion about it.
- **Not harvestable** — `1 ÷ (hardness × 100)` per tick, flat. The held item is
  never consulted on this branch, so a wooden pickaxe chews through
  [[Diamond Ore]] at exactly the speed of a bare fist.

<!-- src: Block.java:327 blockStrength -->

Breaking time in ticks is one divided by that, rounded up: `hardness × 30 ÷
speed` when the block is harvestable, and a flat `hardness × 100` when it is
not. There are twenty ticks in a second.

[[Stone]], at a hardness of 1.5, shows the whole range:

| Held item | Speed | Ticks | Seconds |
|---|---|---|---|
| {{sprite\|Wooden Pickaxe}} | 2 | 23 | 1.15 |
| {{sprite\|Stone Pickaxe}} | 4 | 12 | 0.6 |
| {{sprite\|Iron Pickaxe}} | 6 | 8 | 0.4 |
| {{sprite\|Diamond Pickaxe}} | 8 | 6 | 0.3 |
| {{sprite\|Golden Pickaxe}} | 12 | 4 | 0.2 |
| Anything else, or nothing | — | 150 | 7.5 |

The count starts on the tick *after* the block is first targeted: the first
frame on a new target only records its position. Looking away and back resets
the total to zero, so a partly-mined block recovers completely the moment the
crosshair leaves it.
<!-- src: PlayerControllerSP.java:61 sendBlockRemoving, the else branch that
     stores the position without adding damage -->

### Instant and unbreakable blocks

A hardness of zero divides to infinity, which clears the threshold on the first
frame. Those blocks break the instant the button goes down, before any damage
accumulates at all — [[Torch]], [[Redstone Dust]], [[Sapling]], [[Flower]],
[[Tall Grass]], [[TNT]] and the rest of the zero-hardness list.
<!-- src: PlayerControllerSP.java:43 clickBlock, the blockStrength >= 1.0F test -->

A *negative* hardness short-circuits the other way: strength is returned as zero
outright, and no amount of holding will ever break the block. Only [[Bedrock]]
and the [[Portal]] block are set that way.
<!-- src: Block.java:328 blockStrength; Block.java:207 setBlockUnbreakable -->

### The five-tick floor

Instant blocks do not come down twenty a second. Two separate delays cap the
rate: finishing a block through the damage counter sets a five-tick pause before
the next block starts taking damage, and holding the button down re-clicks only
once every five ticks — a quarter of the tick rate.
<!-- src: PlayerControllerSP.java:83 blockHitWait = 5;
     Minecraft.java:1012 timer.ticksPerSecond / 4.0F -->

Clicking at nothing — swinging at air rather than at a block — costs ten ticks
during which left-click does nothing at all.
<!-- src: Minecraft.java:809 leftClickCounter = 10 -->

### Water and falling

Two conditions divide the player's speed, and both are checked only on the
harvestable branch:

- Mining with the head underwater divides speed by five.
- Mining while not standing on the ground divides speed by five.

<!-- src: EntityPlayer.java:291 getCurrentPlayerStrVsBlock -->

They stack, so mining from a jump underwater runs at a twenty-fifth of normal
speed. The test for water samples eye level rather than the feet, so standing
waist-deep costs nothing.
<!-- src: Entity.java:588 isInsideOfMaterial, which samples posY + eye height -->

Because both penalties live in the harvestable branch, they do not apply at all
to a block the player cannot harvest. Punching [[Stone]] bare-handed takes 7.5
seconds whether the player is dry and standing still or swimming in mid-fall.

## Tools

A tool's speed multiplier depends on the block. Each tool class carries a short
list of blocks it is *effective against*; against anything on the list it
returns its material's multiplier, and against everything else it returns 1 —
the same as a bare hand.
<!-- src: ItemTool.java:19 getStrVsBlock -->

| Material | Speed | Harvest level | Blocks broken before it breaks |
|---|---|---|---|
| Wood | 2 | 0 | 60 |
| Gold | 12 | 0 | 33 |
| Stone | 4 | 1 | 132 |
| Iron | 6 | 2 | 251 |
| Diamond | 8 | 3 | 1562 |

<!-- src: EnumToolMaterial.java:4, constants in the order
     (harvestLevel, maxUses, efficiencyOnProperMaterial, damageVsEntity) -->

Gold is the fastest material in the game and the most fragile, mining at one and
a half times a diamond tool's rate and surviving a twentieth as long.

### What each tool is effective against

The lists are short and literal. A block that is not named gets no speed bonus,
however obviously it looks like it belongs:

- **Pickaxe** — [[Stone]], [[Cobblestone]], [[Moss Stone]], [[Sandstone]],
  [[Stone Slab]], [[Double Stone Slab]], [[Netherrack]], [[Ice]], [[Coal Ore]],
  [[Iron Ore]], [[Gold Ore]], [[Diamond Ore]], [[Lapis Lazuli Ore]],
  [[Block of Iron]], [[Block of Gold]], [[Block of Diamond]] and
  [[Lapis Lazuli Block]].
  <!-- src: ItemPickaxe.java:41 blocksEffectiveAgainst -->
- **Axe** — [[Wooden Planks]], [[Wood]], [[Bookshelf]] and [[Chest]].
  <!-- src: ItemAxe.java:11 blocksEffectiveAgainst -->
- **Shovel** — [[Grass]], [[Dirt]], [[Sand]], [[Gravel]], [[Snow]] in both
  forms, [[Clay]] and [[Farmland]].
  <!-- src: ItemSpade.java:19 blocksEffectiveAgainst -->
- **Sword** — everything, at 1.5×, and [[Cobweb]] at 15×.
  <!-- src: ItemSword.java:13 getStrVsBlock -->
- **[[Shears]]** — [[Leaves]] and [[Cobweb]] at 15×, [[Wool]] at 5×.
  <!-- src: ItemShears.java:22 getStrVsBlock -->

Nothing else carries a multiplier. A hoe mines at bare-hand speed and takes no
damage from it.
<!-- src: ItemHoe.java, which overrides neither getStrVsBlock nor
     onBlockDestroyed -->

Because the lists are written out one block at a time, several things are
missing from them. [[Obsidian]] is not on the pickaxe's list, so even a
[[Diamond Pickaxe]] takes it at speed 1 — fifteen seconds a block. Neither is
[[Bricks]], [[Furnace]], [[Dispenser]], [[Monster Spawner]], [[Redstone Ore]],
[[Glowstone]], [[Iron Door]], the stone [[Pressure Plate]] or [[Stone Stairs]],
all of which still *need* a pickaxe to drop anything. [[Wooden Stairs]] are
absent from the axe's list the same way.

### Tool wear

A tool loses one point of durability per block broken, whatever the block, and
whether or not it was on the tool's list or dropped anything. Breaking a
[[Torch]] with a diamond pickaxe costs the same point as breaking [[Stone]].
<!-- src: ItemTool.java:34 onBlockDestroyed, which has no hardness guard -->

The exceptions:

- A **sword** takes two points per block, halving the number of blocks its
  material would otherwise allow.
  <!-- src: ItemSword.java:22 onBlockDestroyed -->
- **[[Shears]]** take a point only on [[Leaves]] and [[Cobweb]], and nothing at
  all for any other block. They last 239 blocks.
  <!-- src: ItemShears.java:10 onBlockDestroyed; ItemShears.java:6 setMaxDamage(238) -->
- A **hoe**, and anything that is not a tool, take nothing.

A tool is destroyed when its damage passes its material's maximum rather than
when it reaches it, which is why the counts above are one higher than the
material's rating. The block that destroys the tool still breaks, and still
drops.
<!-- src: ItemStack.java:127 damageItem, the > rather than >= -->

## Drops

Breaking a block and harvesting it are different things. The block is always
removed; the drop happens only if the player *can harvest* it, and that is
settled before the tool's speed comes into it at all.
<!-- src: PlayerControllerSP.java:35 sendBlockRemoved, which calls harvestBlock
     only when canHarvestBlock passed -->

Most blocks are harvestable by anything, including an empty hand. The question
is only ever asked of five materials — the only ones flagged as needing a tool:

| Material | Blocks | Harvested by |
|---|---|---|
| Rock | [[Stone]], [[Cobblestone]], every stone ore, [[Obsidian]], [[Bricks]], [[Sandstone]], [[Furnace]], [[Dispenser]], [[Monster Spawner]], [[Glowstone]], [[Netherrack]], the stone slabs and stairs | a pickaxe of sufficient level |
| Iron | [[Block of Iron]], [[Block of Gold]], [[Block of Diamond]], [[Iron Door]] | a pickaxe of sufficient level |
| Snow, built snow | [[Snow]], as a layer and as a block | a shovel, of any material |
| Web | [[Cobweb]] | a sword or [[Shears]] |

<!-- src: Material.java:114,115,129,130,136 setNoHarvest;
     InventoryPlayer.java:271 canHarvestBlock -->

Everything not on that list drops for a bare hand: [[Dirt]], [[Wood]],
[[Wool]], [[Sand]], [[Gravel]], [[Clay]], [[Soul Sand]], [[Rail|rails]],
redstone components and the rest.

### Harvest levels

Within rock and iron, the pickaxe also has to be good enough. The rule is a
sequence of explicit checks on the block rather than a general comparison of
tiers:

| Block | Needs |
|---|---|
| [[Obsidian]] | a [[Diamond Pickaxe]] exactly — level 3, not "3 or better" |
| [[Diamond Ore]], [[Block of Diamond]], [[Gold Ore]], [[Block of Gold]], [[Redstone Ore]] | iron or better |
| [[Iron Ore]], [[Block of Iron]], [[Lapis Lazuli Ore]], [[Lapis Lazuli Block]] | stone or better |
| Any other rock or iron block | any pickaxe |

<!-- src: ItemPickaxe.java:10 canHarvestBlock -->

A [[Golden Pickaxe]] sits at harvest level 0 alongside wood, so for all its
speed it cannot bring back iron, gold, redstone, lapis, diamond or obsidian.

Mining a block the pickaxe cannot harvest is not merely fruitless but slow, the
flat formula applying instead: [[Obsidian]] takes 50 seconds to remove with an
[[Iron Pickaxe]] and leaves nothing.

### What blocks actually give

Mining does not always return the block. The substitutions:

| Block | Drops |
|---|---|
| [[Stone]] | [[Cobblestone]] |
| [[Coal Ore]] | one {{sprite\|Coal}} |
| [[Diamond Ore]] | one {{sprite\|Diamond}} |
| [[Lapis Lazuli Ore]] | four to eight lapis lazuli |
| [[Redstone Ore]] | four or five {{sprite\|Redstone}} |
| [[Glowstone]] | two to four [[Glowstone Dust]] |
| [[Clay]] | four [[Clay Ball\|clay balls]] |
| [[Cobweb]] | one [[String]] |
| [[Snow]], as a layer | one [[Snowball]] |
| [[Snow]], as a block | four [[Snowball\|snowballs]] |
| [[Gravel]] | [[Flint]] one time in ten, gravel otherwise |
| [[Leaves]] | a [[Sapling]] one time in twenty |
| [[Iron Ore]], [[Gold Ore]] | the ore block itself, for [[Smelting\|smelting]] |

<!-- src: BlockOre.java:10; BlockRedstoneOre.java:56; BlockGlowStone.java:10;
     BlockClay.java:14; BlockWeb.java:32; BlockSnow.java:50;
     BlockSnowBlock.java:15; BlockGravel.java:10; BlockLeaves.java:155 -->

Three blocks give nothing at all, however they are broken: [[Glass]],
[[Bookshelf]] and [[Monster Spawner]]. [[Ice]] gives nothing either, and turns
into flowing [[Water]] on the spot if the block beneath it is solid or liquid.
<!-- src: BlockGlass.java:10; BlockBookshelf.java:14; BlockMobSpawner.java:14;
     BlockIce.java:20 harvestBlock -->

[[Shears]] change what [[Leaves]] give: cut with shears, a leaf block returns
itself, of the right wood, instead of rolling for a [[Sapling]]. Shears also
break leaves fast enough to clear the strength threshold on the first frame, so
they come away instantly.
<!-- src: BlockLeaves.java:163 harvestBlock; 15 / (0.2 * 30) = 2.5 per tick -->

## Where the ores are

Ore is placed after the terrain is shaped and the caves are cut. Each chunk gets
a fixed number of attempts per ore; every attempt picks a column in the chunk
and a starting height, and lays a vein two to four blocks above it.
<!-- src: ChunkProviderGenerate.java:353-408; WorldGenMinable.java:20 -->

| Ore | Attempts per chunk | Starting height | Vein size |
|---|---|---|---|
| [[Coal Ore]] | 20 | 0–127 | 16 |
| [[Iron Ore]] | 20 | 0–63 | 8 |
| [[Gold Ore]] | 2 | 0–31 | 8 |
| [[Redstone Ore]] | 8 | 0–15 | 7 |
| [[Diamond Ore]] | 1 | 0–15 | 7 |
| [[Lapis Lazuli Ore]] | 1 | 0–30, peaking at 15 | 6 |
| [[Dirt]] pockets | 20 | 0–127 | 32 |
| [[Gravel]] pockets | 10 | 0–127 | 32 |

Lapis is the odd one out. Its height is the sum of two draws from 0–15 rather
than one draw from 0–31, which makes it a triangular distribution centred on 15
instead of a flat band.
<!-- src: ChunkProviderGenerate.java:405 rand.nextInt(16) + rand.nextInt(16) -->

An attempt is not a vein. The generator only ever replaces [[Stone]], so a vein
rolled inside a cave, a lake, a dirt pocket or another ore quietly writes
nothing at all, and the vein size is an upper bound on what a successful attempt
places rather than a count.
<!-- src: WorldGenMinable.java:44, the getBlockId == Block.stone test -->

## Hazards

- **Lava fills the bottom of every cave.** Cave carving replaces stone with air
  above Y=10 and with flowing [[Lava]] at Y=9 and below, so the depths where
  diamond and redstone sit are also where open lava is guaranteed rather than
  incidental.
  <!-- src: MapGenCaves.java:134 -->
- **Lava springs and lakes.** Twenty attempts per chunk place a single lava
  source in a stone wall, at a height drawn from three nested rolls that
  concentrate them low. A lava lake gets one attempt in eight chunks, and above
  Y=64 only one in ten of those goes ahead.
  <!-- src: ChunkProviderGenerate.java:581 WorldGenLiquids;
       ChunkProviderGenerate.java:330 WorldGenLakes -->
- **[[Sand]] and [[Gravel]] fall.** Mining the block under either turns it into
  a [[Falling Sand]] entity, and a column of gravel over a tunnel comes down as
  a unit.
- **[[Bedrock]] is a band, not a floor.** Y=0 is always bedrock; Y=1 to Y=4 are
  bedrock at random. There is nothing beneath it to fall into, but there is no
  clean flat layer to work along either.
  <!-- src: ChunkProviderGenerate.java:132, y <= rand.nextInt(5) -->
- **Darkness spawns mobs.** Any unlit space large enough is a spawn site, so a
  tunnel lit only by the [[Torch]] behind the player is being repopulated behind
  them as they dig.

## On a server

The client decides when a block breaks and the server checks the arithmetic
afterwards. Three limits apply that do not exist in single-player.

- **Reach.** The client will not target a block more than 4 blocks away, and the
  server independently rejects any dig starting or finishing further than 6
  blocks from the player.
  <!-- src: PlayerControllerMP.java:120 getBlockReachDistance;
       NetServerHandler.java:250, the var14 > 36.0D distance-squared test -->
- **Re-timing.** The server counts ticks from the moment digging started and
  accepts the break once the block would be at least 70% destroyed. A break
  claimed earlier than that is deferred rather than rejected: the server holds
  the position and completes it on the tick its own counter fills.
  <!-- src: ItemInWorldManager.java:66 the >= 0.7F test;
       ItemInWorldManager.java:22 func_328_a, the deferred completion -->
- **Spawn protection.** In the [[Overworld]], a non-operator cannot break any
  block within 16 blocks of the world spawn, measured as the larger of the two
  horizontal distances. The server answers the attempt by sending the block
  back, so it reappears after a moment.
  <!-- src: NetServerHandler.java:263 -->

## Block hardness

Every block in the game, sortable by hardness. Multiply by 30 and divide by the
tool's speed for the tick count with a working tool, or by 100 for the count
without one.

{{list|blocks}}

## See also

- [[Crafting]] — turning what mining produces into the tools that mine faster
- [[Smelting]] — [[Iron Ore|iron]] and [[Gold Ore|gold]] stay ore until a
  [[Furnace]] has them
- [[Dungeon]] — the one structure worth tunnelling towards
