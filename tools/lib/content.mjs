// Loading content/*.md into page records: frontmatter, body, and the URL and
// namespace implied by the file's location.
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative as relPath, sep } from 'node:path';
import yaml from 'js-yaml';
import { slug, titleize } from './slug.mjs';

const FRONTMATTER = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/;

/**
 * Split "---\n...\n---\nbody" into { data, body }.
 *
 * `bodyLine` is the file line the body starts on, so a problem found by
 * scanning the body can be reported at the line an editor will actually find
 * it on rather than one offset by however long the frontmatter ran.
 */
export function parseFrontmatter(raw, file) {
  const m = raw.match(FRONTMATTER);
  if (!m) return { data: {}, body: raw, hasFrontmatter: false, bodyLine: 1 };
  let data;
  try {
    data = yaml.load(m[1]) || {};
  } catch (err) {
    throw new Error(`${file}: invalid YAML frontmatter - ${err.message}`);
  }
  if (typeof data !== 'object' || Array.isArray(data)) {
    throw new Error(`${file}: frontmatter must be a mapping`);
  }
  return {
    data,
    body: raw.slice(m[0].length),
    hasFrontmatter: true,
    bodyLine: (m[0].match(/\n/g) || []).length + 1,
  };
}

function walk(dir, out = []) {
  for (const name of readdirSync(dir).sort()) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) walk(full, out);
    else if (name.endsWith('.md')) out.push(full);
  }
  return out;
}

/**
 * Read every page under contentDir.
 *
 * content/Main_Page.md      -> url "/",              namespace null
 * content/block/stone.md    -> url "/block/stone/",  namespace "block"
 * content/block/index.md    -> url "/block/",        namespace "block"
 */
export function loadPages(root, config) {
  const contentDir = join(root, config.contentDir);
  const files = walk(contentDir);
  const pages = [];

  for (const file of files) {
    const rel = relPath(contentDir, file).split(sep);
    const base = rel[rel.length - 1].replace(/\.md$/, '');
    const dirs = rel.slice(0, -1);
    const raw = readFileSync(file, 'utf8');
    const { data, body, hasFrontmatter, bodyLine } = parseFrontmatter(raw, relPath(root, file));

    const isHome = dirs.length === 0 && /^(main[_ ]page|index|home)$/i.test(base);
    const isIndex = base === 'index';
    const segments = isHome ? [] : isIndex ? dirs : [...dirs, slug(base)];
    const url = '/' + segments.map(slug).filter(Boolean).join('/') + (segments.length ? '/' : '');

    pages.push({
      file,
      relFile: relPath(root, file).split(sep).join('/'),
      slug: segments.length ? slug(segments[segments.length - 1]) : 'main-page',
      url,
      namespace: dirs.length ? dirs[0] : null,
      isHome,
      isIndex,
      title: data.title || titleize(base),
      body,
      bodyLine,
      fm: data,
      hasFrontmatter,
      outPath: join(root, config.outDir, ...segments, 'index.html'),
    });
  }

  return pages;
}

/**
 * What a page is about, in `data/`'s terms: [{ label, name }, ...].
 *
 * Normally one thing, named by `subject` or by the title. A page may name
 * several, because Beta gives one name to ids that are not one thing -- both
 * mushrooms are `tile.mushroom`, both furnaces are `tile.furnace` -- and an
 * article about the pair wants the facts of both:
 *
 *     subject: {Brown: Brown Mushroom, Red: Red Mushroom}   labelled columns
 *     subject: [Brown Mushroom, Red Mushroom]               labelled by name
 *
 * The label is what the infobox writes above a column, so it is the short
 * half of the name: a reader already knows which article they are on.
 */
export function subjectsOf(page) {
  const subject = (page.fm || {}).subject;
  if (!subject) return [{ label: page.title, name: page.title }];
  if (typeof subject === 'string') return [{ label: page.title, name: subject }];
  const pairs = Array.isArray(subject)
    ? subject.map((name) => [name, name])
    : Object.entries(subject);
  return pairs.map(([label, name]) => ({ label: String(label), name: String(name) }));
}

/**
 * Build the lookup used to resolve [[wiki links]]: every page is addressable by
 * its title, its slug, and any aliases it declares.
 *
 * Given `data`, a page also answers to the subtype names of the id it covers:
 * [[Charcoal]] reaches Coal and [[Magenta Wool]] reaches Wool without either
 * page listing them. A subtype with a page of its own, like Fern, keeps it,
 * because titles and aliases claim their names first.
 */
export function buildIndex(pages, data) {
  const byKey = new Map();
  const add = (key, page, kind) => {
    const k = slug(key);
    if (!k) return;
    if (!byKey.has(k)) byKey.set(k, { page, kind });
  };
  for (const p of pages) {
    add(p.title, p, 'title');
    add(p.slug, p, 'slug');
  }
  // Aliases are added after titles so a real page always wins a name clash.
  for (const p of pages) {
    for (const a of p.fm.aliases || p.fm.redirects || []) add(a, p, 'alias');
  }
  for (const rec of data ? [...data.blocks, ...data.items] : []) {
    const owner = byKey.get(slug(rec.name));
    if (!owner) continue;
    for (const name of Object.values(rec.variants || {})) add(name, owner.page, 'variant');
  }
  return byKey;
}
