// Build-time integrity checks. LLM editors touch these files directly, so the
// build is the only thing standing between a typo and a silently broken wiki:
// it names the file, says what is wrong, and fails on anything structural.

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

/**
 * Print the build report and return counts. Errors fail the build; warnings are
 * the editorial to-do list (red links, unwritten pages).
 */
export function report({ pages, problems, links, backlinks, quiet }) {
  const all = problems.slice();
  for (const page of pages) {
    if (!page.generated) checkFrontmatter(page, all);
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
