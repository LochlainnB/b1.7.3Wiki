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

The extractors are dependency-free Python: a Java class-file parser, an
abstract interpreter that reads static initialisers, a concrete JVM interpreter
that *runs* the game's crafting registration rather than pattern-matching it,
and a small PNG codec for slicing the texture sheets.

Sprites go through the same door. Block and Item's initialisers are executed,
and the registry they leave behind is asked what
`RenderItem.drawItemIntoGui` would ask — cube or flat tile, which tile on each
face, what tint — then that is rasterised into the three-quarter cube the
inventory shows, lit by the GUI's own two lamps. So all sixteen wools are
sixteen colours, and a furnace shows its front.

Nine of the sheets' tiles never ship at all: the game paints water, lava, fire, the portal,
the clock and the compass into the atlas at load, over placeholders that in the
file are a blue square, an orange smear and a red card reading FIRE TEX!. Each
of those `TextureFX` classes is reimplemented, down to `java.util.Random` and
`MathHelper`'s sine table, so a page shows the texture and not the placeholder.
And where the inventory itself is misleading — a grass block is half dirt in a
slot, a fern is grey tall grass — the sprite follows what the world draws.

## Commands

| Command | Does |
|---|---|
| `npm run dev` | Build, serve on `:8173`, rebuild on save |
| `npm run build` | One-off build into `site/` |
| `npm run check` | The full test suite: validate content, verify `data/` |
| `npm run new -- block "Mossy Cobblestone"` | Scaffold a page |
| `npm run sourcemap` | Regenerate the skill's `SOURCEMAP.md` |
| `node tools/seed.mjs` | Stub every block/item/entity/biome not yet written |
| `node tools/seed.mjs --force` | Rebuild existing stubs from newly extracted data |

The build reports broken links, missing sprites, unknown templates and bad
frontmatter, naming the file responsible. Recipes are checked in both
directions: a page asking for a recipe the data does not have, and a recipe in
the data that the page never shows. Errors fail the build; warnings are the
editorial to-do list.

`npm run check` adds a second half, replaying `Block`, `Item`, `EntityList`,
`FurnaceRecipes` and the whole crafting registry out of a decompiled copy of
the game and comparing
them against `data/` — an independent second opinion on the extractors. It is
skipped, with a note, when no decompiled source is installed.

## Layout

```
content/        the wiki — Markdown + YAML frontmatter
data/           game data extracted from the jar (generated)
assets/         sprites and textures sliced from the jar (generated)
theme/          wiki.css, wiki.js
tools/          build (Node) and extractors (Python)
site/           build output (generated, gitignored)
wiki.config.js  title, sidebar, namespaces, footer
wiki.local.json optional, gitignored — where the jar, mappings and source live
.claude/skills/ the b173-wiki skill and its generated source map
```

## Editing

See **[AGENTS.md](AGENTS.md)** — the contributor guide and the style guide in
one — and the [template reference](content/wiki/page-templates.md) for the
`{{...}}` templates, with live examples.

The one rule worth repeating here: **pages describe Beta 1.7.3 and nothing
else** — no version history, no comparisons to later releases.

## Regenerating from the jar

Only needed if the extractors change:

```bash
python tools/extract/gamedata.py --out data
python tools/extract/sprites.py  --out .
```

The client jar and the Babric mappings are Mojang's, shipped without a licence,
so they are never vendored here. `tools/extract/paths.py` finds them: `B173_JAR`
and `B173_CACHE`, then `"jarPath"` and `"cachePath"` in `wiki.local.json`, then
the sibling directory `../BabricKit/cache`. Pointing at the cache is normally
enough, since the jar sits beside the mappings; `--jar` and `--cache` override.

`data/name-overrides.json` is hand-maintained and survives regeneration;
everything else in `data/` is overwritten. It names the few things
`lang/en_US.lang` leaves nameless, and splits the ones it names twice: Beta
calls both mushrooms *Mushroom* and both the clay block and the clay ball
*Clay*, and a name is what the wiki hands a page and a sprite to.

## Deploying

The output is plain static files with relative URLs, so `site/` works opened
straight off disk, behind any web server, or on GitHub Pages under a subpath —
no configuration either way.

Pushing to `main` publishes it: `.github/workflows/deploy.yml` builds the site
on GitHub Actions and deploys `site/` to GitHub Pages. A build with errors fails
the workflow and leaves the live site as it was. It needs one setting, once:
the repository's **Settings → Pages → Source** set to **GitHub Actions**.

Built there, "View source" links each page's Markdown on GitHub instead of
opening it in VS Code, and Recent changes dates each page by its last commit.

## Licence and attribution

Wiki prose is available under
[CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/).

This is an unofficial fan project. Minecraft content, textures and materials are
trademarks and copyrights of Mojang AB and its licensors. Textures are extracted
from a local copy of the game for reference use. Not affiliated with Mojang or
Microsoft.
