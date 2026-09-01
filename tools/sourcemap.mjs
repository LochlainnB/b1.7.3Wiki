#!/usr/bin/env node
// Generate .claude/skills/b173-wiki/SOURCEMAP.md — where to look in the
// decompiled Beta 1.7.3 source for a given kind of question.
//
//   node tools/sourcemap.mjs
//
// The topic index below is hand-curated; everything else is read from the tree.
// Every class named here is checked to exist, so the map cannot drift into
// citing classes that are not there.
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { findSource, listClasses, CLIENT_SRC, SERVER_SRC } from './lib/source.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const OUT = join(ROOT, '.claude', 'skills', 'b173-wiki', 'SOURCEMAP.md');

/**
 * Question -> where the answer lives.
 *
 * `entry` names the class to open first. `then` are the classes the answer
 * usually continues into. `note` is the thing that is easy to get wrong.
 */
const TOPICS = [
  {
    topic: 'A block\'s properties (hardness, light, material, drops)',
    entry: 'Block',
    then: ['BlockBreakable', 'Material', 'StepSound'],
    note: 'The static initialiser at the bottom of Block.java registers every block with its ' +
      'builder chain. Per-block behaviour lives in `Block<Name>.java`. Drops come from ' +
      'idDropped/quantityDropped/dropBlockAsItem.',
  },
  {
    topic: 'An item\'s properties, tools, mining speed, durability',
    entry: 'Item',
    then: ['ItemTool', 'EnumToolMaterial', 'ItemFood', 'ItemArmor'],
    note: 'Item ids are offset: `new Item(6)` registers id 262, because Item(int) does ' +
      '`shiftedIndex = 256 + var1`. getStrVsBlock is mining speed; EnumToolMaterial carries ' +
      'harvest level, durability and damage.',
  },
  {
    topic: 'Mob behaviour, AI, drops, health',
    entry: 'EntityLiving',
    then: ['EntityMob', 'EntityCreature', 'EntityAnimal', 'EntityFlying'],
    note: 'Start at the concrete `Entity<Name>`. onLivingUpdate is the per-tick hook, ' +
      'updatePlayerActionState is the AI, dropFewItems is drops, attackEntityFrom is damage, ' +
      'despawnEntity is despawning.',
  },
  {
    topic: 'Mob spawning: where, when, how many',
    entry: 'SpawnerAnimals',
    then: ['SpawnListEntry', 'BiomeGenBase', 'Chunk', 'EntityLiving'],
    note: 'SpawnerAnimals.performSpawning runs the pack/cap logic; each mob then vetoes with its ' +
      'own getCanSpawnHere. Slimes are the special case - they call ' +
      'Chunk.getRandomWithSeed(987234911L), which is the slime-chunk hash. ' +
      'BiomeGenBase holds the per-biome spawn lists.',
  },
  {
    topic: 'Terrain generation, caves, ores, trees',
    entry: 'ChunkProviderGenerate',
    then: ['NoiseGeneratorOctaves', 'MapGenCaves', 'WorldGenMinable', 'WorldGenTrees', 'WorldGenDungeons'],
    note: 'generateTerrain shapes stone, replaceBlocksForBiome puts the surface on, populate ' +
      'places ores, trees, lakes and dungeons. Ore vein sizes and heights are the ' +
      'WorldGenMinable calls inside populate.',
  },
  {
    topic: 'Biomes: which one appears where, and what it looks like',
    entry: 'BiomeGenBase',
    then: ['WorldChunkManager', 'BiomeGenHell', 'BiomeGenSky'],
    note: 'WorldChunkManager maps temperature/rainfall noise onto the biome table. ' +
      'BiomeGenBase\'s static initialiser is the table itself.',
  },
  {
    topic: 'Crafting recipes',
    entry: 'CraftingManager',
    then: ['RecipesTools', 'RecipesWeapons', 'RecipesArmor', 'RecipesIngots', 'RecipesFood',
           'RecipesDyes', 'RecipesCrafting', 'ShapedRecipes', 'ShapelessRecipes'],
    note: 'Only some recipes are written out one at a time in CraftingManager; the seven ' +
      'Recipes* classes generate the rest in loops over a material table. Look in both ' +
      'before concluding a recipe does not exist.',
  },
  {
    topic: 'Smelting, fuel and furnace timings',
    entry: 'TileEntityFurnace',
    then: ['FurnaceRecipes', 'ContainerFurnace', 'SlotFurnace'],
    note: 'FurnaceRecipes lists what smelts into what. TileEntityFurnace holds the numbers: ' +
      'getItemBurnTime is fuel value per item, and the cook duration is the furnaceCookTime ' +
      'threshold in updateEntity.',
  },
  {
    topic: 'Redstone',
    entry: 'BlockRedstoneWire',
    then: ['BlockRedstoneTorch', 'BlockRedstoneRepeater', 'BlockButton', 'BlockLever',
           'BlockPressurePlate', 'BlockDispenser', 'BlockPistonBase'],
    note: 'isIndirectlyPowered / isBlockIndirectlyGettingPowered on World is the read side; ' +
      'each component\'s onNeighborBlockChange and updateTick is the write side.',
  },
  {
    topic: 'Water, lava and fluid spread',
    entry: 'BlockFluid',
    then: ['BlockFlowing', 'BlockStationary', 'Material'],
    note: 'BlockFlowing.updateTick is the spread rule and the tick rate; BlockStationary is the ' +
      'settled form. Source blocks, flow distance and lava/water interaction are all here.',
  },
  {
    topic: 'Fire spread and burning',
    entry: 'BlockFire',
    then: ['Block', 'Material'],
    note: 'BlockFire\'s static initialiser sets each block\'s flammability (chanceToEncourageFire ' +
      'and abilityToCatchFire). updateTick is the spread rule.',
  },
  {
    topic: 'Crops, saplings, grass and other growth',
    entry: 'BlockCrops',
    then: ['BlockSapling', 'BlockFarmland', 'BlockGrass', 'BlockCactus', 'BlockReed', 'BlockMushroom'],
    note: 'Growth is always updateTick plus the block\'s own light/neighbour conditions. ' +
      'Random tick frequency itself is World.tickBlocksAndAmbiance.',
  },
  {
    topic: 'Light levels and the day cycle',
    entry: 'World',
    then: ['Block', 'Chunk'],
    note: 'World.getBlockLightValue reads it; calculateSkylightSubtracted turns time of day into ' +
      'skylight; Block.lightValue and Block.lightOpacity (both static arrays keyed by block id) ' +
      'are what blocks contribute. World.isDaytime and getWorldTime are the clock.',
  },
  {
    topic: 'Damage, combat and death',
    entry: 'Entity',
    then: ['EntityLiving', 'EntityPlayer', 'ItemSword', 'EnumToolMaterial'],
    note: 'attackEntityFrom is the single entry point for all damage, on both Entity and ' +
      'EntityLiving. Armour reduction is in EntityPlayer.damageEntity; fall damage is ' +
      'Entity.fall / EntityLiving.fall.',
  },
  {
    topic: 'Explosions',
    entry: 'Explosion',
    then: ['Block', 'EntityTNTPrimed', 'EntityCreeper'],
    note: 'Block resistance is divided by 5 before use, which is why data/blocks.json stores the ' +
      'divided figure. Explosion.doExplosionA is the ray cast, doExplosionB the block removal.',
  },
  {
    topic: 'The player: inventory, hunger, experience, movement',
    entry: 'EntityPlayer',
    then: ['InventoryPlayer', 'ContainerPlayer', 'ItemStack'],
    note: 'Beta 1.7.3 has no hunger and no experience. Health regenerates from ' +
      'EntityPlayer.onLivingUpdate under difficulty rules only.',
  },
  {
    topic: 'Chests, signs, dispensers and other block entities',
    entry: 'TileEntity',
    then: ['TileEntityChest', 'TileEntityDispenser', 'TileEntitySign', 'TileEntityMobSpawner',
           'TileEntityNote', 'TileEntityRecordPlayer'],
    note: 'updateEntity is the per-tick hook. The paired `Block<Name>` handles placement and ' +
      'interaction; the TileEntity holds the state.',
  },
  {
    topic: 'The Nether',
    entry: 'ChunkProviderHell',
    then: ['BiomeGenHell', 'BlockPortal', 'WorldProviderHell'],
    note: 'The portal shape check and the 1:8 coordinate scale live in BlockPortal and ' +
      'WorldProviderHell respectively.',
  },
  {
    topic: 'World saving, chunk format, NBT',
    entry: 'Chunk',
    then: ['ChunkLoader', 'McRegionChunkLoader', 'NBTTagCompound', 'RegionFile'],
    note: 'Mostly of interest for explaining data values and the region file layout, not for ' +
      'gameplay facts.',
  },
];

/** Class families, matched in order; first match wins. */
const FAMILIES = [
  ['Blocks', /^Block/],
  ['Items', /^Item/],
  ['Entities', /^Entity/],
  ['Block entities', /^TileEntity(?!.*Renderer)/],
  ['World generation', /^(WorldGen|ChunkProvider|MapGen|NoiseGenerator|BiomeGen|WorldChunkManager|WorldProvider)/],
  ['World and chunks', /^(World|Chunk|Region|Explosion|Path|MetadataChunkBlock)/],
  ['Crafting and inventory', /^(Recipes|Shaped|Shapeless|Crafting|Container|Slot|Inventory|Furnace)/],
  ['Saving and NBT', /^(NBT|.*ChunkLoader|SaveHandler|SaveFormat|ChunkFile|ChunkFolder)/],
  ['Networking', /^(Packet|Net|TcpConnection|.*Handler$)/],
  ['Rendering and UI', /^(Gui|Render|Model|Tessellator|Tex|Font|Icon|Effect|EntityFX|.*Renderer$)/],
  ['Sound', /^(Sound|Music|.*SoundManager)/],
];

const IGNORED = new Set(['Rendering and UI', 'Sound', 'Networking']);

function classify(names) {
  const groups = new Map(FAMILIES.map(([label]) => [label, []]));
  groups.set('Other', []);
  for (const name of names) {
    const hit = FAMILIES.find(([, re]) => re.test(name));
    groups.get(hit ? hit[0] : 'Other').push(name);
  }
  return groups;
}

function main() {
  const source = findSource(ROOT);
  if (!source.ok) {
    console.error(`Cannot generate the source map: ${source.reason}`);
    process.exit(1);
  }

  const client = listClasses(source, CLIENT_SRC);
  const server = listClasses(source, SERVER_SRC);
  const clientSet = new Set(client);
  const serverSet = new Set(server);
  const serverOnly = server.filter((c) => !clientSet.has(c));

  // A topic that names a class which is not in the tree would send an agent
  // hunting for something that does not exist.
  const missing = [];
  for (const t of TOPICS) {
    for (const cls of [t.entry, ...t.then]) {
      if (!clientSet.has(cls) && !serverSet.has(cls)) missing.push(`${t.topic}: ${cls}`);
    }
  }
  if (missing.length) {
    console.error('Source map references classes that do not exist:');
    for (const m of missing) console.error(`  ${m}`);
    process.exit(1);
  }

  const groups = classify(client);
  const out = [];
  const p = (s = '') => out.push(s);

  p('# Where to look in the Beta 1.7.3 source');
  p();
  p('<!-- Generated by tools/sourcemap.mjs. Edit the TOPICS table there, not this file. -->');
  p();
  p(`The decompiled game, ${client.length} client classes and ${server.length} server classes.`);
  p('This map exists so a question turns into a file to open rather than a search of the whole tree.');
  p();

  p('## Read the client tree');
  p();
  p('```');
  const cPath = CLIENT_SRC.replace(/\\/g, '/') + '/';
  const sPath = SERVER_SRC.replace(/\\/g, '/') + '/';
  const w = Math.max(cPath.length, sPath.length) + 3;
  p(`${cPath.padEnd(w)}${String(client.length).padStart(3)} classes   <- start here, always`);
  p(`${sPath.padEnd(w)}${String(server.length).padStart(3)} classes`);
  p('```');
  p();
  p('Both trees contain the same game. The client tree is better deobfuscated — 94% of its');
  p('methods and 86% of its fields carry real names, against 86% and 71% on the server — and');
  p('the gameplay logic in them is the same code. `EntitySlime` is 142 lines in both, but the');
  p('client calls it `getSlimeSize()` where the server calls it `func_25027_m()`.');
  p();
  p('**Use the server tree only when:**');
  p();
  p(`- the class is one of the ${serverOnly.length} that exist only there ` +
    `(${serverOnly.slice(0, 6).join(', ')}, …), or`);
  p('- you are specifically asking how a dedicated server differs from singleplayer.');
  p();

  p('## What the names look like');
  p();
  p('- **Local variables are `var1`, `var2`, …** everywhere. That is the decompiler, not a gap');
  p('  in the mapping — expect to read the surrounding code to work out what each holds.');
  p('- **`func_25027_m` and `field_401_a` are finished names**, not placeholders. Around 6% of');
  p('  client methods never got a human name. Quote them as they are.');
  p('- Getters and constants are usually named, so grep for the concept ' +
    '(`getCanSpawnHere`, `987234911L`) rather than for a modern name that may not exist here.');
  p();

  p('## Topic index');
  p();
  for (const t of TOPICS) {
    const side = clientSet.has(t.entry) ? '' : ' *(server tree)*';
    p(`### ${t.topic}`);
    p();
    p(`Start in **\`${t.entry}.java\`**${side}.`);
    if (t.then.length) p(`Then: ${t.then.map((c) => `\`${c}\``).join(', ')}.`);
    p();
    p(t.note);
    p();
  }

  p('## Class index');
  p();
  p('Client tree, grouped. Families marked *(not gameplay)* describe how the game draws or');
  p('transmits things and almost never answer a wiki question.');
  p();
  for (const [label, names] of groups) {
    if (!names.length) continue;
    const tag = IGNORED.has(label) ? ' *(not gameplay)*' : '';
    p(`<details><summary><b>${label}</b> — ${names.length} classes${tag}</summary>`);
    p();
    p(names.map((n) => `\`${n}\``).join(' · '));
    p();
    p('</details>');
    p();
  }

  p('## Server-only classes');
  p();
  p(serverOnly.map((n) => `\`${n}\``).join(' · '));
  p();

  mkdirSync(dirname(OUT), { recursive: true });
  writeFileSync(OUT, out.join('\n'));
  console.log(`Wrote ${OUT.replace(ROOT + '\\', '')}`);
  console.log(`  ${TOPICS.length} topics, ${client.length} client classes, ${serverOnly.length} server-only`);
}

main();
