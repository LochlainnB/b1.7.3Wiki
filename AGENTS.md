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

The authoritative source for behaviour is the Beta 1.7.3 client and server jar.
There is a `babric-b1.7.3` skill available for resolving names and testing
runtime behaviour against a real server when a claim needs verifying.

## Commands

```
npm install            once
npm run dev            build, serve on :8173, rebuild on save
npm run build          one-off build into site/
npm run check          validate only, write nothing
npm run new -- block "Mossy Cobblestone"    scaffold a page
```

**The build must end with `0 errors`.** Warnings are the editorial to-do list
(mostly red links) and are expected to be non-zero.

## Layout

```
content/           the wiki. Markdown + YAML frontmatter. EDIT THIS.
  block/ item/ entity/ biome/ mechanic/ guide/ wiki/
data/              game data extracted from the jar. GENERATED - do not hand-edit,
                   except the two *-overrides.json files.
assets/            sprites and textures sliced from the jar. GENERATED.
theme/             wiki.css and wiki.js.
tools/             the build (Node) and the extractors (Python).
site/              build output. GENERATED, gitignored, never edit.
wiki.config.js     site title, sidebar navigation, namespaces, footer.
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
`aliases`, `categories`, `infobox`, `infoboxTitle`, `stub`, `toc`, `id`,
`order`. Anything else warns, so typos surface at build time.

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
python tools/extract/gamedata.py --jar <client.jar> --cache <BabricKit/cache> --out data
python tools/extract/sprites.py  --jar <client.jar> --out .
node tools/seed.mjs              stub any newly discovered block/item/entity
```

Two files in `data/` are hand-maintained and safe to edit:

- `texture-overrides.json` — the inventory tile for blocks that pick their
  texture per face in code, so it cannot be read from the constructor.
- `name-overrides.json` — display names for the handful of blocks that have no
  entry in `lang/en_US.lang`.

Everything else in `data/` is overwritten by the extractors.

## Conventions

- Plain, present tense, third person. "Cobblestone drops from stone", not "you
  will get cobblestone".
- Lead sentence bolds the page name and defines it.
- Section order: Obtaining, Usage, Behaviour, Data values. Skip what does not apply.
- Strategy and tutorials belong in `content/guide/`, not on reference pages.
- Commit messages: short imperative subject, then why. Commit often.
