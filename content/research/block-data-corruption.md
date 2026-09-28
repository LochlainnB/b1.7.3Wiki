---
title: Block Data Corruption
description: An investigation into corrupting block data to obtain items survival never gives, such as sponge - what works, what cannot, and how each claim was tested.
type: research
categories: [Research]
aliases: [Unobtainable items, Obtaining unobtainable items]
---

**Block data corruption** is an investigation into whether a survival player can
corrupt the world's block data to obtain items the game never hands out, such as
[[Sponge|sponge]].

## Summary

The question was whether any mechanism in the game lets a survival player
obtain an item that normal play never produces. Two kinds of item qualify: the
item form of a block that never drops itself, such as sponge, bedrock or grass,
and an ordinary item with a damage value the game never assigns, such as a
fourth kind of wood.

The answer has two parts.

**Invalid damage values: yes, for 26 items.** Two methods produce them:

- A two-piston machine, the *moving piston merge*, gives any pushable block the
  metadata of a piece of wool. Only two pushable blocks carry that metadata into
  the item they drop: [[Wood|wood]], whose valid values are 0 to 2, and the
  [[Stone Slab|slab]], whose valid values are 0 to 3. That makes wood with damage
  3 to 15 and slabs with damage 4 to 15 obtainable. The machine was built
  through a player's own placement and lever code on a vanilla dedicated server,
  fired, and mined by that player, who ended up holding the invalid items.
- An oak tree grown over a lit redstone torch replaces the torch with leaves
  that briefly carry the torch's metadata. A piston that breaks them in that
  moment gets a [[Sapling|sapling]] with damage 3, one time in 20.

The page [[Block Transmutation]] gives both in the wiki's reference style.

**New block or item IDs: no.** Every block ID the game writes into the world
and every item it creates traces back to a constant in the code or to a block
already in the world. Nothing in the game ever creates sponge, bedrock is never
dropped, and no transmutation changes a block's ID. The 1.12-era technique of
corrupting data with a race condition has nothing to work with here: in both
singleplayer and on a server, only one thread ever touches the world.

Three side findings came out of the same work:

- A [[Piston|piston]] can push a [[Furnace|furnace]] in the tick the furnace
  lights or goes out (tested). The furnace loses its contents and stays lit for good.
- The world's chunk map treats chunks 524,288 blocks apart as the same chunk.
  A block placed at one position reads back 524,288 blocks east of it (tested on
  a server).
- Holding the pointer over an invalid slab in any inventory screen should crash
  the client: the tooltip indexes a four-entry list of slab names. The exception
  was reproduced by calling the client's code directly; the crash itself was not
  seen in a running game.

## Status

As of 29 September 2026:

| Claim | Evidence |
|---|---|
| The moving piston merge transfers wool's metadata to a pushed block | tested |
| Wood 3 to 15 and slabs 4 to 15 can be obtained in survival | tested (values 3, 5, 9 and 15) |
| A tree grown over a lit torch can drop a sapling with damage 3 | tested (4 from 100 trees) |
| No other invalid-damage item can be obtained | read |
| No mechanism creates a block ID or item ID | read |
| No thread but the main one touches the world | read |
| Pistons can push a furnace in the tick it lights | tested |
| Chunks 524,288 blocks apart share one chunk object | tested on the server, read for singleplayer |
| Hovering an invalid slab crashes the client | read; the exception reproduced outside the game |
| Other transmutation methods (liquids, placement) | reported elsewhere, not tested here |

Every *tested* claim was run on the vanilla Beta 1.7.3 dedicated server under
the Babric loader, with a mod that adds console commands and changes no game
behaviour. None was run in a singleplayer client.

## Background

### The question

The research brief asked for any method of corrupting block data, or otherwise
obtaining normally unobtainable items, with sponge as the example.

### Unobtainable items

An item stack is an item ID, a count and a damage value. Blocks 1 to 96 each
have an item form: the game gives every block an item, so a stack with ID 19 is
a sponge.
<!-- src: Block.java:699 creates an ItemBlock for every block without one -->

A block's item form is unobtainable when nothing in survival drops or makes it.
The reasons fall into three groups:

- **Not in the world.** Sponge and [[Locked Chest|locked chest]] are never
  generated and never crafted.
- **Never dropped at all.** [[Bedrock|Bedrock]] cannot be broken. Fire, water,
  lava, portal blocks, [[Ice|ice]], [[Monster Spawner|monster spawners]],
  [[Dead Bush|dead bushes]], cake, piston heads and moving pistons drop nothing
  when broken.
- **Drop something else.** [[Grass|Grass]] drops dirt; the coal, diamond, lapis
  lazuli and redstone ores drop their items; [[Cobweb|cobweb]] drops string;
  [[Tall Grass|tall grass]] and [[Fern|ferns]] drop seeds or nothing;
  [[Farmland|farmland]], [[Snow|snow]] layers,
  [[Double Stone Slab|double slabs]], lit furnaces, unlit redstone torches and
  the blocks that items place (beds, doors, signs, crops, sugar cane, redstone
  dust and repeaters) all drop something other than themselves.

The second kind of unobtainable item is an ordinary item with a damage value
the game never assigns: the prior work calls these *invalid data values*, IDVs.

### Block data

A [[Chunk|chunk]] stores each block as an 8-bit block ID in one array and a
4-bit metadata value in a second array. Metadata means different things to
different blocks: wood kind, wool colour, a torch's facing, a crop's growth
stage. A block with a metadata value its code never assigns is an IDV block.
<!-- src: Chunk.java:12 blocks, :15 data (NibbleArray) -->

A block becomes an item in one of these ways, all *read*:

- **Breaking it**, by a player, an explosion or a piston: the block's
  `idDropped`, `quantityDropped` and `damageDropped` decide the drop
  (`Block.java:339`).
- **Shears on leaves**, which drop leaves (`BlockLeaves.java:163`).
- **A falling block that cannot land**, which drops its own block ID
  (`EntityFallingSand.java:63`). Only sand and gravel ever fall.
- **Contents**: chests, furnaces, dispensers and a jukebox's record.
- **Mob drops**, fixed per mob.

### Prior work

The Minecraft Discontinued Features Wiki documents both lines of inquiry the
brief named. It is *reported* evidence. Of its methods, this page tested only
the moving piston merge.

- **[Block Transmutation](https://mcdf.wiki.gg/wiki/Java_Edition:Block_Transmutation)**
  lists nine methods of giving blocks IDVs across Indev to 1.12. Three are
  given for Beta 1.7.3: *liquid transmutation* (Beta 1.7 to 1.2.3), the
  *moving piston merge* (Beta 1.7.2 to 1.9 pre-release 5) and *onBlockPlaced
  piston transmutation* (Beta 1.7.3). It notes that a few IDV blocks drop IDV
  items when mined.
- **[Parallel Asynchronous Threads](https://mcdf.wiki.gg/wiki/Java_Edition:Parallel_Asynchronous_Threads)**
  documents the race condition used in 14w32a to 17w46a. Placing stained glass
  started a thread that searched downward for beacons. That thread could load
  and populate chunks off the main thread while the main thread unloaded
  others, and chains of observers turned the resulting async block updates into
  torn writes: corrupted palettes, impossible block states, and falling blocks
  carrying the wrong block. This is the "block data corruption in 1.12 using a
  race condition" the brief referred to. It depends on a thread that touches the
  world, and Beta 1.7.3 has none (see the findings).

## Method

### Sources

- The decompiled game, client and server trees with MCP names, read-only and
  kept outside the repository (see `AGENTS.md`). Line numbers below refer to it.
  A path without a tree is the client tree, `minecraft/net/minecraft/src/`.
- The shipped jars: Mojang's `client.jar` and `server.jar`, as downloaded by
  BabricKit's `bk.py setup`.
- Three mapping sets: *barn* (Babric's partial names, what a mod compiles
  against), *intermediary* (`class_18`, `method_154`), and *biny* (Glass
  Launcher's fuller names, used only as a dictionary).

### Names

The decompiled source uses MCP names; a Babric mod compiles against barn names,
which cover only a fraction of the game, falling back to intermediary names for
the rest. Biny names almost everything, and its mapping file lists the
intermediary and obfuscated names beside each biny name, so it serves as the
bridge. `binyq.py` (Appendix B) looks a biny name up and prints the name to use
in code:

```
$ python binyq.py "^net/minecraft/world/World$" "setBlock"
CLASS net/minecraft/world/World  = net/minecraft/class_18  (barn: net/minecraft/world/World)  obf client=fd server=dj
   m setBlockWithoutNotifyingNeighbors      -> method_154       (IIIII)Z
   m setBlock                               -> method_201       (IIIII)Z
   ...
```

The MCP-to-intermediary pairs used in this work:

| MCP name | Intermediary | What it does |
|---|---|---|
| `World.setBlockAndMetadata` | `method_154` | set ID and metadata, no neighbour updates |
| `World.setBlockAndMetadataWithNotify` | `method_201` | the same, then update the neighbours |
| `World.setBlock` | `method_200` | set ID, no updates |
| `World.setBlockWithNotify` | `method_229` | set ID, then update the neighbours |
| `World.setBlockMetadata` | `method_223` | set metadata, no updates |
| `World.setBlockMetadataWithNotify` | `method_215` | set metadata, then update |
| `World.notifyBlocksOfNeighborChange` | `method_244` | update the six neighbours |
| `World.getBlockMetadata` | `method_1778` | |
| `World.createExplosion` | `method_187` | |
| `World.loadedTileEntityList` | `field_199` | every ticking block entity |
| `Chunk.chunkTileEntityMap` | `field_964` | the chunk's own block entity map |
| `Block.dropBlockAsItem` | `method_1592` | |
| `Block.onNeighborBlockChange` | `method_1609` | |
| `TileEntityPiston` | `class_283` | fields `field_1761` to `field_1767` |
| `TileEntityFurnace` | `class_138` | |
| `EntityItem.item` | `class_142.field_564` | |
| `ItemInWorldManager` | `class_70` | `method_1834` harvests, `method_1832` uses an item |
| `NetServerHandler.teleportTo` | `class_11.method_832` | |
| `ConsoleCommandHandler.handleCommand` | `class_426.method_1411` | |

### The lab mod

*TransmuteLab* is a server-side Babric mod whose only job is to expose
single vanilla methods as console commands. One mixin intercepts the server's
console command handler; everything else calls the game's own methods. It does
not change how any block behaves. Its full source is in Appendix A.

| Command | Calls | Use |
|---|---|---|
| `lab set x y z id [meta]` | `setBlockAndMetadata` | build without updating neighbours |
| `lab setn x y z id [meta]` | `setBlockAndMetadataWithNotify` | place and update, like a trigger |
| `lab meta` / `lab metan` | `setBlockMetadata` / `...WithNotify` | |
| `lab fill x1 y1 z1 x2 y2 z2 id [meta]` | `setBlockAndMetadata` in a box | floors and clearing |
| `lab upd x y z` | the block's own `onNeighborBlockChange` | poke one block |
| `lab notify x y z` | `notifyBlocksOfNeighborChange` | |
| `lab get x y z` | reads ID, metadata and the chunk's block entity | |
| `lab box x1 y1 z1 x2 y2 z2 tag` | `get` over a box | |
| `lab tes x y z r tag` | walks `loadedTileEntityList` | flags block entities the chunk does not hold as `ORPHAN` |
| `lab items x y z r tag` / `lab clearitems` | lists or removes item entities | |
| `lab drop x y z` | `dropBlockAsItem` with the block's metadata | what breaking yields |
| `lab boom x y z power` | `createExplosion` | |
| `lab dig x y z` | the first player's `ItemInWorldManager.tryHarvestBlock` | the server's own mining path |
| `lab use x y z side` | the first player's `activeBlockOrUseItem` with the held stack | what a place packet does |
| `lab give id count [damage]`, `lab select slot`, `lab inv`, `lab tp x y z [yaw]` | the first player | |
| `lab furnace x y z inId inN fuelId fuelN` | fills a furnace's slots 0 and 1 | |
| `lab droplog on` / `off` | logs every `dropBlockAsItemWithChance` call | which break made which item |
| `lab spawn`, `lab mark text` | | |

Two things about the commands matter. `lab set` skips only the neighbour
updates: the chunk still calls the new block's `onBlockAdded`, so a lit redstone
torch still updates the blocks around it when placed, and a piston still checks
its power. Build order therefore matters. And the commands that report a
block entity read it straight from the chunk's map, because `World.getBlockTileEntity` creates a block entity
for a container that lacks one, and for a furnace also rewrites its metadata;
a probe must not do that.
<!-- src: Chunk.java:401 getChunkBlockTileEntity creates via onBlockAdded at
     :411; BlockFurnace.java:20 onBlockAdded calls setDefaultDirection -->

### The runner

`tools/lab.py` (Appendix B) starts the server through BabricKit's `drive.py`,
waits for it to finish loading, reads the spawn point, and sends a script's
lines to the console. Script lines are console commands with `{expression}`
substitutions over `X`, `Y`, `Z`, the origin, which defaults to 8 blocks east
and south of spawn at y=100, inside the spawn chunks. `wait` pauses in seconds,
and `join name` logs in a headless player with BabricKit's probe client.

The probe is subclassed to answer a teleport with the yaw it was sent. The stock
probe answers with yaw 0, and the server adopts the answer, which turned the
first player-placed piston the wrong way.

### Singleplayer and the server

The block logic under test is the same in both: `World`, `Chunk`, every block
class and every block entity are shared code, and the flag that stops a client
in multiplayer from running block logic is false in both singleplayer and the
server's world. Three differences are relevant:

- **Tick order.** Singleplayer updates entities and block entities before the
  world tick, a server after it. See [[Game Tick]].
- **Player actions.** Singleplayer mines through `PlayerControllerSP`, a server
  through `ItemInWorldManager`.
- **Chunks.** Singleplayer's `ChunkProvider` never unloads a chunk; the
  server's `ChunkProviderServer` unloads chunks no player is near, except near
  spawn.

A console command runs at the end of a server tick, outside the block entity
pass, as a player's click is in singleplayer.

### Experiments

| Run | What it tested |
|---|---|
| E1 | The merge, three machines side by side: wool 5 onto wood, wool 0 onto wood, wool 9 onto a slab |
| E2 | A real player mining the results |
| E3 | Placing an invalid slab back; chunk aliasing; a furnace pushed as it lights, with a control |
| E4 | Variants: two normal pistons, leaves, a sapling, wool 3 and 15 |
| E5 | The whole machine built by the player's own placement and lever code |
| E6 | 60 oak trees grown with bone meal over two lit torches each, pistons armed to break the new leaves |
| E6b | E6 again, 40 trees, with every block drop logged |
| E6c | E6 without the torches, 60 trees, as a control |

Each run starts from a fresh world, so the spawn point, and every absolute
coordinate, changes between runs. Results below are given relative to the
machine.

## Findings

### No mechanism creates a block or item ID

*Read.* A block ID reaches a chunk only through `Chunk.setBlockID` and
`Chunk.setBlockIDWithMetadata`, through chunk loading, or through world
generation. Every call of the `World` setters that does not pass a constant,
`this.blockID` or 0 was listed with a script over the source tree:

| Call site | Where its block ID comes from |
|---|---|
| `ItemBed`, `ItemDoor` | the bed or door block the item names |
| `ItemBucket:87` | the water or lava of that bucket, fixed per bucket |
| `ItemHoe:21` | farmland |
| `ItemReed:45`, `ItemSeeds:17` | the block the item was built with: sugar cane, cake, repeater, crops |
| `Teleporter:228`, `:243` | obsidian or portal |
| `TileEntityPiston:99`, `:112` | the block it stores |
| `WorldGenBigTree`, `WorldGenClay`, `WorldGenDeadBush`, `WorldGenFlowers`, `WorldGenHellLava`, `WorldGenLakes`, `WorldGenLiquids`, `WorldGenMinable`, `WorldGenTallGrass` | a constant passed to the generator's constructor |
| `NetClientHandler:287`, `WorldClient` | the server's packets, in a multiplayer client only |

A moving piston's stored block comes from the world in every case:
`BlockPistonBase.java:126` stores the piston's own ID, `:161` a block read at
`:131`, `:353` the piston head, and `:356` a block read at `:349`. A falling block is made only by
`BlockSand.java:28`, with sand's or gravel's ID.

Items follow the same pattern. The item IDs created from something other than a
constant are a block's `idDropped` (`Block.java:347`), the contents of chests,
furnaces and dispensers, a falling block's ID (`EntityFallingSand.java:63`), a
mob's `getDropItemId` (`EntityLiving.java:430`), and a jukebox's record
(`BlockJukeBox.java:44`), which only `ItemRecord.java:17` ever sets, to a
record's ID. The rest copy existing stacks or read saves and packets.

Sponge appears in exactly one place outside its own class:
`Session.java:36`, a list of blocks used only by `PlayerControllerTest`, a
debugging controller the game never constructs. An ID with no block behind it
becomes air when a chunk loads (`ChunkBlockMap.java`).

On a server the client cannot supply an item. `NetServerHandler.handlePlace`
uses the server's copy of the held stack, and `handleWindowClick` recomputes
every click and only compares the client's stack to the result.

Bedrock is the one block in the world whose drop is itself and which is still
never obtained. The drop exists; nothing calls it:

- a player's mining progress is the block's strength, which is 0 for a block of
  hardness −1 (`Block.java:327`);
- explosions stop at its blast resistance;
- pistons refuse any block of hardness −1 (`BlockPistonBase.java:253`), so it
  never becomes a moving block, whose drop is the stored block's drop;
- nothing else moves or copies it.

### Nothing touches the world off the main thread

*Read.* The 1.12 race needed a second thread that loads chunks. Beta 1.7.3 has
none. The threads, from every `extends Thread`, `implements Runnable` and
`new Thread(` in both trees:

| Side | Thread | Touches |
|---|---|---|
| Client | `Minecraft` main thread | the world, rendering, input |
| Client | `ThreadDownloadResources` | sound files |
| Client | `ThreadDownloadImage` | skins and capes |
| Client | `ThreadStatSyncherSend`, `ThreadStatSyncherReceive` | the statistics file |
| Client | `ThreadCheckHasPaid`, `ThreadSleepForever` | nothing in the world |
| Client | `ThreadConnectToServer`, `ThreadCloseConnection` | the connection |
| Client | `CanvasIsomPreview`, `ThreadRunIsoClient` | an unused map-preview tool |
| Both | `NetworkReaderThread`, `NetworkWriterThread`, `NetworkMasterThread` | packet bytes only |
| Server | `ThreadServerApplication` | the server's main loop, and the world |
| Server | `ThreadCommandReader` | console lines, queued |
| Server | `NetworkListenThread`, `NetworkAcceptThread`, `ThreadLoginVerifier`, `ThreadMonitorConnection` | sockets and logins |

A reader thread only decodes a packet and adds it to a synchronized list
(`NetworkManager.java:137` in the server tree); `processReadPackets` runs it on
the main thread. Console lines wait in a synchronized list the same way
(`MinecraftServer.java:57`). No packet writer holds a reference to live block
data: `Packet51MapChunk` compresses a copy when it is built. With one thread,
the only way data can be half-updated is one method re-entering another, which
is what every finding below uses.

### Three items can carry an invalid damage value

*Read, and tested for each item named.* Metadata becomes an item's damage in
five blocks:

| Block | `damageDropped` | Valid values | Can a piston push it? |
|---|---|---|---|
| [[Wool]] | the metadata (`BlockCloth.java:17`) | all 16 | yes |
| [[Wood]] | the metadata (`BlockLog.java:56`) | 0 to 2 | yes |
| [[Stone Slab]], [[Double Stone Slab]] | the metadata (`BlockStep.java:68`) | 0 to 3 | yes |
| [[Leaves]] | metadata & 3 (`BlockLeaves.java:173`); shears give the same (`:166`) | 0 to 2 | no, it breaks |
| [[Sapling]] | metadata & 3 (`BlockSapling.java:57`) | 0 to 2 | no, it breaks |

Wool has no invalid value. Wood and slabs can be moved, so the moving piston
merge reaches all their invalid values: 13 and 12 items.

Leaves and saplings break when pushed (`Material.java:118`-`:119`), so no merge
can carry them, and nothing writes the low two bits of either in place: a
leaves block's metadata is only ever changed in bit 8, its decay flag
(`BlockLeaves.java`, `BlockLog.java:23`), and a sapling's only in its growth
bit. The one way in is to read a leaves block in the moment it carries another
block's metadata, which the finding *A sapling with damage value 3* does. It yields a sapling with damage
3, but not leaves: leaves with metadata 3 exist only while a torch is being
removed, and shears are used by a player, never inside an update.

That makes 26 items: wood 3 to 15, slabs 4 to 15 and the sapling with damage 3.

### The moving piston merge

*Tested.* The merge happens when a piston writes a moving block over a moving
block that is already there. Two pieces of the code make that possible.

**A piston checks its line before it moves it.** `tryExtend`
(`BlockPistonBase.java:309`) runs two loops. The first walks the line, returns
if anything cannot be pushed, and when it meets a fragile block (mobility 1)
drops it and removes it with `setBlockWithNotify` (`:336`-`:337`). That removal
updates the neighbours. The second loop (`:345`) then moves whatever is in the
line *now*, without checking again. Any block that appears in the line during
those neighbour updates is pushed or overwritten regardless.

**A block's ID is written before its metadata.** `Chunk.setBlockIDWithMetadata`
(`Chunk.java:236`) writes the new ID (`:245`), calls the *old* block's
`onBlockRemoval` (`:247`), and only then writes the new metadata (`:250`, again
at `:265`). If `onBlockRemoval` places a block in the same space, that block
keeps the ID it was placed with and receives the outer call's metadata.

A moving piston's `onBlockRemoval` does exactly that:
`BlockPistonMoving.java:18` calls `TileEntityPiston.clearPistonTileEntity`
(`TileEntityPiston.java:93`), which places the stored block at once (`:99`)
whenever the space still holds a moving piston, which it does, because the
outer call has just written one.

`setBlockIDWithMetadata` returns without doing anything when the ID and the
metadata both already match (`:240`), so the two moving blocks must differ in
metadata.

#### The tick, step by step

The machine from [[Block Transmutation]], with E the centre, W the wool, B the
normal piston, X the block to transmute and A the sticky piston:

1. The floor lever turns on and updates B. B is powered and its line is W then a
   fragile torch, so it extends at once: `updatePistonState` (`:66`) calls
   `playNoteAt`, which runs `playBlock` (`:112`) immediately. `playBlock` sets
   `ignoreUpdates` for every normal piston (`:113`).
2. B's first loop passes W and breaks the torch at E: it drops the torch
   (`:336`) and calls `setBlockWithNotify(E, 0)` (`:337`).
3. `Chunk.setBlockID` writes air at E (`Chunk.java:284`) and calls the torch's
   `onBlockRemoval` (`:286`). A lit torch updates the neighbours of each of its
   neighbours (`BlockRedstoneTorch.java:61`), which reaches A through X.
4. A is sticky, so its `ignoreUpdates` is not set. It is already powered by the
   lever, so it extends: its line is X, then E, now air. X becomes a moving block
   at E whose block entity stores X's ID and metadata; A's head starts moving
   into X's old space.
5. Back in step 3's `setBlockID`, the metadata at E is set to 0 (`:289`). E is
   now a moving block with metadata 0; its block entity still stores X's
   metadata.
6. B's second loop moves W into E: `setBlockAndMetadata(E, 36, W's metadata)`
   (`BlockPistonBase.java:355`). E already holds block 36 but with metadata 0,
   so the call proceeds: it writes 36, and calls the old moving block's
   `onBlockRemoval`, which lands X at E with X's metadata, updating neighbours.
7. The outer call resumes and writes W's metadata over X's (`Chunk.java:250`,
   `:265`). E now holds X with W's metadata.
8. The second loop then gives E a moving piston block entity for W
   (`BlockPistonBase.java:356`). `World.setBlockTileEntity` adds it to the
   ticking list first (`World.java:1612`); the chunk then refuses it, since E is
   no longer a container, and prints `Attempted to place a tile entity where
   there was no entity tile!` (`Chunk.java:444`). The orphan ticks for two ticks
   and finishes without effect, because E is no longer block 36.
9. B's head moves into W's old space. W is gone.

Step 5 is why white wool fails: its metadata, 0, already matches, so step 6
does nothing but replace the block entity, and X lands with its own metadata
two ticks later.

Step 1's `ignoreUpdates` is why the two pistons must differ. The flag is a field
of the `Block` object (`BlockPistonBase.java:7`), and normal and sticky pistons
are two objects, so while a normal piston moves, every normal piston in the
world ignores updates, and every sticky piston still answers them.

#### Evidence

E1, three machines 10 blocks apart, built with `lab set` and fired with
`lab setn` on the floor levers:

| Wool | X | E afterwards | `lab drop` at E | Orphan message |
|---|---|---|---|---|
| `35:5` | `17:0` | `17:5` | item `17:5` | yes |
| `35:0` | `17:0` | `17:0` | item `17:0` | no |
| `35:9` | `44:0` | `44:9` | item `44:9` | yes |

In every copy B stood extended as `33:13` with its head `34:5` in W's old space,
A as `29:11` with its head `34:11` in X's old space, and the torch lay on the
floor as item `76:0`. No block entity was left ticking 1.5 seconds later.

E4 variants, built the same way:

| Variant | Result |
|---|---|
| A a normal piston, like B | A never moved (`33:3`); W landed at E as `35:5`; X untouched |
| X leaves (`18:0`) | A extended and broke the leaves (a sapling dropped); W landed at E |
| X a sapling (`6:0`) | A extended and broke it (the sapling dropped); W landed at E |
| wool `35:3` onto `17:0` | E became `17:3` |
| wool `35:15` onto `17:0` | E became `17:15` |

### The survival machine

*Tested.* E5 built the machine with nothing but the player's own code: every
block was placed through `ItemInWorldManager.activeBlockOrUseItem` with the
item in the player's hand, the pistons facing the way the player's yaw made
them face, and both levers flipped through the same method, which calls the
lever's `blockActivated`.

| Stage | State |
|---|---|
| Built | torch `76:5`, wool `35:5`, piston `33:5`, wood `17:0`, sticky piston `29:3`, two stone, wall lever `69:1`, floor lever `69:6` |
| Upper lever on | lever `69:9`; the sticky piston still `29:3`, powered and unmoved |
| Floor lever on | E `17:5`; sticky piston `29:11`; piston `33:13` |
| Player mines E | inventory holds `17:5` in its own slot, beside an ordinary `17:0` |

Arming the sticky piston is the step a builder can get wrong. A lever updates
its own neighbours and those of the block it is on (`BlockLever.java:153`). A
lever standing on a block beside the sticky piston would update the piston
through that block, and fire it early. The lever on the side of a block two
spaces away, one up, powers the piston through the space above it without
updating it.

E2 rebuilt E1's first and third machines and had the player mine the results
with `lab dig`, which is the server's own `tryHarvestBlock`, holding a wooden
pickaxe. The player picked up `17:5` and
`44:9`, and the pickaxe took two uses of wear.

### A sapling with damage value 3

*Tested.* This uses the other half of the window the merge uses: while an old
block's `onBlockRemoval` runs, its space already holds the new block's ID but
still the old block's metadata (`Chunk.java:284`-`:289`). Anything that
breaks the space in that moment breaks the new block with the old metadata.

Oak trees overwrite some blocks without checking them. `WorldGenTrees.generate` checks for
room at radius 1 below its top three layers (`WorldGenTrees.java:14`-`:35`),
but places leaves at radius 2 in its lowest two leaf layers, over any block that
is not an opaque cube (`:45`-`:56`), with `World.setBlock`, which sends no
neighbour updates. A lit redstone torch standing 2 blocks from the trunk at that
height is overwritten, and its `onBlockRemoval` runs with the space holding
leaves and the torch's metadata.

A lit torch's removal updates every block two steps away from it, and none of
the blocks next to it: it calls `notifyBlocksOfNeighborChange` on each of its six
neighbours (`BlockRedstoneTorch.java:61`), whose neighbours are the torch's
space and the positions two steps out. In E1 the torch was also removed with
`setBlockWithNotify`, which updates the direct neighbours as well; a tree does
not. A first attempt at E6 put the pistons next to the torches, and they never
fired.

A piston two blocks from the torch, powered but not yet updated, with a
pushable block between it and the torch, answers the update. Its first loop
breaks the leaves in the torch's space with `dropBlockAsItem` and the metadata
the space holds at that moment (`BlockPistonBase.java:336`): the torch's.
Leaves drop a sapling one time in 20 (`BlockLeaves.java:155`), with damage
`metadata & 3`. A torch on the south face of a block has metadata 3.

The build, relative to the sapling on dirt, with both sides mirrored:

| Position | Block |
|---|---|
| ±2, 2, −1 | stone, the torch's support |
| ±2, 2, 0 | redstone torch `76:3` |
| ±3, 2, 0 | stone, pushed by the piston |
| ±4, 2, 0 | piston facing the torch |
| ±5, 2, 0 and ±5, 3, 0 | stone with a lever on it, placed without updates to arm the piston |

A tree 4 or 5 blocks tall (`WorldGenTrees.java:7`) covers the torches; a tree 6
tall, or a big oak (`BlockSapling.java:46`, one time in 10), misses them.

| Run | Trees | Torches overwritten | Leaves broken with metadata 3 | Saplings `6:3` |
|---|---|---|---|---|
| E6 | 60 | 82 of 120 | not logged | 2 |
| E6b | 40 | 46 of 80 | 46, all at the torch positions | 2 |
| E6c, no torches | 60 | none | none | 0 |

That is 4 saplings from 128 leaves broken, against 6.4 expected at one in 20. E6 and E6b also
dropped a few ordinary saplings. The drop log traced them to leaves with
metadata 8 at y=111 and 112, above the 11 layers each trial cleared: leaves of
earlier big oaks, flagged for decay when the clearing removed their logs, and
decaying on random ticks. The control dropped nothing, and no piston in it
fired.

### What the invalid items do

*Tested, except where marked.*

- **Placing.** `ItemLog` and `ItemSlab` place their damage value as metadata.
  A `44:9` slab placed on the floor became block `44:9` (E3).
- **Stacking slabs.** A second `44:9` placed on top turned the pair into a
  double slab `43:9`, which the player mined for two `44:9` (E3).
  `BlockStep.onBlockAdded` (`BlockStep.java:43`) compares metadata only.
- **Stacking items.** Invalid items stack only with the same damage value. `44:9`
  items stacked with each other; `17:5` stayed apart from `17:0` (E2, E5).
- **Appearance** (*read*). Wood 3 to 15 falls through to oak's textures
  (`BlockLog.java` `getBlockTextureFromSideAndMetadata`). Slabs 4 to 15 show the
  smooth top texture on every face (`BlockStep.java:19`), so they look like
  stone slabs with no side seam. Their inventory icons follow.
- **The damage-3 sapling** (*read*). It places a sapling with metadata 3
  (`ItemSapling`), which draws as an oak sapling (`BlockSapling` treats only 1
  and 2 as other kinds), grows into an oak or a big oak (`BlockSapling.java:36`),
  and drops itself with damage 3 again when broken (`BlockSapling.java:57`).
- **Names.** Every wood item is named `tile.log`, and every sapling
  `tile.sapling`. A slab's name is
  `tile.stoneSlab.` plus an entry from a four-entry array, indexed by damage
  (`ItemSlab.java:18`).
- **The tooltip crash** (*read, and reproduced outside the game*). A container
  screen asks for the name of the stack under the pointer
  (`GuiContainer.java:66`). Calling the client jar's own name lookup for slab
  damage 4 to 15 throws `ArrayIndexOutOfBoundsException: Index 4 out of bounds
  for length 4`. Wood, wool, leaves and saplings return names for every value.
  The crash screen itself was not observed. The server has no item names
  (its `ItemSlab` lacks the method), so the server is unaffected; any client
  that hovers the item, including one looking into another player's chest, is.

### A piston can push a furnace in the tick it lights

*Tested.* During the block entity pass, the world defers block entity changes:
a new block entity joins a waiting list (`World.java:1606`-`1610`), and a
removed one is only marked invalid (`:1624`). The chunk treats an invalid
block entity as absent (`Chunk.java:415`).

A furnace swaps block when it lights or goes out, from inside its own update,
in `BlockFurnace.updateFurnaceBlockState` (`BlockFurnace.java:112`). The swap
removes the furnace's block entity, which during the pass only marks it invalid,
and the new furnace block's `onBlockAdded` updates the neighbours through
`setDefaultDirection` (`:48`). A piston that answers that update sees a furnace
with no block entity, and a block entity is the only thing that stops a piston
pushing a furnace (`BlockPistonBase.java:268`). The furnace moves.
`updateFurnaceBlockState` then re-adds the old block entity to the space the
furnace left, where the piston head is; the head's own block entity clears it
two ticks later.

E3 armed a normal piston facing a furnace, filled the furnace with 8
cobblestone and 2 coal, and waited:

| | Pushed furnace | Control furnace |
|---|---|---|
| Block | lit `62:3`, one space along | lit `62:3`, in place |
| Its block entity | empty, burn time 0 | burn time 1561, then 1400 |
| Contents | gone; nothing dropped | smelting |
| Orphaned furnace block entities | three | one |
| 8 seconds later | still lit, still burn time 0 | smelting |

The pushed furnace stays lit forever: a furnace changes block only when its
burn time crosses zero, and an empty one never does. The control shows a leak
of its own: every time a furnace lights or goes out, one spare block entity is
left ticking in the list with nothing in the chunk pointing at it.

### The chunk map repeats every 524,288 blocks

*Tested on the server; read for singleplayer.* Both chunk providers key loaded
chunks by `ChunkCoordIntPair.chunkXZ2Int` (`ChunkCoordIntPair.java:12`), which
keeps a sign bit and the low 15 bits of each coordinate. Chunk x and x + 32768
share a key when both are on the same side of zero, and 32768 chunks is 524,288
blocks. A request for the second chunk returns the first, if it is loaded.
<!-- src: ChunkProvider.java:28, :32, :73; server ChunkProviderServer.java:29,
     :44, :85 -->

E3 placed a gold block and read the same y at other positions:

| Position read | Result |
|---|---|
| 524,288 east | the gold block |
| 524,288 south | the gold block |
| 524,288 west, across zero | air |
| 262,144 east | air |

On a server, whichever of two aliased chunks loads first answers for both until
it unloads. Singleplayer never unloads a chunk, so the first one visited answers
for the rest of the session. Writes through an alias land in the first chunk's
arrays, and block entities placed through it take the first chunk's
coordinates (`Chunk.java:434`). No ID is created; blocks are only seen and
changed in two places at once.

### Other places metadata is written after an update

*Read, not tested.* The merge is one case of a general window: while an old
block's `onBlockRemoval` runs, its space holds the new ID with the old
metadata, and the new metadata is written afterwards. Any code that writes a
space's metadata *after* updating neighbours has the same shape. These were
found and not tested:

- **A redstone torch going out.** `BlockRedstoneTorch.updateTick` replaces a lit
  torch with an unlit one through `setBlockAndMetadataWithNotify`; the lit
  torch's `onBlockRemoval` updates blocks within two first. A block moved in by
  then would get the torch's facing, 1 to 5.
- **A jukebox with a record being replaced.** Its `onBlockRemoval` ejects the
  record and calls `setBlockMetadataWithNotify(..., 0)` on the space, which by
  then holds the replacing block (`BlockJukeBox.java:39`).
- **A door being toggled.** `BlockDoor.blockActivated` updates the upper half
  first (`BlockDoor.java:102`), then writes the lower half's metadata without
  checking what is there (`:105`).
- **A block being placed.** `ItemBlock.onItemUse` places with neighbour updates
  (`ItemBlock.java:47`), then calls `onBlockPlaced` and `onBlockPlacedBy`
  (`:48`-`:49`), which set facing metadata on
  whatever now occupies the space. This matches the prior work's *onBlockPlaced
  piston transmutation*.
- **A furnace changing state**, which writes its old metadata back after the
  swap (`BlockFurnace.java:123`).
- **Flowing liquids**, the prior work's *liquid transmutation*.

Each of these writes metadata onto whatever has arrived in the space, so each
can only transmute blocks a piston can move there. The reverse, reading the new
block while it still has the old metadata, is what the sapling method uses, and
it works on any block a tree or other writer places without updates.

## Dead ends

Each of these was followed far enough to rule out, for the reason given.

- **A race condition.** No thread but the main one touches the world (above).
- **Region file corruption.** `RegionFile.write` allocates sectors correctly. A
  chunk that compresses to 256 sectors or more is silently not saved
  (`RegionFile.java:171`), which rolls it back on reload rather than corrupting
  it. A corrupt compressed chunk fails to decompress and is regenerated.
- **Saved data.** Block entities and entities are rebuilt from their saved `id`,
  and a falling block's `Tile` byte is masked to 0 to 255; a save the game wrote
  itself never names an ID it did not have.
- **A server trusting the client.** It never takes an item from a packet (above).
- **The singleplayer click window.** `PlayerControllerSP.clickBlock` reads the
  block, calls its `onBlockClicked`, checks the strength of the block it first
  read, then breaks whatever is there *now*. A block that is instantly broken
  and changes its own space when clicked would let a player break anything,
  bedrock included. The only instantly broken block with an `onBlockClicked` is
  TNT, which changes only its own metadata.
- **Explosions and piston drops.** Both drop through `idDropped`, which only
  ever names an existing block's normal drop.
- **Unloaded chunks.** Writing to an unloaded chunk on a server writes to an
  empty stand-in whose setters report success (`EmptyChunk.java`), which deletes
  blocks rather than creating them.
- **Chunk aliasing.** Moves real data between places; creates nothing.
- **The jukebox record field.** An arbitrary integer item ID, but only a record
  is ever put in it.
- **Invalid leaves.** Leaves with metadata 3 exist only inside an update, and
  only shears keep a leaves block's metadata in its drop (above).
- **`ChunkProviderLoadOrGenerate`.** The source contains a 32 × 32 ring-buffer
  chunk cache with a stale-chunk shortcut, which looked promising. Nothing
  constructs it: `World.getChunkProvider` returns a `ChunkProvider`.

## Open questions

- **Raise the sapling yield.** Each tree here had two torches. The lowest two
  leaf layers have 12 edge positions each at radius 2, and a powered wall lever
  or powered redstone dust may read the same way as a torch. How many readers
  one tree can feed is untested.
- **Test the other windows.** The torch, jukebox, door, placement and liquid
  cases above are untested. Each would reach a narrower set of metadata values
  than wool does, but some need less material.
- **Confirm the tooltip crash in a running client**, and whether it happens on a
  server when one player hovers an invalid slab another put in a chest.
- **Catalogue the piston glitches that move what cannot move.** The gap between
  a piston's two loops lets it push obsidian, extended pistons, piston heads and
  moving blocks that appear in its line mid-push. Pushing a moving block stores
  block 36 inside another, which lands as a moving piston with no block entity.
  Breaking such a block could recurse in `BlockPistonMoving`'s drop code
  (*hypothesis*). None of this was tested, and none of it yields a new item by
  the reasoning above.
- **Other block entities.** The furnace is the only block that swaps itself
  during the block entity pass. Whether any other container can be caught
  without its block entity is open.
- **Chunk aliasing in singleplayer**, and how entities and block entities behave
  when reached through an alias. No reference page covers chunks yet.
- **A mechanical proof.** The "no new IDs" argument is a read of every call
  site. BabricKit's `callers` command matches by short name and was too noisy
  to replace that read; a bytecode data-flow check would make it airtight.

## Reproducing

### Setup

1. Install BabricKit (`python bk.py setup`) and a JDK no newer than 21; Gradle
   8.6 refuses newer ones.
2. Create a Babric project from BabricKit's `examples/build.gradle` and
   `examples/gradle.properties`, with the files in Appendix A. Change only the
   refmap name in `build.gradle` and the archive name in `gradle.properties`.
3. Run `python bk.py verify path/to/TransmuteLab`, then
   `gradlew build` with `JAVA_HOME` set to the JDK.
4. Put `lab.py` and `binyq.py` (Appendix B) in the project's `tools/`, the
   scripts from Appendix C in `scripts/`, and run
   `python tools/lab.py scripts/e1_merge.txt`. Each run deletes `run/world`
   first, and writes `run/server.properties` with online mode off, so the probe
   can join.

### Pitfalls

- **Build order.** `lab set` still runs `onBlockAdded`. Place a lit redstone
  torch before arming anything near it, and arm pistons last.
- **The spawn chunks.** A server with no players keeps only the chunks near
  spawn. Build within about 100 blocks of it, or a write lands in the empty
  stand-in chunk and reports success.
- **Probe yaw.** Use the subclass in `lab.py`, or pistons placed by the probe
  face the wrong way.
- **Slot numbers.** `lab give` fills the first free slot, and items the player
  picks up take slots too. E2's place-back step selected the redstone torch the
  machine had dropped, and E3 redid it.
- **Line endings.** On Windows, Python's text mode writes CRLF. Most files in
  this repository are LF and a few are CRLF; keep each file's own endings, and
  write from scripts in binary mode.
- **Client-only code.** The server jar lacks item names and rendering. Check
  client-only paths against `client.jar` directly, as in Appendix D. Initialise
  `Block` (`uu`) before touching items (`gm`), or the two static
  initialisers run in the wrong order and fail with a `NullPointerException`.

## References

- [Java Edition: Block Transmutation](https://mcdf.wiki.gg/wiki/Java_Edition:Block_Transmutation), Minecraft Discontinued Features Wiki
- [Java Edition: Parallel Asynchronous Threads](https://mcdf.wiki.gg/wiki/Java_Edition:Parallel_Asynchronous_Threads), Minecraft Discontinued Features Wiki
- [Babric](https://babric.github.io/), the Fabric loader for Beta 1.7.3
- BabricKit, the toolkit of `bk.py`, `drive.py` and the probe client, kept outside this repository
- [[Block Transmutation]], [[Piston]], [[Furnace]], [[Wood]], [[Stone Slab]] and [[Sponge]] on this wiki

## Appendix A: the lab mod

`gradle.properties`:

```properties
org.gradle.jvmargs=-Xmx2G
org.gradle.parallel=true

minecraft_version=b1.7.3
barn_mappings=b1.7.3+build.9
loader_version=0.15.6-babric.2

mod_version=1.0.0
maven_group=lab.transmute
archives_base_name=transmutelab
```

`settings.gradle`:

```groovy
pluginManagement {
    repositories {
        maven { name = 'Fabric'; url = 'https://maven.fabricmc.net/' }
        maven { name = 'Babric'; url = 'https://maven.glass-launcher.net/babric' }
        mavenCentral()
        gradlePluginPortal()
    }
}

rootProject.name = 'transmutelab'
```

`src/main/resources/fabric.mod.json`:

```json
{
  "schemaVersion": 1,
  "id": "transmutelab",
  "version": "${version}",
  "name": "TransmuteLab",
  "description": "Console commands for probing block-data corruption on a b1.7.3 dedicated server.",
  "authors": ["wiki research"],
  "license": "CC0-1.0",
  "environment": "*",
  "mixins": ["transmutelab.mixins.json"],
  "depends": {
    "minecraft": "1.0.0-beta.7.3",
    "fabricloader": ">=0.15.0"
  }
}
```

`src/main/resources/transmutelab.mixins.json`:

```json
{
  "required": true,
  "minVersion": "0.8",
  "package": "lab.transmute.mixin",
  "compatibilityLevel": "JAVA_8",
  "mixins": [
    "BlockDropMixin",
    "PistonBlockEntityAccessor"
  ],
  "server": [
    "ServerCommandHandlerMixin"
  ],
  "injectors": {
    "defaultRequire": 1
  },
  "refmap": "transmutelab.refmap.json"
}
```

`src/main/java/lab/transmute/mixin/ServerCommandHandlerMixin.java`:

```java
package lab.transmute.mixin;

import lab.transmute.Lab;
import net.minecraft.class_38;
import net.minecraft.class_426;
import net.minecraft.server.MinecraftServer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

// class_426 is the dedicated server's console command handler, method_1411 the
// method that parses one console line (it prints "Unknown console command").
@Mixin(class_426.class)
public class ServerCommandHandlerMixin {
    @Shadow
    private MinecraftServer field_1687;

    @Inject(method = "method_1411(Lnet/minecraft/class_38;)V", at = @At("HEAD"), cancellable = true)
    private void transmutelab$handle(class_38 command, CallbackInfo ci) {
        if (Lab.handle(field_1687, command.field_159)) {
            ci.cancel();
        }
    }
}
```

`src/main/java/lab/transmute/mixin/BlockDropMixin.java`:

```java
package lab.transmute.mixin;

import lab.transmute.Lab;
import net.minecraft.block.Block;
import net.minecraft.world.World;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

// Block.dropBlockAsItemWithChance (method_1625): every break that can drop an item,
// by player, explosion, piston or decay, passes through here with the metadata it
// will use. Logged only while "lab droplog on" is set.
@Mixin(Block.class)
public class BlockDropMixin {
    @Inject(method = "method_1625(Lnet/minecraft/world/World;IIIIF)V", at = @At("HEAD"))
    private void transmutelab$log(World world, int x, int y, int z, int meta, float chance, CallbackInfo ci) {
        if (Lab.dropLog) {
            Lab.logDrop((Block) (Object) this, world, x, y, z, meta);
        }
    }
}
```

`src/main/java/lab/transmute/mixin/PistonBlockEntityAccessor.java`:

```java
package lab.transmute.mixin;

import net.minecraft.class_283;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

// class_283 is TileEntityPiston; its stored block, facing and progress are private.
@Mixin(class_283.class)
public interface PistonBlockEntityAccessor {
    @Accessor("field_1761")
    int lab$storedId();

    @Accessor("field_1762")
    int lab$storedMeta();

    @Accessor("field_1763")
    int lab$facing();

    @Accessor("field_1764")
    boolean lab$extending();

    @Accessor("field_1765")
    boolean lab$source();

    @Accessor("field_1766")
    float lab$lastProgress();

    @Accessor("field_1767")
    float lab$progress();
}
```

`src/main/java/lab/transmute/Lab.java`:

```java
package lab.transmute;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import net.minecraft.block.Block;
import net.minecraft.block.entity.BlockEntity;
import net.minecraft.block.entity.JukeboxBlockEntity;
import net.minecraft.class_138;
import net.minecraft.class_142;
import net.minecraft.class_225;
import net.minecraft.class_283;
import net.minecraft.class_339;
import net.minecraft.class_43;
import net.minecraft.class_69;
import net.minecraft.class_73;
import net.minecraft.entity.Entity;
import net.minecraft.item.ItemStack;
import net.minecraft.server.MinecraftServer;
import net.minecraft.util.math.Box;
import net.minecraft.world.World;

import lab.transmute.mixin.PistonBlockEntityAccessor;

/**
 * Console commands for probing block-data corruption.
 *
 * Every line of output starts with "LAB " so a harness can pick it out of the
 * server log. Nothing here changes game behaviour: each command is a thin
 * wrapper around one vanilla method, named in the comment beside it with its
 * MCP name so it can be checked against the decompiled source.
 */
public final class Lab {
    private Lab() {
    }

    /** Set by "lab droplog on"; read by BlockDropMixin. */
    public static boolean dropLog = false;

    public static void logDrop(Block block, World w, int x, int y, int z, int meta) {
        out("DROPCALL " + block.id + ":" + meta + " at " + x + " " + y + " " + z
                + " world now " + w.getBlockId(x, y, z) + ":" + w.method_1778(x, y, z));
    }

    static void out(String line) {
        System.out.println("LAB " + line);
    }

    public static boolean handle(MinecraftServer server, String line) {
        String[] a = line.trim().split("\\s+");
        if (a.length == 0 || !a[0].equalsIgnoreCase("lab")) {
            return false;
        }
        try {
            run(server, a);
        } catch (Throwable t) {
            out("ERROR " + t);
            t.printStackTrace(System.out);
        }
        return true;
    }

    static int i(String s) {
        return Integer.parseInt(s);
    }

    static World world(MinecraftServer server) {
        return server.field_2841[0];
    }

    static void run(MinecraftServer server, String[] a) {
        World w = world(server);
        String cmd = a.length > 1 ? a[1] : "";
        if (cmd.equals("spawn")) {
            net.minecraft.util.math.Vec3i sp = w.getSpawnPos();
            out("SPAWN " + sp.x + " " + sp.y + " " + sp.z);
        } else if (cmd.equals("droplog")) {
            dropLog = a.length > 2 && a[2].equals("on");
            out("DROPLOG " + dropLog);
        } else if (cmd.equals("mark")) {
            StringBuilder b = new StringBuilder();
            for (int k = 2; k < a.length; ++k) b.append(k > 2 ? " " : "").append(a[k]);
            out("MARK " + b);
        } else if (cmd.equals("set")) {
            // setBlockAndMetadata: no neighbour notification
            boolean r = w.method_154(i(a[2]), i(a[3]), i(a[4]), i(a[5]), a.length > 6 ? i(a[6]) : 0);
            out("SET " + a[2] + " " + a[3] + " " + a[4] + " -> " + r);
        } else if (cmd.equals("setn")) {
            // setBlockAndMetadataWithNotify
            boolean r = w.method_201(i(a[2]), i(a[3]), i(a[4]), i(a[5]), a.length > 6 ? i(a[6]) : 0);
            out("SETN " + a[2] + " " + a[3] + " " + a[4] + " -> " + r);
        } else if (cmd.equals("meta")) {
            // setBlockMetadata: no notification
            w.method_223(i(a[2]), i(a[3]), i(a[4]), i(a[5]));
            out("META " + a[2] + " " + a[3] + " " + a[4]);
        } else if (cmd.equals("metan")) {
            // setBlockMetadataWithNotify
            w.method_215(i(a[2]), i(a[3]), i(a[4]), i(a[5]));
            out("METAN " + a[2] + " " + a[3] + " " + a[4]);
        } else if (cmd.equals("fill")) {
            int x1 = i(a[2]), y1 = i(a[3]), z1 = i(a[4]), x2 = i(a[5]), y2 = i(a[6]), z2 = i(a[7]);
            int id = i(a[8]), m = a.length > 9 ? i(a[9]) : 0;
            for (int x = Math.min(x1, x2); x <= Math.max(x1, x2); ++x)
                for (int y = Math.min(y1, y2); y <= Math.max(y1, y2); ++y)
                    for (int z = Math.min(z1, z2); z <= Math.max(z1, z2); ++z)
                        w.method_154(x, y, z, id, m);
            out("FILL done");
        } else if (cmd.equals("upd")) {
            // onNeighborBlockChange on the block at the position itself
            int x = i(a[2]), y = i(a[3]), z = i(a[4]);
            int id = w.getBlockId(x, y, z);
            if (id > 0) Block.BLOCKS[id].method_1609(w, x, y, z, a.length > 5 ? i(a[5]) : 0);
            out("UPD " + x + " " + y + " " + z + " id=" + id);
        } else if (cmd.equals("notify")) {
            // notifyBlocksOfNeighborChange around the position
            int x = i(a[2]), y = i(a[3]), z = i(a[4]);
            w.method_244(x, y, z, w.getBlockId(x, y, z));
            out("NOTIFY " + x + " " + y + " " + z);
        } else if (cmd.equals("get")) {
            int x = i(a[2]), y = i(a[3]), z = i(a[4]);
            out("GET " + x + " " + y + " " + z + " " + describe(w, x, y, z));
        } else if (cmd.equals("box")) {
            int x1 = i(a[2]), y1 = i(a[3]), z1 = i(a[4]), x2 = i(a[5]), y2 = i(a[6]), z2 = i(a[7]);
            String tag = a.length > 8 ? a[8] : "";
            out("BOX " + tag + " begin");
            for (int y = Math.max(y1, y2); y >= Math.min(y1, y2); --y)
                for (int z = Math.min(z1, z2); z <= Math.max(z1, z2); ++z)
                    for (int x = Math.min(x1, x2); x <= Math.max(x1, x2); ++x)
                        if (w.getBlockId(x, y, z) != 0 || mapTe(w, x, y, z) != null)
                            out("BOX " + tag + " " + x + " " + y + " " + z + " " + describe(w, x, y, z));
            out("BOX " + tag + " end");
        } else if (cmd.equals("items")) {
            int x = i(a[2]), y = i(a[3]), z = i(a[4]);
            double r = Double.parseDouble(a[5]);
            String tag = a.length > 6 ? a[6] : "";
            List list = w.getEntities((Entity) null, Box.create(x - r, y - r, z - r, x + 1 + r, y + 1 + r, z + 1 + r));
            out("ITEMS " + tag + " begin");
            for (Object o : list) {
                if (o instanceof class_142) {
                    class_142 e = (class_142) o;
                    ItemStack s = e.field_564;
                    out("ITEMS " + tag + " item " + s.itemId + ":" + s.getDamage() + " x" + s.count
                            + " at " + fmt(e.x) + " " + fmt(e.y) + " " + fmt(e.z));
                }
            }
            out("ITEMS " + tag + " end");
        } else if (cmd.equals("clearitems")) {
            int x = i(a[2]), y = i(a[3]), z = i(a[4]);
            double r = Double.parseDouble(a[5]);
            List list = w.getEntities((Entity) null, Box.create(x - r, y - r, z - r, x + 1 + r, y + 1 + r, z + 1 + r));
            int n = 0;
            for (Object o : list) {
                if (o instanceof class_142) {
                    ((Entity) o).markDead();
                    ++n;
                }
            }
            out("CLEARITEMS " + n);
        } else if (cmd.equals("boom")) {
            // createExplosion with no exploder
            w.method_187((Entity) null, i(a[2]) + 0.5, i(a[3]) + 0.5, i(a[4]) + 0.5, Float.parseFloat(a[5]));
            out("BOOM");
        } else if (cmd.equals("drop")) {
            // what breaking the block yields: dropBlockAsItem with its current metadata
            int x = i(a[2]), y = i(a[3]), z = i(a[4]);
            int id = w.getBlockId(x, y, z), m = w.method_1778(x, y, z);
            if (id > 0) Block.BLOCKS[id].method_1592(w, x, y, z, m);
            out("DROP " + id + ":" + m);
        } else if (cmd.equals("dig")) {
            // the server's own harvest path (ItemInWorldManager.tryHarvestBlock)
            class_69 p = player(server);
            if (p == null) {
                out("DIG no player");
                return;
            }
            int x = i(a[2]), y = i(a[3]), z = i(a[4]);
            String before = describe(w, x, y, z);
            boolean r = p.field_261.method_1834(x, y, z);
            out("DIG " + x + " " + y + " " + z + " was " + before + " -> " + r);
        } else if (cmd.equals("tp")) {
            class_69 p = player(server);
            if (p == null) {
                out("TP no player");
                return;
            }
            // NetServerHandler.teleportTo: moves the player and tells the client
            float yaw = a.length > 5 ? Float.parseFloat(a[5]) : 0.0F;
            p.field_255.method_832(Double.parseDouble(a[2]), Double.parseDouble(a[3]), Double.parseDouble(a[4]), yaw, 0.0F);
            out("TP " + a[2] + " " + a[3] + " " + a[4]);
        } else if (cmd.equals("use")) {
            // what a Packet15Place does: ItemInWorldManager.activeBlockOrUseItem with the held stack
            class_69 p = player(server);
            if (p == null) {
                out("USE no player");
                return;
            }
            int x = i(a[2]), y = i(a[3]), z = i(a[4]), side = i(a[5]);
            int slot = p.inventory.selectedSlot;
            ItemStack held = p.inventory.main[slot];
            String what = held == null ? "nothing" : held.itemId + ":" + held.getDamage() + " x" + held.count;
            boolean r = p.field_261.method_1832(p, w, held, x, y, z, side);
            if (held != null && held.count <= 0) p.inventory.main[slot] = null;
            out("USE " + what + " on " + x + " " + y + " " + z + " side " + side + " -> " + r);
        } else if (cmd.equals("select")) {
            class_69 p = player(server);
            if (p != null) p.inventory.selectedSlot = i(a[2]);
            out("SELECT " + a[2]);
        } else if (cmd.equals("furnace")) {
            // fill a furnace's input (slot 0) and fuel (slot 1)
            int x = i(a[2]), y = i(a[3]), z = i(a[4]);
            BlockEntity te = mapTe(w, x, y, z);
            if (!(te instanceof class_138)) {
                out("FURNACE no furnace tile entity at " + x + " " + y + " " + z);
                return;
            }
            net.minecraft.inventory.Inventory inv = (net.minecraft.inventory.Inventory) te;
            inv.setStack(0, new ItemStack(i(a[5]), i(a[6]), 0));
            inv.setStack(1, new ItemStack(i(a[7]), i(a[8]), 0));
            out("FURNACE filled");
        } else if (cmd.equals("inv")) {
            class_69 p = player(server);
            if (p == null) {
                out("INV no player");
                return;
            }
            out("INV begin");
            ItemStack[] main = p.inventory.main;
            for (int k = 0; k < main.length; ++k)
                if (main[k] != null) out("INV slot " + k + " " + main[k].itemId + ":" + main[k].getDamage() + " x" + main[k].count);
            out("INV end");
        } else if (cmd.equals("give")) {
            class_69 p = player(server);
            if (p == null) {
                out("GIVE no player");
                return;
            }
            boolean r = p.inventory.method_671(new ItemStack(i(a[2]), i(a[3]), a.length > 4 ? i(a[4]) : 0));
            out("GIVE -> " + r);
        } else if (cmd.equals("tes")) {
            // every ticking block entity near a position, flagging ones the chunk map does not hold
            int x = i(a[2]), y = i(a[3]), z = i(a[4]), r = i(a[5]);
            String tag = a.length > 6 ? a[6] : "";
            out("TES " + tag + " begin");
            for (Object o : new ArrayList(w.field_199)) {
                BlockEntity te = (BlockEntity) o;
                if (Math.abs(te.x - x) <= r && Math.abs(te.y - y) <= r && Math.abs(te.z - z) <= r) {
                    BlockEntity mapped = mapTe(w, te.x, te.y, te.z);
                    out("TES " + tag + " " + te.x + " " + te.y + " " + te.z + " " + teString(te)
                            + (te.method_1071() ? " REMOVED" : "") + (mapped == te ? " inmap" : " ORPHAN"));
                }
            }
            out("TES " + tag + " end");
        } else {
            out("UNKNOWN " + cmd);
        }
    }

    static class_69 player(MinecraftServer server) {
        List players = server.field_2842.field_578;
        return players.isEmpty() ? null : (class_69) players.get(0);
    }

    static String fmt(double d) {
        return String.format("%.2f", d);
    }

    /** The chunk's own map entry, read without World.getBlockTileEntity's side effects. */
    static BlockEntity mapTe(World w, int x, int y, int z) {
        class_43 chunk = w.method_214(x >> 4, z >> 4);
        Map map = chunk.field_964;
        return (BlockEntity) map.get(new class_339(x & 15, y, z & 15));
    }

    static String describe(World w, int x, int y, int z) {
        int id = w.getBlockId(x, y, z);
        int m = w.method_1778(x, y, z);
        BlockEntity te = mapTe(w, x, y, z);
        return id + ":" + m + (te == null ? "" : " te=" + teString(te) + (te.method_1071() ? "(removed)" : ""));
    }

    static String teString(BlockEntity te) {
        if (te instanceof class_283) {
            PistonBlockEntityAccessor p = (PistonBlockEntityAccessor) te;
            return "piston[" + p.lab$storedId() + ":" + p.lab$storedMeta() + " facing=" + p.lab$facing()
                    + (p.lab$extending() ? " ext" : " ret") + (p.lab$source() ? " src" : "")
                    + " prog=" + p.lab$lastProgress() + "/" + p.lab$progress() + "]";
        }
        if (te instanceof class_138) return "furnace[burn=" + ((class_138) te).field_1566 + "]";
        if (te instanceof class_225) return "chest";
        if (te instanceof JukeboxBlockEntity) return "jukebox[" + ((JukeboxBlockEntity) te).recordId + "]";
        return te.getClass().getSimpleName();
    }
}
```

## Appendix B: the runner and the name lookup

`tools/lab.py`:

```python
"""Run a TransmuteLab script against a real b1.7.3 dedicated server.

usage: python tools/lab.py SCRIPT [--keep-world]

Script lines:
  # comment
  wait SECONDS
  origin DX DY DZ        set X,Y,Z to spawn + (DX, DY, DZ); default is spawn + (8, 100 - spawnY, 8)
  anything else          sent to the console after {expr} substitution, where expr is
                         Python over X, Y, Z (e.g. "lab set {X+1} {Y} {Z} 1")
Prints every "LAB " line the server writes, in order.
"""
import os, re, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJECT, '..', 'BabricKit', 'scripts'))
sys.path.insert(0, os.path.join(PROJECT, '..', 'BabricKit'))
import drive  # noqa: E402
from babrickit import probe as probe_module  # noqa: E402
from babrickit import protocol  # noqa: E402


class Probe(probe_module.Probe):
    """The kit's probe, but answering a teleport with the yaw and pitch it was given.

    The stock probe replies to 0x0D with yaw 0, and the server adopts the reply, so a
    piston placed after a teleport would face whatever yaw 0 gives rather than the
    direction asked for.
    """

    def _handle(self, packet_id, values):
        if packet_id == 0x0D:
            x, y, z = probe_module._position_from(values)
            self.position = [x, y, z]
            self._centre = None
            if self.spawn is None:
                self.spawn = [x, y, z]
            self._raw(protocol.position_look(x, y, z, float(values[4]), float(values[5])))
            return
        super(Probe, self)._handle(packet_id, values)

PORT = 25599
PROPERTIES = """level-name=world
online-mode=false
server-port=%d
server-ip=
max-players=20
spawn-animals=false
spawn-monsters=false
pvp=true
allow-flight=true
white-list=false
""" % PORT


def main():
    script = sys.argv[1]
    keep = '--keep-world' in sys.argv
    if not keep:
        world = os.path.join(PROJECT, 'run', 'world')
        if os.path.isdir(world):
            shutil.rmtree(world)
    lines = [l.rstrip('\n') for l in open(script, encoding='utf-8')]
    os.makedirs(os.path.join(PROJECT, 'run'), exist_ok=True)
    with open(os.path.join(PROJECT, 'run', 'server.properties'), 'w') as f:
        f.write(PROPERTIES)
    probes = []
    java_home = drive.find_java_home()
    log_path = os.path.join(PROJECT, 'build', 'lab.log')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    server = drive.Server(PROJECT, log_path)
    server.start(java_home)
    server.wait_for(lambda: server.count('Done (') > 0, 600, 'server start')
    seen = [0]

    def lab_lines():
        with server._lock:
            new = server.lines[seen[0]:]
            seen[0] = len(server.lines)
        return [l for l in new if 'LAB ' in l or 'Exception' in l or 'at net.' in l or 'Attempted' in l]

    server.send('lab spawn')
    server.wait_for(lambda: any('LAB SPAWN' in l for l in server.lines), 30, 'spawn reply')
    sp = [l for l in server.lines if 'LAB SPAWN' in l][0].split('LAB SPAWN')[1].split()
    sx, sy, sz = int(sp[0]), int(sp[1]), int(sp[2])
    env = {'X': sx + 8, 'Y': 100, 'Z': sz + 8}
    print('spawn %d %d %d, origin %s' % (sx, sy, sz, env))
    try:
        for raw in lines:
            line = raw.split('#', 1)[0].strip() if not raw.strip().startswith('lab mark') else raw.strip()
            if not line:
                continue
            if line.startswith('wait '):
                time.sleep(float(line.split()[1]))
                for l in lab_lines():
                    print(l)
                continue
            if line.startswith('join '):
                probe = Probe('127.0.0.1', PORT, line.split()[1]).connect()
                probes.append(probe)
                print('joined %s as entity %s' % (line.split()[1], probe.entity_id))
                continue
            if line.startswith('origin '):
                d = [int(v) for v in line.split()[1:4]]
                env = {'X': sx + d[0], 'Y': sy + d[1], 'Z': sz + d[2]}
                print('origin %s' % env)
                continue
            cmd = re.sub(r'\{([^}]*)\}', lambda m: str(eval(m.group(1), {}, env)), line)
            server.send(cmd)
            time.sleep(0.05)
        time.sleep(1.0)
        for l in lab_lines():
            print(l)
    finally:
        for probe in probes:
            probe.close()
        server.stop()
    for l in lab_lines():
        print(l)


if __name__ == '__main__':
    main()
```

`tools/binyq.py`:

```python
"""Look up b1.7.3 names across biny (readable), intermediary and barn (what the mod compiles against).

usage: python binyq.py CLASS_REGEX [MEMBER_REGEX]
Prints, for each biny class matching CLASS_REGEX, its intermediary and barn names,
then each member whose biny name matches MEMBER_REGEX with the name to use in code
(barn if barn names it, else intermediary) and its descriptor in barn names.
"""
import os, re, sys
BINY = os.path.expanduser('~/.gradle/caches/fabric-loom/b1.7.3/net.glasslauncher.biny.b1_7_3.b1.7.3+e1fe071-v2/mappings.tiny')
BARN = os.path.join(os.path.dirname(__file__), '..', '..', 'BabricKit', 'cache', 'barn.tiny')

def parse(path):
    classes = {}
    cur = None
    with open(path, encoding='utf-8') as f:
        header = f.readline().rstrip('\n').split('\t')
        ns = header[3:]
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('c\t'):
                parts = line.split('\t')[1:]
                cur = {'names': dict(zip(ns, parts)), 'm': [], 'f': []}
                classes[parts[0]] = cur
            elif line.startswith('\tm\t') or line.startswith('\tf\t'):
                parts = line.split('\t')
                kind, desc, names = parts[1], parts[2], parts[3:]
                cur[kind].append({'desc': desc, 'names': dict(zip(ns, names))})
    return classes

biny = parse(BINY)
barn = parse(BARN)
cls_barn = {k: v['names'].get('named', k) for k, v in barn.items()}

def to_barn_desc(desc):
    return re.sub(r'L(net/minecraft/[\w/$]+);', lambda m: 'L%s;' % cls_barn.get(m.group(1), m.group(1)), desc)

def member_barn(inter_cls, kind, inter_name):
    c = barn.get(inter_cls)
    if not c: return None
    for m in c[kind]:
        if m['names'].get('intermediary') == inter_name:
            n = m['names'].get('named')
            return n if n and n != inter_name else None
    return None

cre = re.compile(sys.argv[1])
mre = re.compile(sys.argv[2]) if len(sys.argv) > 2 else None
for inter, c in sorted(biny.items()):
    named = c['names'].get('named', '')
    if not (cre.search(named) or cre.search(inter)):
        continue
    print('CLASS %s  = %s  (barn: %s)  obf client=%s server=%s' % (named, inter, cls_barn.get(inter, inter), c['names'].get('clientOfficial'), c['names'].get('serverOfficial')))
    if mre is None:
        continue
    for kind in ('f', 'm'):
        for m in c[kind]:
            bn = m['names'].get('named', '')
            if mre.search(bn):
                iname = m['names']['intermediary']
                b = member_barn(inter, kind, iname)
                print('   %s %-38s -> %-16s %s' % (kind, bn, b or iname, to_barn_desc(m['desc'])))
```

## Appendix C: experiment scripts

`scripts/e1_merge.txt`:

```
# E1: moving piston merge. Normal piston B pushes wool into a lit redstone torch at E;
# removing the torch updates a BUD-armed sticky piston A, which pushes a block into E;
# B's second loop then writes a moving block over A's, and the merge keeps the wool's metadata.
# Three copies side by side: wool 5 onto a log, wool 0 onto a log (control), wool 9 onto a stone slab.
lab fill {X-6} {Y-1} {Z-6} {X+26} {Y-1} {Z+6} 1
lab fill {X-6} {Y} {Z-6} {X+26} {Y+3} {Z+6} 0
wait 1
# copy k at X + 10k: torch first, power for A last
lab set {X} {Y} {Z} 76 5
lab set {X-1} {Y} {Z} 35 5
lab set {X-2} {Y} {Z} 33 5
lab set {X} {Y} {Z-1} 17 0
lab set {X} {Y} {Z-2} 29 3
lab set {X-1} {Y} {Z-2} 1 0
lab set {X-1} {Y+1} {Z-2} 69 13
lab set {X+10} {Y} {Z} 76 5
lab set {X+9} {Y} {Z} 35 0
lab set {X+8} {Y} {Z} 33 5
lab set {X+10} {Y} {Z-1} 17 0
lab set {X+10} {Y} {Z-2} 29 3
lab set {X+9} {Y} {Z-2} 1 0
lab set {X+9} {Y+1} {Z-2} 69 13
lab set {X+20} {Y} {Z} 76 5
lab set {X+19} {Y} {Z} 35 9
lab set {X+18} {Y} {Z} 33 5
lab set {X+20} {Y} {Z-1} 44 0
lab set {X+20} {Y} {Z-2} 29 3
lab set {X+19} {Y} {Z-2} 1 0
lab set {X+19} {Y+1} {Z-2} 69 13
wait 1
lab box {X-3} {Y} {Z-3} {X+1} {Y+1} {Z+1} before0
lab clearitems {X+10} {Y} {Z} 20
lab mark trigger
lab setn {X-2} {Y} {Z+1} 69 13
lab setn {X+8} {Y} {Z+1} 69 13
lab setn {X+18} {Y} {Z+1} 69 13
wait 1.5
lab box {X-3} {Y} {Z-3} {X+1} {Y+1} {Z+1} after0
lab box {X+7} {Y} {Z-3} {X+11} {Y+1} {Z+1} after1
lab box {X+17} {Y} {Z-3} {X+21} {Y+1} {Z+1} after2
lab tes {X+10} {Y} {Z} 14 after
lab items {X+10} {Y} {Z} 16 after
lab drop {X} {Y} {Z}
lab drop {X+10} {Y} {Z}
lab drop {X+20} {Y} {Z}
wait 0.5
lab items {X+10} {Y} {Z} 16 drops
```

`scripts/e2_player.txt`:

```
# E2: a real player harvests the transmuted blocks and places one back;
# chunk aliasing check; furnace pushed while it lights (tile-entity phase).
join alice
wait 3
lab fill {X-6} {Y-1} {Z-6} {X+36} {Y-1} {Z+6} 1
lab fill {X-6} {Y} {Z-6} {X+36} {Y+4} {Z+6} 0
wait 1
lab set {X} {Y} {Z} 76 5
lab set {X-1} {Y} {Z} 35 5
lab set {X-2} {Y} {Z} 33 5
lab set {X} {Y} {Z-1} 17 0
lab set {X} {Y} {Z-2} 29 3
lab set {X-1} {Y} {Z-2} 1 0
lab set {X-1} {Y+1} {Z-2} 69 13
lab set {X+20} {Y} {Z} 76 5
lab set {X+19} {Y} {Z} 35 9
lab set {X+18} {Y} {Z} 33 5
lab set {X+20} {Y} {Z-1} 44 0
lab set {X+20} {Y} {Z-2} 29 3
lab set {X+19} {Y} {Z-2} 1 0
lab set {X+19} {Y+1} {Z-2} 69 13
lab tp {X+2.5} {Y} {Z+2.5}
wait 1
lab setn {X-2} {Y} {Z+1} 69 13
lab setn {X+18} {Y} {Z+1} 69 13
wait 1.5
lab get {X} {Y} {Z}
lab get {X+20} {Y} {Z}
lab mark player harvest
lab give 270 1
lab select 0
lab inv
lab dig {X} {Y} {Z}
lab tp {X+0.5} {Y} {Z+0.5}
wait 1.5
lab dig {X+20} {Y} {Z}
lab tp {X+20.5} {Y} {Z+0.5}
wait 1.5
lab inv
lab mark place back: slab 44:9 onto the floor, then a second 44:9 on top
lab clearitems {X} {Y} {Z} 30
lab select 2
lab tp {X+24.5} {Y} {Z+3.5}
wait 1
lab use {X+24} {Y-1} {Z} 1
lab get {X+24} {Y} {Z}
lab give 44 1 9
lab inv
lab select 2
lab use {X+24} {Y} {Z} 1
lab get {X+24} {Y} {Z}
lab get {X+24} {Y+1} {Z}
lab dig {X+24} {Y} {Z}
lab tp {X+24.5} {Y} {Z+0.5}
wait 1.5
lab inv
```

`scripts/e3_misc.txt`:

```
# E3: (a) IDV slab placed back and stacked into a double slab; (b) chunk aliasing 524288 blocks away;
# (c) a furnace pushed by a BUD piston in the tick it lights; (d) control furnace with no piston.
join alice
wait 3
lab fill {X-6} {Y-1} {Z-6} {X+36} {Y-1} {Z+6} 1
lab fill {X-6} {Y} {Z-6} {X+36} {Y+4} {Z+6} 0
wait 1
lab mark (a) place-back
lab give 270 1
lab give 44 2 9
lab inv
lab tp {X+0.5} {Y} {Z+3.5}
wait 1
lab select 1
lab use {X} {Y-1} {Z} 1
lab get {X} {Y} {Z}
lab use {X} {Y} {Z} 1
lab get {X} {Y} {Z}
lab get {X} {Y+1} {Z}
lab select 0
lab dig {X} {Y} {Z}
lab tp {X+0.5} {Y} {Z+0.5}
wait 1.5
lab inv
lab mark (b) aliasing: gold block at origin+5, read it back 524288 blocks east and west
lab set {X} {Y+5} {Z} 41 0
lab get {X+524288} {Y+5} {Z}
lab get {X-524288} {Y+5} {Z}
lab get {X} {Y+5} {Z+524288}
lab get {X+262144} {Y+5} {Z}
lab mark (c) furnace push in the tile-entity phase
lab set {X+20} {Y} {Z} 61 3
lab set {X+20} {Y} {Z-1} 33 3
lab set {X+19} {Y} {Z-1} 1 0
lab set {X+19} {Y+1} {Z-1} 69 13
lab set {X+30} {Y} {Z} 61 3
wait 0.5
lab box {X+19} {Y} {Z-2} {X+21} {Y+1} {Z+2} c_before
lab tes {X+20} {Y} {Z} 3 c_before
lab furnace {X+20} {Y} {Z} 4 8 263 2
lab furnace {X+30} {Y} {Z} 4 8 263 2
wait 2
lab box {X+19} {Y} {Z-2} {X+21} {Y+1} {Z+2} c_after
lab tes {X+20} {Y} {Z} 3 c_after
lab box {X+30} {Y} {Z} {X+30} {Y} {Z} d_after
lab tes {X+30} {Y} {Z} 1 d_after
lab items {X+20} {Y} {Z} 4 c_after
wait 8
lab tes {X+20} {Y} {Z} 3 c_later
lab tes {X+30} {Y} {Z} 1 d_later
lab box {X+19} {Y} {Z-2} {X+21} {Y+1} {Z+2} c_later
```

`scripts/e4_survival.txt` (the variants; its survival half was rerun as E5):

```
# E4: the merge machine built only through the player's own placement and lever code,
# then variants built directly: same-type pistons, leaves, sapling, and wool 3 / 15.
join alice
wait 3
lab fill {X-6} {Y-1} {Z-6} {X+46} {Y-1} {Z+6} 1
lab fill {X-6} {Y} {Z-6} {X+46} {Y+4} {Z+6} 0
wait 1
lab give 76 1
lab give 35 1 5
lab give 33 1
lab give 17 1
lab give 29 1
lab give 1 2
lab give 69 2
lab give 17 1 0
lab inv
lab mark survival build
lab tp {X+3.5} {Y} {Z+3.5}
wait 0.5
lab select 0
lab use {X} {Y-1} {Z} 1
lab select 1
lab use {X-1} {Y-1} {Z} 1
lab select 2
lab tp {X-1.5} {Y} {Z+3.5} 90
wait 0.5
lab use {X-2} {Y-1} {Z} 1
lab select 3
lab tp {X+3.5} {Y} {Z+3.5}
wait 0.5
lab use {X} {Y-1} {Z-1} 1
lab select 4
lab tp {X+3.5} {Y} {Z-1.5} 180
wait 0.5
lab use {X} {Y-1} {Z-2} 1
lab select 5
lab tp {X+3.5} {Y} {Z+3.5}
wait 0.5
lab use {X-2} {Y-1} {Z-2} 1
lab use {X-2} {Y} {Z-2} 1
lab select 6
lab use {X-2} {Y+1} {Z-2} 5
lab use {X-2} {Y-1} {Z+1} 1
lab box {X-3} {Y} {Z-3} {X+1} {Y+1} {Z+1} built
lab mark flip A's lever (arms the sticky piston without updating it)
lab use {X-1} {Y+1} {Z-2} 1
lab box {X-3} {Y} {Z-3} {X+1} {Y+1} {Z+1} armed
lab mark flip B's lever
lab use {X-2} {Y} {Z+1} 1
wait 1.5
lab box {X-3} {Y} {Z-3} {X+1} {Y+1} {Z+1} fired
lab dig {X} {Y} {Z}
lab tp {X+0.5} {Y} {Z+0.5}
wait 1.5
lab inv
lab mark variants
# V1 at X+12: A is a normal piston like B
lab set {X+12} {Y} {Z} 76 5
lab set {X+11} {Y} {Z} 35 5
lab set {X+10} {Y} {Z} 33 5
lab set {X+12} {Y} {Z-1} 17 0
lab set {X+12} {Y} {Z-2} 33 3
lab set {X+11} {Y} {Z-2} 1 0
lab set {X+11} {Y+1} {Z-2} 69 13
# V2 at X+20: leaves in front of A
lab set {X+20} {Y} {Z} 76 5
lab set {X+19} {Y} {Z} 35 5
lab set {X+18} {Y} {Z} 33 5
lab set {X+20} {Y} {Z-1} 18 0
lab set {X+20} {Y} {Z-2} 29 3
lab set {X+19} {Y} {Z-2} 1 0
lab set {X+19} {Y+1} {Z-2} 69 13
# V3 at X+28: sapling in front of A
lab set {X+28} {Y} {Z} 76 5
lab set {X+27} {Y} {Z} 35 5
lab set {X+26} {Y} {Z} 33 5
lab set {X+28} {Y} {Z-1} 6 0
lab set {X+28} {Y} {Z-2} 29 3
lab set {X+27} {Y} {Z-2} 1 0
lab set {X+27} {Y+1} {Z-2} 69 13
# V4 at X+36 and X+44: wool 3 and wool 15 onto logs
lab set {X+36} {Y} {Z} 76 5
lab set {X+35} {Y} {Z} 35 3
lab set {X+34} {Y} {Z} 33 5
lab set {X+36} {Y} {Z-1} 17 0
lab set {X+36} {Y} {Z-2} 29 3
lab set {X+35} {Y} {Z-2} 1 0
lab set {X+35} {Y+1} {Z-2} 69 13
lab set {X+44} {Y} {Z} 76 5
lab set {X+43} {Y} {Z} 35 15
lab set {X+42} {Y} {Z} 33 5
lab set {X+44} {Y} {Z-1} 17 0
lab set {X+44} {Y} {Z-2} 29 3
lab set {X+43} {Y} {Z-2} 1 0
lab set {X+43} {Y+1} {Z-2} 69 13
wait 1
lab setn {X+10} {Y} {Z+1} 69 13
lab setn {X+18} {Y} {Z+1} 69 13
lab setn {X+26} {Y} {Z+1} 69 13
lab setn {X+34} {Y} {Z+1} 69 13
lab setn {X+42} {Y} {Z+1} 69 13
wait 1.5
lab box {X+9} {Y} {Z-2} {X+12} {Y} {Z} v1_sametype
lab box {X+17} {Y} {Z-2} {X+20} {Y} {Z} v2_leaves
lab box {X+25} {Y} {Z-2} {X+28} {Y} {Z} v3_sapling
lab get {X+36} {Y} {Z}
lab get {X+44} {Y} {Z}
lab items {X+24} {Y} {Z} 30 v_items
```

`scripts/e5_survival_only.txt`:

```
# E4: the merge machine built only through the player's own placement and lever code,
# then variants built directly: same-type pistons, leaves, sapling, and wool 3 / 15.
join alice
wait 3
lab fill {X-6} {Y-1} {Z-6} {X+46} {Y-1} {Z+6} 1
lab fill {X-6} {Y} {Z-6} {X+46} {Y+4} {Z+6} 0
wait 1
lab give 76 1
lab give 35 1 5
lab give 33 1
lab give 17 1
lab give 29 1
lab give 1 2
lab give 69 2
lab give 17 1 0
lab inv
lab mark survival build
lab tp {X+3.5} {Y} {Z+3.5}
wait 0.5
lab select 0
lab use {X} {Y-1} {Z} 1
lab select 1
lab use {X-1} {Y-1} {Z} 1
lab select 2
lab tp {X-1.5} {Y} {Z+3.5} 90
wait 0.5
lab use {X-2} {Y-1} {Z} 1
lab select 3
lab tp {X+3.5} {Y} {Z+3.5}
wait 0.5
lab use {X} {Y-1} {Z-1} 1
lab select 4
lab tp {X+3.5} {Y} {Z-1.5} 180
wait 0.5
lab use {X} {Y-1} {Z-2} 1
lab select 5
lab tp {X+3.5} {Y} {Z+3.5}
wait 0.5
lab use {X-2} {Y-1} {Z-2} 1
lab use {X-2} {Y} {Z-2} 1
lab select 6
lab use {X-2} {Y+1} {Z-2} 5
lab use {X-2} {Y-1} {Z+1} 1
lab box {X-3} {Y} {Z-3} {X+1} {Y+1} {Z+1} built
lab mark flip A's lever (arms the sticky piston without updating it)
lab use {X-1} {Y+1} {Z-2} 1
lab box {X-3} {Y} {Z-3} {X+1} {Y+1} {Z+1} armed
lab mark flip B's lever
lab use {X-2} {Y} {Z+1} 1
wait 1.5
lab box {X-3} {Y} {Z-3} {X+1} {Y+1} {Z+1} fired
lab dig {X} {Y} {Z}
lab tp {X+0.5} {Y} {Z+0.5}
wait 1.5
lab inv
```

E6 was generated by a short loop. Its setup lines, then one trial:

```
# E6: a sapling with damage 3. An oak tree grows over two lit redstone torches (metadata 3).
# A removed torch updates the blocks two away from it, so each piston stands two blocks
# from its torch, pushing a stone into the torch's space; breaking the new leaves there
# reads the torch's metadata. Leaves drop a sapling 1 time in 20. 60 trials.
join alice
wait 3
lab give 351 64 15
lab select 0
lab tp {X+0.5} {Y} {Z+6.5}
wait 1
lab fill {X-7} {Y} {Z-6} {X+7} {Y+10} {Z+6} 0
lab fill {X-7} {Y-1} {Z-6} {X+7} {Y-1} {Z+6} 1
lab set {X} {Y-1} {Z} 3 0
lab set {X} {Y} {Z} 6 0
lab set {X+2} {Y+2} {Z-1} 1 0
lab set {X-2} {Y+2} {Z-1} 1 0
lab set {X+2} {Y+2} {Z} 76 3
lab set {X-2} {Y+2} {Z} 76 3
lab set {X+3} {Y+2} {Z} 1 0
lab set {X-3} {Y+2} {Z} 1 0
lab set {X+4} {Y+2} {Z} 33 4
lab set {X-4} {Y+2} {Z} 33 5
lab set {X+5} {Y+2} {Z} 1 0
lab set {X-5} {Y+2} {Z} 1 0
lab set {X+5} {Y+3} {Z} 69 13
lab set {X-5} {Y+3} {Z} 69 13
lab clearitems {X} {Y} {Z} 9
lab mark trial 0
lab use {X} {Y} {Z} 1
wait 0.4
lab get {X} {Y} {Z}
lab get {X+2} {Y+2} {Z}
lab get {X-2} {Y+2} {Z}
lab items {X} {Y} {Z} 8 t0
```

E6b is E6 with `lab droplog on` before the `use` line, `wait 1.0` and
`lab droplog off` after it, and 40 trials. E6c is E6 without the two
`lab set ... 76 3` lines.

## Appendix D: the offline client check

Compiled with `javac NameTestObf.java` and run with `java -cp client.jar;.
NameTestObf`. `iz` is `ItemStack`, and `iz.l()` its name lookup:

```java
import java.lang.reflect.Constructor;
import java.lang.reflect.Method;

// Runs against Mojang's obfuscated client.jar. iz is ItemStack, and iz.l() is the
// name lookup a container tooltip calls (ItemStack.getItemName in MCP names).
// Block (uu) must be initialised before Item (gm), or the two static
// initialisers meet halfway and fail with a NullPointerException.
public class NameTestObf {
    public static void main(String[] args) throws Exception {
        Class.forName("uu");
        Class<?> stack = Class.forName("iz");
        Constructor<?> ctor = stack.getConstructor(int.class, int.class, int.class);
        Method name = stack.getMethod("l");
        int[] ids = {44, 17, 35, 6, 18};
        for (int id : ids) {
            StringBuilder line = new StringBuilder(id + ":");
            for (int d = 0; d < 16; ++d) {
                Object s = ctor.newInstance(id, 1, d);
                String result;
                try {
                    result = String.valueOf(name.invoke(s));
                } catch (java.lang.reflect.InvocationTargetException e) {
                    result = "THROWS(" + e.getCause() + ")";
                }
                line.append(" ").append(d).append("=").append(result);
            }
            System.out.println(line);
        }
    }
}
```

Output, abridged:

```
44: 0=tile.stoneSlab.stone 1=tile.stoneSlab.sand 2=tile.stoneSlab.wood 3=tile.stoneSlab.cobble
    4=THROWS(java.lang.ArrayIndexOutOfBoundsException: Index 4 out of bounds for length 4) ... 15=THROWS(...)
17: 0=tile.log 1=tile.log ... 15=tile.log
35: 0=tile.cloth.white 1=tile.cloth.orange ... 15=tile.cloth.black
6: 0=tile.sapling ... 15=tile.sapling
18: 0=tile.leaves ... 15=tile.leaves
```
