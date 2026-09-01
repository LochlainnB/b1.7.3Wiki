# Minecraft Beta 1.7.3 Wiki

A static wiki for **Minecraft Beta 1.7.3**, laid out and styled after
[minecraft.wiki](https://minecraft.wiki) — MediaWiki's Vector-legacy skin, with
the game's own inventory chrome for crafting grids and infoboxes.

Pages are Markdown files. Edit them with any tool, run the build, get a site.

```bash
npm install
npm run dev        # http://localhost:8173, rebuilds on save
```

<!-- Screenshot: run `npm run build` and open site/index.html -->

## What makes it different

**The game data is extracted, not transcribed.** Block and item ids, hardness,
blast resistance, light levels, biome colours, every sprite, and every crafting
and smelting recipe are read directly out of the Beta 1.7.3 client jar by
`tools/extract/`. A page never restates a number the game already knows:

- infoboxes build themselves from a page's title,
- `{{crafting}}` renders the real recipe grid,
- `{{id|Cobblestone}}` prints the real id.

That means the reference data is correct by construction, and the part humans
(or language models) write is the prose.

The extractors are dependency-free Python: a Java class-file parser and an
abstract interpreter that reads static initialisers, plus a small PNG codec for
slicing the texture sheets.

## Commands

| Command | Does |
|---|---|
| `npm run dev` | Build, serve on `:8173`, rebuild on save |
| `npm run build` | One-off build into `site/` |
| `npm run check` | Validate content, write nothing |
| `npm run new -- block "Mossy Cobblestone"` | Scaffold a page |
| `node tools/seed.mjs` | Stub every block/item/entity/biome not yet written |

The build reports broken links, missing sprites, unknown templates and bad
frontmatter, naming the file responsible. Errors fail the build; warnings are
the editorial to-do list.

## Layout

```
content/        the wiki — Markdown + YAML frontmatter
data/           game data extracted from the jar (generated)
assets/         sprites and textures sliced from the jar (generated)
theme/          wiki.css, wiki.js
tools/          build (Node) and extractors (Python)
site/           build output (generated, gitignored)
wiki.config.js  title, sidebar, namespaces, footer
```

## Editing

See **[AGENTS.md](AGENTS.md)** for the full contributor guide, or the wiki's own
[style guide](content/wiki/style-guide.md) and
[template reference](content/wiki/page-templates.md).

The one rule worth repeating here: **pages describe Beta 1.7.3 and nothing
else** — no version history, no comparisons to later releases.

## Regenerating from the jar

Only needed if the extractors change:

```bash
python tools/extract/gamedata.py --jar <client.jar> --cache <BabricKit/cache> --out data
python tools/extract/sprites.py  --jar <client.jar> --out .
```

`data/texture-overrides.json` and `data/name-overrides.json` are hand-maintained
and survive regeneration; everything else in `data/` is overwritten.

## Deploying

The output is plain static files with relative URLs, so `site/` works opened
straight off disk, behind any web server, or on GitHub Pages under a subpath —
no configuration either way.

## Licence and attribution

Wiki prose is available under
[CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/).

This is an unofficial fan project. Minecraft content, textures and materials are
trademarks and copyrights of Mojang AB and its licensors. Textures are extracted
from a local copy of the game for reference use. Not affiliated with Mojang or
Microsoft.
