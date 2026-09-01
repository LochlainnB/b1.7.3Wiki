// The Vector-legacy page shell, rebuilt to match minecraft.wiki's structure:
// logo above a portal sidebar, Read/View-source tabs over the content, an
// inline Contents box, and a sticky copy of it in the sidebar.
import { escapeHtml } from './templates.mjs';

/** Group the flat heading list into a tree so nesting is structural. */
function tocTree(toc) {
  const min = Math.min(...toc.map((t) => t.level));
  const root = { children: [] };
  const stack = [root];
  for (const t of toc) {
    const depth = t.level - min;
    while (stack.length > depth + 1) stack.pop();
    while (stack.length < depth + 1) {
      // A jump from h2 straight to h4 still has to nest somewhere.
      const filler = { children: [] };
      stack[stack.length - 1].children.push(filler);
      stack.push(filler);
    }
    const node = { ...t, children: [] };
    stack[stack.length - 1].children.push(node);
    stack.push(node);
  }
  return root;
}

function tocList(nodes, prefix) {
  const items = nodes.map((n, i) => {
    const number = [...prefix, i + 1].join('.');
    const link = n.id
      ? `<a href="#${n.id}"><span class="tocnumber">${number}</span> ` +
        `<span class="toctext">${escapeHtml(n.text)}</span></a>`
      : '';
    const kids = n.children.length ? tocList(n.children, [...prefix, i + 1]) : '';
    return `<li class="toclevel-${prefix.length + 1}">${link}${kids}</li>`;
  });
  return `<ul>${items.join('')}</ul>`;
}

/** Contents box: inline above the article, and again in the sidebar. */
function renderToc(toc, { sidebar = false } = {}) {
  if (toc.length < 2) return '';
  const inner = tocList(tocTree(toc).children, []);
  if (sidebar) {
    return `<nav id="p-toc" class="mw-portlet vector-menu-portal portal">` +
      `<h3 id="p-toc-label" class="vector-menu-heading">Contents</h3>` +
      `<div class="vector-menu-content toc-sidebar">${inner}</div></nav>`;
  }
  return `<div id="toc" class="toc" role="navigation" aria-labelledby="mw-toc-heading">` +
    `<div class="toctitle"><h2 id="mw-toc-heading">Contents</h2></div>${inner}</div>`;
}

function portlet(id, label, linksHtml) {
  return `<nav id="p-${id}" class="mw-portlet mw-portlet-${id} vector-menu-portal portal">` +
    `<h3 id="p-${id}-label" class="vector-menu-heading">${escapeHtml(label)}</h3>` +
    `<div class="vector-menu-content"><ul class="vector-menu-content-list">${linksHtml}</ul></div>` +
    `</nav>`;
}

function sidebarHtml(config, ctx, tocSidebar) {
  const logo =
    `<div id="p-logo" role="banner">` +
    `<a class="mw-wiki-logo" href="${ctx.hrefFor('/')}" title="Visit the main page">` +
    `<span class="wiki-logo-mark" aria-hidden="true"></span>` +
    `<span class="wiki-logo-text">${escapeHtml(config.shortTitle)}</span></a></div>`;

  const portals = (config.sidebar || []).map((p) => {
    const links = p.links.map((l) => {
      const active = ctx.page.url === l.href ? ' class="active"' : '';
      return `<li${active}><a href="${ctx.hrefFor(l.href)}">${escapeHtml(l.text)}</a></li>`;
    }).join('');
    return portlet(p.id, p.label, links);
  }).join('');

  return `<div id="mw-panel" class="vector-legacy-sidebar">${logo}${portals}${tocSidebar}</div>`;
}

function tabsHtml(page, ctx) {
  const ns = page.namespace
    ? (ctx.config.namespaces[page.namespace]?.label || page.namespace)
    : 'Page';
  const left =
    `<nav id="p-associated-pages" class="mw-portlet vector-menu-tabs vector-menu-tabs-legacy">` +
    `<div class="vector-menu-content"><ul class="vector-menu-content-list">` +
    `<li class="selected"><a href="${ctx.hrefFor(page.url)}">${escapeHtml(ns)}</a></li>` +
    `</ul></div></nav>`;

  const source = ctx.config.editorUrl
    ? `<li id="ca-viewsource"><a href="${escapeHtml(ctx.config.editorUrl(page.file))}" ` +
      `title="Open ${escapeHtml(page.relFile)} in your editor">View source</a></li>`
    : `<li id="ca-viewsource"><span title="${escapeHtml(page.relFile)}">View source</span></li>`;

  const right =
    `<nav id="p-views" class="mw-portlet vector-menu-tabs vector-menu-tabs-legacy">` +
    `<div class="vector-menu-content"><ul class="vector-menu-content-list">` +
    `<li id="ca-view" class="selected"><a href="${ctx.hrefFor(page.url)}">Read</a></li>` +
    source +
    `</ul></div></nav>`;

  const search =
    `<div id="p-search" role="search">` +
    `<form id="searchform" action="${ctx.hrefFor('/wiki/search/')}" autocomplete="off">` +
    `<div id="simpleSearch">` +
    `<input type="search" name="q" id="searchInput" placeholder="Search ${escapeHtml(ctx.config.shortTitle)}" ` +
    `aria-label="Search" accesskey="f">` +
    `<button id="searchButton" type="submit" title="Search"><span>Search</span></button>` +
    `</div><div id="searchSuggest" hidden></div></form></div>`;

  return `<div id="left-navigation">${left}</div><div id="right-navigation">${right}${search}</div>`;
}

function breadcrumb(page, ctx) {
  if (page.isHome) return '';
  const parts = [`<a href="${ctx.hrefFor('/')}">Home</a>`];
  if (page.namespace) {
    const ns = ctx.config.namespaces[page.namespace];
    parts.push(`<a href="${ctx.hrefFor('/' + page.namespace + '/')}">${
      escapeHtml(ns?.plural || page.namespace)}</a>`);
  }
  if (!page.isIndex) parts.push(`<span class="crumb-current">${escapeHtml(page.title)}</span>`);
  return `<div id="mw-content-subtitle" class="breadcrumb">${parts.join('<span class="crumb-sep">›</span>')}</div>`;
}

function catlinks(page, ctx) {
  const cats = page.fm.categories || [];
  if (!cats.length) return '';
  const links = cats.map((c) =>
    `<li><a href="${ctx.hrefFor('/wiki/categories/#' + ctx.anchor(c))}">${escapeHtml(c)}</a></li>`).join('');
  return `<div id="catlinks" class="catlinks"><div id="mw-normal-catlinks" class="mw-normal-catlinks">` +
    `<span class="catlinks-label">Categories</span>: <ul>${links}</ul></div></div>`;
}

function footerHtml(config, ctx) {
  const lic = config.license
    ? `Content is available under <a href="${config.license.href}" class="external" rel="nofollow noopener">${
        escapeHtml(config.license.text)}</a> unless otherwise noted.`
    : '';
  return (
    `<footer id="footer" class="mw-footer" role="contentinfo">` +
    `<ul id="footer-info">` +
    `<li id="footer-info-copyright">${lic}</li>` +
    `<li id="footer-info-disclaimer">${escapeHtml(config.disclaimer || '')}</li>` +
    (ctx.buildTime ? `<li id="footer-info-lastmod">Built ${escapeHtml(ctx.buildTime)}.</li>` : '') +
    `</ul>` +
    `<ul id="footer-places">` +
    `<li><a href="${ctx.hrefFor('/wiki/about/')}">About</a></li>` +
    `<li><a href="${ctx.hrefFor('/wiki/style-guide/')}">Style guide</a></li>` +
    `<li><a href="${ctx.hrefFor('/wiki/all-pages/')}">All pages</a></li>` +
    `</ul></footer>`
  );
}

export function renderDocument({ page, contentHtml, infoboxHtml, toc, ctx }) {
  const config = ctx.config;
  const tocInline = page.fm.toc === false ? '' : renderToc(toc);
  const tocSide = page.fm.toc === false ? '' : renderToc(toc, { sidebar: true });
  const desc = page.fm.description
    || `${page.title} in Minecraft ${config.version}.`;

  const bodyClasses = [
    'skin-vector-legacy', 'mediawiki', 'ltr',
    page.namespace ? `ns-${page.namespace}` : 'ns-main',
    `page-${page.slug}`,
    page.fm.stub ? 'page-stub' : '',
  ].filter(Boolean).join(' ');

  return `<!DOCTYPE html>
<html lang="${config.lang}" class="client-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escapeHtml(page.isHome ? config.title : `${page.title} - ${config.shortTitle}`)}</title>
<meta name="description" content="${escapeHtml(desc)}">
<link rel="stylesheet" href="${ctx.hrefFor('/assets/wiki.css')}">
<link rel="icon" href="${ctx.hrefFor('/assets/sprites/terrain/2.png')}" type="image/png">
<script>(function(){try{var t=localStorage.getItem('wgl-theme');if(t==='dark'||(!t&&matchMedia('(prefers-color-scheme: dark)').matches)){document.documentElement.classList.add('wgl-theme-dark');}}catch(e){}})();</script>
</head>
<body class="${bodyClasses}">
<div id="mw-page-base" class="noprint"></div>
<div id="mw-head-base" class="noprint"></div>

<div id="content" class="mw-body" role="main">
  <a id="top"></a>
  <h1 id="firstHeading" class="firstHeading"><span class="mw-page-title-main">${escapeHtml(page.title)}</span></h1>
  <div id="bodyContent" class="vector-body">
    <div id="siteSub" class="noprint">From the ${escapeHtml(config.title)}</div>
    ${breadcrumb(page, ctx)}
    <div id="mw-content-text" class="mw-body-content">
      <div class="mw-parser-output">
${infoboxHtml}
${tocInline}
${contentHtml}
      </div>
    </div>
    ${catlinks(page, ctx)}
  </div>
</div>

<div id="mw-navigation">
  <h2 class="visually-hidden">Navigation menu</h2>
  <div id="mw-head">
    ${tabsHtml(page, ctx)}
  </div>
  ${sidebarHtml(config, ctx, tocSide)}
</div>

${footerHtml(config, ctx)}

<button id="theme-toggle" type="button" title="Toggle dark mode" aria-label="Toggle dark mode"></button>
<script>window.WIKI_BASE=${JSON.stringify(ctx.hrefFor('/'))};</script>
<script src="${ctx.hrefFor('/assets/wiki.js')}" defer></script>
</body>
</html>
`;
}

export { renderToc };
