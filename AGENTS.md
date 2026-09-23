# Working on this wiki

This repository is a **Minecraft Beta 1.7.3 wiki**. Pages are Markdown files
that build into a static site styled after minecraft.wiki. Editing happens by
changing files directly — there is no online editor and no database.

If you are here to write or fix an article, you need three things: the
editorial rule below, **Writing style**, and the template list.

This file is the only style guide. The wiki used to carry a second copy of these
conventions as a page, and the two drifted; do not start another one. Conventions
belong here, and `content/wiki/page-templates.md` stays what it is — a reference
for the templates themselves, with live examples that have to render.

## The editorial rule

**Describe Beta 1.7.3, and nothing else.**

- No `## History` sections. Ever. They were deliberately removed from the page
  template.
- No "this changed in 1.8", "in modern versions", "used to be". Readers are
  playing 1.7.3 right now.
- No Java/Bedrock edition split. Beta 1.7.3 is one Java release.
- If you cannot tell whether a behaviour is 1.7.3 or a later version, leave it
  out, or leave an HTML comment saying what needs checking. Do not guess.

The authoritative source for behaviour is the game itself: a decompiled and
deobfuscated copy of Beta 1.7.3, with MCP names, kept outside this repository.
The tools look for it in this order:

1. the `B173_SOURCE` environment variable,
2. `"sourceDir"` in `wiki.local.json`,
3. a directory named `b1.7.3Source` beside this repository.

In a git worktree, 2 and 3 are also tried against the main checkout, so an
agent's worktree under `.claude/worktrees/` finds the same source as the
checkout it came from.

`npm run check` prints the path it found. If it finds none, say so and do not
write behaviour from memory.

It is read-only, and it is never vendored here — it is Mojang's code with no
licence attached, so it must stay out of this repo and out of `site/`.

The **`b173-wiki`** skill (`.claude/skills/b173-wiki/`) is the workflow for
answering a question from the wiki, falling back to the source, and offering to
write the result back. Its `SOURCEMAP.md` maps a topic to the classes that
answer it.

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

**Pushing to `main` publishes the site.** GitHub Actions rebuilds it and deploys
it to GitHub Pages (`.github/workflows/deploy.yml`); a build with errors does not
deploy. Committing is local; pushing is going live.

A pull request into `main` runs the same build as a check
(`.github/workflows/check.yml`) and publishes nothing. It cannot run the
comparison against the decompiled source, which is never on GitHub, so run
`npm run check` locally as well.

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
  block/ item/ entity/ biome/ dimension/ structure/ mechanic/ guide/ wiki/
data/              game data extracted from the jar. GENERATED - do not hand-edit,
                   except name-overrides.json.
assets/            sprites, inventory icons and textures from the jar. GENERATED.
theme/             wiki.css and wiki.js.
tools/             the build (Node) and the extractors (Python).
  extract/interp.py  a small JVM interpreter; the recipe extractor runs the
                   game's registration code rather than pattern-matching it.
  extract/appearance.py  runs Block's and Item's initialisers and asks the
                   result what the inventory draws for each stack.
  extract/properties.py  asks the same items their stack size, durability,
                   attack damage and healing, and reads each mob's health
                   out of its constructors.
  extract/isometric.py   draws it: the three-quarter cube, lit as the GUI lights it.
  extract/animated.py    the tiles the game generates at load rather than
                   shipping: water, lava, fire, the portal, the clock and the
                   compass.
  extract/paths.py   finds the client jar and the Babric mappings.
site/              build output. GENERATED, gitignored, never edit.
wiki.config.js     site title, sidebar navigation, namespaces, footer.
wiki.local.json    optional, gitignored. Where the external, unvendored inputs
                   are: {"sourceDir": ..., "cachePath": ..., "jarPath": ...}.
.claude/skills/    the b173-wiki skill and its generated SOURCEMAP.md.
```

## Writing a page

The directory a page sits in is its namespace, and decides what belongs on it:

| Namespace | Directory | For |
|---|---|---|
| Block | `content/block/` | Anything placeable in the world |
| Item | `content/item/` | Anything that exists only in an inventory |
| Entity | `content/entity/` | Mobs, projectiles, vehicles |
| Biome | `content/biome/` | The thirteen biomes |
| Dimension | `content/dimension/` | Separate worlds: the Overworld, the Nether |
| Structure | `content/structure/` | What the terrain generator builds: dungeons |
| Mechanic | `content/mechanic/` | Systems: crafting, redstone, mob spawning |
| Guide | `content/guide/` | Task-oriented how-tos |
| Wiki | `content/wiki/` | Pages about the wiki itself |

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

Only `title` is required. The rest:

| Key | Does |
|---|---|
| `title` | the page name, and what a `[[link]]` resolves against |
| `description` | one sentence, used in search results and meta tags |
| `type` | the page's namespace - the same word as the directory it sits in |
| `subject` | what the infobox and data templates look up, if not the title |
| `sprite` | which icon represents the page, if not the title; a map such as `{Item: Sugar cane, Placed: block 83}` shows each, labelled, in the infobox, and the first is the icon everywhere else |
| `aliases` | extra names that resolve to this page |
| `categories` | shown at the foot, indexed on `/wiki/categories/`; names from the list in `wiki.config.js` only |
| `infobox` | extra or overriding infobox rows |
| `infoboxTitle` | heading for the infobox, if not the title |
| `stub` | lists the page on `/wiki/stubs/` |
| `toc: false` | suppresses the contents box |

`redirects` is accepted as an older spelling of `aliases`, and `id` and `order`
are accepted but nothing reads them. Anything else warns, so typos surface at
build time — the full list is `KNOWN_KEYS` in `tools/lib/integrity.mjs`.

Remove `stub: true` when the page is genuinely written. That is what
`/wiki/stubs/` tracks. From then on the build fails the page if anything the
generator seeded is left: the placeholder `description` or lead (any that names
the version), the `{{stub}}` banner, or a heading with nothing under it but a
comment.

`categories` in `wiki.config.js` is the whole list, with the rule for which
pages carry each category. A page takes the one category that names its kind —
Blocks, Items, Mobs — and then every topic category whose rule it meets. Any
other name fails the build. A new category goes into that list first, not
straight onto a page.

## Never hand-type game numbers

Block ids, hardness, blast resistance, light levels, sprites, biome colours,
stack sizes, tool and armour durability, attack damage, what food heals, a
mob's starting health, and every crafting and smelting recipe are extracted
from the client jar into `data/`. They reach pages automatically:

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
  Mushroom*, *Red Mushroom* and *Clay Ball* come from. The same file joins one
  thing the game names twice: item 331 is *Redstone Dust* there and item 338
  *Sugar cane*, so each is one page with its block.
- Where an item and a block share a name, the item's icon is the picture of
  both. The block keeps its own under its id, `block 83`, for a page that wants
  to show it as it stands in the world; Sugar cane does, through `sprite`.
- One page may answer to several names, and cover several ids. `aliases` make a
  page the target for each name, and `tools/seed.mjs` reads them before it stubs
  anything, so the two mushrooms stay one article across a reseed. `subject` may
  name every id the page covers, by name where the names differ and by id where
  they do not — `{Brown: Brown Mushroom, Red: Red Mushroom}`, `{Unlit: block 61,
  Lit: block 62}`. The key becomes a column heading, so keep it to a word. The
  infobox then carries a column each, splitting only the rows where the ids
  disagree, which is usually the light level and the id itself; where the ids
  have separate sprites the picture area shows both, and where they share one it
  shows it once, full size. Six pages needed that: a lit furnace, a lit redstone
  torch, glowing redstone ore and a powered repeater all emit light their unlit
  twin does not, and the infobox used to report the twin's.

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
| `{{id\|Cobblestone}}` | the numeric id; `31:2` for a subtype; `{{id\|block 68}}` for one of several ids |
| `{{list\|blocks}}` | sortable table of a whole data set; `light`, `opacity` and `food` give the narrower tables the hubs use |
| `{{pagelist\|namespace=biome}}` | linked list of pages |
| `{{stub}}` `{{main\|X}}` `{{see also\|X}}` `{{hatnote\|…}}` `{{msgbox\|…}}` | notes |

To show template syntax without running it, wrap it in backticks or a fenced
block — code is parsed before templates are.

## Links

`[[Page Name]]` resolves against titles, slugs and aliases. `[[Page|label]]`
and `[[Page#Section]]` work as expected.

Subtypes, the damage values of one id that the game names apart, resolve too,
with no alias: `[[Charcoal]]` reaches Coal, `[[Magenta Wool]]` reaches Wool,
`[[Wooden Slab]]` reaches Stone Slab. The names come from `data/`. A subtype
with a source or a use its siblings lack has a page of its own under its name,
which a link finds first: Fern, Bone Meal, Ink Sac, Cocoa Beans, Lapis Lazuli.
One that differs only in colour or material stays on its id's page.

A link to a page that does not exist renders **red** and warns at build time.
That is the point — red links are the to-do list. **Do not delete a red link to
silence a warning.** Either write the page or leave the link.

**Inside a table, escape the pipe: `[[Water\|water]]`.** A table row is cut into
cells on every unescaped `|` before `[[ ]]` and `{{ }}` are read at all, so the
ordinary spelling is torn in half — the cell keeps `[[Water`, the rest is
dropped as a surplus column, and the link is gone. The same applies to a
template argument in a table: `{{sprite\|Iron Ore}}`. The build fails on both.

## Regenerating data and assets

Only needed if the extractors change. Requires the Beta 1.7.3 client jar and
two Babric mapping files:

```
python tools/extract/gamedata.py --out data
python tools/extract/sprites.py  --out .
node tools/seed.mjs              stub any newly discovered block/item/entity
node tools/seed.mjs --force      rebuild existing stubs from the new data
```

None of the three is vendored here. The jar is Mojang's, shipped without a
licence, like the decompiled source. Download them into one directory:

| File | From |
|---|---|
| `client.jar` | [Mojang](https://launcher.mojang.com/v1/objects/43db9b498cb67058d2e12d394e6507722e71bb45/client.jar) |
| `barn.tiny` | [barn b1.7.3+build.9](https://maven.glass-launcher.net/babric/babric/barn/b1.7.3+build.9/barn-b1.7.3+build.9-v2.jar) |
| `intermediary.tiny` | [intermediary b1.7.3](https://maven.glass-launcher.net/babric/babric/intermediary/b1.7.3/intermediary-b1.7.3-v2.jar) |

Each mappings jar is a zip holding `mappings/mappings.tiny`; extract it under
the name in the first column. These are the versions `data/` was extracted
with.

Point `B173_CACHE`, or `"cachePath"` in `wiki.local.json`, at that directory.
`B173_JAR` or `"jarPath"` is only for a jar kept somewhere else, and `--jar` and
`--cache` override both. `tools/extract/paths.py` does the finding.

Unlike the source, these are not optional: the build never opens the jar, but
the extractors are nothing without it, so a missing file is a fatal error that
says how to fix it.

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

It joins, too, where the game gives one thing two names. Item 331 is the
redstone a player carries and block 55 the dust it becomes when placed, but the
game calls them *Redstone* and *Redstone Dust*; items 331 and 338 take their
blocks' names here, so redstone and sugar cane are one page each rather than
two. The game's own name for the item then survives only in the jar, so a
joined page gives it as a sentence under its Data values, and keeps it as an
alias.

Everything else in `data/` is overwritten by the extractors.

## Writing style

This wiki is written mostly by agents, and agents overwrite. The failure has
one shape: too many words, narration where a statement would do, and the
mechanism explained when only the rule was asked for. Assume your first draft
has it.

**A page is a reference, not an essay.** The reader arrived from a search box,
wants one fact, and leaves once they have it. Everything below follows from
that.

Concise is not the same as thin. Cut words, not facts. A page that leaves out
what a block actually does is worse than one that takes too long to say it, and
the fix for a bloated page is shorter sentences, not fewer of them.

### The model to copy

The house style is minecraft.wiki's. [Wooden Stairs](https://minecraft.wiki/w/Wooden_Stairs)
and [Trading](https://minecraft.wiki/w/Trading) show it well; read one when you
are unsure how a section should read. Copy their style, not their facts: they
describe modern Minecraft. What to notice is how little happens in each
sentence:

> Wooden stairs can be broken with anything, but axes are the fastest.
>
> Each trade can be used a maximum number of times, after which the villager
> runs out of stock, and the trade becomes disabled.
>
> Growing up takes 20 minutes.

Flat, declarative, one fact each, nobody visibly writing. That is the target.

### Sentences

- **One fact per sentence.** Subject, verb, object. A sentence carrying two
  clauses joined by "and both", "which is why", "so that", or an em dash is
  usually two sentences.
- **Fact first, mechanism second.** "Wooden doors and signs don't burn", then
  the reason — not the reason built up to a conclusion.
- **Drop the mechanism when it adds nothing.** The reader wants the rule. The
  code behind it goes in the `<!-- src: -->` comment, where the next editor
  looks for it anyway.
- **No framing.** A sentence whose only job is to introduce the next paragraph
  carries no fact. "Two questions decide what happens." "The lists are short
  and literal." "Three things must be true." Cut them and start with the fact.
- **No summing up.** Do not close a section by restating it, and do not close a
  sentence with a clause that repeats its own first half.
- **One example at most**, and only where the rule is hard to apply from its
  statement. Never work arithmetic the reader can do from numbers already given.

### The lead

One sentence. Bold the page title, define the thing, stop.

```markdown
**Cobblestone** is the block dropped when [[Stone]] is mined with a pickaxe.
```

A second sentence is allowed only when it carries a fact the page does not
repeat later. A lead paragraph that previews the article is always wrong.

### Voice

- Third person, present tense. "Cobblestone drops from stone", not "you will
  get cobblestone", and never "we".
- No jokes, no enthusiasm, no personification. Blocks do not want, refuse,
  decide, or have opinions about anything.
- No hedging. "Generally", "typically", "in most cases" and "tends to" mean the
  writer did not check. Check, state the rule, then name the exceptions.
- No judging adjectives. "Extremely useful", "surprisingly", "notably",
  "unusually" describe the writer, not the game. A factual comparison is fine:
  gold *is* the fastest tool material, and saying so is reporting.
- Banned openers: "Note that", "It is worth noting", "Interestingly", "In
  fact", "Of course", "Simply", "Actually".
- Give the number, not an impression of it. "12", not "quite fast".
- Describe the game, not the source. "Branch", "returns", "flag", "guard",
  "short-circuits" and method names belong in the `<!-- src: -->` comment.
- Never justify the wiki's own choices in the content. That goes in an HTML
  comment.

### Let the page carry it

- More than about three parallel facts is a table.
- A set of things is a list, not a sentence with commas in it.
- Never restate a table or list in prose on either side of it, and never state
  its inverse either — "everything not on that list drops for a bare hand" adds
  nothing to the list.
- Never type a number a template can produce. See **Never hand-type game
  numbers** above.

### Scope

- Stay on the subject the page is named after. Ore generation belongs on the
  ore pages, not on [[Mining]].
- Strategy and tutorials belong in `content/guide/`, not on reference pages.
- **See also** takes bare links — no glosses — and only pages the body has not
  already linked. It is usually empty, and an empty one is deleted.

### Hubs and subjects

Every mechanic is explained on one page, its **hub**. A hub is a mechanic page,
such as [[Mob Spawning]], [[Mining]] or [[Damage]], or the block or structure
the mechanic belongs to, such as [[Fire]] or [[Dungeon]]. The pages the
mechanic touches are its **subjects**.

- The hub owns how the mechanic works, and the table comparing every subject.
- A subject page owns its own row of that table: the values that apply to it,
  stated as facts, with a link to the hub. It does not explain the mechanism.
- A hub does not describe one subject in full. A hub section about a single
  subject belongs on that subject's page, and the hub keeps one line and
  `{{main|Subject}}`.
- A paragraph that would be as true on a sibling's page belongs on the hub.

[[Zombie]] says zombies spawn in the dark in every Overworld biome, and links
[[Mob Spawning]]. The two random light tests stay on Mob Spawning, because
they apply to skeletons, spiders and creepers too.

When the hub has no page yet, the explanation still does not go on the subject
page. Scaffold the hub and write it there, or leave the red link for whoever
does.

### Length

There is no minimum. A page is as long as the facts about its subject, and many
are short: a sword has a recipe, its rows in two hub tables and little else, and
can be complete at fifty words. Padding a short page to look finished is the
same fault as bloating a long one.

The figures below are a signal to re-read, not a limit:

| Page | Re-read past |
|---|---|
| Block, item, biome | 300 words |
| Entity, structure, dimension | 500 words |
| Mechanic | no total, but each `###` under about 200 words |

A section running past four paragraphs is either two sections or partly another
page's material.

### The edit pass

Reread before saving and delete:

1. Every sentence of the lead after the first that does not carry its own fact.
2. Every sentence that announces, or restates, another sentence.
3. Every trailing clause that repeats what its sentence already said.
4. Every adjective that judges rather than measures.
5. Every paragraph explaining a mechanic that has its own page.
6. Every passage of prose restating a table.

If deleting a sentence loses no fact, it should not have been written.

### Before and after

Real edits made to these pages, kept here because they are the whole guide in
miniature:

- "Two questions decide what happens, and the game answers them separately: how
  long the block takes to come apart, and whether it leaves anything behind."
  → deleted. The lead is one sentence.
- "…and which one applies turns entirely on whether the player can harvest the
  block at all" → "…depending on whether the player can harvest the block at
  all".
- "1 for a bare hand or anything with no opinion about it" → "default of 1 for
  a bare hand or non-tool".
- "[[Stone]], at a hardness of 1.5, shows the whole range:" → "The following
  table shows breaking times for [[Stone]], which has a hardness of 1.5:"
- "A *negative* hardness short-circuits the other way: strength is returned as
  zero outright, and no amount of holding will ever break the block." → "A
  *negative* hardness results in negative strength, preventing the target block
  from ever being broken."
- "both are checked only on the harvestable branch" → "both are checked only
  when mining a harvestable block".
- "The lists are short and literal. A block that is not named gets no speed
  bonus, however obviously it looks like it belongs:" → deleted.
- "Mining a block the pickaxe cannot harvest is not merely fruitless but slow,
  the flat formula applying instead: [[Obsidian]] takes 50 seconds to remove
  with an [[Iron Pickaxe]] and leaves nothing." → "Mining a non-harvestable
  block always uses the slow formula."
- "Every smelt takes the same **200 ticks — 10 seconds** — whatever is being
  smelted." → "One smelt takes **200 ticks — 10 seconds**".
- "Wooden doors and signs are the exception: the furnace tests the item's id
  against the block list, and both exist only as items once they are in an
  inventory, so neither burns." → "Wooden doors and signs don't burn." followed
  by the test that decides it.
- "- [[Smelting]] — the other way to transform items" → deleted; the body
  already linked it.
- Two whole sections of [[Mining]], on where the ores are and on the hazards of
  digging, were deleted. The first belongs to the ore pages, the second to a
  guide.

## Conventions

- `##` headings follow, in this order, skipping what does not apply: **Obtaining**
  (mining, crafting, drops, natural generation), **Usage** (what it does and
  what it makes), **Behaviour** (for mobs and mechanics), **Data values** (ids
  and translation keys).
- A mob is not obtained and used: mob pages run **Spawning** (light level,
  biome, what it needs to stand on, pack size), **Drops** (what it leaves on
  death, and how much), **Behaviour** (movement, what provokes it, how it
  attacks), **Data values** (the entity network id) instead.
  `tools/lib/mobs.mjs` holds the list of which entities count, and both
  generators read it.
- A place is not obtained either. A dimension page runs **Reaching it** (how a
  player travels there and back, and what the trip costs), **Terrain**,
  **Mobs**, **Data values** (the dimension id). A structure page runs
  **Generation** (where it appears, how often, and what decides), **Contents**
  (the blocks it is made of, and anything it holds), **Usage**. Both shapes are
  in `PROSE_SECTIONS` in `tools/new-page.mjs`, which is what `npm run new`
  scaffolds; nothing in `data/` answers to a dimension or a structure, so these
  pages carry no infobox and no recipe templates.
- Always link the first mention of another subject in a section. Don't link further mentions within that section.
  To discover what subjects can be linked, always check what pages exist before writing.
- When linking, use display text to match case/grammar. e.g. `Breaking clay drops [[Clay Ball|clay balls]]`
- **Data values** is a list, one kind of value per line, with every id from
  `{{id}}`:

  ```markdown
  ## Data values

  - Block ID: {{id|Sign}}, {{id|block 68}}
  - Item ID: {{id|item 323}}
  - Translation key: `tile.sign`, `item.sign`
  ```

  Give the name when it resolves to that id. Use `block 68` or `item 323` for a
  second id, or for the item of a name the block also answers to. A subtype
  shows its metadata or damage value, so `{{id|Fern}}` gives `31:2`. Mobs take
  `- Entity network ID: {{id|Chicken}}`, with the name as `data/` spells it
  (`PigZombie`); an `{{id}}` that resolves to nothing warns. A fact the list
  cannot hold, such as what the game itself calls the block, follows it as a
  sentence. Stubs seeded before this rule carry typed ids; replace them when
  writing the page.
- Commit messages: short imperative subject, then why. Commit often, never leave the tree dirty.
- Stage by path, `git add content/item/iron-sword.md`, never `git add -A`,
  `git add .` or `git commit -a`. Other agents and people may have work in the
  same tree. Do not push unless asked: pushing to `main` publishes the site.

## Several agents at once

Agents writing pages in parallel each work in their own git worktree, under
`.claude/worktrees/`. `.claude/settings.json` branches those from the local
HEAD rather than from `origin/main`, so work not yet pushed is in every
worktree. Node finds `node_modules` in the main checkout above, and the tools
find the decompiled source through it, so a worktree needs no setup. Before
writing, `npm run check` must print `Verified against`.

Each agent owns a fixed list of files and edits nothing else: no other page,
and none of `AGENTS.md`, `data/`, `tools/` or `wiki.config.js`. A page it wants
that does not exist stays a red link and goes in its report; two agents
scaffolding the same page is a merge conflict. A fact that belongs on a page it
does not own goes in its report too, with its `src:` line, rather than onto the
page.

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
