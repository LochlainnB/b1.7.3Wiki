# Working on this wiki

This repository is a **Minecraft Beta 1.7.3 wiki**. Pages are Markdown files
that build into a static site styled after minecraft.wiki. Editing happens by
changing files directly — there is no online editor and no database.

If you are here to write or fix an article, you mostly need two things: the
editorial rule below, and the template list.

## The editorial rule

**Describe Beta 1.7.3, and nothing else.**

- No `## History` sections. Ever. They were deliberately removed from the page
  template.
- No "this changed in 1.8", "in modern versions", "used to be". Readers are
  playing 1.7.3 right now.
- No Java/Bedrock edition split. Beta 1.7.3 is one Java release.
- If you cannot tell whether a behaviour is 1.7.3 or a later version, leave it
  out, or leave an HTML comment saying what needs checking. Do not guess.

The authoritative source for behaviour is the game itself. A full decompiled and
deobfuscated copy of Beta 1.7.3 sits outside this repository:

```
C:\Users\Lochlainn\Documents\Source\Minecraft\b1.7.3Source
```

It is read-only, and it is never vendored here — it is Mojang's code with no
licence attached, so it must stay out of this repo and out of `site/`.

Two skills use it:

- **`b173-wiki`** (`.claude/skills/b173-wiki/`) — the workflow for answering a
  question from the wiki, falling back to the source, and offering to write the
  result back. Its `SOURCEMAP.md` maps a topic to the classes that answer it.
- **`babric-b1.7.3`** — obfuscated names, mappings and mixin targets. For
  modding, not for game facts.

## Commands

```
npm install            once
npm run dev            build, serve on :8173, rebuild on save
npm run build          one-off build into site/
npm run check          the full test suite: validate content, verify data
npm run sourcemap      regenerate the skill's SOURCEMAP.md
npm run new -- block "Mossy Cobblestone"    scaffold a page
```

**The build must end with `0 errors`.** Warnings are the editorial to-do list
(mostly red links) and are expected to be non-zero.

`npm run check` does two things. It validates every page — frontmatter, links,
templates, sprites — and it replays `Block`, `Item`, `EntityList`,
`FurnaceRecipes` and the whole crafting registry out of the decompiled source
and compares them against `data/`. A number that disagrees with the game is an
error; something the extractors never picked up is a warning. Without the source
installed the second half is skipped and says so, rather than failing.

The crafting check runs both ways: every output the source names must be in
`data/recipes.json`, and every output in `data/recipes.json` must be one the
source names. That matters because the recipes are not read out of the bytecode
so much as executed — see below — so reading the decompiled Java is a genuinely
independent second opinion.

Page validation runs both ways too. `{{crafting}}` warns when a page asks for a
recipe `data/` does not have; the build also warns when `data/` has a crafting,
smelting or "used in" recipe for a page's subject that the page never displays,
naming the template to add. That second half is the gap `0 errors` used to hide:
a page could be missing an entire recipe section and still look clean, which
invites writing the recipe out in prose instead.

The verification is deliberately not part of `npm run dev`: `data/` only changes
when the extractors are rerun, and a save-triggered rebuild should stay fast.

## Layout

```
content/           the wiki. Markdown + YAML frontmatter. EDIT THIS.
  block/ item/ entity/ biome/ mechanic/ guide/ wiki/
data/              game data extracted from the jar. GENERATED - do not hand-edit,
                   except name-overrides.json.
assets/            sprites, inventory icons and textures from the jar. GENERATED.
theme/             wiki.css and wiki.js.
tools/             the build (Node) and the extractors (Python).
  extract/interp.py  a small JVM interpreter; the recipe extractor runs the
                   game's registration code rather than pattern-matching it.
  extract/appearance.py  runs Block's and Item's initialisers and asks the
                   result what the inventory draws for each stack.
  extract/isometric.py   draws it: the three-quarter cube, lit as the GUI lights it.
  extract/animated.py    the tiles the game generates at load rather than
                   shipping: water, lava, fire, the portal, the clock and the
                   compass.
  extract/paths.py   finds the client jar and the Babric mappings.
site/              build output. GENERATED, gitignored, never edit.
wiki.config.js     site title, sidebar navigation, namespaces, footer.
wiki.local.json    optional, gitignored. Where the external, unvendored inputs
                   are, when they are not in the conventional sibling directory:
                   {"sourceDir": ..., "cachePath": ..., "jarPath": ...}.
.claude/skills/    the b173-wiki skill and its generated SOURCEMAP.md.
```

## Writing a page

A file's path is its URL: `content/block/mossy-cobblestone.md` serves at
`/block/mossy-cobblestone/`.

```markdown
---
title: Cobblestone
description: One sentence, used in search results.
type: block
categories: [Blocks]
stub: true
---

**Cobblestone** is the block dropped when [[Stone]] is mined with a pickaxe.

## Obtaining

## Usage

## Data values
```

Frontmatter keys: `title` (required), `description`, `type`, `subject`,
`sprite`, `aliases`, `categories`, `infobox`, `infoboxTitle`, `stub`, `toc`,
`id`, `order`. Anything else warns, so typos surface at build time.

Remove `stub: true` when the page is genuinely written. That is what
`/wiki/stubs/` tracks.

## Never hand-type game numbers

Block ids, hardness, blast resistance, light levels, sprites, biome colours and
every crafting and smelting recipe are extracted from the client jar into
`data/`. They reach pages automatically:

- The **infobox builds itself** when a page's `title` (or `subject`) matches a
  block, item or entity. You do not write it.
- Recipes come from `{{crafting}}`, `{{smelting}}` and `{{used in}}`.
- Ids come from `{{id|Name}}`.
- Subtypes name themselves, and now look like themselves. One id can hold
  several things — item 351 is Ink Sac at damage 0 and Lapis Lazuli at 4, block
  35 is all sixteen wools — and `data/` carries a `variants` map for those, read
  out of the game's own labelling code. Each gets its own icon, so a recipe
  shows magenta wool as magenta; the name still links the base page.
- Sprites are inventory icons, not textures. A block is drawn as the small
  three-quarter cube a player sees in a slot, with the right tile on each face,
  so a furnace shows its front and a log shows its rings. Nothing needs saying
  on a page for that: `{{sprite}}`, `{{slot}}` and the infobox all use it.
- Where a slot lies, the sprite follows the world. Beta's inventory asks a
  block's *item* for its picture, and an item is blind to metadata and to the
  biome, so a slot puts dirt across the top of a grass block and draws all
  three plants of block 31 as grey tall grass. The extractor asks the block
  instead, at the stack's own metadata, and asks the grass block the texture
  lookup that takes a world. The deviations are listed at the top of
  `tools/extract/sprites.py`, each beside the game code it follows.
- A display name is an identity, not a label. Everything downstream keys off it
  — the page, the sprite, the slot in a recipe — so when the game gives two ids
  one name, the wiki gives them one page. Sometimes that is right; when it is
  not, split them in `data/name-overrides.json`, which is where *Brown
  Mushroom*, *Red Mushroom* and *Clay Ball* come from.
- One page may answer to several names, and cover several ids. `aliases` make a
  page the target for each name, and `tools/seed.mjs` reads them before it stubs
  anything, so the two mushrooms stay one article across a reseed. `subject` may
  name every id the page covers — `{Unlit: block 61, Lit: block 62}` — and the
  infobox then carries a column each, splitting only the rows where the ids
  disagree. Six pages needed that: a lit furnace, a lit redstone torch, glowing
  redstone ore and a powered repeater all emit light their unlit twin does not,
  and the infobox used to report the twin's.

If you find yourself typing "hardness of 2" into prose, stop: either the
infobox already says it, or a template should.

## Templates

Full reference with live examples: `content/wiki/page-templates.md`, rendered at
`/wiki/page-templates/`. The short version:

| Template | Does |
|---|---|
| `{{sprite\|Coal}}` | inline icon + link |
| `{{slot\|Iron Ingot\|3}}` | one inventory slot |
| `{{crafting}}` | every recipe producing this page's subject |
| `{{crafting\|Furnace}}` | every recipe producing a named thing |
| `{{smelting\|Stone}}` | smelting recipes producing it |
| `{{used in\|Cobblestone}}` | recipes that consume it |
| `{{recipe list}}` | every recipe in the game |
| `{{id\|Cobblestone}}` | the numeric id |
| `{{list\|blocks}}` | sortable table of a whole data set |
| `{{pagelist\|namespace=biome}}` | linked list of pages |
| `{{stub}}` `{{main\|X}}` `{{see also\|X}}` `{{hatnote\|…}}` `{{msgbox\|…}}` | notes |

To show template syntax without running it, wrap it in backticks or a fenced
block — code is parsed before templates are.

## Links

`[[Page Name]]` resolves against titles, slugs and aliases. `[[Page|label]]`
and `[[Page#Section]]` work as expected.

A link to a page that does not exist renders **red** and warns at build time.
That is the point — red links are the to-do list. **Do not delete a red link to
silence a warning.** Either write the page or leave the link.

## Regenerating data and assets

Only needed if the extractors change. Requires the Beta 1.7.3 client jar and
the Babric mappings:

```
python tools/extract/gamedata.py --out data
python tools/extract/sprites.py  --out .
node tools/seed.mjs              stub any newly discovered block/item/entity
node tools/seed.mjs --force      rebuild existing stubs from the new data
```

The jar and the mappings are Mojang's, shipped without a licence, so like the
decompiled source they are never vendored here. `tools/extract/paths.py` finds
them the same way `tools/lib/source.mjs` finds the source: `B173_JAR` and
`B173_CACHE`, then `"jarPath"` and `"cachePath"` in `wiki.local.json`, then the
sibling directory `../BabricKit/cache`. The cache is one directory holding
`intermediary.tiny` and `barn.tiny` with the jar beside them, so pointing at it
is normally enough. `--jar` and `--cache` still override.

Unlike the source, these are not optional: the build never opens the jar, but
the extractors are nothing without it, so a bad path is a fatal error that
names all three ways to fix it.

`--force` rewrites only files still carrying `stub: true`, and skips every page
anyone has actually written. Use it when new data should reach pages that were
scaffolded before it existed — a page seeded before its recipe was extracted has
no `{{crafting}}` on it, and only a reseed will add one.

One file in `data/` is hand-maintained and safe to edit: `name-overrides.json`,
which supplies display names for the handful of blocks and subtypes that have no
entry in `lang/en_US.lang` — block 31 is a dead shrub, tall grass and a fern
under one id, and the game names none of them.

It also splits names the game hands out twice. `gamedata.py` ends every run by
listing the names claimed by more than one id, because a display name is the
wiki's identity for a thing — its page, its sprite, its slot in a recipe — and
two ids under one name become one page. That is right for the still and the
flowing halves of water and wrong for the brown and the red mushroom, which is
why 39 and 40 are named apart there, and 337 with them: `item.clay` and
`tile.clay` are both *Clay*, and the collision had the clay block crafted out of
four of itself.

Everything else in `data/` is overwritten by the extractors.

## Conventions

- Plain, present tense, third person. "Cobblestone drops from stone", not "you
  will get cobblestone".
- Lead sentence bolds the page name and defines it.
- Section order: Obtaining, Usage, Behaviour, Data values. Skip what does not apply.
- A mob is not obtained and used: mob pages run Spawning, Drops, Behaviour,
  Data values instead. `tools/lib/mobs.mjs` holds the list of which entities
  count, and both generators read it.
- Strategy and tutorials belong in `content/guide/`, not on reference pages.
- Commit messages: short imperative subject, then why. Commit often, never leave the tree dirty.

## Citing the source

When a fact comes from reading the decompiled game, record where, as an HTML
comment after the passage:

```markdown
Slimes spawn only below Y=16, and only in chunks where a hash of the world seed
and the chunk coordinates comes out to zero.
<!-- src: EntitySlime.java:134 getCanSpawnHere -->
```

The comment does not render. It lets the next editor check the claim in one step
instead of re-deriving it, which matters on a wiki written mostly by agents that
cannot see each other's reasoning. Line numbers are stable: the source is a
fixed decompile and never changes.
