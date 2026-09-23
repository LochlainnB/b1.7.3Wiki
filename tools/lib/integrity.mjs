// Build-time integrity checks. LLM editors touch these files directly, so the
// build is the only thing standing between a typo and a silently broken wiki:
// it names the file, says what is wrong, and fails on anything structural.

import { subjectsOf } from './content.mjs';
import { slug } from './slug.mjs';

const REQUIRED = ['title'];
const KNOWN_KEYS = new Set([
  'title', 'description', 'type', 'subject', 'sprite', 'categories', 'aliases',
  'redirects', 'infobox', 'infoboxTitle', 'stub', 'toc', 'id', 'order',
]);

function checkFrontmatter(page, problems, config) {
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
  // Agents invent categories freely, and each invention is a near-duplicate of
  // one that exists. The list in wiki.config.js is the whole vocabulary.
  if (Array.isArray(cats) && config?.categories) {
    for (const c of cats) {
      if (!Object.hasOwn(config.categories, c)) {
        problems.push({
          page: at, level: 'error',
          message: `unknown category "${c}" - use one from \`categories\` in wiki.config.js, or add it there`,
        });
      }
    }
  }
  if (page.fm.stub !== undefined && typeof page.fm.stub !== 'boolean') {
    problems.push({ page: at, level: 'error', message: '"stub" must be true or false' });
  }
}

/**
 * Pipes inside [[links]] and {{templates}} that sit in a table row.
 *
 * A table row is split into cells on every unescaped "|", and that split
 * happens in the block parser, long before the inline rules that understand
 * [[ ]] and {{ }} ever run. So "[[Water|water]]" written the ordinary way in a
 * table is torn in half: the cell holds a bare "[[Water", the "water]]" half
 * becomes a surplus cell the row's column count silently drops, and the reader
 * gets literal "[[Water" where a link belonged.
 *
 * Nothing downstream can see this. linkWrap is never called, so the page is not
 * even credited with a link, and the broken-link warning that would normally
 * catch a bad target never fires. It is a structural break that renders wrong
 * and reports clean, which is exactly the kind of thing this build exists to
 * refuse. Escape the pipe as "\|" and both halves survive the split.
 */
function checkTablePipes(page, problems) {
  const unescapedPipe = /(?:^|[^\\])\|/;
  let fenced = false;
  const lines = page.body.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/^\s*(?:```|~~~)/.test(line)) { fenced = !fenced; continue; }
    if (fenced || !/^\s*\|/.test(line)) continue;
    for (const m of line.matchAll(/\[\[(.*?)\]\]|\{\{(.*?)\}\}/g)) {
      const inner = m[1] ?? m[2];
      if (!unescapedPipe.test(inner)) continue;
      const wiki = m[1] !== undefined;
      problems.push({
        page: page.relFile,
        level: 'error',
        message: `line ${(page.bodyLine || 1) + i}: ${wiki ? '[[' : '{{'}${inner}${wiki ? ']]' : '}}'} `
          + 'has an unescaped "|" inside a table row, so the row splits through '
          + 'the middle of it - write it as "\\|"',
      });
    }
  }
}

/**
 * Seeded text left on a page that says it is written.
 *
 * tools/seed.mjs and `npm run new` give a stub a description and a lead that
 * name the page and the version and nothing else, a {{stub}} banner, and a
 * comment where each section's prose belongs. That is right on a stub. Once
 * `stub: true` comes off, the page counts as written and all of it publishes as
 * content: "Chicken in Minecraft Beta 1.7.3." as the search-result text, a
 * banner calling a finished page a stub, a heading with nothing under it. An
 * agent that rewrites every section but the lead leaves exactly this behind,
 * and nothing else would notice.
 *
 * The version test is wider than the generators' exact wording on purpose.
 * Every page on this wiki is Beta 1.7.3, so a lead or description that says so
 * is saying nothing, whoever wrote it. Pages about the wiki itself are exempt:
 * there the version is the subject.
 */
function checkPlaceholders(page, problems, config) {
  if (page.fm.stub || page.isHome || page.namespace === 'wiki') return;
  const at = page.relFile;
  const version = `Minecraft ${config?.version ?? 'Beta 1.7.3'}`;
  const flag = (line, message) => problems.push({
    page: at, level: 'error', message: `${line ? `line ${line}: ` : ''}${message}`,
  });

  const desc = String(page.fm.description ?? '');
  if (desc.includes(version)) {
    flag(0, `the description "${desc}" is the stub's placeholder - say in one sentence what the subject is`);
  }

  // `lines` blanks code blocks, so a "#" or a "{{stub}}" shown as an example is
  // not read as the real thing; blanked rather than dropped, so line numbers
  // still match. A code block is still content, so emptiness reads `raw`.
  const raw = page.body.split(/\r?\n/);
  let fenced = false;
  const lines = raw.map((line) => {
    const fence = /^\s*(?:```|~~~)/.test(line);
    if (fence) fenced = !fenced;
    return fence || fenced ? '' : line;
  });
  const lineNo = (i) => (page.bodyLine || 1) + i;
  const prose = (text) => /\S/.test(text.replace(/<!--[\s\S]*?-->/g, ''));

  if (/\{\{\s*stub\s*[|}]/i.test(lines.join('\n'))) {
    flag(0, 'the page is not marked `stub: true` but still shows {{stub}} - remove the banner');
  }

  const headings = [];
  lines.forEach((line, i) => {
    const m = /^(#{1,6})\s+(.*?)\s*#*\s*$/.exec(line);
    if (m) headings.push({ i, level: m[1].length, text: m[2] });
  });

  // The lead: the first paragraph before any heading that is neither a
  // template on a line of its own (a hatnote, the stub banner) nor a comment.
  const firstHeading = headings.length ? headings[0].i : lines.length;
  const paragraphs = lines.slice(0, firstHeading).join('\n')
    .replace(/<!--[\s\S]*?-->/g, '')
    .split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean);
  const lead = paragraphs.find((p) => !/^\{\{[\s\S]*\}\}$/.test(p));
  if (lead && (lead.includes(version) || /^\*\*[^*]+\*\*$/.test(lead))) {
    flag(0, `the lead "${lead.split('\n')[0]}" is the stub's placeholder - define the subject in one sentence`);
  }

  // A section is empty when nothing but blank lines and comments sits between
  // its heading and the next one. A section whose next heading is deeper has a
  // subsection, which counts as content; that subsection is judged on its own.
  headings.forEach((h, n) => {
    const next = headings[n + 1];
    if (next && next.level > h.level) return;
    if (!prose(raw.slice(h.i + 1, next ? next.i : raw.length).join('\n'))) {
      flag(lineNo(h.i), `section "${h.text}" is empty - write it or delete the heading`);
    }
  });
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
 *
 * A page covering several subjects is asked about each of them, but only for
 * what its earlier subjects did not already account for: the two stew recipes
 * belong to the brown mushroom and the red one alike, and showing them once is
 * showing them.
 */
function checkRecipeCoverage(pages, data, shown, problems) {
  if (!data) return;
  for (const page of pages) {
    if (page.generated) continue;
    const seen = shown.get(page.url);
    const accounted = new Set();
    for (const subject of subjectsOf(page)) {
      // A subject may point at an id rather than a name; recipes are indexed
      // by name, so ask the data what this one is called.
      const name = data.nameOf(subject.name);
      for (const section of RECIPE_SECTIONS) {
        const found = section.find(data, name);
        const fresh = found.filter((r) => !accounted.has(r));
        for (const r of found) accounted.add(r);
        if (!fresh.length) continue;
        if (seen && seen.has(`${section.kind}\u0000${slug(name)}`)) continue;
        problems.push({
          page: page.relFile,
          level: 'warn',
          message: `data/ has ${section.describe(found.length, name)} that this page ` +
            `never shows - add ${section.template(name)}`,
        });
      }
    }
  }
}

/**
 * Print the build report and return counts. Errors fail the build; warnings are
 * the editorial to-do list (red links, unwritten pages).
 */
export function report({ pages, problems, links, backlinks, data, shown, quiet, config }) {
  const all = problems.slice();
  for (const page of pages) {
    if (page.generated) continue;
    checkFrontmatter(page, all, config);
    checkTablePipes(page, all);
    checkPlaceholders(page, all, config);
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
