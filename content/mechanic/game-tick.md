---
title: Game Tick
description: The step the world advances in, twenty times a second — the order of work in a tick, neighbour updates, scheduled ticks and random ticks.
type: mechanic
categories: [Game mechanics]
aliases: [Tick, Random Tick, Scheduled Tick, Neighbour Update]
---

A **game tick** is one step of the world simulation, run 20 times a second.

## The loop

A server measures how much real time has passed since its last pass and banks
it, then runs one tick for every 50 milliseconds banked. A tick is never partly
run.
<!-- src: MinecraftServer.java:254 the accumulator tested against 50L -->

Singleplayer holds the same rate with a timer that turns elapsed real time into
whole ticks, and runs at most 10 of them between two frames.
<!-- src: Minecraft.java:114 new Timer(20.0F), :535 the elapsedTicks loop;
     Timer.java:60 the clamp -->

A frame is not a tick. Each frame is drawn part of the way from the last tick to
the next, with positions and angles interpolated across the gap.
<!-- src: Timer.java:64 renderPartialTicks; Minecraft.java:569
     updateCameraAndRender -->

Most open screens stop the world in singleplayer. Ticks keep running, and
input and the interface are still handled, but every part of a tick that touches
the world is skipped, particles included. The [[Chest|chest]], [[Furnace|furnace]],
[[Crafting Table|crafting table]] and inventory screens are the exception, along
with the death screen.
<!-- src: Minecraft.java:610 sets isGamePaused from currentScreen.doesGuiPauseGame();
     GuiContainer.java:168 and GuiGameOver.java:45 return false; the world calls
     at Minecraft.java:1160 and :1165 are gated on it -->

## What one tick does

The world tick runs in this order:

| Order | Step |
|---|---|
| 1 | Rain and thunder timers advance |
| 2 | The night is skipped if every player is asleep |
| 3 | [[Mob Spawning\|Mobs spawn]] |
| 4 | Up to 100 queued chunks are saved and unloaded |
| 5 | The sky light reduction for the time of day is recalculated |
| 6 | The world time advances by one, and every 40th tick starts a save |
| 7 | Scheduled ticks that have come due run |
| 8 | Each active chunk gets its weather rolls and 80 random ticks |

<!-- src: World.java:1745 tick -->

Entities and block entities are updated in a pass of their own. Singleplayer
runs that pass before the world tick, a server after it.
<!-- src: Minecraft.java:1160 updateEntities, :1165 tick;
     MinecraftServer.java:328 tick, :333 updateEntities -->

## Entities

Every entity in the world list is updated once per tick, in list order. The
update stores the previous position for interpolation, applies gravity and
motion, resolves collisions, and then runs whatever the entity does for itself.
<!-- src: World.java:1208 the loadedEntityList loop; Entity.java:193
     onEntityUpdate -->

An entity is skipped unless every chunk within 32 blocks of it is loaded. An
entity carrying a passenger updates the passenger immediately after itself, so a
rider never lags its mount by a tick.
<!-- src: World.java:1294 checkChunksExist at byte var5 = 32, :1344 the
     riddenByEntity call -->

Entities that die during the pass are dropped from the list before the next one.

Most of what a tick means for an entity is a counter moving by one:

| Counter | Effect |
|---|---|
| Burning | 1 [[Damage\|damage]] every 20 ticks, counting down to zero |
| Air | 300 at the surface, falling by 1 each tick underwater; 2 damage every 20 ticks once it is gone |
| Death | the body drops its items at once and lies for 20 ticks before it is removed |
| Item age | a dropped item disappears after 6000 ticks — 5 minutes |
| Fuse | [[Primed TNT\|primed TNT]] explodes 80 ticks after it is lit |

<!-- src: Entity.java:247 fire, :259 the kill below y = -64; Entity.java:100
     maxAir = 300; EntityLiving.java:123 drowning, :357 onDeath at zero health
     and :418 dropFewItems, :157 deathTime;
     EntityItem.java:73; EntityTNTPrimed.java:21 -->

## Block entities

Every block entity is offered a tick, and three of the nine kinds use it. The
[[Furnace|furnace]] burns fuel and advances its smelt, the
[[Monster Spawner|monster spawner]] counts down its delay, and a moving
[[Piston|piston]] advances its animation. The [[Chest|chest]], [[Sign|sign]],
[[Dispenser|dispenser]], [[Note Block|note block]] and [[Jukebox|jukebox]] hold
state but keep no timer.
<!-- src: World.java:1236 the loadedTileEntityList loop; TileEntity.java:42 is
     empty, and only TileEntityFurnace:105, TileEntityMobSpawner:25 and
     TileEntityPiston:105 override it -->

## Neighbour updates

Changing a block tells its six neighbours, within the same tick. They are told
in the order −x, +x, −y, +y, −z, +z.
<!-- src: World.java:506 notifyBlocksOfNeighborChange -->

Nothing is queued. A notified block that changes another block notifies again
from inside the first notification, so a whole [[Redstone Dust|redstone]] line
settles before the tick that started it is over.

A block told about a neighbour rarely acts at once. It schedules a tick instead,
which is where redstone's delays come from.

## Scheduled ticks

A block asks the world to call it back a fixed number of ticks later. The
request records the position and the block id.
<!-- src: World.java:1152 scheduleBlockUpdate -->

One set holds every pending tick in the world. There is no queue per block type
and none per chunk. Entries are ordered by due time first and by a serial number
second, so ticks that come due together run in the order they were asked for.
<!-- src: World.java:17 the single TreeSet on World;
     NextTickListEntry.java:38 comparer, breaking a tie on tickEntryID from a
     static counter -->

At most 1000 scheduled ticks run in one tick. Anything still due waits for the
next one.
<!-- src: World.java:1972 -->

Two conditions are checked before a due tick runs. Every chunk within 8 blocks
must be loaded, and the block at the position must still be the one that asked.
A block broken while its tick was pending gets nothing.
<!-- src: World.java:1984 checkChunksExist, then the var6 == var4.blockID test -->

One position holds one pending tick per block id, so asking twice before the
first comes due achieves nothing.
<!-- src: World.java:1170 the scheduledTickSet.contains guard;
     NextTickListEntry.equals compares position and block id only -->

| Block | Delay |
|---|---|
| {{sprite\|Redstone Torch}} | 2 ticks |
| {{sprite\|Redstone Repeater}} | 2, 4, 6 or 8 ticks, by setting |
| {{sprite\|Sand}} {{sprite\|Gravel}} | 3 ticks |
| {{sprite\|Dispenser}} | 4 ticks |
| {{sprite\|Water}} | 5 ticks |
| {{sprite\|Button}} {{sprite\|Pressure Plate}} {{sprite\|Detector Rail}} | 20 ticks |
| {{sprite\|Lava}} | 30 ticks |
| {{sprite\|Fire}} | 40 ticks |

<!-- src: BlockRedstoneTorch.java:41; BlockRedstoneRepeater.java:6, the
     {1,2,3,4} array doubled at :95; BlockSand.java:45; BlockDispenser.java:13;
     BlockFluid.java:187; BlockButton.java:15; BlockPressurePlate.java:17;
     BlockDetectorRail.java:12; BlockFire.java:51 -->

## Random ticks

A random tick picks one block out of an active chunk and calls the same
`updateTick` a scheduled tick would. Eighty are drawn per chunk per tick, from
the whole 16×16×128 column, so a given block is picked about once every 410
ticks — around 20 seconds.
<!-- src: World.java:1952; 32768 positions against 80 draws gives 409.6 -->

Positions come from a counter the world keeps rather than from its random number
generator, and nothing stops the same block being drawn twice in a tick.
<!-- src: World.java:1953, the field_9437_g * 3 + 1013904223 sequence -->

A chunk more than 9 chunks from every player draws none, so nothing grows there
however long the world runs.

Only blocks flagged for it do anything when drawn:

| Block | On a random tick |
|---|---|
| {{sprite\|Grass}} | spreads to nearby {{sprite\|Dirt}}, or turns back to dirt in the dark |
| {{sprite\|Flower}} {{sprite\|Rose}} {{sprite\|Tall Grass}} {{sprite\|Dead Bush}} | drop if the spot has become illegal |
| {{sprite\|Crops}} | the same check, then one growth stage in light 9 or better |
| {{sprite\|Sapling}} | the same check, then one stage, then a tree |
| {{sprite\|Brown Mushroom\|text=Mushroom}} | spreads to a nearby space, 1 time in 100 |
| {{sprite\|Cactus}} {{sprite\|Sugar cane}} | advance one of 16 stages, and grow a block on the sixteenth, up to three tall |
| {{sprite\|Farmland}} | wets to full beside water, dries one stage otherwise, and turns to dirt when dry — 1 time in 5 |
| {{sprite\|Leaves}} | decay when a nearby break has flagged them and no {{sprite\|Wood\|text=log}} is within 4 blocks |
| {{sprite\|Fire}} | spreads to what it can reach, and burns out |
| {{sprite\|Water}} {{sprite\|Lava}} | flowing forms recompute where they flow |
| {{sprite\|Ice}} | melts above block light 8 |
| {{sprite\|Snow}} | melts above block light 11 |
| {{sprite\|Redstone Ore}} | stops glowing |
| {{sprite\|Redstone Torch}} | rechecks whether it should be lit |
| {{sprite\|Torch}} | reattaches itself, or drops, if it has no facing set |
| {{sprite\|Button}} {{sprite\|Pressure Plate}} {{sprite\|Detector Rail}} | release |
| {{sprite\|Locked chest}} | vanishes |
| {{sprite\|Cake}} {{sprite\|Pumpkin}} {{sprite\|Jack 'o' Lantern}} | nothing |

<!-- src: the setTickOnLoad(true) call in each Block* constructor, plus
     Block.java:687 for the locked chest; BlockCake and BlockPumpkin are flagged
     but never override Block.updateTick, which is empty at Block.java:297;
     BlockLeaves.java:37 onBlockRemoval sets the decay bit on leaves within 1 -->

Still water takes no random ticks. Still lava does, which is how a lava pool
sets fire to what is above it.
<!-- src: BlockStationary.java:7 clears the flag, then sets it again for lava -->

### Skipping a delay

A block can be flagged for random ticks and schedule ticks as well, and one
`updateTick` serves both. A random draw then does the work early, before the
delay it was waiting on has run out:

| Block | An early draw |
|---|---|
| {{sprite\|Redstone Torch}} | toggles inside its 2 ticks |
| {{sprite\|Button}} {{sprite\|Pressure Plate}} {{sprite\|Detector Rail}} | release inside their 20 |
| {{sprite\|Fire}} | spreads and burns down inside its 40 |
| {{sprite\|Water}} {{sprite\|Lava}} | recompute their flow inside their 5 and 30 |

<!-- src: the intersection of the setTickOnLoad(true) constructors and the
     scheduleBlockUpdate callers: BlockRedstoneTorch, BlockButton,
     BlockPressurePlate, BlockDetectorRail, BlockFire, BlockFlowing -->

The odds are the random-tick odds — about 1 in 410 for each tick the block
spends waiting, and nothing at all beyond 9 chunks from a player.

The {{sprite|Redstone Repeater}} and the {{sprite|Dispenser}} are not flagged,
and neither are falling {{sprite|Sand}} and {{sprite|Gravel}}. Their delays are
exact.

## Display ticks

The client runs a random tick of its own for particles. Once a tick it takes
1000 stabs at a block within 15 in each direction of the player and asks it for a
display effect, which is what makes torches smoke and [[Nether Portal|portals]]
shimmer. None of it touches the world, and a server never does it.
<!-- src: World.java:1997 randomDisplayUpdates; Minecraft.java:1169 -->

## The world clock

The world time advances by one every tick, and a full day is 24000 ticks — 20
minutes. Sky light is recalculated from it each tick, and every renderer is
refreshed on the ticks where the figure changes.
<!-- src: World.java:1763 calculateSkylightSubtracted, :1772 the increment -->

[[Weather]] runs on countdowns of its own. Rain and thunder each hold a number
of ticks, and the state flips when the number reaches zero. Rain lasts 12000 to
24000 ticks and stays away for 12000 to 180000; thunder lasts 3600 to 15600
ticks over the same gap. Rain fades in and out at 0.01 a tick, taking 100 ticks
either way.
<!-- src: World.java:1792 updateWeather -->

Every 40th tick starts a save. A server writes at most 24 modified chunks before
leaving the rest until next time, singleplayer at most 2.
<!-- src: World.java:1773 against autosavePeriod = 40 (World.java:81);
     ChunkProviderServer.java:159 and ChunkProviderLoadOrGenerate.java:177 -->

While every player is asleep a server stops waiting 50 milliseconds between
ticks and runs them as fast as it can.
<!-- src: MinecraftServer.java:250, the isAllPlayersFullyAsleep branch calls
     doTick once per pass and clears the accumulator -->

## In multiplayer

The server ticks the world. A client ticks a world that only advances its clock,
reads packets and updates entities: it spawns no mobs, runs no scheduled ticks,
draws no random ticks, and keeps no weather timers.
<!-- src: WorldClient.java:22 tick; scheduleBlockUpdate, TickUpdates and
     updateBlocksAndPlayCaveSounds are empty overrides at :73-81 -->

Neighbour updates are suppressed on a client too, so a block a player places
changes nothing around it until the server says so.
<!-- src: World.java:516 skips notification when multiplayerWorld is set -->

## Falling behind

A server that cannot keep up clamps the gap since its last pass to 2000
milliseconds and logs `Can't keep up! Did the system time change, or is the
server overloaded?`. Ticks past the 40 that fit in that gap are never run, and
the world falls behind real time.
<!-- src: MinecraftServer.java:238 -->

Singleplayer has no warning and no catch-up past 10 ticks a frame, so the world
runs slow below 2 frames a second.
<!-- src: Timer.java:60 -->
