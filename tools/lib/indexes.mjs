// Pages the wiki maintains for itself: namespace indexes, all-pages, category
// listings, the search results page, stub tracking and the sprite reference.
// They go through the same layout as hand-written pages, so they never drift
// from the site's chrome.
import { join } from 'node:path';
import { statSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { iconOf } from './content.mjs';
import { escapeHtml } from './templates.mjs';
import { slug, anchorId } from './slug.mjs';

function virtual({ url, title, render, root, config, namespace = null, fm = {} }) {
  const segments = url.replace(/^\/+|\/+$/g, '').split('/').filter(Boolean);
  return {
    generated: true,
    url,
    slug: segments.length ? segments[segments.length - 1] : 'main-page',
    namespace,
    title,
    fm: { toc: false, ...fm },
    body: '',
    isHome: false,
    isIndex: true,
    file: '(generated)',
    relFile: '(generated)',
    render,
    outPath: join(root, config.outDir, ...segments, 'index.html'),
  };
}

/**
 * When each page last changed, in ms: its last commit, or its file's mtime when
 * it has uncommitted edits or is not in git at all. The mtime alone is useless
 * on a fresh checkout, which stamps every file with the moment it was cloned.
 */
function lastChanged(pages, root, contentDir) {
  const git = (...args) => {
    try {
      return execFileSync('git', ['-c', 'core.quotepath=off', ...args], {
        cwd: root, encoding: 'utf8', maxBuffer: 64 << 20, stdio: ['ignore', 'pipe', 'ignore'],
      });
    } catch { return ''; }
  };
  // Newest commit first, so a path's first appearance is its latest change.
  const committed = new Map();
  let time = 0;
  for (const line of git('log', '--relative', '--name-only', '--format=%x01%ct', '--', contentDir).split('\n')) {
    if (line.startsWith('\x01')) time = Number(line.slice(1)) * 1000;
    else if (line && !committed.has(line)) committed.set(line, time);
  }
  const edited = new Set(git('diff', '--relative', '--name-only', 'HEAD', '--', contentDir).split('\n'));
  return pages.map((p) => {
    if (committed.has(p.relFile) && !edited.has(p.relFile)) return { p, time: committed.get(p.relFile) };
    try { return { p, time: statSync(p.file).mtimeMs }; } catch { return { p, time: 0 }; }
  });
}

/** Alphabetical, sprite-led list of pages. */
function pageGrid(pages, ctx) {
  if (!pages.length) return '<p class="mcui-empty">No pages here yet.</p>';
  const items = pages
    .slice()
    .sort((a, b) => a.title.localeCompare(b.title))
    .map((p) => {
      const name = iconOf(p, ctx.data);
      const sp = ctx.data.sprite(name) ? ctx.sprite(name, { size: 32 }) : '<span class="sprite-file"></span>';
      const stub = p.fm.stub ? ' <span class="stub-flag" title="This page is a stub">stub</span>' : '';
      return `<li>${ctx.hrefWrap(p.url, `${sp}<span class="pagelist-name">${escapeHtml(p.title)}</span>`)}${stub}</li>`;
    });
  return `<ul class="pagelist">${items.join('')}</ul>`;
}

const contentPages = (pages) => pages.filter((p) => !p.generated && !p.isHome && !p.isIndex);

export function generatedPages(filePages, config, data, root) {
  const out = [];
  const has = (url) => filePages.some((p) => p.url === url);

  // ---- one index per namespace ---------------------------------------------
  for (const [ns, meta] of Object.entries(config.namespaces)) {
    const url = `/${ns}/`;
    if (has(url)) continue;
    out.push(virtual({
      root, config, url, namespace: ns, title: meta.index || meta.plural,
      render: (ctx) => {
        const mine = contentPages(ctx.allPages()).filter((p) => p.namespace === ns);
        return `<p>${mine.length} page${mine.length === 1 ? '' : 's'} in ${
          escapeHtml(meta.plural.toLowerCase())}.</p>` + pageGrid(mine, ctx);
      },
    }));
  }

  // ---- all pages ------------------------------------------------------------
  out.push(virtual({
    root, config, url: '/wiki/all-pages/', namespace: 'wiki', title: 'All pages',
    render: (ctx) => {
      const all = contentPages(ctx.allPages()).slice().sort((a, b) => a.title.localeCompare(b.title));
      const groups = new Map();
      for (const p of all) {
        const letter = /^[a-z]/i.test(p.title) ? p.title[0].toUpperCase() : '#';
        if (!groups.has(letter)) groups.set(letter, []);
        groups.get(letter).push(p);
      }
      const nav = [...groups.keys()].map((l) => `<a href="#letter-${l === '#' ? 'other' : l}">${l}</a>`).join(' ');
      const body = [...groups.entries()].map(([letter, ps]) =>
        `<h2><span class="mw-headline" id="letter-${letter === '#' ? 'other' : letter}">${letter}</span></h2>` +
        pageGrid(ps, ctx)).join('');
      return `<p>${all.length} pages.</p><div class="alpha-nav">${nav}</div>${body}`;
    },
  }));

  // ---- categories -----------------------------------------------------------
  out.push(virtual({
    root, config, url: '/wiki/categories/', namespace: 'wiki', title: 'Categories',
    render: (ctx) => {
      const cats = new Map();
      for (const p of contentPages(ctx.allPages())) {
        for (const c of p.fm.categories || []) {
          if (!cats.has(c)) cats.set(c, []);
          cats.get(c).push(p);
        }
      }
      if (!cats.size) return '<p class="mcui-empty">No categories yet.</p>';
      return [...cats.entries()]
        .sort((a, b) => a[0].localeCompare(b[0]))
        .map(([name, ps]) =>
          `<h2><span class="mw-headline" id="${anchorId(name)}">${escapeHtml(name)}</span> ` +
          `<span class="cat-count">${ps.length}</span></h2>${pageGrid(ps, ctx)}`)
        .join('');
    },
  }));

  // ---- stubs ----------------------------------------------------------------
  out.push(virtual({
    root, config, url: '/wiki/stubs/', namespace: 'wiki', title: 'Stubs',
    render: (ctx) => {
      const stubs = contentPages(ctx.allPages()).filter((p) => p.fm.stub);
      return `<p>${stubs.length} page${stubs.length === 1 ? '' : 's'} still need writing. ` +
        `This is the work queue.</p>` + pageGrid(stubs, ctx);
    },
  }));

  // ---- recently edited ------------------------------------------------------
  out.push(virtual({
    root, config, url: '/wiki/recent-changes/', namespace: 'wiki', title: 'Recent changes',
    render: (ctx) => {
      const rows = lastChanged(contentPages(ctx.allPages()), root, config.contentDir)
        .filter((r) => r.time)
        .sort((a, b) => b.time - a.time)
        .slice(0, 100)
        .map(({ p, time }) =>
          `<tr><td>${new Date(time).toISOString().slice(0, 16).replace('T', ' ')}</td>` +
          `<td>${ctx.hrefWrap(p.url, escapeHtml(p.title))}</td>` +
          `<td><code>${escapeHtml(p.relFile)}</code></td></tr>`);
      if (!rows.length) return '<p class="mcui-empty">No pages yet.</p>';
      return `<p>The 100 most recently changed pages.</p>` +
        `<table class="wikitable"><thead><tr><th>Modified</th><th>Page</th><th>Source file</th></tr></thead>` +
        `<tbody>${rows.join('')}</tbody></table>`;
    },
  }));

  // ---- data values ----------------------------------------------------------
  out.push(virtual({
    root, config, url: '/wiki/data-values/', namespace: 'wiki', title: 'Data values',
    render: (ctx) =>
      `<p>Every block and item id in ${escapeHtml(config.version)}, read directly from the game.</p>` +
      `<h2><span class="mw-headline" id="blocks">Blocks</span></h2>` +
      ctx.renderInline('') +
      renderTable(ctx, 'blocks') +
      `<h2><span class="mw-headline" id="items">Items</span></h2>` + renderTable(ctx, 'items') +
      `<h2><span class="mw-headline" id="entities">Entities</span></h2>` + renderTable(ctx, 'entities'),
  }));

  // ---- sprite reference -----------------------------------------------------
  out.push(virtual({
    root, config, url: '/wiki/sprites/', namespace: 'wiki', title: 'Sprite reference',
    render: (ctx) => {
      const names = Object.keys(ctx.data.sprites).sort();
      const cells = names.map((n) =>
        `<li><span class="sprite-cell">${ctx.sprite(n, { size: 32 })}</span>` +
        `<code>${escapeHtml(n)}</code></li>`).join('');
      return `<p>Every sprite available to <code>{{sprite|Name}}</code>, ${names.length} in total. ` +
        `Names come from <code>data/sprites.json</code>.</p><ul class="sprite-sheet">${cells}</ul>`;
    },
  }));

  // ---- search results -------------------------------------------------------
  out.push(virtual({
    root, config, url: '/wiki/search/', namespace: 'wiki', title: 'Search',
    render: () =>
      `<div id="search-page"><p class="search-status">Loading the search index…</p>` +
      `<ol id="search-results"></ol></div>`,
  }));

  // ---- random ---------------------------------------------------------------
  out.push(virtual({
    root, config, url: '/wiki/random/', namespace: 'wiki', title: 'Random page',
    render: () => `<p>Taking you somewhere…</p><p id="random-fallback"></p>`,
  }));

  // ---- red-link landing -----------------------------------------------------
  out.push(virtual({
    root, config, url: '/wiki/missing/', namespace: 'wiki', title: 'Page does not exist',
    render: (ctx) =>
      `<p>You followed a link to a page that has not been written yet. Red links ` +
      `are how this wiki tracks what is missing.</p>` +
      `<p>To create it, add a Markdown file under <code>content/</code> whose ` +
      `<code>title</code> matches the link text. The conventions live in ` +
      `<code>AGENTS.md</code> at the root of the repository. See ` +
      `${ctx.hrefWrap('/wiki/page-templates/', 'the page templates')} for what can go on it, ` +
      `and ${ctx.hrefWrap('/wiki/stubs/', 'the stub list')} for what else needs work.</p>`,
  }));

  return out;
}

function renderTable(ctx, which) {
  if (which === 'blocks') {
    const rows = ctx.data.blocks.filter((b) => b.key).map((b) =>
      `<tr><td>${ctx.data.sprite(b.name) ? ctx.sprite(b.name) : ''}</td>` +
      `<td>${ctx.linkWrap(b.name, escapeHtml(b.name))}</td><td>${b.id}</td>` +
      `<td><code>${escapeHtml(b.key)}</code></td>` +
      `<td>${b.hardness == null ? '—' : b.hardness < 0 ? 'Unbreakable' : b.hardness}</td>` +
      `<td>${b.blastResistance ?? '—'}</td><td>${b.lightEmission || 0}</td></tr>`).join('');
    return `<table class="wikitable sortable"><thead><tr><th></th><th>Name</th><th>ID</th>` +
      `<th>Key</th><th>Hardness</th><th>Blast res.</th><th>Light</th></tr></thead><tbody>${rows}</tbody></table>`;
  }
  if (which === 'items') {
    // An item that shares its name with another keeps its own picture under its
    // id, "item 2257": the cat disc, where the name draws the 13 disc.
    const picture = (i) => (ctx.data.sprite(`item ${i.id}`) ? `item ${i.id}` : i.name);
    const rows = ctx.data.items.map((i) =>
      `<tr><td>${ctx.data.sprite(picture(i)) ? ctx.sprite(picture(i)) : ''}</td>` +
      `<td>${ctx.linkWrap(i.name, escapeHtml(i.name))}</td><td>${i.id}</td>` +
      `<td><code>${escapeHtml(i.key || '')}</code></td></tr>`).join('');
    return `<table class="wikitable sortable"><thead><tr><th></th><th>Name</th><th>ID</th>` +
      `<th>Key</th></tr></thead><tbody>${rows}</tbody></table>`;
  }
  // Mob and Monster are abstract superclasses, not things you meet in a world.
  const abstract = new Set(['Mob', 'Monster']);
  const rows = ctx.data.entities.filter((e) => !abstract.has(e.name)).map((e) =>
    `<tr><td>${ctx.linkWrap(e.name, escapeHtml(e.name))}</td><td>${e.networkId}</td>` +
    `<td><code>${escapeHtml(e.class)}</code></td></tr>`).join('');
  return `<table class="wikitable sortable"><thead><tr><th>Name</th><th>Network ID</th>` +
    `<th>Class</th></tr></thead><tbody>${rows}</tbody></table>`;
}
