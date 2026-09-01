#!/usr/bin/env node
// Generate a stub page for every block, item and entity in data/*.json.
//
//   node tools/seed.mjs              create pages that do not exist yet
//   node tools/seed.mjs --force      overwrite existing stubs too (never
//                                    touches a page whose `stub` is not true)
//
// Stubs are not blank: the lead sentence, ids, sprite and any crafting or
// smelting recipes come from the extracted data, so a stub is already correct
// as far as it goes. What is missing is prose, which is what editors add.
import { mkdirSync, writeFileSync, existsSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadData } from './lib/data.mjs';
import { slug } from './lib/slug.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const force = process.argv.includes('--force');

const data = loadData(ROOT);

/** One page per display name: Beta 1.7.3 gives several ids the same name. */
function mergeByName() {
  const byName = new Map();
  const get = (name) => {
    if (!byName.has(name)) {
      byName.set(name, { name, blockIds: [], itemIds: [], entity: null, rec: null });
    }
    return byName.get(name);
  };
  for (const b of data.blocks) {
    if (!b.key) continue;                      // technical blocks have no name
    const e = get(b.name);
    e.blockIds.push(b.id);
    if (!e.rec) e.rec = { kind: 'block', ...b };
  }
  for (const i of data.items) {
    const e = get(i.name);
    e.itemIds.push(i.id);
    if (!e.rec) e.rec = { kind: 'item', ...i };
  }
  for (const en of data.entities) {
    const e = get(en.name);
    e.entity = en;
    if (!e.rec) e.rec = { kind: 'entity', ...en };
  }
  return [...byName.values()];
}

const MOBS = new Set(['Creeper', 'Skeleton', 'Spider', 'Zombie', 'Slime', 'Ghast',
  'PigZombie', 'Pig', 'Sheep', 'Cow', 'Chicken', 'Squid', 'Wolf', 'Giant']);

/** Abstract or purely technical entities that should not get their own page. */
const SKIP_ENTITIES = new Set(['Mob', 'Monster', 'Item']);

function namespaceFor(entry) {
  if (entry.blockIds.length) return 'block';
  if (entry.itemIds.length) return 'item';
  return 'entity';
}

function prettyName(name) {
  // "PigZombie" -> "Pig Zombie", "PrimedTnt" -> "Primed Tnt"
  return name.replace(/([a-z])([A-Z])/g, '$1 $2');
}

function leadSentence(entry) {
  const r = entry.rec;
  const name = prettyName(entry.name);
  if (r.kind === 'block') {
    const bits = [];
    if (r.hardness != null) {
      bits.push(r.hardness < 0
        ? 'It cannot be broken in survival mode'
        : `It has a hardness of ${round(r.hardness)}`);
    }
    if (r.blastResistance != null && r.hardness >= 0) {
      bits.push(`a blast resistance of ${round(r.blastResistance)}`);
    }
    let s = `**${name}** is a block in Minecraft Beta 1.7.3.`;
    if (bits.length) s += ` ${bits.join(' and ')}.`;
    if (r.lightEmission) s += ` It emits light level ${r.lightEmission}.`;
    return s;
  }
  if (r.kind === 'item') return `**${name}** is an item in Minecraft Beta 1.7.3.`;
  const kind = MOBS.has(entry.name) ? 'mob' : 'entity';
  return `**${name}** is a ${kind} in Minecraft Beta 1.7.3.`;
}

const round = (n) => String(Math.round(n * 1000) / 1000);

function categoriesFor(entry) {
  if (entry.blockIds.length) return ['Blocks'];
  if (entry.itemIds.length) return ['Items'];
  return MOBS.has(entry.name) ? ['Mobs'] : ['Entities'];
}

function dataValuesSection(entry) {
  const lines = [];
  if (entry.blockIds.length) {
    lines.push(`- Block ID: ${entry.blockIds.map((i) => `\`${i}\``).join(', ')}`);
  }
  if (entry.itemIds.length) {
    lines.push(`- Item ID: ${entry.itemIds.map((i) => `\`${i}\``).join(', ')}`);
  }
  if (entry.entity) lines.push(`- Entity network ID: \`${entry.entity.networkId}\``);
  if (entry.rec.langKey) lines.push(`- Translation key: \`${entry.rec.langKey}\``);
  return lines.join('\n');
}

function buildPage(entry) {
  const name = prettyName(entry.name);
  const ns = namespaceFor(entry);
  const cats = categoriesFor(entry);
  const recipes = data.recipesFor(entry.name).filter((r) => r.type !== 'smelting');
  const smelts = data.recipesFor(entry.name).filter((r) => r.type === 'smelting');
  const uses = data.recipesUsing(entry.name);

  const fm = [
    '---',
    `title: ${name}`,
    `description: ${name} in Minecraft Beta 1.7.3.`,
    `type: ${ns}`,
    entry.name !== name ? `subject: ${entry.name}` : null,
    // Keep the game's own spelling linkable, e.g. [[PigZombie]].
    entry.name !== name ? `aliases: [${entry.name}]` : null,
    `categories: [${cats.join(', ')}]`,
    'stub: true',
    '---',
  ].filter(Boolean).join('\n');

  const body = ['', '{{stub|' + ns + '}}', '', leadSentence(entry), '', '## Obtaining', ''];

  if (recipes.length) {
    body.push('### Crafting', '', `{{crafting|${entry.name}}}`, '');
  }
  if (smelts.length) {
    body.push('### Smelting', '', `{{smelting|${entry.name}}}`, '');
  }
  if (!recipes.length && !smelts.length) {
    body.push('<!-- How is it obtained? Mining, crafting, mob drops, generation. -->', '');
  }

  body.push('## Usage', '');
  if (uses.length) {
    body.push('### Crafting ingredient', '', `{{used in|${entry.name}}}`, '');
  } else {
    body.push('<!-- What is it for? -->', '');
  }

  body.push('## Data values', '', dataValuesSection(entry), '');

  return `${fm}\n${body.join('\n')}`;
}

function isStubFile(path) {
  if (!existsSync(path)) return true;
  const raw = readFileSync(path, 'utf8');
  return /^stub:\s*true\s*$/m.test(raw.split('---')[1] || '');
}

function buildBiomePage(b) {
  const fm = [
    '---',
    `title: ${b.name}`,
    `description: The ${b.name} biome in Minecraft Beta 1.7.3.`,
    'type: biome',
    'categories: [Biomes]',
    `infobox: {Map colour: '${b.color}'}`,
    'stub: true',
    '---',
  ].join('\n');
  const body = [
    '',
    '{{stub|biome}}',
    '',
    `**${b.name}** is one of the thirteen biomes in Minecraft Beta 1.7.3.`,
    '',
    '## Terrain',
    '',
    '<!-- Height, surface blocks, notable formations. -->',
    '',
    '## Vegetation',
    '',
    '<!-- Which trees, grass and flowers generate here. -->',
    '',
    '## Mobs',
    '',
    '<!-- Which mobs spawn, and anything unusual about spawn rates. -->',
    '',
    '## Data values',
    '',
    `- Map colour: \`${b.color}\``,
    '',
  ].join('\n');
  return `${fm}\n${body}`;
}

let created = 0;
let skipped = 0;
let overwritten = 0;

for (const b of data.biomes) {
  const file = join(ROOT, 'content', 'biome', `${slug(b.name)}.md`);
  const exists = existsSync(file);
  if (exists && (!force || !isStubFile(file))) { skipped++; continue; }
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, buildBiomePage(b), 'utf8');
  if (exists) overwritten++; else created++;
}

for (const entry of mergeByName()) {
  if (!entry.rec) continue;
  if (entry.entity && SKIP_ENTITIES.has(entry.name) && !entry.blockIds.length
      && !entry.itemIds.length) {
    continue;
  }
  const ns = namespaceFor(entry);
  const file = join(ROOT, 'content', ns, `${slug(prettyName(entry.name))}.md`);
  const exists = existsSync(file);
  if (exists && !force) { skipped++; continue; }
  if (exists && force && !isStubFile(file)) { skipped++; continue; }
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, buildPage(entry), 'utf8');
  if (exists) overwritten++; else created++;
}

console.log(`seeded: ${created} created, ${overwritten} rewritten, ${skipped} left alone`);
