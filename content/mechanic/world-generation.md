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
is the [[Nether]]'s only biome. [[Sky]] belongs to the [[Sky Dimension|Sky
dimension]], which the game never creates a world for.
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

### The noise fields

Every field the generator reads is Perlin gradient noise. A lattice of random
gradient vectors is laid over space, and a point's value is a smoothly faded
blend of the gradients at the corners of the cell it falls in. Values drift
rather than jump, so a field looks like a spread of soft rounded lumps and never
like static.
<!-- src: NoiseGeneratorPerlin.java:35 generateNoise, with the
     6t^5 - 15t^4 + 10t^3 fade curve -->

Each field is a stack of octaves, and each octave is a separate lattice seeded
from the world seed. Every octave has half the frequency and twice the amplitude
of the one before it. The last octave alone therefore carries half the field's
range and sets its shape, and the earlier octaves only roughen it.
<!-- src: NoiseGeneratorOctaves.java:31 generateNoiseOctaves, halving the
     coordinate scale and the amplitude divisor on each pass -->

Five fields build the density:

| Field | Octaves | Read in | Broadest lump | Role |
|---|---|---|---|---|
| Landscape A | 16 | 3D | about 190 blocks | a complete landscape |
| Landscape B | 16 | 3D | about 190 blocks | a second complete landscape |
| Selector | 8 | 3D | about 60 blocks | chooses between A and B |
| Depth | 16 | 2D | about 650 blocks | the column's centre height |
| Stretch | 10 | 2D | about 1800 blocks | how far the column may stray from its centre |

<!-- src: ChunkProviderGenerate.java:30 the constructor fixes the octave counts,
     :211-:219 func_4061_a the scales. A lump is the wavelength of the lowest
     octave: the base scale divided by 2^(octaves-1), then by the 4-block
     horizontal sample spacing. -->

The two landscape fields are read on the 4×8×4 sample grid at the same numeric
scale in every direction, so their lumps come out twice as tall as they are wide.
That stretch is what produces overhangs, arches and floating islands.

The selector is mapped so that a value below 0 takes landscape A whole and a
value above 1 takes landscape B whole, with a crossfade between. Most sample
points land outside that range, so most of the world is one landscape or the
other and the blend shows only in narrow bands.
<!-- src: ChunkProviderGenerate.java:282, (selector / 10 + 1) / 2 against a field
     whose octave amplitudes sum to 255 -->

The depth field separates sea from land. Below its threshold the column's centre
height is set somewhere between y=56 and y=68 and the stretch is forced to its
minimum, which gives the flat low ground of an ocean basin. Above the threshold
the centre height rises as far as y=72 and the stretch is left alone.
<!-- src: ChunkProviderGenerate.java:241-:270; the low branch zeroes the stretch
     term before 0.5 is added back to it -->

The stretch field is the broadest of the five, so whether a region is mountainous
or gentle holds across more than a thousand blocks. It is then scaled by
temperature multiplied by rainfall. Cold or dry columns are pulled flat towards
their centre height, and hot wet ones keep their full relief. Rainforest and
Swampland carry the most extreme terrain, Tundra and Desert the least.
<!-- src: ChunkProviderGenerate.java:230, the (1 - t*h)^4 term applied to the
     vertical scale -->

Above y=112 the finished density is blended towards a large negative value,
reaching it at y=128. Terrain does not reach the top of the world.

### Water, ice and bedrock

Any space below y=64 that is not stone becomes water. At y=63 exactly it becomes
ice instead, where the column's temperature is below 0.5.
<!-- src: ChunkProviderGenerate.java:81 -->

Bedrock is placed by rolling a number from 0 to 4 separately for every block from
y=0 to y=4, and placing bedrock where the roll is at or above that block's y:

| y | Chance of bedrock |
|---|---|
| 0 | always |
| 1 | 4 in 5 |
| 2 | 3 in 5 |
| 3 | 2 in 5 |
| 4 | 1 in 5 |

<!-- src: ChunkProviderGenerate.java:132, `var17 <= 0 + this.rand.nextInt(5)`,
     evaluated once per block as the column is walked down from y=127 -->

Every block is rolled on its own, so a column can have bedrock at y=3 and stone
at y=2. Y=0 is bedrock everywhere in the world.

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

Carving replaces stone, dirt and grass and nothing else. Below y=10 the carved
block becomes flowing [[Lava|lava]] rather than air. Dirt left exposed by a
removed grass block becomes grass.
<!-- src: MapGenCaves.java:133 -->

Carving runs before population, so the sand and gravel the surface pass laid down
are already in place and a tunnel that reaches a beach leaves it standing. The
gravel and dirt veins that population adds are not: they replace stone only, so a
vein that meets an existing tunnel is cut off at the tunnel wall.
<!-- src: ChunkProviderGenerate.java:200-:201, replaceBlocksForBiome then
     MapGenCaves.generate, both inside provideChunk -->

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
| [[Sugar cane]] | 10 runs of 20 | 0–127 |
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

Every chunk starts with a tree count of zero, and one time in ten that count is
raised to one. The biome is then applied on top of it.

| Biome | Trees |
|---|---|
| Forest, Rainforest, Taiga | `n` + 5, plus the bonus |
| Seasonal Forest | `n` + 2, plus the bonus |
| Shrubland, Savanna, Swampland | the bonus alone |
| Desert, Plains, Tundra | none |

`n` is a noise value read from the same field the game uses for mob spawning, and
averages 2 before it is truncated to a whole number. It drifts over about sixteen
chunks, so tree density shifts across a forest rather than jumping from one chunk
to the next.
<!-- src: ChunkProviderGenerate.java:411, mobSpawnerNoise read at half scale;
     :413 the one-in-ten bonus, applied before any biome term -->

Desert, Plains and Tundra subtract 20 and add nothing, so their count stays
negative and the bonus can never lift it above zero. Shrubland, Savanna and
Swampland appear in none of the biome terms, so the bonus is the only tree they
ever get.
<!-- src: ChunkProviderGenerate.java:417-:443 -->

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
| {{sprite\|Flower}} | 4 in Seasonal Forest, 3 in Plains, 2 in Forest and Taiga, else none | 64 |
| {{sprite\|Rose}} | 1 chunk in 2 | 64 |
| {{sprite\|Tall Grass}} | 10 in Rainforest and Plains, 2 in Forest and Seasonal Forest, 1 in Taiga, else none | 128 |
| {{sprite\|Brown Mushroom}} | 1 chunk in 4 brown, 1 chunk in 8 red | 64 |
| {{sprite\|Dead Bush}} | 2 in Desert, else none | 4 |

<!-- src: ChunkProviderGenerate.java:454-546 -->

Two patches in three in Rainforest place [[Fern|ferns]] instead of tall grass.
<!-- src: ChunkProviderGenerate.java:505, metadata 2 rather than 1 -->

[[Sugar cane]] is placed by ten separate runs per chunk. Each run picks one point
at a random y from 0 to 127, then makes 20 attempts to plant a stalk within 3
blocks of that point in x and z, all at the run's single y. An attempt needs air
at that y and water beside the block below it, so almost every one fails. A stalk
that does take hold is 2 to 4 blocks tall.
<!-- src: ChunkProviderGenerate.java:548 the ten runs, WorldGenReed.java:7 the
     twenty attempts inside one run -->

[[Cactus|Cacti]] are 1 to 3 blocks tall.
<!-- src: WorldGenCactus.java:12 -->

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

A fixed vertical profile is added to the density, pushing the outermost four
sample levels at each end of the world towards solid and doing it far harder at
the last two. The result is netherrack floor and ceiling under every column.
<!-- src: ChunkProviderHell.java:207-:218, a cubic term subtracted from the
     density within 4 of either end of the 17-level sample column -->

Bedrock is then rolled the same way as in the Overworld, once at each end:

| y | Chance of bedrock |
|---|---|
| 0 and 127 | always |
| 1 and 126 | 4 in 5 |
| 2 and 125 | 3 in 5 |
| 3 and 124 | 2 in 5 |
| 4 and 123 | 1 in 5 |

<!-- src: ChunkProviderHell.java:121 the ceiling test, :123 the floor test -->

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
