#!/usr/bin/env node
// Scaffold a new page with correct frontmatter.
//
//   npm run new -- block "Mossy Cobblestone"
//   npm run new -- guide "Building a mob farm"
//
// If the title matches a block, item, entity or biome in the extracted data,
// the ids and any real recipes are filled in, exactly as tools/seed.mjs does.
import { mkdirSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadData } from './lib/data.mjs';
import { slug } from './lib/slug.mjs';
import { ENTITY_SECTIONS, isMob, MOB_SECTIONS } from './lib/mobs.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const [, , nsArg, ...titleParts] = process.argv;
const title = titleParts.join(' ').trim();

const config = (await import(pathToFileURL(join(ROOT, 'wiki.config.js')).href)).default;
const namespaces = Object.keys(config.namespaces);

if (!nsArg || !title) {
  console.error('usage: npm run new -- <namespace> "<Page Title>"');
  console.error(`namespaces: ${namespaces.join(', ')}`);
  process.exit(1);
}
if (!namespaces.includes(nsArg)) {
  console.error(`unknown namespace "${nsArg}". Try one of: ${namespaces.join(', ')}`);
  process.exit(1);
}

const data = loadData(ROOT);
const rec = data.lookup(title);
const recipes = data.recipesFor(title);
const uses = data.recipesUsing(title);

const categoryFor = {
  block: 'Blocks', item: 'Items', entity: isMob(title) ? 'Mobs' : 'Entities', biome: 'Biomes',
  dimension: 'Dimensions', structure: 'Structures',
  mechanic: 'Game mechanics', guide: 'Guides', research: 'Research', wiki: 'Wiki',
}[nsArg];

// Namespaces whose pages describe a place or a system rather than a thing in
// data/. Nothing there answers to their titles -- no id, no recipe, no infobox
// to build -- so they get their own headings instead of Obtaining and Usage.
const PROSE_SECTIONS = {
  guide: ['## Overview', '', '## Steps', '', '## See also', ''],
  mechanic: ['## How it works', '', '## See also', ''],
  // A research page is the one long-form shape: AGENTS.md "Research pages".
  research: [
    '## Summary', '',
    '<!-- The question, and the answer as it stands, in a few paragraphs. -->', '',
    '## Status', '',
    '<!-- What is settled, what is open, and when the last experiment ran. -->', '',
    '## Background', '',
    '<!-- Prior work, including other versions, and what it suggested. -->', '',
    '## Method', '',
    '<!-- Sources read, tools built, how experiments were run. -->', '',
    '## Findings', '',
    '<!-- One subsection per finding, each with its evidence level. -->', '',
    '## Dead ends', '',
    '<!-- Leads that were followed and ruled out, and why. -->', '',
    '## Open questions', '',
    '<!-- What a newcomer could pick up next. -->', '',
    '## Reproducing', '',
    '<!-- Enough to rerun every experiment from scratch. -->', '',
    '## References', '',
  ],
  dimension: [
    '## Reaching it', '',
    '<!-- How a player travels there and back, and what the trip costs. -->', '',
    '## Terrain', '',
    '<!-- What the generator makes: surface, caves, the blocks it is built of. -->', '',
    '## Mobs', '',
    '<!-- Which mobs spawn, and anything unusual about spawn rates. -->', '',
    '## Data values', '',
    '<!-- The dimension id. -->', '',
  ],
  structure: [
    '## Generation', '',
    '<!-- Where it generates, how often, and what decides. -->', '',
    '## Contents', '',
    '<!-- The blocks it is made of, and anything it holds. -->', '',
    '## Usage', '',
    '<!-- What a player does with it. -->', '',
  ],
};

const lines = [
  '---',
  `title: ${title}`,
  `description: ${title} in Minecraft ${config.version}.`,
  `type: ${nsArg}`,
  `categories: [${categoryFor}]`,
  'stub: true',
  '---',
  '',
  `{{stub|${nsArg}}}`,
  '',
  `**${title}** `,
  '',
];

if (PROSE_SECTIONS[nsArg]) {
  lines.push(...PROSE_SECTIONS[nsArg]);
} else {
  // Match the shape tools/seed.mjs gives the same subject.
  if (nsArg === 'entity') {
    lines.push(...(isMob(title) ? MOB_SECTIONS : ENTITY_SECTIONS));
  } else {
    lines.push('## Obtaining', '');
    if (recipes.some((r) => r.type !== 'smelting')) {
      lines.push('### Crafting', '', `{{crafting|${title}}}`, '');
    }
    if (recipes.some((r) => r.type === 'smelting')) {
      lines.push('### Smelting', '', `{{smelting|${title}}}`, '');
    }
    lines.push('## Usage', '');
    if (uses.length) lines.push('### Crafting ingredient', '', `{{used in|${title}}}`, '');
  }
  if (rec) {
    lines.push('## Data values', '');
    if (rec.id != null) {
      lines.push(`- ${rec.kind === 'block' ? 'Block' : 'Item'} ID: {{id|${title}}}`);
    }
    if (rec.networkId != null) lines.push(`- Entity network ID: {{id|${title}}}`);
    if (rec.langKey) lines.push(`- Translation key: \`${rec.langKey}\``);
    lines.push('');
  }
}

const file = join(ROOT, 'content', nsArg, `${slug(title)}.md`);
if (existsSync(file)) {
  console.error(`already exists: ${file}`);
  process.exit(1);
}
mkdirSync(dirname(file), { recursive: true });
writeFileSync(file, lines.join('\n'), 'utf8');

console.log(`created content/${nsArg}/${slug(title)}.md`);
if (!rec && ['block', 'item', 'entity', 'biome'].includes(nsArg)) {
  console.log(`note: "${title}" does not match anything in data/, so there is no`);
  console.log('      infobox or sprite for it. Check the spelling against /wiki/data-values/.');
}
