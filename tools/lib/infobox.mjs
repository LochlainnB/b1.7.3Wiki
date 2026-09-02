// The infobox builds itself from data/*.json, so a block page states hardness,
// blast resistance and id without an editor retyping (or mistyping) them.
// Anything in the page's `infobox:` frontmatter overrides or extends the
// generated rows.
import { escapeHtml } from './templates.mjs';

const fmt = (n) => (n == null ? null : String(Math.round(n * 1000) / 1000));

/** Rows derived from the extracted game data for this page's subject. */
function autoRows(rec, ctx) {
  if (!rec) return [];
  const rows = [];
  if (rec.kind === 'block') {
    rows.push(['Stackable', 'Yes (64)']);
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
    rows.push(['Item ID', `<code>${rec.id}</code>`]);
    if (rec.damage) rows.push(['Damage value', `<code>${rec.damage}</code>`]);
  } else if (rec.kind === 'entity') {
    rows.push(['Entity ID', `<code>${rec.networkId}</code>`]);
  }
  return rows;
}

/**
 * Render the page's infobox, or '' when the page neither declares one nor
 * matches a known block/item/entity.
 */
export function renderInfobox(page, ctx) {
  const fm = page.fm || {};
  if (fm.infobox === false || fm.infobox === 'none') return '';

  const subject = fm.subject || page.title;
  const rec = ctx.data.lookup(subject);
  const custom = (fm.infobox && typeof fm.infobox === 'object' && !Array.isArray(fm.infobox))
    ? fm.infobox : {};
  const auto = autoRows(rec, ctx);
  if (!auto.length && !Object.keys(custom).length) return '';

  // Custom values replace generated ones of the same name; the rest append,
  // keeping the generated order stable across pages.
  const seen = new Set();
  const rows = [];
  for (const [k, v] of auto) {
    const override = Object.keys(custom).find((c) => c.toLowerCase() === k.toLowerCase());
    if (override !== undefined) {
      rows.push([k, String(custom[override])]);
      seen.add(override);
    } else {
      rows.push([k, v]);
    }
  }
  for (const [k, v] of Object.entries(custom)) {
    if (!seen.has(k)) rows.push([k, String(v)]);
  }

  const spriteName = fm.sprite || subject;
  const image = ctx.data.sprite(spriteName)
    ? `<div class="infobox-imagearea">${ctx.sprite(spriteName, { size: 128, link: false })}</div>`
    : '';

  const body = rows
    .map(([k, v]) => `<tr><th>${escapeHtml(k)}</th><td>${ctx.renderInline(String(v))}</td></tr>`)
    .join('');

  return (
    `<div class="infobox notaninfobox">` +
    `<div class="mcwiki-header infobox-title">${escapeHtml(fm.infoboxTitle || page.title)}</div>` +
    image +
    `<table class="infobox-rows"><tbody>${body}</tbody></table>` +
    `</div>`
  );
}
