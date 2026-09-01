// Cross-check data/*.json against the decompiled source.
//
// data/ is extracted from the client jar's bytecode; the decompiled source is
// an independent reading of the same jar. When the two agree, the numbers on
// every page are right. When they disagree, one of the two extractors is wrong
// and a reader would be told something false.
//
// Disagreements are errors: a value that contradicts the source is a bug.
// Omissions are warnings: something the extractors never picked up is a
// to-do, in the same way a red link is.

import { readClass } from './source.mjs';

// ---------------------------------------------------------------------------
// Java source parsing
//
// Only static initialisers are read, and only the handful of registration
// idioms the game uses. This is deliberately not a Java parser.
// ---------------------------------------------------------------------------

/**
 * Assignment statements in a class body, joined across lines.
 * Yields [lhs, rhs] for every `name = ... ;` at field-initialiser depth.
 */
function statements(src) {
  const out = [];
  const lines = src.split('\n');
  let lhs = null;
  let buf = '';
  for (const line of lines) {
    if (lhs === null) {
      const m = /^\s{4,}([A-Za-z_]\w*) = (.*)$/.exec(line);
      if (!m) continue;
      lhs = m[1];
      buf = m[2];
    } else {
      buf += ' ' + line.trim();
    }
    if (buf.trimEnd().endsWith(';')) {
      out.push([lhs, buf.trimEnd().slice(0, -1)]);
      lhs = null;
      buf = '';
    }
  }
  return out;
}

/** Java float arithmetic, so light values truncate exactly as the game does. */
const f32 = (n) => Math.fround(n);

/** Setter calls in source order: [name, firstArgText]. */
function chain(rhs) {
  const out = [];
  const re = /\.(set[A-Za-z]+|disableStats|disableNeighborNotifyOnMetadataChange)\(([^()]*(?:\([^()]*\))?[^()]*)\)/g;
  let m;
  while ((m = re.exec(rhs))) out.push([m[1], m[2]]);
  return out;
}

/**
 * Replay Block's builder chain.
 *
 * The order matters. From Block.java:
 *   setResistance(r)  -> blockResistance = r * 3
 *   setHardness(h)    -> blockHardness = h; if (blockResistance < h * 5) blockResistance = h * 5
 * so setHardness only ever raises resistance. Reordering the calls, or treating
 * the second as an assignment, gets bedrock and portal wrong.
 */
function parseBlocks(src, superId) {
  const blocks = new Map();   // id -> record
  const fields = new Map();   // field name -> id
  for (const [field, rhs] of statements(src)) {
    const ctor = /new\s+(\w+)\(\s*(\d+)?/.exec(rhs);
    if (!ctor) continue;
    // A few blocks take no id: BlockCloth() hardcodes super(35, ...) instead.
    const id = ctor[2] !== undefined ? Number(ctor[2]) : superId(ctor[1]);
    if (id === null) continue;
    let hardness = 0;
    let resistance = 0;
    let light = 0;
    let key = null;
    for (const [name, arg] of chain(rhs)) {
      const v = parseFloat(arg);
      if (name === 'setHardness') {
        hardness = v;
        if (resistance < v * 5) resistance = v * 5;
      } else if (name === 'setBlockUnbreakable') {
        hardness = -1;
        if (resistance < -5) resistance = -5;
      } else if (name === 'setResistance') {
        resistance = v * 3;
      } else if (name === 'setLightValue') {
        light = Math.trunc(f32(15 * f32(v)));
      } else if (name === 'setBlockName') {
        key = /"([^"]+)"/.exec(arg)?.[1] ?? null;
      }
    }
    if (rhs.includes('setBlockUnbreakable()')) hardness = -1;
    fields.set(field, id);
    // Blocks are declared once each; a later re-registration would be a bug.
    if (!blocks.has(id)) {
      blocks.set(id, { id, field, key, hardness, blastResistance: resistance / 5, lightEmission: light });
    }
  }
  return { blocks, fields };
}

function parseItems(src) {
  const items = new Map();
  const fields = new Map();
  for (const [field, rhs] of statements(src)) {
    const ctor = /new\s+(\w+)\(\s*(\d+)/.exec(rhs);
    if (!ctor) continue;
    const id = 256 + Number(ctor[2]);   // Item(int): this.shiftedIndex = 256 + var1
    let icon = null;
    let key = null;
    for (const [name, arg] of chain(rhs)) {
      if (name === 'setIconCoord') {
        const xy = /(\d+)\s*,\s*(\d+)/.exec(arg);
        if (xy) icon = { x: Number(xy[1]), y: Number(xy[2]) };
      } else if (name === 'setItemName') {
        key = /"([^"]+)"/.exec(arg)?.[1] ?? null;
      }
    }
    fields.set(field, id);
    if (!items.has(id)) items.set(id, { id, field, key, icon });
  }
  return { items, fields };
}

function parseEntities(src) {
  const out = new Map();
  const re = /addMapping\((\w+)\.class,\s*"([^"]+)",\s*(\d+)\)/g;
  let m;
  while ((m = re.exec(src))) out.set(m[2], { name: m[2], cls: m[1], networkId: Number(m[3]) });
  return out;
}

/** Resolve `Block.foo.blockID` / `Item.bar.shiftedIndex` / a bare literal. */
function resolveRef(text, blockFields, itemFields) {
  let m = /Block\.(\w+)\.blockID/.exec(text);
  if (m) return blockFields.has(m[1]) ? { block: blockFields.get(m[1]) } : null;
  m = /Item\.(\w+)\.shiftedIndex/.exec(text);
  if (m) return itemFields.has(m[1]) ? { item: itemFields.get(m[1]) } : null;
  m = /new ItemStack\(\s*Block\.(\w+)/.exec(text);
  if (m) return blockFields.has(m[1]) ? { block: blockFields.get(m[1]) } : null;
  m = /new ItemStack\(\s*Item\.(\w+)/.exec(text);
  if (m) return itemFields.has(m[1]) ? { item: itemFields.get(m[1]) } : null;
  return null;
}

function parseSmelting(src, blockFields, itemFields) {
  const out = [];
  const re = /addSmelting\(([^,]+),\s*(new ItemStack\([^;]*?\))\)\s*;/g;
  let m;
  while ((m = re.exec(src))) {
    const input = resolveRef(m[1], blockFields, itemFields);
    const output = resolveRef(m[2], blockFields, itemFields);
    if (input && output) out.push({ input, output });
  }
  return out;
}

// ---------------------------------------------------------------------------
// Comparisons
// ---------------------------------------------------------------------------

const near = (a, b) => Math.abs((a ?? 0) - (b ?? 0)) < 0.001;
const idOf = (ref) => (ref?.item ?? ref?.block ?? null);

function compareBlocks(source, data, add) {
  const src = readClass(source, 'Block');
  if (!src) return add('warn', 'Block.java not found in the source tree');

  /** The id a no-argument subclass passes to super(), e.g. BlockCloth -> 35. */
  const superId = (cls) => {
    const sub = readClass(source, cls);
    const m = sub && new RegExp(`public ${cls}\\(\\)\\s*\\{\\s*super\\(\\s*(\\d+)`).exec(sub);
    return m ? Number(m[1]) : null;
  };
  const { blocks, fields } = parseBlocks(src, superId);
  const mine = new Map(data.blocks.map((b) => [b.id, b]));

  let checked = 0;
  for (const [id, s] of blocks) {
    const m = mine.get(id);
    if (!m) {
      add('warn', `block ${id} (${s.field}) is in Block.java but not in data/blocks.json`);
      continue;
    }
    checked++;
    const label = `block ${id} (${m.name || s.field})`;
    if (!near(m.hardness, s.hardness)) {
      add('error', `${label}: hardness is ${m.hardness} in data/blocks.json, ${s.hardness} in Block.java`);
    }
    if (!near(m.blastResistance, s.blastResistance)) {
      add('error', `${label}: blast resistance is ${m.blastResistance} in data/blocks.json, ${s.blastResistance} in Block.java`);
    }
    if ((m.lightEmission ?? 0) !== s.lightEmission) {
      add('error', `${label}: light is ${m.lightEmission} in data/blocks.json, ${s.lightEmission} in Block.java`);
    }
  }
  for (const b of data.blocks) {
    if (!blocks.has(b.id)) add('warn', `block ${b.id} (${b.name}) is in data/blocks.json but was not found in Block.java`);
  }
  return { checked, fields };
}

function compareItems(source, data, add) {
  const src = readClass(source, 'Item');
  if (!src) return add('warn', 'Item.java not found in the source tree');
  const { items, fields } = parseItems(src);
  const mine = new Map(data.items.map((i) => [i.id, i]));

  let checked = 0;
  for (const [id, s] of items) {
    const m = mine.get(id);
    if (!m) {
      add('warn', `item ${id} (${s.field}) is in Item.java but not in data/items.json`);
      continue;
    }
    checked++;
    if (s.icon && m.icon && (s.icon.x !== m.icon.x || s.icon.y !== m.icon.y)) {
      add('error', `item ${id} (${m.name || s.field}): icon is ${m.icon.x},${m.icon.y} in data/items.json, ` +
        `${s.icon.x},${s.icon.y} in Item.java`);
    }
  }
  for (const i of data.items) {
    if (!items.has(i.id)) add('warn', `item ${i.id} (${i.name}) is in data/items.json but was not found in Item.java`);
  }
  return { checked, fields };
}

function compareEntities(source, data, add) {
  const src = readClass(source, 'EntityList');
  if (!src) return add('warn', 'EntityList.java not found in the source tree');
  const entities = parseEntities(src);
  const mine = new Map(data.entities.map((e) => [e.name, e]));

  let checked = 0;
  for (const [name, s] of entities) {
    const m = mine.get(name);
    if (!m) {
      add('warn', `entity "${name}" is in EntityList.java but not in data/entities.json`);
      continue;
    }
    checked++;
    if (m.networkId !== s.networkId) {
      add('error', `entity "${name}": network id is ${m.networkId} in data/entities.json, ` +
        `${s.networkId} in EntityList.java`);
    }
  }
  return { checked };
}

function compareSmelting(source, data, blockFields, itemFields, add) {
  const src = readClass(source, 'FurnaceRecipes');
  if (!src) return add('warn', 'FurnaceRecipes.java not found in the source tree');
  const recipes = parseSmelting(src, blockFields, itemFields);
  const key = (r) => `${r.input.block ?? 'i' + r.input.item}>${idOf(r.output)}`;
  const mine = new Set(data.smelting.map((r) => key(r)));

  let checked = 0;
  for (const r of recipes) {
    if (mine.has(key(r))) checked++;
    else add('error', `smelting ${JSON.stringify(r.input)} -> ${JSON.stringify(r.output)} ` +
      `is in FurnaceRecipes.java but not in data/smelting.json`);
  }
  if (data.smelting.length > recipes.length) {
    add('warn', `data/smelting.json has ${data.smelting.length} recipes, FurnaceRecipes.java registers ${recipes.length}`);
  }
  return { checked };
}

/**
 * Crafting is checked by output, not by pattern: the point is to notice recipes
 * that never reached data/ at all.
 *
 * Most of the game's recipes are not written out one by one. Seven generator
 * classes build them in loops over a material table, and the bytecode extractor
 * does not follow those loops - so every tool, weapon, armour piece, dye and
 * ingot-block conversion is currently absent.
 */
const GENERATORS = ['RecipesTools', 'RecipesWeapons', 'RecipesIngots', 'RecipesFood',
                    'RecipesCrafting', 'RecipesArmor', 'RecipesDyes'];

function compareRecipes(source, data, blockFields, itemFields, add) {
  const src = readClass(source, 'CraftingManager');
  if (!src) return add('warn', 'CraftingManager.java not found in the source tree');

  const outputs = new Set();
  const re = /add(?:Shapeless)?Recipe\(\s*(new ItemStack\([^,)]*(?:,\s*\d+)?(?:,\s*\d+)?\))/g;
  let m;
  while ((m = re.exec(src))) {
    const ref = resolveRef(m[1], blockFields, itemFields);
    if (ref) outputs.add(idOf(ref));
  }
  const mine = new Set(data.recipes.map((r) => idOf(r.output)));

  let checked = 0;
  for (const id of outputs) {
    if (mine.has(id)) checked++;
    else add('error', `CraftingManager.java registers a recipe producing id ${id}, ` +
      `but data/recipes.json has none`);
  }

  const present = GENERATORS.filter((g) => src.includes(`new ${g}()`));
  if (present.length) {
    add('warn', `data/recipes.json holds only the recipes CraftingManager writes out individually. ` +
      `${present.length} generator classes (${present.join(', ')}) build the rest in loops, so no ` +
      `tool, weapon, armour, dye or ingot-block recipe is in the data`);
  }
  return { checked };
}

// ---------------------------------------------------------------------------

/**
 * Verify data/ against the source tree.
 *
 * Returns { ran, summary, problems }. When the source is not installed this is
 * a no-op with ran: false - the wiki is expected to build without it.
 */
export function verifyData(source, data) {
  const problems = [];
  const add = (level, message) => problems.push({ page: 'data/', level, message });
  if (!source.ok) return { ran: false, summary: source.reason, problems };

  const blocks = compareBlocks(source, data, add) || {};
  const items = compareItems(source, data, add) || {};
  const entities = compareEntities(source, data, add) || {};
  const blockFields = blocks.fields || new Map();
  const itemFields = items.fields || new Map();
  const smelting = compareSmelting(source, data, blockFields, itemFields, add) || {};
  const recipes = compareRecipes(source, data, blockFields, itemFields, add) || {};

  const summary = `${blocks.checked || 0} blocks, ${items.checked || 0} items, ` +
    `${entities.checked || 0} entities, ${smelting.checked || 0} smelting, ` +
    `${recipes.checked || 0} crafting outputs`;
  return { ran: true, summary, problems };
}
