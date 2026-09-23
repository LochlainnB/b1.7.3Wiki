---
name: b173-wiki
description: Answer questions about how Minecraft Beta 1.7.3 works - mobs, blocks, redstone, spawning, world generation, crafting, any game mechanic - by reading the b1.7.3 wiki first and the decompiled game source when the wiki falls short, then offering to write what was learned back to the wiki. Use for any factual question about Beta 1.7.3 behaviour, and for writing or correcting wiki pages.
---

# Answering Beta 1.7.3 questions

Two sources of truth, in this order:

- **The wiki**: `content/` in this repository. Edit this.
- **The game**: a decompiled copy of Beta 1.7.3, outside this repository. Read
  only. `npm run check` prints where it is, and `AGENTS.md` says where it is
  looked for. If none is installed, tell the user so rather than answering
  from memory.

The wiki is what has already been established. The source is the game itself and
settles anything the wiki does not, or gets wrong. **Never answer from memory of
modern Minecraft.** Beta 1.7.3 is fifteen years of changes away from current
behaviour, and confident recall is the main way this goes wrong: no hunger, no
experience, no sprinting, different redstone, different mob AI, different world
generation.

## The loop

1. **Search the wiki.** If it answers the question, answer and stop.
2. **Read the source** when the wiki does not answer it, or looks wrong.
3. **Answer the question**, saying which source it came from.
4. **Then offer the wiki edit** — never make it unprompted. Wait for a yes.

Step 4 is separate from step 3 on purpose. Answer first, in full; the wiki
proposal comes after, as an offer.

**Dispatched to write pages?** If a brief assigned you a list of pages, the
brief is the yes. Write those pages without offering, and touch nothing outside
the list. Where the brief and this skill differ, the brief wins.

## 1. Search the wiki

```bash
rg -i "slime" content/          # every page that mentions it
ls content/entity/              # what pages exist in a namespace
cat content/entity/slime.md     # read the page
```

`content/` is the wiki. A file's path is its URL: `content/block/mossy-cobblestone.md`
serves at `/block/mossy-cobblestone/`.

**A stub is not an answer.** Most pages carry `stub: true` in their frontmatter
and contain nothing but headings, an auto-built infobox and recipe templates.
The infobox numbers and the recipe grids are real and can be quoted — both come
from the extracted data — but empty prose sections mean the wiki has nothing to
say. Treat that as a
miss and go to the source.

Watch for a **red link** in a page you read: `[[Dungeon]]` pointing at a page
that does not exist. Red links are the wiki's to-do list, and one on the topic
being asked about is a strong signal that step 4 is worth offering.

## 2. Read the source

**Read `SOURCEMAP.md` in this directory first.** It maps question to class —
mob spawning to `SpawnerAnimals`, furnace timings to `TileEntityFurnace`,
ore generation to `ChunkProviderGenerate` — and lists what is where. Going in
without it means searching 675 classes by guesswork.

The three things that will otherwise cost time:

- **Always read `minecraft/net/minecraft/src/`, the client tree.** It carries the
  same gameplay code as the server tree but is far better named. Drop to
  `minecraft_server/` only for the 41 server-only classes or for a genuine
  client/server difference.
- **`var1`, `var2` locals everywhere.** Read the surrounding code; do not expect
  a variable name to tell you anything.
- **`func_25027_m` and `field_401_a` are real, finished names** for the ~6% of
  members that were never named. Quote them as they are.

The tree is **read-only**. Nothing in this workflow writes to it, ever.

## 3. Answer

Answer the question directly. Say where it came from, and cite the class and
method for anything read from source, so the user can check it:

> Slimes spawn below Y=16, and only in chunks where a hash of the world seed and
> the chunk coordinates comes out zero — about one chunk in ten. Each attempt in
> such a chunk then succeeds one time in ten. Light level is never checked:
> `EntitySlime` overrides `getCanSpawnHere` outright rather than inheriting
> `EntityMob`'s light test. — `EntitySlime.getCanSpawnHere`, `Chunk.getRandomWithSeed`

If the source does not settle it either, say so plainly. "The code does not make
this clear" is a real answer; a guess dressed as a fact is not.

## 4. Offer the wiki edit

Only when you learned something the wiki does not already say. Offering nothing
is correct when the wiki already had the answer.

Be specific enough that the user can approve without asking what you mean —
name the file, the section, whether it is new or a correction, and show the
actual prose:

```
This isn't on the wiki. I can add it:

  File     content/entity/slime.md
  Section  ## Spawning  (new — the page is a stub)
  From     EntitySlime.java:134, SpawnerAnimals.java:130

  Slimes spawn only below Y=16, and only in chunks where a hash of the world
  seed and the chunk coordinates comes out to zero — roughly one chunk in ten.
  Within such a chunk each spawn attempt succeeds one time in ten. Light level
  does not affect slime spawning. Slimes above the smallest size additionally
  require a difficulty above Peaceful.

Add it?
```

For a **correction**, show what is there now and what replaces it, and say what
made the current text wrong:

```
  content/block/redstone-torch.md says a redstone torch emits light 8.
  Block.java:668 sets 0.5F, and setLightValue truncates ((int)(15.0F * 0.5F)),
  so it is 7. Replace that sentence?
```

Then:

- **Wait.** Do not apply an edit that has not been approved.
- If declined, leave no trace — no file changes, no notes.
- If approved, make the edit, then run `npm run check` from the wiki root and
  report the result. **It must end with `0 errors`.** If the edit broke the
  build, fix it or revert it; do not leave it failing. A warning that names a
  template to add — `data/ has 2 crafting recipes for "X" that this page never
  shows` — is also yours to fix: the wiki holds that data and the page is simply
  not displaying it.

### Writing the edit

`AGENTS.md` in the wiki root is the full contributor guide — read it before a
first edit in a session. The four rules that matter most:

- **Describe Beta 1.7.3 and nothing else.** No `## History` sections, ever. No
  "this changed in 1.8", no "in modern versions", no Java/Bedrock split.
- **Never hand-type game numbers.** Ids, hardness, blast resistance, light
  levels, stack sizes, durability, attack damage, healing, mob health and
  recipes come from `data/` through the infobox and the `{{crafting}}`,
  `{{smelting}}`, `{{id}}` templates. If you are typing "hardness of 2" into
  prose, the infobox already says it.
- **Remove `stub: true`** when a page stops being a stub. That is what
  `/wiki/stubs/` tracks.
- **Do not delete a red link** to silence a build warning. Write the page or
  leave the link.

Record where a fact came from, as an HTML comment after the passage:

```markdown
Slimes spawn only below Y=16, and only in chunks where a hash of the world seed
and the chunk coordinates comes out to zero.
<!-- src: EntitySlime.java:134 getCanSpawnHere -->
```

The next agent to touch that claim can then verify it in one step instead of
re-deriving it. Line numbers are stable — the source never changes.

If the answer needs a page that does not exist yet, scaffold it rather than
burying the fact somewhere loosely related:

```bash
npm run new -- entity "Slime"
```

## When the wiki and the source disagree

The source wins. Say so in the answer rather than quietly correcting, and
propose the fix as a correction under step 4 — a wrong fact on the wiki is worth
more attention than a missing one, because a reader has no way to tell it is
wrong.

If the disagreement is in a **number** rather than prose — an infobox value, an
id, a recipe — that is not a page edit. It means `data/` is wrong, which is a
bug in the extractors in `tools/extract/`. Say so and stop; `npm run check`
cross-checks all of `data/` against the source and is the right place to fix it.
