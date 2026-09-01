// Access to the game data extracted from client.jar by tools/extract/*.py.
// Templates and infoboxes read from here, so a page never has to restate a
// number the game itself already tells us.
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { slug } from './slug.mjs';

function readJson(dir, name, fallback) {
  const p = join(dir, name);
  if (!existsSync(p)) return fallback;
  return JSON.parse(readFileSync(p, 'utf8'));
}

export function loadData(root) {
  const dir = join(root, 'data');
  const blocks = readJson(dir, 'blocks.json', []);
  const items = readJson(dir, 'items.json', []);
  const entities = readJson(dir, 'entities.json', []);
  const biomes = readJson(dir, 'biomes.json', []);
  const recipes = readJson(dir, 'recipes.json', []);
  const smelting = readJson(dir, 'smelting.json', []);
  const spriteFile = readJson(dir, 'sprites.json', { sprites: {} });
  const meta = readJson(dir, 'meta.json', {});

  // Blocks and items share one id space in Beta 1.7.3: 1-255 are blocks,
  // 256+ are items, which is exactly how recipes refer to them.
  const blockById = new Map(blocks.map((b) => [b.id, b]));
  const itemById = new Map(items.map((i) => [i.id, i]));
  const bySlug = new Map();
  for (const b of blocks) if (!bySlug.has(slug(b.name))) bySlug.set(slug(b.name), { kind: 'block', ...b });
  for (const i of items) if (!bySlug.has(slug(i.name))) bySlug.set(slug(i.name), { kind: 'item', ...i });
  for (const e of entities) if (!bySlug.has(slug(e.name))) bySlug.set(slug(e.name), { kind: 'entity', ...e });

  /** Resolve a recipe reference ({block:4} / {item:280}) to a data record. */
  function resolveRef(ref) {
    if (!ref) return null;
    if (ref.block != null) {
      const b = blockById.get(ref.block);
      return b ? { kind: 'block', ...b, count: ref.count, damage: ref.damage } : null;
    }
    if (ref.item != null) {
      const i = itemById.get(ref.item);
      return i ? { kind: 'item', ...i, count: ref.count, damage: ref.damage } : null;
    }
    return null;
  }

  const refSlug = (ref) => {
    const r = resolveRef(ref);
    return r ? slug(r.name) : null;
  };

  // Index recipes by what they produce and what they consume, so a page can
  // ask for both without scanning.
  const producedBy = new Map();
  const usedIn = new Map();
  const push = (map, key, val) => {
    if (!key) return;
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(val);
  };
  for (const r of recipes) {
    push(producedBy, refSlug(r.output), r);
    const ings = r.type === 'shaped' ? Object.values(r.key || {}) : r.ingredients || [];
    for (const s of new Set(ings.map(refSlug))) push(usedIn, s, r);
  }
  for (const s of smelting) {
    push(producedBy, refSlug(s.output), { ...s, type: 'smelting' });
    push(usedIn, refSlug(s.input), { ...s, type: 'smelting' });
  }

  return {
    meta,
    blocks,
    items,
    entities,
    biomes,
    recipes,
    smelting,
    sprites: spriteFile.sprites || {},
    spriteTile: spriteFile.tile || 16,

    blockById: (id) => blockById.get(id),
    itemById: (id) => itemById.get(id),
    /** Look up a block/item/entity by display name or slug. */
    lookup: (name) => bySlug.get(slug(name)) || null,
    sprite: (name) => (spriteFile.sprites || {})[slug(name)] || null,
    resolveRef,
    refSlug,
    recipesFor: (name) => producedBy.get(slug(name)) || [],
    recipesUsing: (name) => usedIn.get(slug(name)) || [],
  };
}
