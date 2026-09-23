---
title: Mining
description: How blocks are broken in Beta 1.7.3 — breaking speed, tools, harvest levels and what drops.
type: mechanic
categories: [Game mechanics]
---

**Mining** is breaking a block in the world by holding the attack button on it.

## Breaking a block

Damage to a block is measured in *strength* — a fraction added once per tick,
with the block breaking on the tick the running total reaches 1. Strength comes
from one of two formulas, depending on whether the player can harvest the block
at all:

- **Harvestable** — `speed ÷ (hardness × 30)` per tick, where *speed* is the
  held item's multiplier against that particular block, default of 1 for a bare
  hand or non-tool
- **Not harvestable** — `1 ÷ (hardness × 100)` per tick, flat. The held item is
  never consulted on this branch, so a wooden pickaxe chews through
  [[Diamond Ore]] at exactly the speed of a bare fist.

<!-- src: Block.java:327 blockStrength -->

Breaking time in ticks is one divided by that, rounded up: `hardness × 30 ÷
speed` when the block is harvestable, and a flat `hardness × 100` when it is
not. There are twenty ticks in a second.

The following table shows breaking times for [[Stone]], which has a hardness
of 1.5:

| Held item | Speed | Ticks | Seconds |
|---|---|---|---|
| {{sprite\|Wooden Pickaxe}} | 2 | 23 | 1.15 |
| {{sprite\|Stone Pickaxe}} | 4 | 12 | 0.6 |
| {{sprite\|Iron Pickaxe}} | 6 | 8 | 0.4 |
| {{sprite\|Diamond Pickaxe}} | 8 | 6 | 0.3 |
| {{sprite\|Golden Pickaxe}} | 12 | 4 | 0.2 |
| Anything else, or nothing | — | 150 | 7.5 |

The count starts on the tick *after* the block is first targeted: the first
tick on a new target only records its position. Looking away and back resets
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

A *negative* hardness results in negative strength, preventing the target
block from ever being broken. Only [[Bedrock]] and the [[Portal]] block have
negative hardness.
<!-- src: Block.java:328 blockStrength; Block.java:207 setBlockUnbreakable -->

### The five-tick floor

Instant blocks do not come down twenty a second. Two separate delays cap the
rate, and they work independently of each other.

The first is a countdown on the controller. Finishing a block through the damage
counter sets it to 5, and every tick it stands above zero is spent decrementing
it: no target is read and no damage is added to anything. Five ticks go that
way, and the sixth is the re-target tick, which only stores the new block's
position. Holding the attack button down therefore leaves **seven ticks**, just
over a third of a second, between one block breaking and the next taking its
first damage.
<!-- src: PlayerControllerSP.java:83 blockHitWait = 5;
     PlayerControllerSP.java:62 the > 0 branch, which returns before damaging;
     PlayerControllerSP.java:85 the else branch, which only stores the position -->

The second is auto-repeat. Holding the button re-runs the click path once every
five ticks — `ticksPerSecond / 4`, against a timer running at 20 — while a fresh
press runs it at once, with no such test. That click path is the one that breaks
a zero-hardness block, so instant blocks come down on the auto-repeat rather
than through the damage counter, and a player clicking faster than five ticks
apart breaks them faster than a player holding the button.
<!-- src: Minecraft.java:1012 the ticksRan - mouseTicksRan >= ticksPerSecond / 4.0F
     test; Minecraft.java:114 new Timer(20.0F);
     Minecraft.java:1112 the press event, which calls clickMouse ungated -->

Clicking at nothing — swinging at air rather than at a block — costs ten ticks
during which left-click does nothing at all.
<!-- src: Minecraft.java:809 leftClickCounter = 10 -->

### Releasing the attack button

Once a tick the game asks whether the attack button is down and the crosshair is
on a block. Whenever either answer is no it calls `resetBlockRemoving`, and that
does more than discard the accumulated damage: it zeroes the five-tick countdown
and the ten-tick air-swing lockout as well. Both are cancelled outright rather
than left to run down.
<!-- src: Minecraft.java:779 func_6254_a — the leftClickCounter = 0 at the top
     and the else branch calling resetBlockRemoving;
     PlayerControllerSP.java:56 resetBlockRemoving, which zeroes blockHitWait -->

Releasing and re-pressing the button does therefore start the next block sooner.
The countdown dies on the tick the button reads as up, the press re-targets on
the tick after, and damage begins on the tick after that — three ticks against
the seven a held button costs:

| Tick | Button held | Button released and re-pressed |
|---|---|---|
| T | the block breaks, countdown set to 5 | the block breaks, countdown set to 5 |
| T+1 | countdown 5 → 4 | button up: damage and countdown both zeroed |
| T+2 | countdown 4 → 3 | button down: the new block is targeted |
| T+3 | countdown 3 → 2 | first damage |
| T+4 | countdown 2 → 1 | |
| T+5 | countdown 1 → 0 | |
| T+6 | the new block is targeted | |
| T+7 | first damage | |

Two things bound it. The button must read as up at the moment the check runs, so
a release and a press inside one tick achieve nothing — the check sees a button
that never left the mouse. And the same reset throws away accumulated damage, so
letting go part-way through a block loses that progress; it is free only in the
window straight after a break, where the damage is already zero.

Looking away costs nothing extra, because it is the same reset. A crosshair that
leaves the block for a tick cancels the countdown exactly as a released button
does.

That is the single-player controller. Multiplayer runs a different one, on which
letting go does not clear the countdown; re-pressing still pays there, but for a
different reason. See [[Mining#The pause in multiplayer|the pause in multiplayer]].

### Water and falling

Two conditions reduce the player's speed, and both are checked *only* when
mining a harvestable block:

- Mining with the head underwater divides speed by five.
- Mining while not standing on the ground divides speed by five.

<!-- src: EntityPlayer.java:291 getCurrentPlayerStrVsBlock -->

They stack, so mining from a jump underwater runs at a twenty-fifth of normal
speed. The test for water samples eye level rather than the feet, so standing
waist-deep costs nothing.
<!-- src: Entity.java:588 isInsideOfMaterial, which samples posY + eye height -->

Because both penalties only apply to harvestable blocks, they do not apply at
all to a block the player cannot harvest. Punching [[Stone]] bare-handed takes
7.5 seconds whether the player is dry and standing still or swimming in mid-fall.

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
[[Diamond Pickaxe]] takes it at speed 1 — fifteen seconds a block. Neither are
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
removed; the drop happens only if the player *can harvest* it.
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

This table is separate from the lists of what each tool is effective against.
A tool can harvest a block it is not effective against.

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
speed it cannot harvest iron, gold, redstone, lapis, diamond or obsidian.

Mining a non-harvestable block always uses the slow `strength = 1 ÷ (hardness × 100)`
formula.

### What blocks drop

Mining does not always return the block. The substitutions:

| Block | Drops |
|---|---|
| {{sprite\|Stone}} | {{sprite\|Cobblestone}} |
| {{sprite\|Coal Ore}} | one {{sprite\|Coal}} |
| {{sprite\|Diamond Ore}} | one {{sprite\|Diamond}} |
| {{sprite\|Lapis Lazuli Ore}} | four to eight {{sprite\|Lapis Lazuli}} |
| {{sprite\|Redstone Ore}} | four or five {{sprite\|Redstone}} |
| {{sprite\|Glowstone}} | two to four {{sprite\|Glowstone Dust}} |
| {{sprite\|Clay}} | four {{sprite\|Clay Ball\|text=clay balls}} |
| {{sprite\|Cobweb}} | one {{sprite\|String}} |
| {{sprite\|Snow}}, as a layer | one {{sprite\|Snowball}} |
| {{sprite\|Snow}}, as a block | four {{sprite\|Snowball\|text=snowballs}} |
| {{sprite\|Gravel}} | {{sprite\|Flint}} one time in ten, gravel otherwise |
| {{sprite\|Leaves}} | a {{sprite\|Sapling}} one time in twenty |
| {{sprite\|Iron Ore}}, {{sprite\|Gold Ore}} | the ore block itself, for [[Smelting\|smelting]] |

<!-- src: BlockOre.java:10; BlockRedstoneOre.java:56; BlockGlowStone.java:10;
     BlockClay.java:14; BlockWeb.java:32; BlockSnow.java:50;
     BlockSnowBlock.java:15; BlockGravel.java:10; BlockLeaves.java:155 -->

Three blocks give nothing at all, however they are broken: [[Glass]],
[[Bookshelf]] and [[Monster Spawner]]. [[Ice]] gives nothing either, and turns
into flowing [[Water]] on the spot if the block beneath it is solid or liquid.
<!-- src: BlockGlass.java:10; BlockBookshelf.java:14; BlockMobSpawner.java:14;
     BlockIce.java:20 harvestBlock -->

[[Shears]] change what [[Leaves]] give: cut with shears, a leaf block returns
itself, of the right wood, instead of rolling for a [[Sapling]].
<!-- src: BlockLeaves.java:163 harvestBlock; 15 / (0.2 * 30) = 2.5 per tick -->

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

### The pause in multiplayer

Multiplayer runs its own controller, and the five-tick countdown works
differently on it. Letting go of the button does not zero it — the reset cancels
the dig and leaves the countdown where it is — and the countdown only runs down
while a dig is armed, which happens in the click path. So the five ticks are
paid whatever the player does. What re-pressing skips is the wait for the click
path itself, and that is worth having.
<!-- src: PlayerControllerMP.java:70 the isHittingBlock guard around the
     countdown; PlayerControllerMP.java:64 resetBlockRemoving, which clears
     isHittingBlock but not blockHitDelay; PlayerControllerMP.java:96
     blockHitDelay = 5; PlayerControllerMP.java:52 clickBlock arming the dig -->

For an ordinary block, a held button leaves six to ten ticks between one block
breaking and the next taking damage, depending on where the break falls in the
five-tick auto-repeat cycle. A press on the tick after the release runs the
click path at once and makes it a flat seven — worth about a tick a block on
average, and nothing at all when the break happens to land just before an
auto-repeat would have fired anyway.

For an instant block the difference is much larger, because in multiplayer the
click path is the only thing that breaks one. `clickBlock` removes a
zero-hardness block without arming a dig, so the damage counter never runs on it
at all, and a held button takes exactly four a second. Each fresh press takes
one at once, so clicking is as fast as the player can click.
<!-- src: PlayerControllerMP.java:49 the blockStrength >= 1.0F branch, which
     returns before the isHittingBlock = true in the else below it, leaving
     sendBlockRemoving's isHittingBlock guard closed -->

The exception is a dig already armed on some other block. The controller answers
a target that is not the armed one by calling the click path again, once a tick
and with no auto-repeat test, and breaking an instant block that way still
leaves the armed position untouched — so every later target mismatches too. A
player who starts on [[Stone]] and then sweeps across [[Torch\|torches]] or
[[Tall Grass]] without letting go takes one a tick, twenty a second, until the
button comes up.
<!-- src: PlayerControllerMP.java:99 the else branch calling clickBlock;
     PlayerControllerMP.java:52 currentBlockX/Y/Z are only written on the
     non-instant path, so they stay on the armed block -->

## Block hardness

Every block in the game, sortable by hardness. Multiply by 30 and divide by the
tool's speed for the tick count with a working tool, or by 100 for the count
without one.

{{list|blocks}}
