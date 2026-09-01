// Slugs are the wiki's identity system: a page's file name, its URL and the
// target of every [[wiki link]] all reduce to the same slug, so links resolve
// by title without editors having to know paths.

/** "Wooden Planks" -> "wooden-planks" */
export function slug(name) {
  return String(name)
    .normalize('NFKD')
    .replace(/['’]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

/** "wooden-planks" -> "Wooden Planks" (only a fallback; frontmatter wins). */
export function titleize(s) {
  return String(s)
    .split('-')
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

/**
 * Split a [[link target]] into its page part and heading anchor.
 * "Crafting#Recipes" -> { page: "Crafting", anchor: "Recipes" }
 */
export function splitAnchor(target) {
  const i = target.indexOf('#');
  if (i === -1) return { page: target.trim(), anchor: '' };
  return { page: target.slice(0, i).trim(), anchor: target.slice(i + 1).trim() };
}

/** Heading anchor id, matching what the ToC generates. */
export function anchorId(text) {
  return slug(text) || 'section';
}

/**
 * Relative href from one page URL to another, so the built site works from any
 * directory: a local file:// open, a subpath on GitHub Pages, or a dev server.
 * Both arguments are absolute site paths like "/block/stone/".
 */
export function relative(fromUrl, toUrl) {
  const from = fromUrl.replace(/^\/+|\/+$/g, '').split('/').filter(Boolean);
  const to = toUrl.replace(/^\/+/, '');
  // A page URL "/block/stone/" is served as "/block/stone/index.html", so the
  // document sits one level deeper than its path segments suggest.
  const up = from.length;
  const prefix = up === 0 ? './' : '../'.repeat(up);
  return (prefix + to).replace(/\/{2,}/g, '/') || './';
}
