# Brief: writing one group of pages

You have been dispatched to write one group of stub pages on the Beta 1.7.3
wiki. Your prompt names the group's id. Other agents are writing the other
groups at the same time, each in its own worktree, and nobody is available to
answer questions. Where something is unclear, make the conservative choice and
say so in your report.

This brief is your approval to write every page in your group. Write them
without offering first. Where this brief and the `b173-wiki` skill differ, this
brief wins.

## 1. Before writing

1. Run `npm run check`. It must print `Verified against <path>` and end with
   `0 errors`. If it prints `Source cross-check skipped`, stop and report:
   without the source you would be writing from memory, and memory of Minecraft
   is memory of later versions.
2. Run `node .claude/population/check.mjs --group <id>`. It lists the pages you
   own, the hub pages you rely on, and notes for your group. If it reports a
   hub missing, stop and report: your worktree started from the wrong commit.
3. Read `AGENTS.md` in full. **Writing style**, **Hubs and subjects** and
   **Conventions** are the rules this work is judged by.
4. Read every hub page your group lists, all the way through. Those pages
   already say what they say, and your pages link to them, not repeat them.
5. Read `.claude/skills/b173-wiki/SOURCEMAP.md` before opening the source.

## 2. What you may change

Only the files `check.mjs` listed for your group. A listed page that does not
exist yet is yours to create with `npm run new`.

Nothing else. Leave other pages alone, even to fix a typo or add a link, and
leave `AGENTS.md`, `data/`, `tools/`, `wiki.config.js` and this directory
alone too. Instead:

- A page you want to link that does not exist: link it anyway, leave it red,
  and list it in your report.
- A fact that belongs on a page you do not own: list it in your report, with
  its `src:` line.
- Something on a hub that looks wrong: list it in your report, with the source
  that says otherwise.
- A number in the infobox or a recipe that disagrees with the source: list it
  in your report. That is a bug in `data/`, not a page edit.

## 3. Writing the pages

- Write one page completely first, then the rest of the group to the same
  shape: the same sections in the same order, and the same wording for the
  same kind of fact. Your notes name which page to start with, when it matters.
- Rewrite the whole stub: the lead, the frontmatter `description`, the
  categories, and the Data values in the format **Conventions** gives. Remove
  `{{stub|…}}` and `stub: true`.
- Keep every `{{crafting}}`, `{{smelting}}` and `{{used in}}` the stub carries.
  Keep `subject` maps and `aliases`.
- Choose categories from `categories` in `wiki.config.js` only, using the rule
  written next to each.
- State your subject's own values and link the hub for how they come about.
  If a paragraph would be as true on a sibling page, it belongs on the hub.
- Cite every fact read from the source with a `<!-- src: -->` comment.
- Where the source does not settle something, leave it out and leave a
  `<!-- check: … -->` comment saying what is unsettled.
- A page can be short. A sword or a helmet is complete at about fifty words.
  Do not pad.

## 4. Before finishing

1. Run `npm run check`. It must end with `0 errors`. Warnings naming your own
   files must be red links you intend to leave, and nothing else.
2. Run `node .claude/population/check.mjs --group <id> --changes`. It must
   report every changed file in your group. If it lists anything else, revert
   that file.
3. Commit your pages by path, as **Conventions** says, with a message like
   `docs(<id>): write the <group title> pages`. Do not merge, push or rebase.

## 5. Report

Your last message is read by the person merging your work, not by a reader of
the wiki. Keep it to these headings, and leave out any that are empty:

- **Written**: how many pages, and any listed page left as a stub, with the
  reason.
- **Red links left**: each missing page, and which of your pages link it.
- **For other pages**: each fact that belongs elsewhere, with the page it
  belongs on and its `src:` line.
- **Hub or data problems**: anything on a hub or in `data/` that the source
  contradicts, with the source.
- **Unsettled**: every `<!-- check: -->` you left, and on which page.
- **Branch**: the branch and the last commit.
