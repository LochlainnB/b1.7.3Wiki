// Markdown pipeline: CommonMark via markdown-it, plus the two wiki affordances
// editors actually write -- [[Wiki Links]] and {{templates}}.
import MarkdownIt from 'markdown-it';
import { slug, splitAnchor, anchorId } from './slug.mjs';
import { renderTemplate, escapeHtml } from './templates.mjs';

/**
 * Parse a template call starting at `pos` (which must point at "{{").
 * Returns { name, args, named, end } or null when unterminated.
 */
export function parseTemplateCall(src, pos) {
  if (src.slice(pos, pos + 2) !== '{{') return null;
  let depth = 0;
  let i = pos;
  let end = -1;
  while (i < src.length - 1) {
    if (src.startsWith('{{', i)) { depth++; i += 2; continue; }
    if (src.startsWith('}}', i)) {
      depth--;
      if (depth === 0) { end = i + 2; break; }
      i += 2; continue;
    }
    i++;
  }
  if (end === -1) return null;

  const inner = src.slice(pos + 2, end - 2);
  // Split on top-level pipes so nested {{...}} arguments survive intact.
  const parts = [];
  let buf = '';
  let d = 0;
  for (let k = 0; k < inner.length; k++) {
    if (inner.startsWith('{{', k)) { d++; buf += '{{'; k++; continue; }
    if (inner.startsWith('}}', k)) { d--; buf += '}}'; k++; continue; }
    if (inner[k] === '|' && d === 0) { parts.push(buf); buf = ''; continue; }
    buf += inner[k];
  }
  parts.push(buf);

  const name = (parts.shift() || '').trim();
  const args = [];
  const named = {};
  for (const raw of parts) {
    const eq = raw.indexOf('=');
    // A key must be a short bare word; anything else is positional so that
    // prose containing "=" is not silently swallowed.
    if (eq > 0 && /^[\w#.\- ]{1,24}$/.test(raw.slice(0, eq))) {
      named[raw.slice(0, eq).trim()] = raw.slice(eq + 1).trim();
    } else {
      args.push(raw.trim());
    }
  }
  return { name, args, named, end };
}

function wikiLinkPlugin(md, ctx) {
  md.inline.ruler.before('link', 'wikilink', (state, silent) => {
    const src = state.src;
    let pos = state.pos;
    if (src.charCodeAt(pos) !== 0x5b || src.charCodeAt(pos + 1) !== 0x5b) return false;
    const close = src.indexOf(']]', pos + 2);
    if (close === -1) return false;
    const inner = src.slice(pos + 2, close);
    if (inner.includes('[[')) return false;
    if (!silent) {
      const bar = inner.indexOf('|');
      const target = (bar === -1 ? inner : inner.slice(0, bar)).trim();
      const label = (bar === -1 ? '' : inner.slice(bar + 1).trim()) || target;
      const token = state.push('html_inline', '', 0);
      token.content = ctx.linkWrap(target, escapeHtml(label));
    }
    state.pos = close + 2;
    return true;
  });
}

function templatePlugin(md, ctx) {
  // Block form: a line that begins with {{ and whose call spans to its own end.
  md.block.ruler.before('paragraph', 'template_block', (state, startLine, endLine, silent) => {
    const start = state.bMarks[startLine] + state.tShift[startLine];
    if (state.src.slice(start, start + 2) !== '{{') return false;
    const call = parseTemplateCall(state.src, start);
    if (!call) return false;
    // Only treat it as a block when nothing but whitespace follows the call.
    const rest = state.src.slice(call.end).match(/^[ \t]*(\r?\n|$)/);
    if (!rest) return false;
    if (silent) return true;

    let line = startLine;
    while (line < endLine && state.eMarks[line] < call.end) line++;

    const token = state.push('html_block', '', 0);
    token.map = [startLine, line + 1];
    token.content = renderTemplate(call.name, call.args, call.named, ctx) + '\n';
    state.line = line + 1;
    return true;
  }, { alt: ['paragraph', 'blockquote'] });

  // Inline form, e.g. "drops {{sprite|Cobblestone}} when mined".
  md.inline.ruler.before('link', 'template_inline', (state, silent) => {
    if (state.src.slice(state.pos, state.pos + 2) !== '{{') return false;
    const call = parseTemplateCall(state.src, state.pos);
    if (!call) return false;
    if (!silent) {
      const token = state.push('html_inline', '', 0);
      token.content = renderTemplate(call.name, call.args, call.named, ctx);
    }
    state.pos = call.end;
    return true;
  });
}

/** Give headings MediaWiki's markup and collect the table of contents. */
function headingPlugin(md, ctx) {
  md.core.ruler.push('wiki_headings', (state) => {
    const used = new Map();
    for (let i = 0; i < state.tokens.length; i++) {
      const tok = state.tokens[i];
      if (tok.type !== 'heading_open') continue;
      const inline = state.tokens[i + 1];
      const text = inline.content.replace(/\[\[([^\]|]*)\|?([^\]]*)\]\]/g, (m, a, b) => b || a)
        .replace(/\{\{[^}]*\}\}/g, '').trim();
      let id = anchorId(text);
      if (used.has(id)) {
        const n = used.get(id) + 1;
        used.set(id, n);
        id = `${id}-${n}`;
      } else {
        used.set(id, 1);
      }
      const level = Number(tok.tag.slice(1));
      tok.attrSet('data-level', String(level));
      inline.children = inline.children || [];
      const open = new state.Token('html_inline', '', 0);
      open.content = `<span class="mw-headline" id="${id}">`;
      const close = new state.Token('html_inline', '', 0);
      close.content = '</span>';
      inline.children.unshift(open);
      inline.children.push(close);
      if (level >= 2) ctx.toc.push({ level, id, text });
    }
  });
}

/** Tables get MediaWiki's .wikitable look; external links get an indicator. */
function polishPlugin(md, ctx) {
  md.core.ruler.push('wiki_polish', (state) => {
    for (const tok of state.tokens) {
      if (tok.type === 'table_open') tok.attrJoin('class', 'wikitable');
    }
  });
  const defaultLink = md.renderer.rules.link_open
    || ((tokens, idx, opts, env, self) => self.renderToken(tokens, idx, opts));
  md.renderer.rules.link_open = (tokens, idx, opts, env, self) => {
    const href = tokens[idx].attrGet('href') || '';
    if (/^https?:\/\//i.test(href)) {
      tokens[idx].attrJoin('class', 'external');
      tokens[idx].attrSet('rel', 'nofollow noopener');
    }
    return defaultLink(tokens, idx, opts, env, self);
  };
}

export function createRenderer(ctx) {
  const md = new MarkdownIt({
    html: true,
    linkify: true,
    typographer: false,
    breaks: false,
  });
  wikiLinkPlugin(md, ctx);
  templatePlugin(md, ctx);
  headingPlugin(md, ctx);
  polishPlugin(md, ctx);

  ctx.renderInline = (text) => md.renderInline(String(text || ''));
  return {
    render: (body) => md.render(body),
    renderInline: (text) => md.renderInline(String(text || '')),
  };
}

export { slug, splitAnchor };
