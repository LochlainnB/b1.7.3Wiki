---
title: Style guide
description: Conventions for writing and editing pages on this wiki.
type: wiki
categories: [Wiki]
---

Pages are Markdown files under `content/`. Edit them directly; there is no
online editor. Run `npm run build` afterwards, or leave `npm run dev` running
and it rebuilds on save.

## The one rule

**Describe Beta 1.7.3, and nothing else.**

Do not write version history sections. Do not write "this was changed in 1.8",
"in modern versions", or "previously". A reader of this wiki is playing 1.7.3
right now and wants to know how it behaves now. If you are unsure whether a
behaviour belongs to 1.7.3 or a later version, leave it out or mark it with a
comment rather than guessing.

## Where a page goes

| Namespace | Directory | For |
|---|---|---|
| Block | `content/block/` | Anything placeable in the world |
| Item | `content/item/` | Anything that exists only in an inventory |
| Entity | `content/entity/` | Mobs, projectiles, vehicles |
| Biome | `content/biome/` | The thirteen biomes |
| Mechanic | `content/mechanic/` | Systems: crafting, redstone, mob spawning |
| Guide | `content/guide/` | Task-oriented how-tos |
| Wiki | `content/wiki/` | Pages about the wiki itself |

The file name becomes the URL, so `content/block/mossy-cobblestone.md` is served
at `/block/mossy-cobblestone/`.

## Frontmatter

Every page starts with a YAML block. Only `title` is required.

```yaml
---
title: Cobblestone            # required; also the [[link]] target
description: One sentence.    # used in search results and meta tags
type: block                   # block | item | entity | biome | mechanic | guide | wiki
subject: Cobblestone          # what the data templates look up, if not the title
sprite: Cobblestone           # which icon represents the page, if not the title
aliases: [Cobble]             # extra names that resolve to this page
categories: [Blocks]          # shown at the foot, indexed on /wiki/categories/
infobox:                      # extra or overriding infobox rows
  Tool: Pickaxe
stub: true                    # lists the page on /wiki/stubs/
toc: false                    # suppress the contents box
---
```

Unknown keys produce a build warning, so a typo will not sit unnoticed.

### A page about more than one id

Beta gives one name to ids that are not one thing: both mushrooms are
`tile.mushroom`, a furnace is one id lit and another unlit. When a single
article is the right home for the pair, `subject` names them all, and the
infobox grows a column each:

```yaml
subject: {Brown: Brown Mushroom, Red: Red Mushroom}   # by name
subject: {Unlit: block 61, Lit: block 62}             # by id, when the name is shared
aliases: [Brown Mushroom, Red Mushroom]               # so both names reach the page
```

The key is the column heading, so keep it to a word. Rows the ids agree on stay
single, and only the ones that differ split, which is usually the light level
and the id itself. Where the two have separate sprites the picture area shows
both; where they share one it shows it once, full size.

`aliases` matter here beyond linking: `tools/seed.mjs` reads them before it
stubs anything, so a name an existing article already covers does not sprout a
second page on the next reseed.

## Article shape

Lead with a bolded page name and a one-sentence definition. Then use `##`
headings. Prefer this order, skipping anything that does not apply:

1. `## Obtaining` — mining, crafting, drops, natural generation
2. `## Usage` — what it does and what it makes
3. `## Behaviour` — for mobs and mechanics
4. `## Data values` — IDs and translation keys

A mob is not obtained and then used, so mob pages take a different shape:

1. `## Spawning` — light level, biome, what it needs to stand on, pack size
2. `## Drops` — what it leaves on death, and how much
3. `## Behaviour` — movement, what provokes it, how it attacks
4. `## Data values` — the entity network ID

Do not add a `## History` section. See the rule above.

## Linking

Use `[[Page Name]]`, which matches on the target's title, slug or alias.
`[[Page Name|other text]]` changes the label and `[[Page#Section]]` jumps to a
heading. Link the first mention of another subject in a section, not every
mention.

A link to a page that does not exist renders red and produces a build warning.
That is intentional: red links are the wiki's to-do list. Do not remove a red
link just to silence the warning.

## Numbers

Do not type IDs, hardness, blast resistance or recipes into prose. They are
already extracted from the game and available through the infobox and the
templates on [[Page templates]]. If a number is worth stating in a sentence,
pull it in with a template so it cannot drift.

## Tone

Plain, present tense, third person. "Cobblestone drops from stone", not "You
will get cobblestone". Avoid strategy advice in reference pages; put that in a
[[Guides|guide]].
