---
title: World Generation
description: How Beta 1.7.3 builds a world — biome selection, terrain noise, caves, ore veins, and every feature the populate step adds.
type: mechanic
categories: [Game mechanics]
---

**World generation** is the game building the blocks of a chunk from the world
seed and the chunk's coordinates.

## Chunks

A chunk is 16 blocks in x, 16 in z and 128 in y. Sea level is y=64.

A chunk is built in two passes. The first runs when the chunk is first needed
and does five things in order:

1. look up the biome and temperature of each of the chunk's 256 columns,
2. place [[Stone|stone]], [[Water|water]] and [[Ice|ice]] from the terrain noise,
3. replace the top blocks of each column with the biome's surface, and add
   [[Bedrock|bedrock]],
4. carve caves,
5. build the skylight map.

<!-- src: ChunkProviderGenerate.java:193 provideChunk -->

The second pass, *population*, adds ores, features and plants. It runs on a
chunk only once the chunks at +1 x, +1 z and both have also been built.
Population places its features in a 16×16 area offset 8 blocks in x and z from
the chunk origin, which overlaps four chunks — hence the wait.
<!-- src: ChunkProvider.java:52; ChunkProviderGenerate.java:310 populate, where
     every feature's coordinate is chunkX * 16 + nextInt(16) + 8 -->

Population seeds its random numbers from the chunk coordinates and the world
seed together, so a chunk's features do not depend on when it was generated.
<!-- src: ChunkProviderGenerate.java:318 -->

## Biomes

Two noise fields cover the world: temperature and rainfall, each a value from 0
to 1. Neither varies with height or with the terrain below.
<!-- src: WorldChunkManager.java:73 loadBlockGeneratorData -->

The biome is read from a 64×64 table indexed by the two values. Taking `r` as
rainfall multiplied by temperature, the first matching row wins:

| Condition | Biome |
|---|---|
| temperature < 0.1 | [[Tundra]] |
| `r` < 0.2 and temperature < 0.5 | [[Tundra]] |
| `r` < 0.2 and temperature < 0.95 | [[Savanna]] |
| `r` < 0.2 | [[Desert]] |
| `r` > 0.5 and temperature < 0.7 | [[Swampland]] |
| temperature < 0.5 | [[Taiga]] |
| temperature < 0.97 and `r` < 0.35 | [[Shrubland]] |
| temperature < 0.97 | [[Forest]] |
| `r` < 0.45 | [[Plains]] |
| `r` < 0.9 | [[Seasonal Forest]] |
| otherwise | [[Rainforest]] |

<!-- src: BiomeGenBase.java:100 getBiome; the table is built once in
     generateBiomeLookup and read by getBiomeFromLookup -->

[[Ice Desert]] is never returned by that table and does not generate. [[Hell]]
is the [[Nether]]'s only biome. [[Sky]] belongs to a third generator that the
game never creates a world for.
<!-- src: WorldProvider.java:100 getProviderForDimension returns null for every
     dimension but -1 and 0 -->

Each biome carries the block it puts on the surface and the block underneath it.
Every biome uses [[Grass|grass]] over [[Dirt|dirt]] except Desert and Ice Desert,
which use [[Sand|sand]] over sand.
<!-- src: BiomeGenBase.java:34, :66 -->

## Terrain

Terrain is a density field. Stone is placed wherever the density is above zero.
The field is sampled every 4 blocks in x and z and every 8 in y, then
interpolated between the samples, which is what gives Beta terrain its smooth,
rounded slopes.
<!-- src: ChunkProviderGenerate.java:43 generateTerrain -->

Two noise fields supply the density, blended together by a third that selects
between them. A fourth field sets each column's centre height, and a fifth sets
how far the terrain is allowed to stray from it.
<!-- src: ChunkProviderGenerate.java:206 func_4061_a -->

The stray allowance is scaled by temperature multiplied by rainfall. Cold or dry
columns are pulled flat towards their centre height, and hot wet ones keep their
full relief. Rainforest and Swampland carry the most extreme terrain, Tundra and
Desert the least.
<!-- src: ChunkProviderGenerate.java:230, the (1 - t*h)^4 term applied to the
     vertical scale -->

Above y=112 the density is blended towards a large negative value, reaching it at
y=128. Terrain does not reach the top of the world.

Any space below y=64 that is not stone becomes water. At y=63 exactly it becomes
ice instead, where the column's temperature is below 0.5.
<!-- src: ChunkProviderGenerate.java:81 -->

Bedrock fills y=0, and replaces the block at y=1 to y=4 at random.
<!-- src: ChunkProviderGenerate.java:132 -->

## Surface

The surface pass walks each column from y=127 downwards and rewrites the first
few blocks below every air gap, so it shapes cave roofs and overhangs as well as
the open surface.
<!-- src: ChunkProviderGenerate.java:113 replaceBlocksForBiome -->

A noise field sets how deep the filler runs beneath the top block. Where it comes
out at zero or less the column gets no top block at all, and bare stone reaches
the surface.

Between y=60 and y=65 two more noise fields override the biome's choice:

- about half of columns take [[Sand|sand]] as both top and filler, which is what
  makes beaches;
- a much rarer roll takes [[Gravel|gravel]] as filler and leaves the top block
  empty, so gravel shores sit under water.

A top block left empty below y=64 becomes water. Sand filler is followed by 0 to
3 blocks of [[Sandstone|sandstone]] once the sand runs out.
<!-- src: ChunkProviderGenerate.java:176 -->

## Caves

Caves are carved into a chunk before it is populated. Every chunk within 8 chunks
of the one being built is asked to seed caves into it, so one cave system can run
128 blocks across chunk borders.
<!-- src: MapGenBase.java:9 generate, with range 8 -->

One chunk in fifteen seeds any caves. Such a chunk starts up to 39 systems,
strongly biased towards one or two. Each starts at a random point in the chunk,
at a y biased towards the bottom of the world.
<!-- src: MapGenCaves.java:161 recursiveGenerate; the y is
     nextInt(nextInt(120) + 8) -->

One system in four opens with a wide room and then sends out 1 to 4 tunnels. The
rest are a single tunnel. A tunnel is a chain of overlapping ellipsoids that
turns as it advances, and one tunnel in six turns more sharply than the others. A
tunnel may fork in two at its midpoint, each fork narrower than the parent.
<!-- src: MapGenCaves.java:29, :49 -->

Carving replaces stone, dirt and grass and nothing else, which is why a cave stops
dead at a vein of gravel. Below y=10 the carved block becomes flowing
[[Lava|lava]] rather than air. Dirt left exposed by a removed grass block becomes
grass.
<!-- src: MapGenCaves.java:133 -->

A segment whose bounding box contains water is skipped entirely, so caves do not
breach the bottom of an ocean or a lake.
<!-- src: MapGenCaves.java:104 -->

## Ores

Every ore is placed by the same generator. It draws a line through the chunk at a
random horizontal angle, walks along it, and fills an ellipsoid at each step. Only
[[Stone|stone]] is replaced, so a vein running into a cave or into dirt loses
those blocks. Size is the generator's block count, not the number of blocks a
player finds.

| Ore | Veins per chunk | Size | Y |
|---|---|---|---|
| {{sprite\|Dirt}} [[Dirt]] | 20 | 32 | 0–127 |
| {{sprite\|Gravel}} [[Gravel]] | 10 | 32 | 0–127 |
| {{sprite\|Coal Ore}} [[Coal Ore]] | 20 | 16 | 0–127 |
| {{sprite\|Iron Ore}} [[Iron Ore]] | 20 | 8 | 0–63 |
| {{sprite\|Gold Ore}} [[Gold Ore]] | 2 | 8 | 0–31 |
| {{sprite\|Redstone Ore}} [[Redstone Ore]] | 8 | 7 | 0–15 |
| {{sprite\|Diamond Ore}} [[Diamond Ore]] | 1 | 7 | 0–15 |
| {{sprite\|Lapis Lazuli Ore}} [[Lapis Lazuli Ore]] | 1 | 6 | 0–30, peaking at 15 |

<!-- src: ChunkProviderGenerate.java:354-408. Lapis alone draws its y as
     nextInt(16) + nextInt(16), which is why it is triangular. -->

The y in the table is where the line is drawn. The generator then lifts the vein 2
to 4 blocks above it, so a diamond vein reaches a few blocks higher than 15.
<!-- src: WorldGenMinable.java:20 -->

[[Clay]] uses the same shape at size 32, 10 times per chunk, but replaces sand
instead of stone and gives up unless the point it starts from is water.
<!-- src: WorldGenClay.java:14 -->

## Population

Every feature below is attempted at a random point in the populated area, and most
of them fail most of the time. Attempts are per chunk.

| Feature | Attempts | Y |
|---|---|---|
| Water lake | 1 chunk in 4 | 0–127 |
| Lava lake | 1 chunk in 8 | biased low; above y=63 only 1 time in 10 |
| [[Dungeon]] | 8 | 0–127 |
| Trees | by biome | surface |
| Flowers, grass, mushrooms | by biome | 0–127 |
| [[Sugar cane]] | 10 | 0–127 |
| [[Pumpkin]] | 1 chunk in 32 | 0–127 |
| [[Cactus]] | 10 in Desert, else none | 0–127 |
| Water spring | 50 | biased low |
| Lava spring | 20 | strongly biased low |

Sand and gravel do not fall while a chunk is being populated. A feature that
undercuts them leaves them hanging until something disturbs them.
<!-- src: ChunkProviderGenerate.java:311, BlockSand.fallInstantly -->

### Lakes

A lake is 4 to 7 overlapping ellipsoids inside a box 16 across, 16 deep and 8
tall, placed from four blocks below the first solid block under the chosen point.
The bottom four layers are filled with the liquid and the top four are cleared to
air.

The whole shape is abandoned if any block bordering the upper half is liquid, or
if any block bordering the lower half is neither solid nor the lake's own liquid.
A lake cannot form against open air, and cannot merge into an existing body of
water.
<!-- src: WorldGenLakes.java:52 -->

Dirt directly under the liquid becomes [[Grass|grass]] where sky light reaches it.
A lava lake seals itself in a shell of stone: every solid neighbour of the lower
half is replaced, and half of those around the upper half.
<!-- src: WorldGenLakes.java:80, :87 -->

### Dungeons

{{main|Dungeon}}

A dungeon is attempted 8 times per chunk at a y from 0 to 127. The room is 5 or 7
blocks across in each horizontal direction, and 4 blocks tall inside.

Placement needs between 1 and 5 openings, counted as wall positions at floor level
with two air blocks beyond them. A sealed room is rejected, and so is one with six
or more openings. The floor below and the ceiling above must both be solid.
<!-- src: WorldGenDungeons.java:27, :34 -->

The walls are built of [[Cobblestone|cobblestone]]. The floor is
[[Moss Stone|moss stone]] three times in four and cobblestone otherwise. The
ceiling is left as whatever stone was already there. A
[[Monster Spawner|monster spawner]] goes at the centre, and up to two
[[Chest|chests]] against the walls.
<!-- src: WorldGenDungeons.java:43, :98 -->

### Trees

The number of trees a chunk gets is a biome bonus plus a noise value `n`, which is
usually 1 or 2. A chunk of any biome gets one extra tree one time in ten.

| Biome | Trees |
|---|---|
| Forest, Rainforest, Taiga | `n` + 5 |
| Seasonal Forest | `n` + 2 |
| Shrubland, Savanna, Swampland | none |
| Desert, Plains, Tundra | none |

<!-- src: ChunkProviderGenerate.java:411. Desert, Plains and Tundra subtract 20
     and never add n, so their count is always negative. -->

Which tree is built depends on the biome as well:

| Biome | Trees built |
|---|---|
| Forest | birch 1 in 5; of the rest, big 1 in 3 |
| Rainforest | big 1 in 3 |
| Taiga | pine 1 in 3, spruce otherwise |
| Everything else | big 1 in 10 |

<!-- src: BiomeGenBase.java:70 getRandomWorldGenForTrees, overridden in
     BiomeGenForest, BiomeGenRainforest and BiomeGenTaiga -->

Every tree needs grass or dirt beneath it and a clear column, and turns the block
under its trunk to dirt. Trunk heights are 4 to 6 for the plain tree, 5 to 7 for
birch, 6 to 9 for spruce, 7 to 11 for pine and 5 to 16 for the big tree.
<!-- src: WorldGenTrees.java:7, WorldGenForest.java:7, WorldGenTaiga2.java:7,
     WorldGenTaiga1.java:7, WorldGenBigTree.java:339 -->

### Plants

A plant generator is given one point and makes many attempts around it, so each
count below is a patch rather than a plant.

| Plant | Patches per chunk | Attempts per patch |
|---|---|---|
| {{sprite\|Flower}} [[Flower]] | 4 in Seasonal Forest, 3 in Plains, 2 in Forest and Taiga, else none | 64 |
| {{sprite\|Rose}} [[Rose]] | 1 chunk in 2 | 64 |
| {{sprite\|Tall Grass}} [[Tall Grass]] | 10 in Rainforest and Plains, 2 in Forest and Seasonal Forest, 1 in Taiga, else none | 128 |
| {{sprite\|Brown Mushroom}} [[Mushroom]] | 1 chunk in 4 brown, 1 chunk in 8 red | 64 |
| {{sprite\|Dead Bush}} [[Dead Bush]] | 2 in Desert, else none | 4 |

<!-- src: ChunkProviderGenerate.java:454-546 -->

Two patches in three in Rainforest place [[Fern|ferns]] instead of tall grass.
<!-- src: ChunkProviderGenerate.java:505, metadata 2 rather than 1 -->

[[Sugar cane]] is attempted 10 times per chunk with 20 attempts each, and needs
water beside the block below it. Each stalk placed is 2 to 4 blocks tall.
[[Cactus|Cacti]] are 1 to 3 blocks tall.
<!-- src: WorldGenReed.java:12, WorldGenCactus.java:12 -->

### Springs

A spring is a single source block set into a wall of stone. It is placed only
where the blocks above and below are stone, exactly three of the four horizontal
neighbours are stone, and exactly one is air.
<!-- src: WorldGenLiquids.java:54 -->

Water springs are attempted 50 times per chunk and lava springs 20, both at a y
biased towards the bottom of the world. The source flows immediately rather than
waiting for a tick.

### Snow

The last step of population lays [[Snow|snow]] over the populated area. A column
is covered when the top solid block is not ice, and the column's temperature
reduced by `(y − 64) ÷ 64 × 0.3` comes out below 0.5.
<!-- src: ChunkProviderGenerate.java:588 -->

The height term is what puts snow on mountain tops in biomes that are otherwise
bare. It reads the temperature directly, not the biome's snow flag.

## The Nether

The [[Nether]] uses a generator of its own. It shares the density-field approach
but replaces stone with [[Netherrack|netherrack]] and water with [[Lava|lava]],
and its lava level is y=32.
<!-- src: ChunkProviderHell.java:38 generateNetherTerrain -->

A fixed vertical profile is added to the density, forcing solid ground within four
levels of the top and bottom of the world. Bedrock then covers y=0 to y=4 and
y=123 to y=127, so the Nether is a closed slab.
<!-- src: ChunkProviderHell.java:207, :121 -->

The surface pass runs the same way as the Overworld's, with netherrack as both top
and filler. Between y=60 and y=65 about half of columns take [[Gravel|gravel]] and
about half take [[Soul Sand|soul sand]], with soul sand winning where both apply.
<!-- src: ChunkProviderHell.java:137 -->

Caves are seeded in one chunk in five rather than one in fifteen, and their tunnels
are twice as wide and half as tall. They carve netherrack only, and a segment is
skipped where its box contains lava.
<!-- src: MapGenCavesHell.java:148, :168, :128 -->

Population is short:

| Feature | Attempts per chunk |
|---|---|
| Lava spring | 8 |
| [[Fire]] patch | 1 to 10 |
| [[Glowstone]] cluster | 0 to 9 hanging from ceilings, plus 10 more anywhere |
| [[Mushroom]] patch | 1 brown and 1 red |

<!-- src: ChunkProviderHell.java:302 populate -->

A glowstone cluster starts from one block against a netherrack ceiling and makes
1500 attempts to grow downwards, adding a block only where exactly one of the six
neighbours is already glowstone.
<!-- src: WorldGenGlowStone1.java:14 -->

There are no ores, lakes, dungeons or trees in the Nether. Its population step
does not reseed its random numbers per chunk, so which features a chunk receives
depends on the order chunks were generated in.
<!-- src: ChunkProviderHell.java:302, which has no setSeed call -->

## The world spawn point

On a new world the game walks outwards from x=0, z=0 in random steps of up to 63
blocks until it finds a column whose topmost uncovered block is [[Sand|sand]].
Every world's spawn point is on sand.
<!-- src: World.java:215 getInitialSpawnLocation; WorldProvider.java:37
     canCoordinateBeSpawn tests against Block.sand -->

The spawn y is recorded as 64 whatever the terrain does. A player joining is
placed on the first non-air column found by stepping up to 7 blocks at a time from
the recorded point, at the height of the first block with air above it.
<!-- src: World.java:229 setSpawnLocation, :245 getFirstUncoveredBlock -->
