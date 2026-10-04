---
title: Chunk
description: Chunk dimensions and coordinates, terrain population, singleplayer and multiplayer loading, spawn chunks, ticking rules, and the McRegion save format.
type: mechanic
categories: [Game mechanics]
aliases: [Chunks, Chunk Loading, Spawn Chunks]
---

A **chunk** is a 16×16-block column containing the full height of the world, used to generate, load, simulate, and save terrain.
<!-- src: Chunk.java:30-53; World.java:311-328; ChunkProviderGenerate.java:193-204 -->

## Size and coordinates

| Property | Size |
|---|---|
| Width along x | 16 blocks |
| Width along z | 16 blocks |
| Height | 128 blocks, y=0–127 |
| Horizontal area | 256 block columns |
| Block positions | 32,768, including air |

<!-- src: Chunk.java:40,67-77,232-233; World.java:311-328;
     ChunkProviderGenerate.java:195 allocates a 32768-byte block array -->

A chunk includes underground terrain and the air above it. The [[Overworld]] and [[Nether]] use the same chunk dimensions. A biome does not have to end at a chunk border: the Overworld generator reads a biome for each block column.
<!-- src: ChunkProviderGenerate.java:193-204; ChunkProviderHell.java:180-187;
     WorldChunkManager.java:73 loadBlockGeneratorData -->

### Chunk coordinates

Each chunk has an x coordinate and a z coordinate. A block's chunk coordinates are its horizontal block coordinates divided by 16, rounded down. Its local x and z coordinates run from 0 to 15. Its y coordinate is unchanged.
<!-- src: World.java:316,362-367; Chunk.java:232-233 -->

| Block x or z | Chunk coordinate | Local coordinate |
|---|---|---|
| −32 to −17 | −2 | 0 to 15 |
| −16 to −1 | −1 | 0 to 15 |
| 0 to 15 | 0 | 0 to 15 |
| 16 to 31 | 1 | 0 to 15 |
| 32 to 47 | 2 | 0 to 15 |

<!-- src: World.java:316 uses an arithmetic right shift by 4 and a bitwise
     mask of 15, equivalent to floor division and a non-negative remainder -->

For example, the block at (−1, 70, 16) is in chunk (−1, 1), at local position (15, 70, 0).
<!-- src: World.java:316; Chunk.java:232-233 -->

Chunk borders occur at multiples of 16 along x and z.
<!-- src: World.java:362-367 -->

## Generation and population

{{main|World Generation}}

A requested chunk is loaded from its save if one exists. Otherwise, the dimension's generator creates it. Reloading a saved chunk restores its blocks rather than rebuilding the terrain from the seed.
<!-- src: ChunkProvider.java:31-49,77-87;
     minecraft_server/ChunkProviderServer.java:43-61;
     ChunkLoader.java:151-160 -->

Generation and *population* are separate passes. Generation builds the terrain, surface, and caves. Population adds features such as ores, trees, and [[Dungeon|dungeons]]. An unpopulated chunk waits until the neighbouring chunks at +x, +z, and both +x and +z are loaded.
<!-- src: ChunkProviderGenerate.java:193-204,310 populate;
     ChunkProvider.java:52-65;
     minecraft_server/ChunkProviderServer.java:64-77 -->

Population chooses feature origins in a 16×16 area offset eight blocks along both horizontal axes from the chunk origin. Features can extend across chunk borders. The saved chunk records whether population has already run, preventing it from being repeated on every load.
<!-- src: ChunkProviderGenerate.java:312-327 and subsequent populate calls;
     ChunkProvider.java:118-124; ChunkLoader.java:118,160 -->

## Loading and unloading

### Loaded, active, and rendered chunks

| Term | Meaning |
|---|---|
| Saved chunk | Chunk data exists on disk. This does not make it run. |
| Loaded chunk | Its terrain is held in memory. Entities, block entities, and scheduled updates have their own rules for running. |
| Active chunk | It is in the player-centred area selected for random block ticks and local weather checks. |
| Rendered terrain | The client has built geometry to draw it. Visibility does not determine whether the world simulates it. |

<!-- src: McRegionChunkLoader.java:15-38; ChunkProvider.java:27-49;
     World.java:1236-1248,1291-1306,1868-1898,1967-1993;
     RenderGlobal.java:186-226; WorldRenderer.java:82-111 -->

A chunk can remain loaded without receiving random ticks. A chunk outside the visible terrain can still contain a working [[Furnace|furnace]] or ticking entities.
<!-- src: World.java:1236-1242,1291-1306,1875-1885;
     TileEntityFurnace.java:105 updateEntity;
     RenderGlobal.java:186-204 -->

### Singleplayer

Singleplayer loads chunks as the world needs their block data. The initial terrain-loading screen requests a 17×17 square around the player, or the world spawn if there is no player yet. Random ticking and terrain rendering can request further chunks. Reading or changing a block, or looking up a block entity, also loads its chunk if it is absent.
<!-- src: World.java:311-316,366-398,405-415,1599-1601;
     ChunkProvider.java:31-49,72-74;
     Minecraft.java:1346-1373; World.java:1892-1898;
     WorldRenderer.java:100; ChunkCache.java:9-23 -->

Singleplayer keeps loaded chunks in memory until the player leaves the world or changes dimension. Walking away does not unload them. Leaving the world or changing dimension saves the old world.
<!-- src: World.java:210-213 selects ChunkProvider; ChunkProvider.java:11-188
     has no insertion into droppedChunksSet; Minecraft.java:1236-1248,1268-1279.
     Independently checked against Mojang's original client.jar, SHA-1
     43db9b498cb67058d2e12d394e6507722e71bb45: fd.b()Lcl; constructs ok;
     ok contains no Set.add invocation. ChunkProviderLoadOrGenerate (kx),
     which contains a 32x32 cache and a +/-15 range, is not instantiated.
     Jar: https://launcher.mojang.com/v1/objects/43db9b498cb67058d2e12d394e6507722e71bb45/client.jar -->

Render distance changes the area drawn by the client. It does not change the nine-chunk random-tick radius or evict chunks already loaded. A singleplayer world therefore has no fixed player-centred square containing all of its loaded chunks.
<!-- src: RenderGlobal.java:186-204; World.java:1875-1898;
     ChunkProvider.java:27-74,160-178 -->

### Multiplayer

The dedicated server loads a square of chunks around each player according to `view-distance` in `server.properties`.

| Setting | Value |
|---|---|
| Default view distance | 10 chunks in each horizontal direction |
| Accepted view distance | 3–15 chunks |
| Default square per player | 21×21 chunks, or 441 chunks |

<!-- src: minecraft_server/ServerConfigurationManager.java:39-41;
     minecraft_server/PlayerManager.java:16-25,61-93 -->

Overlapping player areas share their chunks. The watched area follows the player's movement. Its centre is reconsidered after at least eight blocks of horizontal displacement from the last tracked position and a change of tracked chunk.
<!-- src: minecraft_server/PlayerManager.java:40-48,122-151;
     minecraft_server/PlayerInstance.java:33-40 -->

When the last player stops watching a chunk, the server queues it for unloading unless it lies in the spawn-retention area. Up to 100 queued chunks are saved and unloaded per world tick. Loading a queued chunk cancels its pending unload.
<!-- src: minecraft_server/PlayerInstance.java:44-54;
     minecraft_server/ChunkProviderServer.java:32-45,176-196;
     minecraft_server/World.java:1516 -->

Respawning loads the destination chunk and checks chunks around a saved [[Bed|bed]]. [[Nether Portal|Portal]] searches during dimension travel can also load missing terrain. Ordinary block reads and changes do not load an absent server chunk unless automatic loading is temporarily enabled for spawn selection or portal travel.
<!-- src: minecraft_server/ServerConfigurationManager.java:132-154,205-211;
     minecraft_server/EntityPlayer.java:628-639;
     minecraft_server/World.java:96-112;
     minecraft_server/ChunkProviderServer.java:84-90;
     minecraft_server/Teleporter.java:15-32 -->

The multiplayer client receives terrain from the server. It does not generate missing terrain or save the server's chunks locally. The client's render-distance setting does not replace the server's view distance.
<!-- src: ChunkProviderClient.java:39-68;
     NetClientHandler.java:271-272,294-302;
     RenderGlobal.java:186-204;
     minecraft_server/ServerConfigurationManager.java:39-41 -->

### Spawn chunks

On a dedicated server, a chunk is exempt from normal player-triggered unloading when its centre lies within 128 blocks of the world spawn along both x and z. This is a square, not a circular distance test. Depending on the spawn's alignment within its chunk, it includes 16 or 17 chunk centres along each axis.
<!-- src: minecraft_server/ChunkProviderServer.java:32-39;
     centres are chunkCoordinate * 16 + 8, with both endpoints included -->

The same retention test applies in the [[Overworld]] and [[Nether]]. At startup, the server also loads a 25×25-chunk region around each enabled dimension's spawn. That initial region is larger than the area protected from unloading. Being outside the protected area does not itself queue a chunk; losing its last watching player does.
<!-- src: minecraft_server/MinecraftServer.java:138-183;
     minecraft_server/ChunkProviderServer.java:32-39,43-45;
     minecraft_server/PlayerInstance.java:44-54 -->

Spawn retention does not grant random ticks or natural [[Mob Spawning|mob spawning]] without a nearby player. Loaded spawn chunks can still run block entities, scheduled updates, and entities where those updates' own conditions are met.
<!-- src: minecraft_server/ChunkProviderServer.java:32-39;
     World.java:1236-1242,1291-1306,1875-1885,1982-1988;
     SpawnerAnimals.java:23-38 -->

## Simulation

{{main|Game Tick}}

### Random ticks and local weather

Random ticks select chunks within nine chunk coordinates of a player along both horizontal axes. This is a 19×19 square, or 361 chunk coordinates for one player. It is not a circle measured from the player's exact block position. Overlapping areas are processed once per tick.
<!-- src: World.java:1868-1885,1892-1898;
     minecraft_server/World.java:1622-1652 -->

Each available chunk in that square receives 80 random block selections per game tick. Selections cover the full 16×16×128 volume, including air. Only blocks that use random ticks respond. A particular block is selected about once every 410 ticks on average.
<!-- src: World.java:1952-1961; minecraft_server/World.java:1706-1715;
     32768 block positions / 80 selections = 409.6 ticks -->

Random-tick growth, such as [[Crops|crop]] and [[Sapling|sapling]] growth, stops outside this area even if the chunk remains loaded. The same active-chunk area receives the local [[Weather|weather]] checks for lightning, snow, and freezing water. Player height does not change the horizontal selection area.
<!-- src: World.java:1875-1885,1920-1961;
     BlockCrops.java:36 updateTick; BlockSapling.java:14 updateTick -->

A dedicated server with a view distance below nine can have missing chunks inside the selected square. Selecting a coordinate for random ticks does not force that server chunk to load.
<!-- src: minecraft_server/World.java:1622-1652;
     minecraft_server/ChunkProviderServer.java:84-90 returns dummyChunk
     without worldChunkLoadOverride or chunkLoadOverride -->

### Entities

Ordinary entities update only when every chunk intersecting the horizontal square extending 32 blocks from their position is loaded. This covers a 5×5-chunk area centred on their own chunk.
<!-- src: World.java:335-352,1291-1306;
     minecraft_server/World.java:1028-1043 updateEntityWithOptionalForce -->

The outer two-chunk-wide border of a rectangular loaded area can be described as *lazy chunks*: their ordinary entities do not tick. An unloaded hole creates the same effect within two chunk coordinates of it. Block entities and eligible block updates can still run there.
<!-- src: World.java:335-352,1236-1242,1291-1306,1984-1988;
     the entity check needs chunk offsets -2 through +2 on both axes -->

This check does not use the nine-chunk random-tick radius. Entities in a fully loaded distant area can continue moving or advancing timers. An entity crossing a chunk border is moved into the destination chunk's entity list.
<!-- src: World.java:1291-1306,1329-1342; Chunk.java:356-378 -->

Unloading removes the chunk's entities from the world update list. Their saved state is restored when the chunk loads again. A [[Dropped Item|dropped item's]] age does not advance while it is not being updated, but walking away in singleplayer does not necessarily stop its timer.
<!-- src: Chunk.java:459-479; World.java:1178-1207;
     ChunkLoader.java:124-137,176-185;
     EntityItem.java:71-74,96-107; ChunkProvider.java:11-188 -->

### Block entities

Valid [[Tile Entity|block entities]] in the world's loaded list receive an update every game tick. They do not require the surrounding 5×5 chunks or a place inside the random-tick area. A [[Furnace|furnace]] can continue smelting in a loaded chunk beyond crop-growth range.
<!-- src: World.java:1235-1248; TileEntityFurnace.java:105-160 -->

An individual block entity can impose additional conditions. A [[Monster Spawner|monster spawner]] needs a player within 16 blocks to run its spawning cycle. Normal chunk unloading invalidates the block entities mapped to the chunk. An [[Tile Entity#Orphaned and mismatched tile entities|orphaned block entity]] missing from that map can survive unloading.
<!-- src: TileEntityMobSpawner.java:21-30; Chunk.java:469-475;
     World.java:1238-1248 -->

### Scheduled updates and chunk borders

[[Game Tick#Scheduled ticks|Scheduled block updates]] are kept in one world-wide queue, not a queue attached to each chunk. Scheduling an update requires every chunk intersecting an eight-block neighbourhood of the block to be loaded. The same neighbourhood is checked when the update becomes due.
<!-- src: World.java:17-18,1152-1173,1967-1988 -->

The eight-block-wide border inside a loaded area's edge can be described as *lazy blocks* for scheduled updates. An unloaded hole creates the same border around itself. Random ticks and neighbour notifications can still affect these blocks.
<!-- src: World.java:335-352,506-513,1164-1173,1952-1961,1984-1988;
     at a loaded block range [L,R], scheduled updates require x-8 >= L
     and x+8 <= R, and the equivalent conditions along z -->

A due update is removed from the queue even when the surrounding chunks are missing. It is discarded rather than postponed until those chunks return. Scheduled updates can run beyond random-tick range if their required chunks remain loaded.
<!-- src: World.java:1982-1988;
     minecraft_server/World.java:1736-1743 -->

A chunk border is not a wall for [[Redstone Power|redstone]], [[Fluid|fluids]], or moving entities. Neighbour notifications cross it. Missing neighbouring chunks can prevent scheduled updates or entity movement from being simulated near a loaded region's edge.
<!-- src: World.java:506-513,1152-1173,1291-1306,1329-1342;
     BlockFlowing.java:16 updateTick -->

### Mob spawning and slime chunks

{{main|Mob Spawning}}

Natural spawning considers the 17×17 square within eight chunk coordinates of each player. This is separate from both the random-tick area and the server's watched area. A chunk being loaded or retained at spawn is not enough to make natural spawning occur there.
<!-- src: SpawnerAnimals.java:19-38 -->

The natural mob cap scales with the size of this eligible area, not the total number of loaded chunks. Existing mobs in all loaded chunks count towards it, including mobs outside the eligible area and in lazy chunks.
<!-- src: SpawnerAnimals.java:23-48; World.java:2064-2074 -->

A *slime chunk* is a chunk whose coordinates and world seed pass the [[Slime|slime]] spawning test. About one chunk in ten qualifies. The designation covers the whole horizontal chunk, but slimes spawn only below y=16. Loading or unloading a chunk does not change its designation.
<!-- src: EntitySlime.java:134-136; Chunk.java:598-599 -->

## Saving and data layout

### Region files

Chunks are saved in the McRegion format. One `.mcr` region file covers 32×32 chunks, or 512×512 horizontal blocks. A file contains only the chunks that have actually been saved, not necessarily every chunk in its region.
<!-- src: RegionFileCache.java:19-21,68-75;
     RegionFile.java:113-126 getChunkDataInputStream checks zero offsets -->

| Dimension | Region-file path inside the world folder |
|---|---|
| [[Overworld]] | `region/r.<regionX>.<regionZ>.mcr` |
| [[Nether]] | `DIM-1/region/r.<regionX>.<regionZ>.mcr` |

<!-- src: SaveOldDir.java:11-18; RegionFileCache.java:19-21 -->

Region coordinates are chunk coordinates divided by 32, rounded down. A chunk's position within its region runs from 0 to 31 on each axis. Negative region coordinates follow the same floor-division rule as negative chunk coordinates.
<!-- src: RegionFileCache.java:21,68-75 -->

Chunks are compressed separately inside the region file. Saving one chunk does not regenerate the other chunks in that region.
<!-- src: McRegionChunkLoader.java:42-52;
     RegionFile.java:161-177,219-237 -->

### Chunk contents

Each chunk's saved NBT data is held in a `Level` compound.

| Field | Contents |
|---|---|
| `xPos`, `zPos` | Chunk coordinates |
| `LastUpdate` | World time when the chunk was saved |
| `Blocks` | 32,768 block IDs, one byte per position |
| `Data` | 16,384 bytes of block metadata, four bits per position |
| `SkyLight` | 16,384 bytes of saved sky light, four bits per position |
| `BlockLight` | 16,384 bytes of saved block light, four bits per position |
| `HeightMap` | 256 bytes, one sky-obstruction height per column |
| `TerrainPopulated` | Whether the population pass has run |
| `Entities` | Saved entities belonging to the chunk |
| `TileEntities` | Saved block entities in the chunk's map |

<!-- src: McRegionChunkLoader.java:47-51; ChunkLoader.java:108-148;
     Chunk.java:48-53,67-77,232-233; NibbleArray.java:6-8 -->

The block array stores y positions consecutively, then z, then x. Entity lookup uses eight vertical groups of 16 blocks within the chunk; these groups are not independently loaded terrain chunks. Biome IDs are not stored in the chunk: the biome manager derives biomes from the world seed and coordinates.
<!-- src: Chunk.java:32-43,232-233,356-378;
     ChunkLoader.java:108-148; WorldChunkManager.java:17-38,73-110 -->

### Saving and resuming

Changed blocks, lighting, and block-entity data mark a chunk for saving. Chunks containing entities are also saved periodically even without a changed terrain block. Saving preserves the chunk's state; it does not unload the chunk.
<!-- src: Chunk.java:228,236-273,304,536-548;
     TileEntity.java:70-74; World.java:2053-2059;
     ChunkProvider.java:130-157 -->

Loading does not replay the ticks that passed while a chunk was unloaded. Crops do not receive missed random ticks, and furnaces do not smelt a backlog merely because their chunk's saved time is old.
<!-- src: ChunkLoader.java:151-199 does not read LastUpdate;
     World.java:1952-1961; TileEntityFurnace.java:49-64,105-160 -->

Pending scheduled block updates are not included in the chunk's saved data. Closing and reopening the world does not restore that queue. Unloading a chunk also does not create a saved queue of updates to replay later.
<!-- src: ChunkLoader.java:108-149; World.java:17-18,153-155;
     Chunk.java:469-479 -->
