---
title: Tile Entity
description: Block data, ticking order, deferred creation, orphaned tile entities, saving, and furnace and piston glitches.
type: mechanic
categories: [Game mechanics]
aliases: [Tile Entities, Block Entity, Block Entities, TE, TE Phase]
---

A **tile entity** is an object that stores a block's data beyond its block ID and metadata.

## Types

There are eight tile-entity types. Several block IDs share one type.

| Block | Stored state | Work each tick |
|---|---|---|
| [[Chest]] | Inventory | None |
| [[Furnace]], lit or unlit | Inventory, burn time and cooking progress | Burns fuel and [[Smelting\|smelts]] |
| [[Dispenser]] | Inventory | None; dispensing uses a scheduled block tick |
| [[Sign]], standing or wall-mounted | Four lines of text | None |
| [[Monster Spawner]] | Mob type and spawn delay | Counts down and attempts to spawn while a player is nearby |
| [[Note Block]] | Pitch and previous redstone state | None |
| [[Jukebox]] | Inserted record's item ID | None |
| Moving [[Piston\|piston block]] | Carried block ID and metadata, direction, progress, extension state and retracting-base rendering state | Advances motion and settles the carried block |

<!-- src: TileEntity.java:100-108 registers eight subclasses; TileEntityChest.java:4;
     TileEntityFurnace.java:4-7,105-145; TileEntityDispenser.java:6,39-53;
     BlockDispenser.java:150-154 updateTick; TileEntitySign.java:4;
     TileEntityMobSpawner.java:4-7,25-87; TileEntityNote.java:4-5;
     TileEntityRecordPlayer.java:4; TileEntityPiston.java:8-25,105-125 -->

A double chest retains one tile entity in each half. An ordinary piston base
and a settled piston head have none. [[Crafting Table|Crafting tables]],
[[Bed|beds]] and [[Locked chest|locked chests]] also have none.
<!-- src: BlockChest.java:185-229 blockActivated combines separate inventories;
     BlockPistonBase.java:5, BlockPistonExtension.java:6, BlockWorkbench.java:3,
     BlockBed.java:6 and BlockLockedChest.java:5 extend Block, not BlockContainer -->

Tile entities are not moving entities. A moving piston keeps its tile entity
at the block position where its carried block will settle.
<!-- src: TileEntity.java:6 does not extend Entity;
     BlockPistonBase.java:345-356 writes moving TEs at destination coordinates -->

## Behaviour

### Bookkeeping

A tile entity holds a world reference, absolute block coordinates and an
invalid-state marker. A new object has no world reference, coordinates 0, 0, 0
and a valid state. Invalidating an object does not erase its inventory or other
data. Revalidating it clears the invalid state.
<!-- src: TileEntity.java:9-13,88-98; no constructor overrides these defaults -->

Three collections have separate roles:

| Collection | Scope | Purpose |
|---|---|---|
| Chunk tile-entity map | One per chunk | Finds one tile entity at a block position; supplies the tile entities saved with that chunk |
| Loaded tile-entity list | One per world | Supplies the objects updated during the tile-entity phase, in list order |
| Deferred tile-entity list | One per world | Holds objects added while the loaded list is being updated |

<!-- src: Chunk.java:22,30 chunkTileEntityMap; World.java:19-20
     loadedTileEntityList and field_30900_E; World.java:1235-1273;
     ChunkLoader.java:138-148 -->

The chunk map uses local x and z coordinates. Tile entities themselves keep
absolute coordinates.
<!-- src: World.java:1600-1601 masks x and z with 15;
     Chunk.java:437-439 adds the chunk's absolute offset -->

The chunk map and loaded list can disagree. Replacing a map entry does not
invalidate the displaced object or remove it from the loaded list. Several
valid objects can therefore tick at the same coordinates, although a block
lookup finds only one.
<!-- src: Chunk.java:434-445 setChunkBlockTileEntity; World.java:1612-1615;
     verified with original client.jar method probes: overwrite retains old
     valid object in loaded list -->

### Creation and lookup

Placing a tile-entity block creates its default tile entity. Ordinary removal
removes the block's mapped tile entity. A moving piston is the exception to
default creation: the piston movement supplies its carried block and motion
data separately.
<!-- src: BlockContainer.java:14-22; BlockPistonMoving.java:11-16,76-77;
     BlockPistonBase.java:125-126,160-161,352-356 -->

Looking up a tile entity reads the chunk map, not the loaded or deferred lists.
The lookup has these effects:

| Map entry | Result |
|---|---|
| Valid object | Returns that object, without checking whether its type or the block at its coordinates matches |
| Invalid object | Removes the map entry and returns no tile entity; does not create a replacement in the same lookup |
| No object, tile-entity block present | Runs the block's placement behaviour to create a replacement, then reads the map again |
| No object, another block or air present | Returns no tile entity |

<!-- src: World.java:1599-1601 getBlockTileEntity;
     Chunk.java:401-420 getChunkBlockTileEntity; verified invalid lookup followed
     by a second lookup repairing a chest against original client.jar -->

Repairing a missing [[Furnace|furnace]] or [[Dispenser|dispenser]] also resets
its facing and sends neighbour updates. Looking up a missing [[Chest|chest]]
does not send those updates. A missing moving-piston tile entity is not repaired.
<!-- src: BlockFurnace.java:20-49; BlockDispenser.java:21-50;
     BlockChest.java inherits BlockContainer.onBlockAdded, which only creates
     a TE; BlockPistonMoving.java:15-16 overrides onBlockAdded with an empty body.
     HackMD's claim about chest lookup sending updates does not apply here. -->

Repeated lookups during deferred creation can create several replacement
objects without finding any of them. A lookup is therefore not a passive
inspection of the world.
<!-- src: Chunk.java:404-412; World.java:1606-1610; verified deferred chest
     lookup queues a second TE and still returns null in original client.jar -->

### Installation and removal

Outside the tile-entity phase, installing a valid tile entity first appends it
to the loaded list. It then receives its world reference and coordinates.
The chunk accepts it only if a tile-entity block occupies those coordinates.
It checks for a tile-entity block, not for a matching tile-entity type.
Installation requests ignore invalid objects.
<!-- src: World.java:1604-1618; Chunk.java:434-445 -->

A rejected object still has its world reference and coordinates, and remains
in the loaded list. Installing the same object twice outside the phase also
adds it twice to that list. If it stays valid, it receives two updates per pass.
<!-- src: World.java:1612 has no contains check; Chunk.java:436-439 runs before
     the container check; verified rejection and duplicate insertion against
     original client.jar -->

Removing a tile entity by coordinates first performs a lookup. Outside the
phase, the found object is removed from the loaded list and the chunk entry
is removed and invalidated. During the phase, a found object is only
invalidated. An object present only in the deferred list cannot be found or
removed this way.
<!-- src: World.java:1622-1635; Chunk.java:448-455 removes only while
     isChunkLoaded; verified removal of invisible pending TE does not cancel
     it in original client.jar -->

### Ticking

The **tile-entity phase**, or **TE phase**, follows the ordinary entity update
pass. It runs before scheduled and random block ticks in singleplayer, but
after them on a dedicated server. See [[Game Tick#What one tick does]].
<!-- src: World.java:1208-1273; Minecraft.java:1160-1165;
     server MinecraftServer.java:328-333 -->

The phase runs in this order:

1. Enable deferred additions.
2. Visit the loaded tile-entity list in order. Update each valid object.
3. After each object's turn, remove it if it is invalid. Remove the chunk-map
   entry at its coordinates too.
4. Disable deferred additions.
5. Process the deferred list in insertion order. Skip invalid objects. Add
   each valid object to the loaded list if it is not already there, attempt
   to install it in the chunk map, and mark the position for a display update.
6. Clear the deferred list.

<!-- src: World.java:1235-1273 updateEntities -->

A newly deferred object gets its first update in the next TE phase. The ticking
list is not sorted by position. Loading a chunk appends its map's objects;
that map does not define a coordinate order.
<!-- src: World.java:1236 iterator and :1261 append; Chunk.java:30 HashMap,
     :459-461 onChunkLoad; World.java:1278-1283 addTileEntity -->

Tile-entity updates do not require random-tick selection, a nearby player, or
the surrounding chunks required for ordinary entity updates. Individual types
can impose their own conditions; a [[Monster Spawner|monster spawner]] checks
for a nearby player.
<!-- src: World.java:1238-1242 has only an invalidity check, unlike :1294-1295
     entity chunk-radius gate; TileEntityMobSpawner.java:21-27 -->

Cleanup uses coordinates, not object identity. An invalid object left in the
loaded list can remove and invalidate a different object now occupying its
chunk-map entry. An object invalidated after its turn waits until the next
phase for list cleanup.
<!-- src: World.java:1244-1248; Chunk.java:448-453;
     verified invalid displaced chest TE also removes its valid replacement
     during original client.jar updateEntities -->

### Deferred additions

During the ticking pass, installation assigns coordinates and queues the
object. It does not assign a world reference or change the chunk map.
A newly constructed object therefore has no world reference until the queue
is processed. An existing object retains its previous world reference.
<!-- src: World.java:1606-1610; verified both new and reused-object world
     references against original client.jar -->

Deferred objects are invisible to coordinate lookups for the rest of the
ticking pass. Removing their block does not cancel them. At the end of the
phase, they join the loaded list even if their position is now air or a block
without a tile entity.
<!-- src: World.java:1599-1601,1259-1266; Chunk.java:434-445 -->

When several deferred objects share a position, each accepted installation
overwrites the previous map entry. The last accepted object occupies the map.
The displaced objects remain in the loaded list.
<!-- src: World.java:1255-1267; Chunk.java:441-442 -->

### Orphaned and mismatched tile entities

An **orphaned tile entity** remains in the loaded list without being the object
held in the chunk map. It can continue ticking, but coordinate lookups cannot
find it. A **mismatched tile entity** is held under a block that does not
normally use its type, including a non-container block or air.
<!-- src: World.java:1238-1242; Chunk.java:401-420,434-445 -->

A furnace orphan can continue burning and smelting from its own inventory.
A moving-piston orphan expires when its motion finishes. It restores its
carried block only if a moving piston block still occupies its coordinates.
<!-- src: TileEntityFurnace.java:105-145 has no block-identity check;
     TileEntityPiston.java:105-113 checks the moving-block ID before restoring -->

Unloading a chunk invalidates only the objects in its map. An orphan absent
from that map can survive unloading and continue ticking. Leaving and
reopening the world discards list-only orphans because they are not saved.
<!-- src: Chunk.java:469-475; World.java:1238-1242;
     ChunkLoader.java:138-148 -->

## Furnace state changes

{{main|Furnace}}

A [[Furnace|furnace]] changes between lit and unlit blocks when its burning
state changes. The change takes place during its TE update:

1. Remember the position's metadata and mapped tile entity.
2. Suppress furnace inventory drops and replace the block with the lit or
   unlit furnace. The replacement invalidates the old tile entity and queues
   a new, empty one.
3. Restore inventory drops and the remembered metadata.
4. Revalidate the remembered tile entity and queue it for installation.

<!-- src: TileEntityFurnace.java:137-139; BlockFurnace.java:112-125;
     BlockContainer.java:14-21; World.java:1606-1610,1624-1625 -->

An ordinary transition leaves one extra empty furnace tile entity ticking.
The original object is installed last and keeps the inventory in the chunk
map. The empty replacement becomes an orphan.
<!-- src: BlockFurnace.java:20-22,124-125; World.java:1259-1266;
     Chunk.java:442; original client.jar probe confirms one additional
     persistent loaded TE after an ordinary extinguishing transition.
     Also tested in Block Data Corruption, experiment E3. -->

### Moving a furnace

A [[Piston|piston]] can move a furnace during the neighbour updates sent by
that transition. Its mobility check finds the invalid tile entity, removes it
from the map, and treats the furnace as having none. Any replacement created
by another lookup is deferred and remains invisible.
<!-- src: BlockPistonBase.java:268-269,273-307,309-337;
     Chunk.java:404-417; BlockFurnace.java:20-49,117-123 -->

The piston carries the furnace's block ID and metadata, not its inventory.
The moved furnace receives a new, empty tile entity when it settles. A furnace
moved as it lights can remain permanently lit without burning fuel. A furnace
moved as it goes out settles unlit.
<!-- src: BlockPistonBase.java:345-356; TileEntityPiston.java:111-112;
     TileEntityFurnace.java:137-139 changes blocks only when burn state changes;
     original client.jar probe: powered east-facing piston pushes furnace as
     it lights, destination is lit with zero burn time and three empty slots;
     tested in running server in Block Data Corruption E3 -->

### Destruction and substitution

Destroying the furnace during its state change can leave the original tile
entity behind after it is revalidated. The result depends on whether
destruction removes the invalid map entry:

| Destruction path | Result at the old position |
|---|---|
| Looks up the invalid tile entity, as piston removal can do | The original and empty replacement can remain list-only orphans under air or another non-container block |
| Avoids that lookup and leaves the entry intact | The original can remain mapped under air or another non-container block; the empty replacement remains list-only |

<!-- src: BlockFurnace.java:115-125,152-181; World.java:1622-1635,1259-1267;
     Chunk.java:415-417,434-445; HackMD Exploiting updateFurnaceBlockState,
     Illegal TEs 1-2 reports piston and door constructions respectively.
     Door construction details are absent; conditional mechanism only. -->

Placing a tile-entity block at a burning furnace orphan's coordinates supplies
a new mapped object. When the orphan stops burning, it replaces that block
with a furnace and restores the supplied object, not necessarily itself.
A chest tile entity can therefore end up mapped under a furnace. Destroying
the replacement during this transition can leave the supplied object under
air, either mapped or list-only by the same rules above.
<!-- src: TileEntityFurnace.java:137-139; BlockFurnace.java:113-125;
     Chunk.java:440-442; original client.jar probe confirms chest TE retained
     under idle furnace after a burning list-only furnace TE expires -->

### Metadata transfer and crashes

The state change copies the metadata of whatever block occupies the orphan's
coordinates. Placing [[Wool|wool]] there can give the resulting furnace the
wool's colour value as metadata when the orphan stops burning. The block and
metadata change first. The missing mapped tile entity then causes an exception.
<!-- src: BlockFurnace.java:113-125; Chunk.java:404-408;
     original client.jar probe: wool metadata 11 becomes idle furnace metadata
     11 before NullPointerException. HackMD Block transmutation 1 omits this. -->

| Condition | Failure |
|---|---|
| A list-only furnace changes burning state over air or a non-container block, with no mapped tile entity | `NullPointerException` after the furnace block and remembered metadata have been written |
| A furnace containing a non-furnace tile entity is opened or removed normally | `ClassCastException` when the block treats that object as a furnace inventory |
| A powered piston faces a transitioning furnace but cannot finish its push scan because of an obstruction beyond it or the push limit | `StackOverflowError` from recursively repairing the furnace's missing tile entity |

<!-- src: BlockFurnace.java:106,124,154; BlockPistonBase.java:268-269,273-307;
     Chunk.java:404-411; BlockFurnace.java:20-49 metadata notification calls
     piston again while newly created TEs remain deferred. Original client.jar
     probes reproduce NPE over wool, CCE removing a chest-TE furnace and
     StackOverflowError with a powered east-facing piston, furnace and obsidian
     beyond the furnace. The null-world piston-clear failure is separate. -->

## Pistons during the TE phase

{{main|Piston}}

Piston extension and retraction events run immediately inside the update
that triggers them. If triggered during the TE phase, their moving tile
entities are deferred. Normal pistons share one suppression of nested updates;
[[Sticky Piston|sticky pistons]] share another. This suppression does not
prevent one kind from activating the other.
<!-- src: World.java:2369-2373 playNoteAt; BlockPistonBase.java:7,52-55,
     66-79,112-113,172; Block.java:621,625 registers one Block object per kind -->

### Motion and clearing

A moving tile entity created in the TE phase settles on its third subsequent
TE update:

| Phase | Progress |
|---|---|
| Creation phase | Queued; no update |
| Next phase | Advances from 0 to 0.5 |
| Second phase after creation | Advances from 0.5 to 1; still a moving block |
| Third phase after creation | Removes its tile entity and restores the carried block, if a moving block is still present |

<!-- src: World.java:1235-1273; TileEntityPiston.java:105-125;
     original client.jar probe verifies all four phase boundaries -->

Explicitly clearing unfinished motion also removes the tile entity at its
coordinates and invalidates the motion object. It restores the carried block
only over a moving piston block. Clearing can remove a different mapped object
at the same coordinates.
<!-- src: TileEntityPiston.java:93-103 -->

Clearing an unfinished piston tile entity with no world reference throws
`NullPointerException`; it is not a no-op. Newly deferred piston tile entities
normally escape clearing because the coordinate lookup cannot find them.
<!-- src: TileEntityPiston.java:93-99 has no null-world guard;
     World.java:1599-1601; original client.jar probe directly calls clear on
     a fresh piston TE and confirms NPE, contradicting HackMD null-world claim -->

### Zero-tick sequences

A **zero-tick sequence** extends and retracts a piston within the same TE
phase. Its newly created head tile entity is invisible during retraction.
Removing the moving head block leaves that object queued. If its position
remains air, it joins the loaded list without a map entry and expires on its
third update without restoring a head.
<!-- src: BlockPistonBase.java:120-126,147-166;
     BlockPistonMoving.java:18-24; World.java:1259-1266;
     TileEntityPiston.java:105-113; original client.jar probe calls normal
     piston extend/retract events inside an updateEntities hook -->

| Sequence within one TE phase | Result |
|---|---|
| Normal piston extends and retracts into empty space | Retracts, leaving a temporary list-only head tile entity |
| Sticky piston pushes a block, then retracts | Does not pull the newly pushed block; that block finishes moving at the pushed position |
| Sticky piston extends into air with a movable block two spaces ahead, then retracts to pull it | The old head tile entity can settle into the pulled block's moving position first, replacing the pulled block with a head in front of a retracted base |
| First piston extends and retracts, then an opposing second piston extends into the same position | The first head can settle into the second head's moving position; the first base retains a head and the powered second base has no matching head |

<!-- src: BlockPistonBase.java:131-165,345-356; TileEntityPiston.java:105-113;
     World.java:1255-1267; Chunk.java:440-442. Original client.jar method
     probes confirm each row: stone in push/pull cases; two opposing normal
     pistons for shared position, with second kept powered. Events are invoked
     sequentially inside a TE hook, not generated by a reproduced redstone
     pulse circuit. Source attribution: HackMD TE phase piston mechanics. -->

The retained-head results are described as **double-headed** pistons in the
HackMD notes. They depend on another moving block occupying the orphan's
coordinates when it finishes. The competing tile entities' insertion and
update order determines which carried block survives. The sticky-piston
special case that abandons a just-pushed block requires finding its extending
tile entity; it cannot find one newly deferred in the same phase.
<!-- src: TileEntityPiston.java:111-112; BlockPistonBase.java:134-150;
     HackMD's alternative double-head explanation depends on deferred lookup
     in other versions and is not a separate Beta 1.7.3 push outcome -->

## Saving and multiplayer

### Saving and loading

Chunks save the objects in their tile-entity maps, not every object in the
loaded list. List-only orphans are not saved. A mapped object under air or a
non-container block is written, but rejected when loaded again. A mismatched
object under a tile-entity block can survive loading because the check does
not compare types.
<!-- src: ChunkLoader.java:138-148,188-195; Chunk.java:423-445;
     McRegionChunkLoader.java:26,50 reuses ChunkLoader compound routines;
     original client.jar NBT round-trip probes verify all three cases -->

Saved tile entities are reconstructed from their string type ID. Unknown IDs
are skipped. The world reference and invalid state are not saved.
<!-- src: TileEntity.java:24-63,100-108; Chunk.java:434-442 -->

Changes reported by a tile entity mark its chunk for saving. This does not
send a redstone neighbour update or schedule a block tick.
<!-- src: TileEntity.java:70-73 onInventoryChanged;
     World.java:2053-2059 func_698_b marks chunk modified and calls world
     access doNothingWithTileEntity, not notifyBlocksOfNeighborChange -->

### Multiplayer

The server owns inventories and world changes. Inventory windows receive
their contents separately from chunk block data. Furnace windows also receive
cooking progress, remaining burn time and the current fuel's total burn time.
<!-- src: server EntityPlayerMP.java:306-328 Packet103SetSlot,
     Packet104WindowItems and Packet105UpdateProgressbar;
     ContainerFurnace.java:28-63 -->

Signs receive text updates. Note sounds and piston motion use block-event
packets, which the client executes at the supplied coordinates. These are
not transfers of every tile entity's saved data.
<!-- src: server TileEntity.java:77-78 default getDescriptionPacket null;
     server TileEntitySign.java:29-36 Packet130UpdateSign;
     server PlayerInstance.java:171-176; server WorldServer.java:100-102;
     client NetClientHandler.java:551-563,587-588 -->

## Data values

Tile entities have string save IDs, not ordinary entity network IDs. Every
saved object has `id` as a string and `x`, `y`, `z` as integer block coordinates.
<!-- src: TileEntity.java:30-38,100-108; TileEntity does not extend Entity -->

| Type | Save ID | Additional saved fields |
|---|---|---|
| Furnace | `Furnace` | `Items` list; `BurnTime`, `CookTime` shorts |
| Chest | `Chest` | `Items` list |
| Jukebox | `RecordPlayer` | `Record` integer, written only when a record is present |
| Dispenser | `Trap` | `Items` list |
| Sign | `Sign` | `Text1`, `Text2`, `Text3`, `Text4` strings |
| Monster spawner | `MobSpawner` | `EntityId` string; `Delay` short |
| Note block | `Music` | `note` byte |
| Moving piston | `Piston` | `blockId`, `blockData`, `facing` integers; `progress` float; `extending` boolean |

<!-- src: TileEntity.java:100-108; TileEntityFurnace.java:49-82;
     TileEntityChest.java:49-77; TileEntityRecordPlayer.java:6-15;
     TileEntityDispenser.java:69-97; TileEntitySign.java:8-25;
     TileEntityMobSpawner.java:93-102; TileEntityNote.java:7-22;
     TileEntityPiston.java:128-143 -->

Each `Items` entry has a `Slot` byte, an `id` short, a `Count` byte and a
`Damage` short. Chest slots are 0–26, dispenser slots 0–8, and furnace slots
0–2 for input, fuel and output. A double chest saves two separate inventories.
<!-- src: TileEntityChest.java:6-7,49-77; TileEntityDispenser.java:9-10,69-97;
     TileEntityFurnace.java:4,49-82,149-179; ItemStack.java:75-85;
     BlockChest.java:185-229 -->

Loading truncates sign lines to 15 characters and clamps note pitch to 0–24.
A note block's previous redstone state is not saved. Furnace loading
recalculates total fuel duration from the item still in its fuel slot.
<!-- src: TileEntitySign.java:20-24; TileEntityNote.java:4-22;
     TileEntityFurnace.java:62-64 -->

Moving-piston saves record the previous update's progress, not its current
progress. Reloading can repeat a movement step. The separate retracting-base
rendering state is not saved.
<!-- src: TileEntityPiston.java:13-14,25,106,128-143; :133 restores both
     current and previous progress from the saved previous-progress field;
     field_31023_j is omitted from writeToNBT -->

## Verification and sources

Jan Matula and Spheres (v3rtices) document the deferred-creation mechanism and
the furnace and piston exploits in three April 2022 HackMD notes:

- [Investigation of TE mechanics](https://hackmd.io/@pa-2w-2MT5iGybHuegbruw/BkaSMRHV9)
- [Exploiting updateFurnaceBlockState](https://hackmd.io/@pa-2w-2MT5iGybHuegbruw/HyUrqxVN9)
- [TE phase piston mechanics](https://hackmd.io/@pa-2w-2MT5iGybHuegbruw/Hk1bpzs4c)

The rules on this page are checked against the Beta 1.7.3 decompile.
Method-level probes against the original client jar verify the bookkeeping,
furnace and piston sequences, crash corrections and NBT loading described
above. The probes use in-memory chunks and direct piston events, not a full
client session or a reconstruction of every reported redstone machine.
<!-- Verification: original Mojang client.jar SHA-1
     43db9b498cb67058d2e12d394e6507722e71bb45; Java 17; 21 assertion-based
     scenarios. Obfuscated World fd, Chunk lm, TileEntity ow, Furnace sk,
     Piston uk and BlockFurnace tc resolved using Babric intermediary b1.7.3.
     Unsafe constructs a disposable World, proxy IChunkProvider supplies empty
     chunks, a one-shot TileEntity hook invokes additions and piston events
     during the unmodified World.updateEntities loop. Blocks and TEs execute
     original jar bytecode. No decompiled source or vanilla methods modified. -->

The furnace note's door-based constructions lack placement and timing details.
Their proposed map-preserving result is conditional on avoiding removal of
the invalid map entry; those constructions are not independently reproduced.
[[Block Data Corruption#A piston can push a furnace in the tick it lights]]
records an earlier in-game test of furnace movement and the empty-tile-entity
leak.
<!-- Reported: HackMD Exploiting updateFurnaceBlockState, Illegal TEs 2 and 5
     contain "add details" placeholders. Read: Chunk.java:401-420 permits a
     valid mapped TE under air; :434-445 cannot newly install it there. -->
