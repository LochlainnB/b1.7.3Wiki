---
title: Tile Entity
description: Block data, ticking order, deferred creation, orphaned tile entities, saving, and furnace and piston glitches.
type: mechanic
categories: [Game mechanics]
aliases: [Tile Entities, Block Entity, Block Entities, TE, TE Phase]
---

A **tile entity** is an object that stores a block's data beyond its block ID and metadata.

## Types

The **block ID** is a number identifying the kind of block at a position.
**Metadata** stores a small amount of additional information, such as the
direction a block faces or its colour. A tile entity is a separate object in
the game's memory. It holds information that cannot fit into those block
values, such as an inventory.
Replacing a block and replacing its tile entity are therefore separate parts
of a block change.
<!-- src: Chunk.java:12-15 stores blocks and metadata separately from :22
     chunkTileEntityMap; :275-308 setBlockID;
     BlockFurnace.java:58-62 facing; TileEntityFurnace.java:4 inventory -->

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
| Moving [[Piston\|piston block]] | ID and metadata of the block being moved, movement direction and progress, whether it is extending, and whether the animation represents a retracting base | Advances the animation and puts the moved block in its final position |

<!-- src: TileEntity.java:100-108 registers eight subclasses; TileEntityChest.java:4;
     TileEntityFurnace.java:4-7,105-145; TileEntityDispenser.java:6,39-53;
     BlockDispenser.java:150-154 updateTick; TileEntitySign.java:4;
     TileEntityMobSpawner.java:4-7,25-87; TileEntityNote.java:4-5;
     TileEntityRecordPlayer.java:4; TileEntityPiston.java:8-25,105-125 -->

A double chest retains one tile entity in each half. An ordinary piston base
and a piston head that has finished moving have none.
[[Crafting Table|Crafting tables]], [[Bed|beds]] and
[[Locked chest|locked chests]] also have none.
<!-- src: BlockChest.java:185-229 blockActivated combines separate inventories;
     BlockPistonBase.java:5, BlockPistonExtension.java:6, BlockWorkbench.java:3,
     BlockBed.java:6 and BlockLockedChest.java:5 extend Block, not BlockContainer -->

While a piston head, base or pushed/pulled block is animating, the game uses
a temporary **moving piston block**. Its tile entity records what block should
occupy that position once the motion finishes. Tile entities are not ordinary
entities, such as mobs or dropped items: the moving-piston tile entity stays
at the final block position, rather than moving its coordinates along with
the animation.
<!-- src: TileEntity.java:6 does not extend Entity;
     BlockPistonBase.java:125-126,160-161,345-356 writes moving blocks and
     their TEs at final coordinates -->

A **tile-entity block** is a block type that uses a tile entity. These are also
called **container blocks** in the game's code, even when they have no
inventory, as with signs. A **non-container block** is a block type that does
not normally have a tile entity. The distinction matters when the game decides
whether to attach a tile entity to a block position.
<!-- src: BlockContainer.java:3-10; Chunk.java:405-411,440-445 -->

## Behaviour

### Bookkeeping

Every tile entity stores these bookkeeping properties:

- **World reference:** A link to the game object representing the world the
  tile entity operates in. It identifies *which world* to work in, rather
  than holding a copy of that world. The tile entity uses this link to ask
  what blocks are nearby, read block metadata or change blocks. A newly
  constructed tile entity has no world reference. The game assigns the link
  when it attempts to attach the object to a chunk.
  <!-- src: TileEntity.java:9,66-73,84-85; TileEntityPiston.java:75-77,96-99;
       TileEntityFurnace.java:139; Chunk.java:434-445 -->

- **Block coordinates:** The x, y and z position where the tile entity's
  work takes place, measured in the world as a whole. These coordinates
  identify *where* to work, but do not give the object access to the blocks
  there without a world reference. A newly constructed tile entity has
  coordinates 0, 0, 0. Installation assigns its intended block position;
  a deferred installation can assign these coordinates before the object
  receives its world reference.
  <!-- src: TileEntity.java:10-12,66-67; World.java:1606-1610;
       Chunk.java:437-439 -->

- **Invalid-state marker:** Whether the object has been marked as no longer
  active. Invalidating it lets the game skip its updates and remove it from
  its tracking collections. It does not erase the inventory or other stored
  data. Revalidating the same object clears the marker; it does not create a
  new object or inventory. A newly constructed tile entity is marked valid.
  Here, **valid** only means that this marker is clear. It does not guarantee
  that the object is attached to a block or matches that block's type.
  <!-- src: TileEntity.java:13,88-98; World.java:1238-1248;
       no constructor overrides the base fields' defaults -->

The game tracks tile entities in three separate collections. A **chunk** is a
section of the world that is loaded and saved as a unit. Its tile-entity
**map** associates block positions with tile-entity objects: one **map entry**
records which object belongs to one position. A **mapped tile entity** means
the object recorded for that position in this map.

The two lists serve different purposes from the map. The loaded list is the
list of objects offered an update each [[Game Tick|game tick]]. Working through
this list once is the **loaded-list update pass**. The deferred list is a
waiting queue for additions requested during that pass. These updates form
the **tile-entity phase**, explained under Ticking.

| Collection | Scope | Purpose |
|---|---|---|
| Chunk tile-entity map | One per chunk | Finds the tile entity associated with a block position. The game also uses this map to decide which tile entities to save with the chunk. |
| Loaded tile-entity list | One per world | Supplies the objects offered an update during the tile-entity phase, in list order. An object's presence here does not guarantee that it also has a chunk-map entry. |
| Deferred tile-entity list | One per world | Holds additions requested during the loaded-list update pass. The game processes this waiting queue after that pass, rather than changing the loaded list while working through it. |

<!-- src: Chunk.java:22,30 chunkTileEntityMap; World.java:19-20
     loadedTileEntityList and field_30900_E; World.java:1235-1273;
     ChunkLoader.java:138-148 -->

The chunk map uses x and z coordinates measured within its own chunk. Tile
entities themselves keep absolute coordinates, measured in the world as a
whole. These are two ways of identifying the same block position, not two
different locations for the tile entity.
<!-- src: World.java:1600-1601 masks x and z with 15;
     Chunk.java:437-439 adds the chunk's absolute offset -->

The chunk map and loaded list can disagree because changing one does not
automatically change the other. Replacing the object recorded in a map entry
does not invalidate the previously recorded object or remove it from the
loaded list. The old and new objects can both remain active at the same
coordinates. The game can update both, but asking for the tile entity at that
position finds only the one recorded in the map.
<!-- src: Chunk.java:434-445 setChunkBlockTileEntity; World.java:1612-1615;
     verified with original client.jar method probes: overwrite retains old
     valid object in loaded list -->

### Creation and lookup

Placing a tile-entity block creates a default tile entity for it. This means
new data, such as an empty inventory for a chest or furnace. Ordinary removal
of the block also removes its mapped tile entity. Moving piston blocks are an
exception to default creation: the piston movement has to supply the identity
of the block being moved and the animation's state separately.
<!-- src: BlockContainer.java:14-22; BlockPistonMoving.java:11-16,76-77;
     BlockPistonBase.java:125-126,160-161,352-356 -->

A **lookup** is the game's request for the tile entity at particular block
coordinates. Opening a furnace and checking whether a piston can push a block
are examples of actions that perform this request. The game checks the chunk
map, not the loaded or deferred lists.

| Map entry | Result |
|---|---|
| Valid object | Finds the recorded object even if its type does not match the current block, or the block has been removed. |
| Invalid object | Deletes the map entry and finds no tile entity. This request does not also create a replacement; a later lookup can try to do that. |
| No object, tile-entity block present | Runs the block's placement behaviour again to try to create a default tile entity, then reads the map again. This attempt to replace missing block data is called **repairing a missing tile entity**. |
| No object, another block or air present | Finds no tile entity and does not attempt a repair. |

<!-- src: World.java:1599-1601 getBlockTileEntity;
     Chunk.java:401-420 getChunkBlockTileEntity; verified invalid lookup followed
     by a second lookup repairing a chest against original client.jar;
     BlockFurnace.java:106 and BlockPistonBase.java:268-269 lookup callers -->

Repairing a missing [[Furnace|furnace]] or [[Dispenser|dispenser]] also
recalculates the block's facing using its placement rules and sends neighbour
updates. A **neighbour update** is a notification asking adjacent blocks to
react to a change. Those blocks can respond immediately, before the original
lookup finishes. Repairing a missing [[Chest|chest]] does not send these
updates. A moving piston has no default tile entity to create, so this repair
process cannot replace its missing motion data.
<!-- src: BlockFurnace.java:20-49; BlockDispenser.java:21-50;
     BlockChest.java inherits BlockContainer.onBlockAdded, which only creates
     a TE; BlockPistonMoving.java:15-16 overrides onBlockAdded with an empty body.
     World.java:506-523 notifyBlocksOfNeighborChange;
     HackMD's claim about chest lookup sending updates does not apply here. -->

Repairing creates a new object with default data. It does not recover the
inventory or other contents of the missing tile entity.
<!-- src: BlockContainer.java:14-16; BlockFurnace.java:128-129;
     TileEntityFurnace.java:4 and TileEntityChest.java:6 start with empty slots -->

During the loaded-list update pass, a repair puts its new tile entity in the
deferred list instead of the chunk map. Reading the map again still finds no
object. Another lookup can therefore attempt another repair, adding another
replacement to the deferred list. Looking up a tile entity can change the
world and create new objects; it is not just an inspection of existing data.
<!-- src: Chunk.java:404-412; World.java:1606-1610; verified deferred chest
     lookup queues a second TE and still returns null in original client.jar -->

### Installation and removal

**Installing** a tile entity means asking the game to attach that object to a
block position. When the game is not working through the loaded-list update
pass, it handles a request for a valid object immediately:

1. Add the object to the loaded tile-entity list.
2. Give the object its world reference and block coordinates.
3. Check the block at those coordinates. If it is a tile-entity block, record
   the object in the chunk map. If it is air or a non-container block, do not
   add a map entry.

The block check does not compare tile-entity types. It can accept a chest tile
entity at a furnace's position, for example. An installation request for an
object marked invalid is ignored entirely.
<!-- src: World.java:1604-1618; Chunk.java:434-445 -->

Rejection in step 3 only prevents an entry in the chunk map. The rejected
object still has its world reference and coordinates, and remains in the
loaded list. It can therefore keep receiving updates despite not being
associated with a block in the map.

Immediate installation also does not check for an existing loaded-list entry.
Installing the same object twice adds two entries referring to that one object.
If the object stays valid, the game updates it twice per loaded-list pass.
<!-- src: World.java:1612 has no contains check; Chunk.java:436-439 runs before
     the container check; verified rejection and duplicate insertion against
     original client.jar -->

Removing a tile entity at a block position first performs a coordinate lookup.
When the loaded-list update pass is not running, the game removes the found
object from the loaded list, removes the chunk-map entry and invalidates the
object. During the update pass, it only marks the found object invalid; the
pass's cleanup handles removal later.

This removal request does not search the deferred list. If an object is waiting
there and has no chunk-map entry, the lookup cannot find it. Removing the tile
entity at its coordinates does not cancel that waiting object's addition.
<!-- src: World.java:1622-1635; Chunk.java:448-455 removes only while
     isChunkLoaded; verified removal of invisible pending TE does not cancel
     it in original client.jar -->

### Ticking

The **tile-entity phase**, or **TE phase**, is the part of a
[[Game Tick|game tick]] that updates tile entities. Updating a tile entity gives
it a turn to do its per-tick work, such as burning fuel or advancing a piston
animation. Some types only store data and do no work during this turn.

The TE phase follows the update pass for ordinary entities, such as mobs and
dropped items. It runs before scheduled and random block ticks in singleplayer,
but after those block ticks on a dedicated server.
See [[Game Tick#What one tick does]].
<!-- src: World.java:1208-1273; Minecraft.java:1160-1165;
     server MinecraftServer.java:328-333 -->

The phase runs in this order:

1. Start deferring additions. Requests to install tile entities go into the
   deferred tile-entity list instead of changing the loaded list during its
   update pass.
2. Visit the loaded tile-entity list in order. Update each object that is still
   valid. Skip the update of an object already marked invalid.
3. After checking each object, remove it from the loaded list if it is invalid.
   Also ask its chunk to remove the map entry at that object's coordinates.
4. Stop deferring additions once the loaded-list pass is finished.
5. Process the deferred tile-entity list in the order additions were requested.
   Skip invalid objects. Add each valid object to the loaded list if it is not
   already present, then attempt to put it in the chunk map. Mark its block
   position for a display update so the game can redraw the change.
6. Empty the deferred list. The next TE phase uses the updated loaded list.

<!-- src: World.java:1235-1273 updateEntities -->

A newly added, deferred object gets its first update in the next TE phase.
By the time it joins the loaded list, the current phase's update pass has
already finished.

The loaded list is not sorted by block position. Loading a chunk adds that
chunk's mapped objects to the end of the world list, and the chunk map does
not supply them in a fixed coordinate order. Tile entities do not have a rule
such as updating from the lowest x coordinate to the highest.
<!-- src: World.java:1236 iterator and :1261 append; Chunk.java:30 HashMap,
     :459-461 onChunkLoad; World.java:1278-1283 addTileEntity -->

Tile entities do not have to be selected for a random block tick to receive
their updates. The world also does not require a nearby player or check that
surrounding chunks are loaded before offering a tile entity its update.
Individual tile-entity types can still impose conditions on their own work;
a [[Monster Spawner|monster spawner]] checks for a nearby player before
attempting to spawn mobs.
<!-- src: World.java:1238-1242 has only an invalidity check, unlike :1294-1295
     entity chunk-radius gate; TileEntityMobSpawner.java:21-27 -->

Cleanup removes a chunk-map entry using the invalid object's coordinates. It
does not check that the map still points to the object being cleaned up. If
an old tile entity is marked invalid after being replaced in the map, but
remains in the loaded list, cleanup of that old object can remove and
invalidate the new tile entity at the same position as well.

An object marked invalid after the update pass has already checked it remains
in the loaded list until the next TE phase's cleanup reaches it.
<!-- src: World.java:1244-1248; Chunk.java:448-453;
     verified invalid displaced chest TE also removes its valid replacement
     during original client.jar updateEntities -->

### Deferred additions

During the loaded-list update pass, an installation request assigns block
coordinates to the tile entity and adds it to the **deferred tile-entity list**.
This is the waiting queue described under Bookkeeping, not the loaded list
that the game is currently updating. The request does not yet assign a world
reference or create a chunk-map entry.

A newly constructed tile entity therefore knows its intended coordinates but
still has no link to a world. It receives that world reference when the game
processes the deferred list and attempts to attach it to a chunk. If the
request reuses an existing tile entity rather than creating one, that object
keeps its previous world reference until this attachment attempt.
<!-- src: World.java:1606-1610; verified both new and reused-object world
     references against original client.jar -->

Coordinate lookups cannot find objects that are only in the deferred list,
because lookups search the chunk map. This is what it means for a pending tile
entity to be **invisible to lookups**; it is not a statement about the block's
appearance on screen.

Removing a pending tile entity's intended block does not cancel the object
waiting in the deferred list. At the end of the TE phase, a still-valid object
joins the loaded list even if the block is gone. Attachment to the chunk map
then fails over air or a non-container block, but that failure does not undo
the addition to the loaded list.
<!-- src: World.java:1599-1601,1259-1266; Chunk.java:434-445 -->

When several deferred objects are waiting for the same block position, the
game processes them in the order they were added. Each successful chunk-map
installation replaces the object recorded by the previous installation at
that position. Only the last accepted object remains mapped, but all the
valid objects added to the loaded list can continue receiving updates.
<!-- src: World.java:1255-1267; Chunk.java:441-442 -->

### Orphaned and mismatched tile entities

An **orphaned tile entity** is still in the loaded list, but no longer has a
chunk-map entry of its own. Its position's map entry may be empty or may point
to a different tile entity. The orphan can continue receiving updates, but
asking for the tile entity at its coordinates does not find it. **List-only**
describes an object tracked in the loaded list but not the chunk map.

A **mismatched tile entity** is recorded in the chunk map for a block that
does not normally use its type. A chest tile entity recorded at a furnace's
position is one example. A map entry can also be left at coordinates containing
a block that normally has no tile entity, or even air.
<!-- src: World.java:1238-1242; Chunk.java:401-420,434-445 -->

An orphaned furnace tile entity still has its own inventory and fuel timers,
so it can continue burning and smelting even without a mapped furnace at its
position. An orphaned moving-piston tile entity continues its motion timer,
then invalidates itself when the motion finishes. It puts its saved block
back only if a moving piston block still occupies the orphan's coordinates.
If those coordinates contain air, it does not place a block there.
<!-- src: TileEntityFurnace.java:105-145 has no block-identity check;
     TileEntityPiston.java:105-113 checks the moving-block ID before restoring -->

Unloading a chunk invalidates the tile entities recorded in that chunk's map.
It does not search the world's loaded list for every object whose coordinates
lie in the chunk. An orphan missing from the map can therefore remain valid
in the loaded list and continue ticking after the chunk unloads.

Leaving and reopening the world has a different result. List-only orphans are
not written to the world save, so reopening the world does not recreate them.
<!-- src: Chunk.java:469-475; World.java:1238-1242;
     ChunkLoader.java:138-148 -->

## Furnace state changes

{{main|Furnace}}

A [[Furnace|furnace]] uses different block IDs for its lit and unlit states.
Starting or stopping fuel burning replaces the block, rather than just changing
its appearance. The inventory and fuel timers belong to the tile entity, so
the game keeps the original tile-entity object to preserve those contents.
<!-- src: TileEntityFurnace.java:4-7,105-139; BlockFurnace.java:112-125 -->

During the furnace tile entity's update, this replacement proceeds as follows:

1. Read the block's metadata and look up its mapped tile entity. Remember the
   metadata and that same tile-entity object for restoration later. Normally,
   this is the furnace's own tile entity.
2. Temporarily prevent the usual dropping of furnace inventory contents when
   the old block is removed. Replace the block with the lit or unlit furnace.
   Removal marks the old tile entity invalid. Placement of the new block
   creates an empty furnace tile entity and adds it to the deferred list.
3. Run the block replacement's neighbour updates. Adjacent blocks can respond
   while the original tile entity is invalid and the empty replacement is
   still waiting in the deferred list.
4. Re-enable furnace inventory drops and restore the remembered block metadata.
   Restoring this metadata sends further neighbour updates.
5. Revalidate the tile entity remembered in step 1 and add it to the deferred
   list for installation at the furnace's coordinates. Its inventory and
   other data are preserved because it is the same object, not a new copy.

<!-- src: TileEntityFurnace.java:137-139; BlockFurnace.java:112-125;
     BlockContainer.java:14-21; World.java:1606-1610,1624-1625 -->

In an ordinary state change, with no intervening block removal or piston
movement, the empty replacement is installed first when the deferred list is
processed at the end of the TE phase. The original furnace tile entity is
installed after it. The chunk map ends up pointing to the original object,
so opening the furnace still accesses the original inventory. Both objects
remain in the loaded list. The extra empty furnace tile entity becomes an
orphan and continues receiving updates.
<!-- src: BlockFurnace.java:20-22,124-125; World.java:1259-1266;
     Chunk.java:442; original client.jar probe confirms one additional
     persistent loaded TE after an ordinary extinguishing transition.
     Also tested in Block Data Corruption, experiment E3:
     content/research/block-data-corruption.md, section
     "A piston can push a furnace in the tick it lights" records an earlier
     in-game test of furnace movement and the empty-tile-entity leak. -->

### Moving a furnace

A [[Piston|piston]] normally cannot move a block that has a tile entity. During
the neighbour updates sent by a furnace lighting or going out, the original
furnace tile entity is temporarily invalid. If a piston checks the furnace
then, its tile-entity lookup deletes the invalid map entry and finds no object.
The furnace can pass the tile-entity part of the piston's movement check.

Another lookup may try to repair the missing furnace tile entity before the
push finishes. However, a repair made during the TE update pass adds the new
object to the deferred list, not the chunk map. That replacement still cannot
be found by the piston's coordinate lookups.
<!-- src: BlockPistonBase.java:268-269,273-307,309-337;
     Chunk.java:404-417; BlockFurnace.java:20-49,117-123 -->

The piston moves the furnace's block ID and metadata, not its inventory or
fuel timers. The original furnace tile entity stays at the old coordinates.
When the piston finishes moving the furnace block, placement at the new
position creates a new, empty furnace tile entity.

A furnace moved as it lights can arrive as a lit block with an empty inventory
and no burning fuel. Waiting does not turn that block unlit: the new tile
entity already has no burning fuel, and the lit-to-unlit replacement only
happens when its burning state changes. A furnace moved as it goes out arrives
as an unlit block instead.
<!-- src: BlockPistonBase.java:345-356; TileEntityPiston.java:111-112;
     TileEntityFurnace.java:137-139 changes blocks only when burn state changes;
     original client.jar probe: powered east-facing piston pushes furnace as
     it lights, destination is lit with zero burn time and three empty slots;
     tested in running server in Block Data Corruption E3 -->

### Destruction and substitution

#### Tile entities left after removal

Removing the furnace block during the neighbour updates of a lit/unlit state
change can leave its tile entity behind. The state-change procedure still
remembers the original furnace tile entity from its initial lookup. The new,
empty furnace tile entity created by placement of the lit or unlit block is
also waiting in the deferred list. The procedure later revalidates the
remembered original object and requests installation, even though the furnace
block has already been removed.

If the old position is now air or a non-container block, the result depends
on whether removal deleted the original tile entity's invalid map entry:

| Destruction path | Result at the old position |
|---|---|
| Removal looks up the invalid tile entity and deletes its map entry, as piston removal can do | The original furnace tile entity and the empty replacement can remain in the loaded list without map entries. They are list-only orphans at the old coordinates. |
| Removal avoids that lookup and leaves the map entry intact | Revalidation makes the original furnace tile entity valid again in its existing map entry, even if the position now contains air or a non-container block. The empty replacement remains list-only. |

<!-- src: BlockFurnace.java:115-125,152-181; World.java:1622-1635,1259-1267;
     Chunk.java:415-417,434-445; HackMD Exploiting updateFurnaceBlockState,
     Illegal TEs 1-2 reports piston and door constructions respectively.
     Door-based constructions lack placement and timing details and are not
     independently reproduced. Their proposed map-preserving result requires
     removal to leave the invalid map entry intact until the furnace
     state-change procedure revalidates the remembered object. Conditional
     mechanism only. Reported: Illegal TEs 2 and 5 contain "add details"
     placeholders. Read: Chunk.java:401-420 permits a valid mapped TE at
     coordinates containing air; :434-445 cannot newly install it there. -->

#### Replacing a chest with a furnace

An orphaned furnace tile entity can also replace a different tile-entity
block. The orphan still runs its fuel timer at the old coordinates. Its
lit/unlit replacement procedure looks up whichever tile entity is currently
mapped at those coordinates, not necessarily the furnace object performing
the update.

For a chest placed at the burning furnace orphan's position, the sequence is:

1. Placing the chest creates a chest tile entity and records it in the chunk
   map. The orphaned furnace tile entity remains separately in the loaded list.
2. When the orphan's burning fuel runs out, it starts the unlit-furnace
   replacement procedure. The procedure looks up the tile entity at the old
   coordinates and remembers the **chest tile entity** for later restoration.
3. The procedure replaces the chest block with an unlit furnace block.
4. It revalidates the remembered chest tile entity and adds that object to the
   deferred list. At the end of the TE phase, the chunk accepts it at the
   furnace's position because installation checks for a tile-entity block,
   not a matching tile-entity type.

The result is a furnace block with a chest tile entity associated with its
position.
If neighbour updates remove the newly placed furnace block before this same
replacement procedure finishes, the **remembered chest tile entity** can be
left at coordinates that now contain air. It remains mapped if removal leaves
its invalid map entry intact; it becomes list-only if removal deletes that
entry. This is the chest object remembered in step 2, not the orphaned furnace
object that triggered the replacement.
<!-- src: TileEntityFurnace.java:137-139; BlockFurnace.java:113-125;
     Chunk.java:440-442; original client.jar probe confirms chest TE retained
     under idle furnace after a burning list-only furnace TE expires -->

### Metadata transfer and crashes

The furnace state-change procedure also reads the block metadata currently
at the orphan's coordinates. It does not check that this value came from a
furnace. Placing [[Wool|wool]] at a burning furnace orphan's position therefore
makes the procedure remember the wool's colour metadata when the orphan's
fuel runs out. It writes an unlit furnace block and restores that wool value
as the furnace's metadata.

Wool normally has no tile entity, so the procedure's initial lookup remembers
no tile-entity object to restore. After changing the block and metadata, the
procedure tries to revalidate that missing object and throws an exception.
The metadata transfer occurs before the failure; it is not a crash-free
method of changing a furnace's metadata.
<!-- src: BlockFurnace.java:113-125; Chunk.java:404-408;
     original client.jar probe: wool metadata 11 becomes idle furnace metadata
     11 before NullPointerException. HackMD Block transmutation 1 omits this. -->

| Condition | Failure |
|---|---|
| A list-only furnace tile entity changes burning state at coordinates containing air or a non-container block, with no mapped tile entity | `NullPointerException`: the state-change procedure tries to use a missing tile-entity object. The furnace block and remembered metadata have already been written. |
| A furnace block with a non-furnace tile entity, such as the chest object above, is opened or removed normally | `ClassCastException`: the game tries to treat a different kind of object as a furnace tile entity so it can access the furnace inventory. |
| A powered piston faces a furnace changing between lit and unlit, but an obstruction beyond the furnace or the push limit prevents a complete push | `StackOverflowError`: attempts to repair the furnace's missing tile entity repeatedly trigger more piston checks before the previous checks can finish. |

<!-- src: BlockFurnace.java:106,124,154; BlockPistonBase.java:268-269,273-307;
     Chunk.java:404-411; BlockFurnace.java:20-49 metadata notification calls
     piston again while newly created TEs remain deferred. Original client.jar
     probes reproduce NPE over wool, CCE removing a chest-TE furnace and
     StackOverflowError with a powered east-facing piston, furnace and obsidian
     beyond the furnace. The null-world piston-clear failure is separate. -->

## Pistons during the TE phase

{{main|Piston}}

Piston extension and retraction start immediately when the game processes the
block update that triggers them. If a tile entity's update triggers a piston,
the piston acts before that tile entity's update finishes. The piston changes
blocks immediately, but its requests to install moving tile entities go into
the deferred list because the loaded-list update pass is still running.

While a normal piston processes extension or retraction, normal pistons
temporarily ignore neighbour updates that could make them react in the middle
of that movement operation. This protection is shared by all normal pistons.
[[Sticky Piston|Sticky pistons]] have a separate, shared protection. A normal
piston's operation therefore does not prevent a sticky piston from reacting
to its neighbour updates, or the reverse.
<!-- src: World.java:2369-2373 playNoteAt; BlockPistonBase.java:7,52-55,
     66-79,112-113,172; Block.java:621,625 registers one Block object per kind -->

### Motion and clearing

A moving-piston tile entity remembers the block ID and metadata to put at its
position when the motion finishes. This saved block is the **carried block**;
it can be a piston head or base, not just a block being pushed or pulled.
**Settling** means replacing the temporary moving piston block with that
carried block.
<!-- src: BlockPistonBase.java:125-126,160-161,345-356;
     TileEntityPiston.java:8-25,111-112 -->

Motion progress runs from 0 at the start to 1 at the end; 0.5 is halfway.
A moving tile entity created during the loaded-list update pass does not
advance in that same pass. It settles on its third subsequent TE update:

| Phase | Progress |
|---|---|
| Creation phase | Added to the deferred list. It receives no motion update in this phase. |
| Next phase | Advances from 0 to 0.5: halfway through the motion. |
| Second phase after creation | Advances from 0.5 to 1. The animation reaches its endpoint, but the position still contains a temporary moving piston block. |
| Third phase after creation | Removes the motion tile entity and replaces the temporary moving piston block with the carried block, if a moving piston block is still present at those coordinates. |

<!-- src: World.java:1235-1273; TileEntityPiston.java:105-125;
     original client.jar probe verifies all four phase boundaries -->

**Clearing** a moving piston tile entity means explicitly finishing its motion
early, rather than waiting for its normal updates to finish. Retraction can
attempt this for a head that is still extending. The clear operation removes
the mapped tile entity at the motion object's coordinates and invalidates the
motion object itself. It restores the carried block only if the position
still contains a moving piston block.

As with other coordinate-based removal, clearing does not check that the map
entry belongs to the motion object being cleared. It can remove a different
tile entity now recorded at the same position.
<!-- src: TileEntityPiston.java:93-103; BlockPistonBase.java:120-122 -->

If clearing is attempted on an unfinished piston tile entity with no world
reference, it throws `NullPointerException`: the object tries to use a world
that it has not yet been linked to. It does not safely ignore the request.
However, ordinary coordinate lookups cannot find newly deferred piston tile
entities. Retraction therefore cannot clear those pending objects through
such a lookup in the first place.
<!-- src: TileEntityPiston.java:93-99 has no null-world guard;
     World.java:1599-1601; original client.jar probe directly calls clear on
     a fresh piston TE and confirms NPE, contradicting HackMD null-world claim -->

### Zero-tick sequences

A **zero-tick sequence** extends and retracts a piston within the same TE
phase, before the newly created motion tile entities get their first update.
The extending head's tile entity is still in the deferred list when retraction
tries to look it up. Retraction cannot find and clear that pending head object.
Removing the moving head block therefore leaves its tile entity waiting in
the deferred list.

If the head's intended position remains air, the pending head object joins
the loaded list at the end of the phase but is rejected by the chunk map.
It runs its motion timer as a list-only orphan. On its third update, it
invalidates itself without restoring a head because the position is still air.
<!-- src: BlockPistonBase.java:120-126,147-166;
     BlockPistonMoving.java:18-24; World.java:1259-1266;
     TileEntityPiston.java:105-113; original client.jar probe calls normal
     piston extend/retract events inside an updateEntities hook -->

| Sequence within one TE phase | Result |
|---|---|
| Normal piston extends and retracts into empty space | The base retracts. The pending head tile entity temporarily survives as a list-only orphan, then expires without placing a head if its position stays air. |
| Sticky piston pushes a block, then retracts | The piston does not pull the newly pushed block back. That block's motion tile entity finishes the push, leaving the block at the pushed position. |
| Sticky piston extends into air with a movable block two spaces ahead of the base, then retracts to pull that block | The old extending-head tile entity can finish first at the position now used for the pull. It places a head instead of the pulled block, leaving a head in front of a retracted base. |
| First piston extends and retracts, then an opposing second piston extends its head into the same position | The first piston's old head tile entity can finish at the shared position before the second head's tile entity. The head there belongs to the first piston; the powered second base has no matching head. |

<!-- src: BlockPistonBase.java:131-165,345-356; TileEntityPiston.java:105-113;
     World.java:1255-1267; Chunk.java:440-442. Original client.jar method
     probes confirm each row: stone in push/pull cases; two opposing normal
     pistons for shared position, with second kept powered. Events are invoked
     sequentially inside a TE hook, not generated by a reproduced redstone
     pulse circuit. Source attribution: HackMD TE phase piston mechanics. -->

The retained-head results are described as **double-headed** pistons in the
HackMD notes. Unlike the empty-space case, a new moving piston block occupies
the old head tile entity's coordinates when that old object finishes. The old
object checks only that a moving piston block is present, not that it belongs
to the old object's original movement. It can replace that new moving block
with its own carried head. The order in which the competing tile entities
join the loaded list and receive updates determines which block survives.

Sticky pistons also have special handling for a block that is still being
pushed: retraction can finish that push without pulling the block back. This
special handling requires finding the pushed block's extending tile entity.
It cannot identify a tile entity that is newly deferred in the same TE phase.
<!-- src: TileEntityPiston.java:111-112; BlockPistonBase.java:134-150;
     HackMD's alternative double-head explanation depends on deferred lookup
     in other versions and is not a separate Beta 1.7.3 push outcome -->

#### A sticky pull, step by step

For the sticky-piston pull in the table, the head and the block being pulled
both use the position immediately in front of the base, but at different
points in the sequence:

1. Extension into air creates a moving head at that position. Its head tile
   entity is added to the deferred list.
2. Retraction begins in the same TE phase. It cannot find the deferred head
   tile entity to clear it. Instead, the pull places a new moving piston block
   at the head's position, carrying the block that was two spaces ahead of the
   base. The pull's tile entity is added to the deferred list after the head's.
3. At the end of the phase, both objects join the loaded list in that order.
   The pull's object is installed last at the shared position and gets the
   chunk-map entry. The older head object remains as an orphan in the loaded
   list.
4. When the older head object finishes its motion timer, the shared position
   still contains the pull's moving piston block. The head object removes
   the mapped pull tile entity and places its own carried head there. The
   pulled block is lost, and a head remains in front of the retracted base.

<!-- src: BlockPistonBase.java:120-161,345-356; World.java:1255-1267;
     Chunk.java:440-453; TileEntityPiston.java:105-113;
     original client.jar sticky zero-tick pull probe verifies the final state -->

## Saving and multiplayer

### Saving and loading

Saving a chunk writes the tile entities recorded in that chunk's map. It does
not walk through the world's loaded list to save every ticking object.
List-only orphans therefore have no saved tile-entity record and cannot be
recreated when the world is reopened.

A mapped tile entity at coordinates containing air or a non-container block
is written to the save, but loading tries to attach it to its block position
again. The chunk rejects that attachment because the block does not use a
tile entity. A mismatched object at a tile-entity block's position can survive
this loading check: as during normal installation, the check asks whether the
block uses *any* tile entity, not whether it uses that object's type.
<!-- src: ChunkLoader.java:138-148,188-195; Chunk.java:423-445;
     McRegionChunkLoader.java:26,50 reuses ChunkLoader compound routines;
     original client.jar NBT round-trip probes verify all three cases -->

Loading creates a new tile-entity object using the saved type name, then reads
its stored data. An unknown type name is skipped rather than creating an
object. The world reference and invalid-state marker are not saved fields;
the new object receives its link to the current world during attachment.
<!-- src: TileEntity.java:24-63,100-108; Chunk.java:434-442 -->

When a tile entity reports that its data has changed, the game marks its chunk
as needing to be saved. This is separate from notifying adjacent blocks about
a block change. Reporting the data change does not send a redstone neighbour
update or request a future scheduled block tick.
<!-- src: TileEntity.java:70-73 onInventoryChanged;
     World.java:2053-2059 func_698_b marks chunk modified and calls world
     access doNothingWithTileEntity, not notifyBlocksOfNeighborChange -->

### Multiplayer

In multiplayer, the server maintains the inventories and makes world changes.
The client receives the information needed to display and interact with them.
Sending a chunk's block data is not the same as sending all of its tile
entities' saved fields. When an inventory window is open, its slot contents
are sent separately. Furnace windows also receive cooking progress, remaining
burn time and the current fuel's total burn time for their progress indicators.
<!-- src: server EntityPlayerMP.java:306-328 Packet103SetSlot,
     Packet104WindowItems and Packet105UpdateProgressbar;
     ContainerFurnace.java:28-63 -->

Signs receive messages containing their text. Note sounds and piston motion
use **block-event packets**: network messages telling the client to perform a
block action at particular coordinates. These messages let the client play
the sound or execute the piston movement; they do not transfer every saved
field of the server's tile entity.
<!-- src: server TileEntity.java:77-78 default getDescriptionPacket null;
     server TileEntitySign.java:29-36 Packet130UpdateSign;
     server PlayerInstance.java:171-176; server WorldServer.java:100-102;
     client NetClientHandler.java:551-563,587-588 -->

## Data values

Tile-entity data is stored in **NBT**, the game's structured save-data format.
A saved tile entity consists of named fields, each with a value and a data
type. In the table below, a string is text, a boolean is true or false, and
byte, short and integer are whole-number types. A float can store fractional
values, such as motion progress.
<!-- src: ChunkLoader.java:138-148; NBTTagCompound.java:43-84 stores typed fields;
     TileEntity.java:30-38 -->

Each tile entity has a text **save ID** identifying which kind of object to
recreate during loading. This is not an ordinary entity network ID. Every
saved object has `id` as a string and `x`, `y`, `z` as integer block coordinates.
<!-- src: TileEntity.java:30-38,100-108; TileEntity does not extend Entity -->

| Type | Save ID | Additional saved fields |
|---|---|---|
| Furnace | `Furnace` | `Items`: inventory list. `BurnTime`: remaining fuel-burning ticks, short. `CookTime`: current smelting progress in ticks, short. |
| Chest | `Chest` | `Items`: inventory list. |
| Jukebox | `RecordPlayer` | `Record`: inserted record's item ID, integer. Written only when a record is present. |
| Dispenser | `Trap` | `Items`: inventory list. |
| Sign | `Sign` | `Text1`, `Text2`, `Text3`, `Text4`: the four lines of text, strings. |
| Monster spawner | `MobSpawner` | `EntityId`: mob type, string. `Delay`: spawn delay, short. |
| Note block | `Music` | `note`: pitch, byte. |
| Moving piston | `Piston` | `blockId`, `blockData`: carried block's ID and metadata, integers. `facing`: movement direction, integer. `progress`: previous update's motion progress, float. `extending`: true for extension, false for retraction, boolean. |

<!-- src: TileEntity.java:100-108; TileEntityFurnace.java:49-82;
     TileEntityChest.java:49-77; TileEntityRecordPlayer.java:6-15;
     TileEntityDispenser.java:69-97; TileEntitySign.java:8-25;
     TileEntityMobSpawner.java:93-102; TileEntityNote.java:7-22;
     TileEntityPiston.java:128-143 -->

Each entry in an inventory's `Items` list describes an item stack. `Slot`
(byte) identifies its inventory slot, `id` (short) identifies the item, `Count`
(byte) is the stack size, and `Damage` (short) is the item's damage or subtype
value. Slot numbers start at 0. Chest slots are 0–26, dispenser slots 0–8,
and furnace slots 0–2 for input, fuel and output respectively. A double chest
saves the inventories of its two halves separately.
<!-- src: TileEntityChest.java:6-7,49-77; TileEntityDispenser.java:9-10,69-97;
     TileEntityFurnace.java:4,49-82,149-179; ItemStack.java:75-85;
     BlockChest.java:185-229 -->

Loading shortens sign lines longer than 15 characters to their first 15
characters. A note pitch below 0 is changed to 0, and one above 24 is changed
to 24. A note block's remembered previous redstone state is not saved.
Furnace loading recalculates the fuel's total burning duration from the item
still in the fuel slot, rather than reading that total from a saved field.
<!-- src: TileEntitySign.java:20-24; TileEntityNote.java:4-22;
     TileEntityFurnace.java:62-64 -->

Moving-piston saves record the previous update's progress, not the current
progress. If a motion update has just advanced from 0.5 to 1, the saved
`progress` is still 0.5. Loading starts the motion at that saved value, so it
can repeat a movement step. The separate state identifying a retracting-base
animation is not saved.
<!-- src: TileEntityPiston.java:13-14,25,106,128-143; :133 restores both
     current and previous progress from the saved previous-progress field;
     field_31023_j is omitted from writeToNBT -->

## References

Jan Matula and Spheres (v3rtices) document the deferred-creation mechanism and
the furnace and piston exploits in three April 2022 HackMD notes:

- [Investigation of TE mechanics](https://hackmd.io/@pa-2w-2MT5iGybHuegbruw/BkaSMRHV9)
- [Exploiting updateFurnaceBlockState](https://hackmd.io/@pa-2w-2MT5iGybHuegbruw/HyUrqxVN9)
- [TE phase piston mechanics](https://hackmd.io/@pa-2w-2MT5iGybHuegbruw/Hk1bpzs4c)

<!-- Verification: rules checked against the Beta 1.7.3 decompile.
     Method-level probes calling the original client jar's game code verify
     bookkeeping, furnace and piston sequences, crash corrections and NBT
     loading. Test chunks are created in memory and piston extension and
     retraction are invoked directly during a tile-entity update. This is not
     a full client session or a reconstruction of every reported redstone
     machine. Original Mojang client.jar SHA-1
     43db9b498cb67058d2e12d394e6507722e71bb45; Java 17; 21 assertion-based
     scenarios. Obfuscated World fd, Chunk lm, TileEntity ow, Furnace sk,
     Piston uk and BlockFurnace tc resolved using Babric intermediary b1.7.3.
     Unsafe constructs a disposable World, proxy IChunkProvider supplies empty
     chunks, a one-shot TileEntity hook invokes additions and piston events
     during the unmodified World.updateEntities loop. Blocks and TEs execute
     original jar bytecode. No decompiled source or vanilla methods modified. -->
