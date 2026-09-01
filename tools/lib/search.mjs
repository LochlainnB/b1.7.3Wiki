// A prebuilt search index, small enough to ship to the browser whole so search
// works with no server and no request per keystroke.

const stripTags = (html) => html
  .replace(/<script[\s\S]*?<\/script>/gi, ' ')
  .replace(/<style[\s\S]*?<\/style>/gi, ' ')
  .replace(/<[^>]+>/g, ' ')
  .replace(/&[a-z]+;|&#\d+;/gi, ' ')
  .replace(/\s+/g, ' ')
  .trim();

/** Text between the article body markers, i.e. without chrome or navigation. */
function articleText(html) {
  const start = html.indexOf('<div class="mw-parser-output">');
  const end = html.indexOf('</div>\n    </div>', start);
  const slice = start === -1 ? html : html.slice(start, end === -1 ? undefined : end);
  return stripTags(slice);
}

function headings(html) {
  const out = [];
  const re = /<span class="mw-headline" id="([^"]+)">([\s\S]*?)<\/span>/g;
  let m;
  while ((m = re.exec(html))) out.push({ id: m[1], text: stripTags(m[2]) });
  return out;
}

export function buildSearchIndex(pages, outputs) {
  const byPage = new Map(outputs.map(([p, html]) => [p.url, html]));
  const docs = [];
  for (const page of pages) {
    if (page.isHome && page.generated) continue;
    const html = byPage.get(page.url) || '';
    const text = articleText(html);
    docs.push({
      u: page.url,
      t: page.title,
      n: page.namespace || '',
      d: page.fm.description || text.slice(0, 180),
      // Enough body text to match on, without shipping the whole wiki twice.
      b: text.slice(0, 1200).toLowerCase(),
      h: headings(html).slice(0, 24),
      s: page.fm.stub ? 1 : 0,
    });
  }
  docs.sort((a, b) => a.t.localeCompare(b.t));
  return { built: new Date().toISOString(), docs };
}
