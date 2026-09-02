// Build-time integrity checks. LLM editors touch these files directly, so the
// build is the only thing standing between a typo and a silently broken wiki:
// it names the file, says what is wrong, and fails on anything structural.

import { slug } from './slug.mjs';

const REQUIRED = ['title'];
const KNOWN_KEYS = new Set([
  'title', 'description', 'type', 'subject', 'sprite', 'categories', 'aliases',
  'redirects', 'infobox', 'infoboxTitle', 'stub', 'toc', 'id', 'order',
]);

function checkFrontmatter(page, problems) {
  const at = page.relFile;
  if (!page.hasFrontmatter) {
    problems.push({ page: at, level: 'error', message: 'missing YAML frontmatter block' });
    return;
  }
  for (const key of REQUIRED) {
    if (!page.fm[key]) {
      problems.push({ page: at, level: 'error', message: `frontmatter is missing "${key}"` });
    }
  }
  for (const key of Object.keys(page.fm)) {
    if (!KNOWN_KEYS.has(key)) {
      problems.push({ page: at, level: 'warn', message: `unrecognised frontmatter key "${key}"` });
    }
  }
  const cats = page.fm.categories;
  if (cats !== undefined && !Array.isArray(cats)) {
    problems.push({ page: at, level: 'error', message: '"categories" must be a list' });
  }
  if (page.fm.stub !== undefined && typeof page.fm.stub !== 'boolean') {
    problems.push({ page: at, level: 'error', message: '"stub" must be true or false' });
  }
}

// The three data-driven recipe sections a subject page can carry, and how to
// ask the data whether each one has anything to say.
const RECIPE_SECTIONS = [
  {
    kind: 'crafting',
    template: (subject) => `{{crafting|${subject}}}`,
    find: (data, s) => data.recipesFor(s).filter((r) => r.type !== 'smelting'),
    describe: (n, s) => `${n} crafting recipe${n === 1 ? '' : 's'} for "${s}"`,
  },
  {
    kind: 'smelting',
    template: (subject) => `{{smelting|${subject}}}`,
    find: (data, s) => data.recipesFor(s).filter((r) => r.type === 'smelting'),
    describe: (n, s) => `${n} smelting recipe${n === 1 ? '' : 's'} for "${s}"`,
  },
  {
    kind: 'used in',
    template: (subject) => `{{used in|${subject}}}`,
    find: (data, s) => data.recipesUsing(s),
    describe: (n, s) => `${n} recipe${n === 1 ? '' : 's'} using "${s}"`,
  },
];

/**
 * Extracted data that no page shows.
 *
 * {{crafting}} already warns when a page asks for a recipe the data does not
 * have. Without the mirror image, a page that never asks looks perfectly
 * clean, which is how a batch of freshly extracted recipes can sit invisible
 * behind a green build. That gap is worse than a missing section: an editor
 * who trusts "0 errors" cannot tell "the game has no such recipe" from "the
 * page simply never displayed it", and the second one invites hand-typing
 * numbers the data already knows.
 *
 * `shown` records what the templates actually rendered rather than what the
 * markdown says, so aliases and {{crafting|for=X}} all count.
 */
function checkRecipeCoverage(pages, data, shown, problems) {
  if (!data) return;
  for (const page of pages) {
    if (page.generated) continue;
    const subject = page.fm.subject || page.title;
    const seen = shown.get(page.url);
    for (const section of RECIPE_SECTIONS) {
      const found = section.find(data, subject);
      if (!found.length) continue;
      if (seen && seen.has(`${section.kind}\u0000${slug(subject)}`)) continue;
      problems.push({
        page: page.relFile,
        level: 'warn',
        message: `data/ has ${section.describe(found.length, subject)} that this page ` +
          `never shows - add ${section.template(subject)}`,
      });
    }
  }
}

/**
 * Print the build report and return counts. Errors fail the build; warnings are
 * the editorial to-do list (red links, unwritten pages).
 */
export function report({ pages, problems, links, backlinks, data, shown, quiet }) {
  const all = problems.slice();
  for (const page of pages) {
    if (!page.generated) checkFrontmatter(page, all);
  }
  checkRecipeCoverage(pages, data, shown || new Map(), all);

  // Two pages sharing a title make [[links]] ambiguous: whichever loads first
  // wins and the other becomes unreachable by name.
  const byTitle = new Map();
  for (const p of pages) {
    const key = p.title.toLowerCase();
    if (!byTitle.has(key)) byTitle.set(key, []);
    byTitle.get(key).push(p);
  }
  for (const [, group] of byTitle) {
    if (group.length < 2) continue;
    all.push({
      page: group.map((p) => p.relFile).join(' + '),
      level: 'error',
      message: `duplicate page title "${group[0].title}" - [[links]] to it are ambiguous`,
    });
  }

  // Orphans: real pages nothing links to. Index and generated pages are
  // reachable through navigation, so they do not count.
  const orphans = pages.filter((p) =>
    !p.generated && !p.isHome && !p.isIndex && !(backlinks.get(p.url)?.size));

  const errors = all.filter((p) => p.level === 'error');
  const warns = all.filter((p) => p.level === 'warn');

  // Collapse repeats: one broken link repeated on 40 pages is one problem.
  const group = (list) => {
    const m = new Map();
    for (const p of list) {
      const k = p.message;
      if (!m.has(k)) m.set(k, []);
      m.get(k).push(p.page);
    }
    return [...m.entries()].sort((a, b) => b[1].length - a[1].length);
  };

  if (errors.length) {
    console.error(`\n${errors.length} error${errors.length === 1 ? '' : 's'}:`);
    for (const [msg, where] of group(errors)) {
      console.error(`  ${msg}`);
      for (const w of where.slice(0, 5)) console.error(`      ${w}`);
      if (where.length > 5) console.error(`      ...and ${where.length - 5} more`);
    }
  }

  if (!quiet && warns.length) {
    const grouped = group(warns);
    console.warn(`\n${warns.length} warning${warns.length === 1 ? '' : 's'} ` +
      `(${grouped.length} distinct):`);
    for (const [msg, where] of grouped.slice(0, 25)) {
      console.warn(`  ${msg}  (${where.length}x, e.g. ${where[0]})`);
    }
    if (grouped.length > 25) console.warn(`  ...and ${grouped.length - 25} more kinds`);
  }

  if (!quiet) {
    const stubs = pages.filter((p) => p.fm.stub).length;
    console.log(`\n${pages.length} pages | ${stubs} stubs | ${orphans.length} orphans | ` +
      `${errors.length} errors | ${warns.length} warnings`);
    if (orphans.length && orphans.length <= 20) {
      console.log(`  orphans: ${orphans.map((o) => o.url).join(', ')}`);
    }
  }

  return { errors: errors.length, warnings: warns.length, orphans: orphans.length };
}
