// Loading content/*.md into page records: frontmatter, body, and the URL and
// namespace implied by the file's location.
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative as relPath, sep } from 'node:path';
import yaml from 'js-yaml';
import { slug, titleize } from './slug.mjs';

const FRONTMATTER = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/;

/** Split "---\n...\n---\nbody" into { data, body }. */
export function parseFrontmatter(raw, file) {
  const m = raw.match(FRONTMATTER);
  if (!m) return { data: {}, body: raw, hasFrontmatter: false };
  let data;
  try {
    data = yaml.load(m[1]) || {};
  } catch (err) {
    throw new Error(`${file}: invalid YAML frontmatter - ${err.message}`);
  }
  if (typeof data !== 'object' || Array.isArray(data)) {
    throw new Error(`${file}: frontmatter must be a mapping`);
  }
  return { data, body: raw.slice(m[0].length), hasFrontmatter: true };
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
    const { data, body, hasFrontmatter } = parseFrontmatter(raw, relPath(root, file));

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
      fm: data,
      hasFrontmatter,
      outPath: join(root, config.outDir, ...segments, 'index.html'),
    });
  }

  return pages;
}

/**
 * Build the lookup used to resolve [[wiki links]]: every page is addressable by
 * its title, its slug, and any aliases it declares.
 */
export function buildIndex(pages) {
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
  return byKey;
}
