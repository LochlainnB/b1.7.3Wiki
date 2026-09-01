#!/usr/bin/env node
// Build content/*.md into a static wiki in site/.
//
//   node tools/build.mjs            build
//   node tools/build.mjs --check    validate only, write nothing
//   node tools/build.mjs --quiet    only report problems
import { mkdirSync, writeFileSync, readFileSync, readdirSync, rmSync, cpSync,
         existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

import { loadPages, buildIndex } from './lib/content.mjs';
import { loadData } from './lib/data.mjs';
import { createRenderer } from './lib/markdown.mjs';
import { renderDocument } from './lib/layout.mjs';
import { renderInfobox } from './lib/infobox.mjs';
import { escapeHtml } from './lib/templates.mjs';
import { slug, splitAnchor, anchorId, relative } from './lib/slug.mjs';
import { generatedPages } from './lib/indexes.mjs';
import { buildSearchIndex } from './lib/search.mjs';
import { report } from './lib/integrity.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

/** Every file under a directory, recursively. Missing directory yields none. */
function walkFiles(dir, out = []) {
  if (!existsSync(dir)) return out;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) walkFiles(full, out);
    else out.push(full);
  }
  return out;
}

/**
 * Per-page rendering context. Templates, the infobox and the layout all talk to
 * the wiki through this object rather than reaching into globals.
 */
function makeContext({ config, data, pages, index, problems, links }) {
  const ctx = {
    config,
    data,
    page: null,
    toc: [],
    buildTime: new Date().toISOString().replace('T', ' ').slice(0, 16),

    allPages: () => pages,
    anchor: anchorId,

    warn(message) {
      problems.push({ page: ctx.page?.relFile || '(build)', message, level: 'warn' });
    },
    error(message) {
      problems.push({ page: ctx.page?.relFile || '(build)', message, level: 'error' });
    },
    markStub() {
      if (ctx.page) ctx.page.isStub = true;
    },

    /** The thing this page is about, used by data-driven templates. */
    subjectName: () => ctx.page?.fm?.subject || ctx.page?.title || '',

    hrefFor(url) {
      if (/^(https?:|mailto:|#)/i.test(url)) return url;
      return relative(ctx.page ? ctx.page.url : '/', url);
    },

    /** Resolve a [[target]] to a page, recording the link for backlinks. */
    resolveLink(target) {
      const { page: name, anchor } = splitAnchor(target);
      const hit = index.get(slug(name));
      if (ctx.page && hit) {
        const set = links.get(ctx.page.url) || new Set();
        set.add(hit.page.url);
        links.set(ctx.page.url, set);
      }
      return { hit: hit ? hit.page : null, anchor };
    },

    linkWrap(target, innerHtml, extraClass = '') {
      const { hit, anchor } = ctx.resolveLink(target);
      const cls = [extraClass, hit ? '' : 'new'].filter(Boolean).join(' ');
      const clsAttr = cls ? ` class="${cls}"` : '';
      if (!hit) {
        ctx.warn(`broken link [[${target}]]`);
        return `<a href="${ctx.hrefFor('/wiki/missing/')}"${clsAttr} ` +
          `title="${escapeHtml(target)} (page does not exist)">${innerHtml}</a>`;
      }
      const frag = anchor ? `#${anchorId(anchor)}` : '';
      return `<a href="${ctx.hrefFor(hit.url)}${frag}"${clsAttr} title="${escapeHtml(hit.title)}">${innerHtml}</a>`;
    },

    hrefWrap(url, innerHtml, extraClass = '') {
      const clsAttr = extraClass ? ` class="${extraClass}"` : '';
      return `<a href="${ctx.hrefFor(url)}"${clsAttr}>${innerHtml}</a>`;
    },

    /** <img> for a named sprite, sized in CSS pixels. */
    sprite(name, { size = 32, link = false, title } = {}) {
      const sp = data.sprite(name);
      if (!sp) {
        ctx.warn(`no sprite for "${name}"`);
        return `<span class="sprite-file sprite-missing" title="${escapeHtml(name)}"></span>`;
      }
      const img =
        `<span class="sprite-file" style="height:${size}px;width:${size}px">` +
        `<img class="pixel-image" src="${ctx.hrefFor('/' + sp.file)}" ` +
        `width="${size}" height="${size}" loading="lazy" decoding="async" ` +
        `alt="${escapeHtml(title || name)}"></span>`;
      return link ? ctx.linkWrap(name, img) : img;
    },
  };
  return ctx;
}

function renderPage(page, ctx, renderer) {
  ctx.page = page;
  ctx.toc = [];
  page.isStub = Boolean(page.fm.stub);
  const contentHtml = page.generated ? page.render(ctx) : renderer.render(page.body);
  const infoboxHtml = page.generated ? '' : renderInfobox(page, ctx);
  return renderDocument({ page, contentHtml, infoboxHtml, toc: ctx.toc, ctx });
}

async function main() {
  const args = process.argv.slice(2);
  const checkOnly = args.includes('--check');
  const quiet = args.includes('--quiet');
  const t0 = Date.now();

  const config = (await import(pathToFileURL(join(ROOT, 'wiki.config.js')).href)).default;
  const data = loadData(ROOT);
  const problems = [];
  const links = new Map();

  const filePages = loadPages(ROOT, config);
  const pages = [...filePages, ...generatedPages(filePages, config, data, ROOT)];
  const index = buildIndex(pages);

  const ctx = makeContext({ config, data, pages, index, problems, links });
  const renderer = createRenderer(ctx);

  // Pass 1 populates the link graph so backlinks and orphan detection can see
  // the whole wiki; pass 2 is the one whose HTML we keep.
  for (const page of pages) renderPage(page, ctx, renderer);
  ctx.backlinks = new Map();
  for (const [from, targets] of links) {
    for (const to of targets) {
      if (!ctx.backlinks.has(to)) ctx.backlinks.set(to, new Set());
      ctx.backlinks.get(to).add(from);
    }
  }
  problems.length = 0;

  const outputs = [];
  for (const page of pages) outputs.push([page, renderPage(page, ctx, renderer)]);

  const stats = report({ pages, problems, links, backlinks: ctx.backlinks, quiet });

  if (!checkOnly) {
    const outDir = join(ROOT, config.outDir);
    // Write over the previous build and prune what is left behind, rather than
    // clearing the directory first: with `npm run dev` running, wiping would
    // 404 every page for the length of each rebuild.
    const written = new Set();
    const emit = (path, contents) => {
      mkdirSync(dirname(path), { recursive: true });
      writeFileSync(path, contents);
      written.add(resolve(path));
    };

    for (const [page, html] of outputs) emit(page.outPath, html);

    if (existsSync(join(ROOT, 'assets'))) {
      cpSync(join(ROOT, 'assets'), join(outDir, 'assets'), { recursive: true, force: true });
      for (const f of walkFiles(join(outDir, 'assets'))) written.add(resolve(f));
    }
    emit(join(outDir, 'assets', 'wiki.css'), readFileSync(join(ROOT, 'theme', 'wiki.css')));
    emit(join(outDir, 'assets', 'wiki.js'), readFileSync(join(ROOT, 'theme', 'wiki.js')));
    // Shipped as a script rather than JSON: fetch() is blocked on file://, so
    // this keeps search working when the site is opened straight off disk.
    emit(join(outDir, 'assets', 'search-index.js'),
      'window.__WIKI_SEARCH__=' + JSON.stringify(buildSearchIndex(pages, outputs)) + ';');

    for (const f of walkFiles(outDir)) {
      if (!written.has(resolve(f))) rmSync(f, { force: true });
    }
    if (!quiet) {
      console.log(`\nBuilt ${outputs.length} pages into ${config.outDir}/ in ${Date.now() - t0}ms`);
    }
  }

  if (stats.errors > 0) process.exitCode = 1;
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
