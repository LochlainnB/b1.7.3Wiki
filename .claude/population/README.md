# Populating the stubs

The plan for writing every stub page with parallel agents, one agent per group
of related pages. It is for whoever runs the population, whether a person or
the Claude Code session doing the dispatching. The agents themselves read
`brief.md`.

| File | What it is |
|---|---|
| `groups.json` | Which group owns each page, what hubs it relies on, and notes on who says what |
| `brief.md` | The instructions every page-writing agent follows |
| `check.mjs` | Checks that every stub has a group, shows one group, and catches edits outside a group |

Delete this directory once `/wiki/stubs/` is empty.

## Before dispatching

All of these must hold. Agents cannot fix any of them from inside a worktree.

1. **The hub pages exist.** The `hubs` group is written first, one page at a
   time and reviewed, not dispatched. `node .claude/population/check.mjs`
   prints `waiting on:` beside every group whose hubs are still missing. If a
   hub was written under a different name from the one `groups.json` guessed,
   rename it in `groups.json`.
2. **Every stub has a group.** `node .claude/population/check.mjs` exits 0.
   A new stub must be added to a group before dispatch.
3. **`npm run check` ends with `0 errors`** and prints `Verified against`.
4. **Everything is committed.** Each worktree starts from the local HEAD
   (`.claude/settings.json` sets that). Uncommitted work, this directory
   included, is not in any worktree.

## Dispatching

Run the two `pilot` groups first, `tools` and `hostile-mobs`. The wiki has no
finished item page or mob page yet, and these two become the pattern the rest
copy. Review them, merge them, and correct `brief.md` or the notes for
whatever went wrong. Then dispatch the `main` groups, about five at a time, so
each batch's reports can be read before the next starts.

For each group, from a Claude Code session in the main checkout, one Agent
call with `isolation: "worktree"` and `run_in_background: true`, and this
prompt:

```
Write the "<id>" group of pages on the Beta 1.7.3 wiki. Your group id is
<id>. Read .claude/population/brief.md first and follow it exactly. End with
the report it describes.
```

## Merging a finished group

The agent's result names its branch. From the main checkout:

1. `node .claude/population/check.mjs --group <id> --changes --branch <branch>`
   must report every file inside the group. Groups own separate files, so a
   clean result means the merge cannot conflict.
2. Read the diff. The pilots especially: they set the pattern.
3. `git merge --no-ff <branch>`, then `npm run check`, which must end with
   `0 errors`.
4. Copy the report's **For other pages**, **Hub or data problems** and
   **Red links left** into one running list.
5. Remove the worktree and its branch:
   `git worktree remove .claude/worktrees/<name>` and `git branch -d <branch>`.

## After the last group

Work through the running list in one pass, with a single agent, once no group
is still being written. Hand-offs go onto the pages they were meant for, and
red links become pages or stay red on purpose.
