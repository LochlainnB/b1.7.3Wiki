// The infobox builds itself from data/*.json, so a page states hardness, blast
// resistance, stack size, durability, attack damage, healing, a mob's health
// and the id without an editor retyping (or mistyping) them.
// Anything in the page's `infobox:` frontmatter overrides or extends the
// generated rows.
import { subjectsOf, spritesOf } from './content.mjs';
import { escapeHtml } from './templates.mjs';

const fmt = (n) => (n == null ? null : String(Math.round(n * 1000) / 1000));

/** A stack size the way minecraft.wiki words it: "Yes (64)", "Yes (16)", "No". */
const stackable = (n) => (n == null ? null : n > 1 ? `Yes (${n})` : 'No');

/**
 * How many of a block fit in one slot. A block that shares its name with an
 * item -- a sign, a door, a bed, a cake, a repeater -- is placed from that
 * item, which is the thing a player carries and the picture the page shows,
 * so its stack size is the item's. Every other block is carried as its own
 * item form, which every block id has.
 */
function blockStackSize(rec, ctx) {
  const item = ctx.data.items.find((i) => i.name === rec.name);
  return (item || rec).stackSize;
}

/** Rows derived from the extracted game data for this page's subject. */
function autoRows(rec, ctx) {
  if (!rec) return [];
  const rows = [];
  const push = (label, value) => {
    if (value != null) rows.push([label, String(value)]);
  };
  if (rec.kind === 'block') {
    push('Stackable', stackable(blockStackSize(rec, ctx)));
    if (rec.hardness != null) {
      rows.push(['Hardness', rec.hardness < 0 ? 'Unbreakable' : fmt(rec.hardness)]);
    }
    if (rec.blastResistance != null) {
      rows.push(['Blast resistance', fmt(rec.blastResistance)]);
    }
    rows.push(['Luminous', rec.lightEmission ? `Yes (${rec.lightEmission})` : 'No']);
    if (rec.lightOpacity != null) {
      rows.push(['Opacity', rec.lightOpacity === 0 ? 'Transparent'
        : rec.lightOpacity >= 255 ? 'Opaque' : `Filters light (${rec.lightOpacity})`]);
    }
    rows.push(['Block ID', `<code>${rec.id}</code>`]);
    if (rec.damage) rows.push(['Metadata', `<code>${rec.damage}</code>`]);
  } else if (rec.kind === 'item') {
    push('Stackable', stackable(rec.stackSize));
    push('Durability', rec.durability);
    push('Attack damage', rec.attackDamage);
    push('Heals', rec.heal);
    rows.push(['Item ID', `<code>${rec.id}</code>`]);
    if (rec.damage) rows.push(['Damage value', `<code>${rec.damage}</code>`]);
  } else if (rec.kind === 'entity') {
    push('Health', rec.health);
    rows.push(['Entity ID', `<code>${rec.networkId}</code>`]);
  }
  return rows;
}

/**
 * Merge one column of generated rows per subject into rows of several values.
 *
 * Columns agree far more often than they differ -- both mushrooms are equally
 * soft, both furnaces equally hard -- so a row whose values all match collapses
 * back to one cell and the box reads as a single infobox with two exceptions,
 * rather than a comparison table nobody asked for.
 */
function mergeColumns(columns, ctx) {
  const perColumn = columns.map((c) => new Map(autoRows(c.rec, ctx)));
  const keys = [];
  for (const rows of perColumn) {
    for (const key of rows.keys()) if (!keys.includes(key)) keys.push(key);
  }
  return keys.map((key) => [key, perColumn.map((rows) => rows.get(key) ?? '')]);
}

/**
 * Render the page's infobox, or '' when the page neither declares one nor
 * matches a known block/item/entity.
 *
 * `subject` may name more than one thing; see subjectsOf(). Each becomes a
 * column, and a custom `infobox:` row still overrides all of them at once,
 * since a value written by hand is a statement about the page as a whole.
 */
export function renderInfobox(page, ctx) {
  const fm = page.fm || {};
  if (fm.infobox === false || fm.infobox === 'none') return '';

  const subjects = subjectsOf(page);
  const columns = subjects
    .map((s) => ({ ...s, rec: ctx.data.lookup(s.name) }))
    .filter((c) => c.rec);
  const multi = columns.length > 1;
  const custom = (fm.infobox && typeof fm.infobox === 'object' && !Array.isArray(fm.infobox))
    ? fm.infobox : {};
  const auto = columns.length ? mergeColumns(columns, ctx) : [];
  if (!auto.length && !Object.keys(custom).length) return '';

  // Custom values replace generated ones of the same name; the rest append,
  // keeping the generated order stable across pages.
  const seen = new Set();
  const rows = [];
  for (const [k, values] of auto) {
    const override = Object.keys(custom).find((c) => c.toLowerCase() === k.toLowerCase());
    if (override !== undefined) {
      rows.push([k, [String(custom[override])]]);
      seen.add(override);
    } else {
      rows.push([k, values]);
    }
  }
  for (const [k, v] of Object.entries(custom)) {
    if (!seen.has(k)) rows.push([k, [String(v)]]);
  }

  const image = imageArea(page, columns, ctx);

  const cells = (values) => {
    const span = values.length < columns.length || values.every((v) => v === values[0]);
    if (span) {
      const wide = multi ? ` colspan="${columns.length}"` : '';
      return `<td${wide}>${ctx.renderInline(String(values[0]))}</td>`;
    }
    return values.map((v) => `<td>${ctx.renderInline(String(v))}</td>`).join('');
  };
  const head = multi
    ? `<thead><tr><td></td>${columns
      .map((c) => `<th scope="col">${escapeHtml(c.label)}</th>`).join('')}</tr></thead>`
    : '';
  const body = rows
    .map(([k, values]) => `<tr><th scope="row">${escapeHtml(k)}</th>${cells(values)}</tr>`)
    .join('');

  return (
    `<div class="infobox notaninfobox">` +
    `<div class="mcwiki-header infobox-title">${escapeHtml(fm.infoboxTitle || page.title)}</div>` +
    image +
    `<table class="infobox-rows${multi ? ' infobox-multi' : ''}">${head}` +
    `<tbody>${body}</tbody></table>` +
    `</div>`
  );
}

/**
 * The picture above the rows: one sprite, or several, each with its label.
 *
 * A `sprite:` map names the pictures outright; otherwise a page with several
 * subjects gets one per column. Two sprites have to share the width one had,
 * so they shrink. A single `sprite:` still overrides the one picture, where a
 * page may want a subtype's icon rather than its id's.
 */
function imageArea(page, columns, ctx) {
  const asked = spritesOf(page);
  // A name like "block 83" is no description of a picture, so a named one is
  // described by the page and its label instead.
  const shown = asked.length > 1
    ? asked.map((s) => ({ ...s, alt: `${page.title} (${s.label})` }))
    : columnPictures(columns, ctx);
  if (shown.length < 2) {
    const only = (asked[0] || {}).name || (shown[0] || {}).name || page.title;
    return ctx.data.sprite(only)
      ? `<div class="infobox-imagearea">${ctx.sprite(only, { size: 128, link: false })}</div>`
      : '';
  }
  const size = Math.max(48, Math.floor(224 / shown.length));
  const cells = shown.map((s) =>
    `<span class="infobox-image">${ctx.sprite(s.name, { size, link: false, title: s.alt })}` +
    `<span class="infobox-image-label">${escapeHtml(s.label)}</span></span>`);
  return `<div class="infobox-imagearea infobox-imagearea-multi">${cells.join('')}</div>`;
}

/**
 * One picture per column, as [{ name, label }, ...].
 *
 * Sprites are drawn per name, and two columns may share one: a lit furnace and
 * an unlit one are both Furnace, and labelling one picture twice would promise
 * a difference the wiki cannot show. Distinct pictures get labels; one picture
 * stands alone at full size, as on any other page.
 */
function columnPictures(columns, ctx) {
  const shown = [];
  for (const column of columns) {
    // A subtype draws its own icon where it has one: Fern is not Tall Grass.
    const { label, name: idName } = column.rec;
    const name = label && ctx.data.sprite(label) ? label : idName;
    if (ctx.data.sprite(name) && !shown.some((s) => s.name === name)) {
      shown.push({ name, label: column.label });
    }
  }
  return shown;
}
