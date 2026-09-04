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
  // Subtypes answer to their own names too. A page called "Fern" or "Magenta
  // Wool" is a page about one damage value of a block, and it wants that
  // block's id and hardness; the damage comes with it so the infobox can say
  // which one. A subtype named after its own id -- wool's damage 0 is "Wool"
  // -- is already indexed, hence the guard.
  const variantsOf = (rec, kind) => Object.entries(rec.variants || {})
    .filter(([, name]) => !bySlug.has(slug(name)))
    .forEach(([damage, name]) => bySlug.set(slug(name),
      { kind, ...rec, damage: Number(damage), label: name }));
  for (const b of blocks) variantsOf(b, 'block');
  for (const i of items) variantsOf(i, 'item');

  /**
   * Look a thing up by display name, or by id when the name is not enough.
   *
   * "block 75" and "block 76" are both called Redstone Torch, one lit and one
   * not, and only one of them can own the name. A page covering the pair says
   * which it means the way a recipe does, by kind and number, and gets a record
   * back either way.
   */
  const BY_ID = /^(block|item|entity)\s+(\d+)$/i;
  function lookup(name) {
    const byId = BY_ID.exec(String(name).trim());
    if (!byId) return bySlug.get(slug(name)) || null;
    const kind = byId[1].toLowerCase();
    const id = Number(byId[2]);
    const rec = kind === 'block' ? blockById.get(id)
      : kind === 'item' ? itemById.get(id)
        : entities.find((e) => e.networkId === id);
    return rec ? { kind, ...rec } : null;
  }

  /**
   * Resolve a recipe reference ({block:4} / {item:280}) to a data record.
   *
   * `name` stays the id's own name, because that is what has a sprite and a
   * page. `label` is what the game would call this particular stack: an id
   * with subtypes picks its name from the damage value, so item 351 is "Ink
   * Sac" at damage 0 and "Lapis Lazuli" at 4. Callers show the label and link
   * the name.
   */
  function withLabel(rec, ref) {
    const variant = rec.variants && rec.variants[String(ref.damage ?? 0)];
    return { ...rec, count: ref.count, damage: ref.damage, label: variant || rec.name };
  }

  function resolveRef(ref) {
    if (!ref) return null;
    if (ref.block != null) {
      const b = blockById.get(ref.block);
      return b ? withLabel({ kind: 'block', ...b }, ref) : null;
    }
    if (ref.item != null) {
      const i = itemById.get(ref.item);
      return i ? withLabel({ kind: 'item', ...i }, ref) : null;
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
    /** Look up a block/item/entity by display name, slug, or "block 75". */
    lookup,
    /** The display name of whatever a subject points at, for callers wanting one. */
    nameOf: (name) => (lookup(name) || {}).name || String(name),
    sprite: (name) => (spriteFile.sprites || {})[slug(name)] || null,
    resolveRef,
    refSlug,
    recipesFor: (name) => producedBy.get(slug(name)) || [],
    recipesUsing: (name) => usedIn.get(slug(name)) || [],
  };
}
