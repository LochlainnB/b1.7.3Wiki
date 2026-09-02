// Template implementations: the {{...}} calls editors write in page bodies.
//
// Markup deliberately mirrors minecraft.wiki's own class names (.mcui,
// .invslot, .infobox-rows, .sprite-file) so the stylesheet is a faithful
// reimplementation rather than an approximation.
import { slug } from './slug.mjs';

export const escapeHtml = (s) =>
  String(s).replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const registry = new Map();
const define = (names, fn) => {
  for (const n of [].concat(names)) registry.set(n, fn);
};

export function hasTemplate(name) {
  return registry.has(slug(name));
}

export function renderTemplate(name, args, named, ctx) {
  const fn = registry.get(slug(name));
  if (!fn) {
    ctx.warn(`unknown template {{${name}}}`);
    return `<span class="template-error">Unknown template: ${escapeHtml(name)}</span>`;
  }
  try {
    return fn({ args, named, ctx }) || '';
  } catch (err) {
    ctx.warn(`template {{${name}}} failed: ${err.message}`);
    return `<span class="template-error">Template error in ${escapeHtml(name)}</span>`;
  }
}

// ---------------------------------------------------------------------------
// Inventory primitives
// ---------------------------------------------------------------------------

/**
 * The name whose sprite a resolved reference should show.
 *
 * A stack's label is its subtype ("Magenta Wool") and its name is the id that
 * owns the page ("Wool"). Sixteen wools and sixteen dyes each have an icon of
 * their own, so the label is preferred wherever the manifest has one; the link
 * and the page stay with the name.
 */
function spriteName(ctx, name, label) {
  return label && ctx.data.sprite(label) ? label : name;
}

/** One inventory slot, optionally holding a linked item sprite and a count. */
function invslot(ctx, name, { count, large = false, plain = false, title, label } = {}) {
  const cls = ['invslot', large && 'invslot-large', plain && 'invslot-plain']
    .filter(Boolean).join(' ');
  // A cell may carry a subtype label ("Magenta Wool") alongside the name that
  // owns the page ("Wool"). Show the subtype, link the name.
  if (name && typeof name === 'object') {
    title = title || name.label;
    label = label || name.label;
    name = name.name;
  }
  if (!name) return `<span class="${cls}"></span>`;
  const icon = ctx.sprite(spriteName(ctx, name, label), { link: false, title: title || name });
  const inner = ctx.linkWrap(name, icon, '', title || name);
  const stack = count && count > 1
    ? `<span class="invslot-stacksize">${escapeHtml(count)}</span>` : '';
  return `<span class="${cls}"><span class="invslot-item invslot-item-image">${inner}</span>${stack}</span>`;
}

/** A reference from data/recipes.json rendered into a slot. */
function refSlot(ctx, ref, opts) {
  const rec = ctx.data.resolveRef(ref);
  if (!rec) return invslot(ctx, null, opts);
  return invslot(ctx, rec.name, { ...opts, count: ref.count, title: rec.label, label: rec.label });
}

function craftingGrid(ctx, cells, output, count) {
  const rows = [];
  for (let r = 0; r < 3; r++) {
    const slots = [];
    for (let c = 0; c < 3; c++) slots.push(invslot(ctx, cells[r * 3 + c] || null));
    rows.push(`<span class="mcui-row">${slots.join('')}</span>`);
  }
  const out = typeof output === 'string'
    ? invslot(ctx, output, { large: true, count })
    : refSlot(ctx, output, { large: true });
  return (
    `<span class="mcui mcui-Crafting_Table pixel-image">` +
    `<span class="mcui-input">${rows.join('')}</span>` +
    `<span class="mcui-arrow" aria-hidden="true"></span>` +
    `<span class="mcui-output">${out}</span>` +
    `</span>`
  );
}

/** Expand a shaped recipe's pattern rows + key map into 9 cell names. */
function cellsFromPattern(ctx, pattern, keyMap) {
  const cells = new Array(9).fill(null);
  pattern.forEach((row, r) => {
    if (r > 2) return;
    [...row].forEach((ch, c) => {
      if (c > 2 || ch === ' ') return;
      const ref = keyMap[ch];
      if (!ref) return;
      const rec = typeof ref === 'string' ? { name: ref } : ctx.data.resolveRef(ref);
      if (rec) cells[r * 3 + c] = { name: rec.name, label: rec.label };
    });
  });
  return cells;
}

function recipeToGrid(ctx, recipe) {
  if (recipe.type === 'shaped') {
    return craftingGrid(ctx, cellsFromPattern(ctx, recipe.pattern, recipe.key), recipe.output);
  }
  if (recipe.type === 'shapeless') {
    const cells = new Array(9).fill(null);
    recipe.ingredients.slice(0, 9).forEach((ref, i) => {
      const rec = ctx.data.resolveRef(ref);
      if (rec) cells[i] = { name: rec.name, label: rec.label };
    });
    return craftingGrid(ctx, cells, recipe.output);
  }
  if (recipe.type === 'smelting') return smeltingGrid(ctx, recipe.input, recipe.output);
  return '';
}

function smeltingGrid(ctx, input, output) {
  const inSlot = typeof input === 'string'
    ? invslot(ctx, input) : refSlot(ctx, input, {});
  const outSlot = typeof output === 'string'
    ? invslot(ctx, output, { large: true }) : refSlot(ctx, output, { large: true });
  return (
    `<span class="mcui mcui-Furnace pixel-image">` +
    `<span class="mcui-input">${inSlot}` +
    `<span class="mcui-fuel-arrow" aria-hidden="true"></span>` +
    `${invslot(ctx, 'Coal', { title: 'Any fuel' })}</span>` +
    `<span class="mcui-arrow" aria-hidden="true"></span>` +
    `<span class="mcui-output">${outSlot}</span>` +
    `</span>`
  );
}

// ---------------------------------------------------------------------------
// Templates
// ---------------------------------------------------------------------------

define(['sprite', 'icon', 'item', 'block'], ({ args, named, ctx }) => {
  const name = args[0] || named.name;
  if (!name) return '';
  const link = named.link !== 'no' && named.link !== 'false';
  const text = named.text || (named.notext === 'yes' ? '' : name);
  const img = ctx.sprite(name, { link: false, title: name });
  const label = text ? `<span class="sprite-text">${escapeHtml(text)}</span>` : '';
  const body = `${img}${label ? ' ' + label : ''}`;
  return link ? ctx.linkWrap(name, body, 'sprite-link') : `<span class="sprite-link">${body}</span>`;
});

define(['slot', 'invslot'], ({ args, named, ctx }) =>
  invslot(ctx, args[0] || named.name, { count: named.count || args[1], large: named.large === 'yes' }));

define(['crafting', 'craft'], ({ args, named, ctx }) => {
  // Explicit grid: {{crafting|pattern=###/ X /###|#=Stone|X=Coal|output=...}}
  if (named.pattern || named.a1 || named.A1) {
    let cells;
    if (named.pattern) {
      const keyMap = {};
      for (const [k, v] of Object.entries(named)) {
        if (k.length === 1) keyMap[k] = v;
      }
      cells = cellsFromPattern(ctx, named.pattern.split('/'), keyMap);
    } else {
      cells = ['a1', 'b1', 'c1', 'a2', 'b2', 'c2', 'a3', 'b3', 'c3'].map(
        (k) => named[k] || named[k.toUpperCase()] || null);
    }
    return `<div class="mcui-wrapper">${craftingGrid(ctx, cells, named.output, named.count)}</div>`;
  }
  // Data-driven: every recipe that produces this thing.
  const subject = args[0] || named.for || ctx.subjectName();
  ctx.showedRecipes('crafting', subject);
  const recipes = ctx.data.recipesFor(subject).filter((r) => r.type !== 'smelting');
  if (!recipes.length) {
    ctx.warn(`{{crafting}}: no recipe produces "${subject}"`);
    return `<div class="mcui-wrapper mcui-empty">No crafting recipe produces ${escapeHtml(subject)}.</div>`;
  }
  return `<div class="mcui-wrapper">${recipes.map((r) => recipeToGrid(ctx, r)).join('')}</div>`;
});

define(['smelting', 'furnace'], ({ args, named, ctx }) => {
  if (named.input || named.output) {
    return `<div class="mcui-wrapper">${smeltingGrid(ctx, named.input, named.output)}</div>`;
  }
  const subject = args[0] || named.for || ctx.subjectName();
  ctx.showedRecipes('smelting', subject);
  const recipes = ctx.data.recipesFor(subject).filter((r) => r.type === 'smelting');
  if (!recipes.length) {
    ctx.warn(`{{smelting}}: nothing smelts into "${subject}"`);
    return `<div class="mcui-wrapper mcui-empty">Nothing smelts into ${escapeHtml(subject)}.</div>`;
  }
  return `<div class="mcui-wrapper">${recipes.map((r) => recipeToGrid(ctx, r)).join('')}</div>`;
});

define(['used-in', 'usedin', 'crafting-uses'], ({ args, named, ctx }) => {
  const subject = args[0] || named.for || ctx.subjectName();
  ctx.showedRecipes('used in', subject);
  const recipes = ctx.data.recipesUsing(subject);
  if (!recipes.length) {
    return `<div class="mcui-wrapper mcui-empty">${escapeHtml(subject)} is not used in any recipe.</div>`;
  }
  const rows = recipes.map((r) => {
    const out = ctx.data.resolveRef(r.output);
    const icon = out ? ctx.sprite(spriteName(ctx, out.name, out.label)) : '';
    return `<tr><td>${out ? ctx.linkWrap(out.name, `${icon} ${escapeHtml(out.label)}`) : '?'}</td>` +
      `<td>${recipeToGrid(ctx, r)}</td></tr>`;
  });
  return `<table class="wikitable recipe-uses"><thead><tr><th>Result</th><th>Recipe</th></tr></thead>` +
    `<tbody>${rows.join('')}</tbody></table>`;
});

define(['stub'], ({ named, ctx }) => {
  ctx.markStub();
  const what = named.type || 'article';
  return msgbox('stub', `This ${escapeHtml(what)} is a stub. You can help the wiki by expanding it.`);
});

define(['hatnote', 'about'], ({ args, ctx }) =>
  `<div class="hatnote navigation-not-searchable">${ctx.renderInline(args.join('|'))}</div>`);

define(['main'], ({ args, ctx }) => {
  const links = args.filter(Boolean).map((a) => ctx.linkWrap(a, escapeHtml(a)));
  return `<div class="hatnote navigation-not-searchable">Main article: ${links.join(', ')}</div>`;
});

define(['see-also', 'seealso'], ({ args, ctx }) => {
  const links = args.filter(Boolean).map((a) => ctx.linkWrap(a, escapeHtml(a)));
  return `<div class="hatnote navigation-not-searchable">See also: ${links.join(', ')}</div>`;
});

function msgbox(kind, html) {
  return `<div class="msgbox msgbox-${kind}"><div class="msgbox-text">${html}</div></div>`;
}

define(['msgbox', 'notice'], ({ args, named, ctx }) =>
  msgbox(named.type || 'notice', ctx.renderInline(args.join('|') || named.text || '')));

define(['exclusive', 'version'], ({ args, ctx }) =>
  `<sup class="version-note">[${escapeHtml(args[0] || ctx.config.version)}]</sup>`);

/** Inline "ID 4" style reference pulled from the extracted data. */
define(['id', 'dv'], ({ args, ctx }) => {
  const rec = ctx.data.lookup(args[0] || ctx.subjectName());
  if (!rec) return '<code>?</code>';
  return `<code>${rec.id != null ? rec.id : rec.networkId}</code>`;
});

/** A sortable table of a whole data set: {{list|blocks}} */
define(['list', 'datatable'], ({ args, named, ctx }) => {
  const which = (args[0] || named.of || 'blocks').toLowerCase();
  const rows = [];
  const head = [];
  if (which.startsWith('block')) {
    head.push('Icon', 'Name', 'ID', 'Hardness', 'Blast resistance', 'Light');
    for (const b of ctx.data.blocks) {
      if (!b.key) continue;
      rows.push([
        ctx.sprite(b.name),
        ctx.linkWrap(b.name, escapeHtml(b.name)),
        b.id,
        fmtNum(b.hardness),
        fmtNum(b.blastResistance),
        b.lightEmission || 0,
      ]);
    }
  } else if (which.startsWith('item')) {
    head.push('Icon', 'Name', 'ID');
    for (const i of ctx.data.items) {
      rows.push([ctx.sprite(i.name), ctx.linkWrap(i.name, escapeHtml(i.name)), i.id]);
    }
  } else if (which.startsWith('entit') || which.startsWith('mob')) {
    head.push('Name', 'Network ID', 'Class');
    for (const e of ctx.data.entities) {
      rows.push([ctx.linkWrap(e.name, escapeHtml(e.name)), e.networkId, `<code>${escapeHtml(e.class)}</code>`]);
    }
  } else {
    ctx.warn(`{{list}}: unknown data set "${which}"`);
    return '';
  }
  return `<table class="wikitable sortable data-list"><thead><tr>${
    head.map((h) => `<th>${h}</th>`).join('')}</tr></thead><tbody>${
    rows.map((r) => `<tr>${r.map((c) => `<td>${c == null ? '' : c}</td>`).join('')}</tr>`).join('')
  }</tbody></table>`;
});

const fmtNum = (n) => (n == null ? '&ndash;' : String(Math.round(n * 1000) / 1000));

/** Every page in a namespace or category, as a linked gallery. */
define(['pagelist', 'gallery'], ({ args, named, ctx }) => {
  const ns = named.namespace || args[0];
  const cat = named.category;
  const pages = ctx.allPages().filter((p) => {
    if (p.isIndex || p.isHome) return false;
    if (ns && p.namespace !== slug(ns)) return false;
    if (cat && !(p.fm.categories || []).some((c) => slug(c) === slug(cat))) return false;
    return true;
  });
  if (!pages.length) return '<p class="mcui-empty">No pages yet.</p>';
  const items = pages.map((p) => {
    const sp = ctx.data.sprite(p.fm.sprite || p.title) ? ctx.sprite(p.fm.sprite || p.title) : '';
    return `<li>${ctx.hrefWrap(p.url, `${sp}<span class="pagelist-name">${escapeHtml(p.title)}</span>`)}</li>`;
  });
  return `<ul class="pagelist">${items.join('')}</ul>`;
});

/** Every recipe in the game as one table: {{recipe list}} / {{recipe list|type=smelting}} */
define(['recipe-list', 'all-recipes'], ({ named, ctx }) => {
  const smelting = String(named.type || '').toLowerCase().startsWith('smelt');
  const list = smelting
    ? ctx.data.smelting.map((s) => ({ ...s, type: 'smelting' }))
    : ctx.data.recipes;
  if (!list.length) return '<p class="mcui-empty">No recipes.</p>';
  const rows = list
    .map((r) => ({ r, out: ctx.data.resolveRef(r.output) }))
    .filter((x) => x.out)
    .sort((a, b) => a.out.label.localeCompare(b.out.label))
    .map(({ r, out }) =>
      `<tr><td>${ctx.linkWrap(out.name,
        `${ctx.sprite(spriteName(ctx, out.name, out.label))} ${escapeHtml(out.label)}`)}</td>` +
      `<td>${r.output.count || 1}</td>` +
      `<td>${recipeToGrid(ctx, r)}</td></tr>`);
  return `<table class="wikitable recipe-list"><thead><tr><th>Result</th><th>Qty</th>` +
    `<th>Recipe</th></tr></thead><tbody>${rows.join('')}</tbody></table>`;
});

export { invslot, craftingGrid, smeltingGrid, recipeToGrid, msgbox };
