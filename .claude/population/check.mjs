#!/usr/bin/env node
// Checks for the stub population. See README.md.
//
//   node .claude/population/check.mjs                      every stub in exactly one group
//   node .claude/population/check.mjs --group tools        a group's pages, notes and hubs
//   node .claude/population/check.mjs --group tools --changes
//        files changed outside the group, since this worktree branched
//   node .claude/population/check.mjs --group tools --changes --branch <branch>
//        the same for a finished branch, run from the main checkout
//
// Exits 1 when something is wrong, so it can gate a dispatch or a merge.
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const { groups } = JSON.parse(readFileSync(join(ROOT, '.claude', 'population', 'groups.json'), 'utf8'));

const args = process.argv.slice(2);
const opt = (name) => {
  const i = args.indexOf(name);
  return i < 0 ? undefined : args[i + 1];
};

const fileOf = (page) => join(ROOT, 'content', `${page}.md`);
const isStub = (file) => {
  const fm = readFileSync(file, 'utf8').replace(/\r\n/g, '\n').match(/^---\n([\s\S]*?)\n---/);
  return Boolean(fm && /^stub:\s*true\s*$/m.test(fm[1]));
};
const status = (page) => (!existsSync(fileOf(page)) ? 'to create' : isStub(fileOf(page)) ? 'stub' : 'written');
const git = (...a) => execFileSync('git', a, { cwd: ROOT, encoding: 'utf8' }).trim();

function allStubs() {
  const out = [];
  const content = join(ROOT, 'content');
  for (const ns of readdirSync(content)) {
    if (!statSync(join(content, ns)).isDirectory()) continue;
    for (const f of readdirSync(join(content, ns))) {
      if (f.endsWith('.md') && isStub(join(content, ns, f))) out.push(`${ns}/${basename(f, '.md')}`);
    }
  }
  return out;
}

function coverage() {
  let bad = 0;
  const owner = new Map();
  for (const g of groups) {
    for (const p of g.pages) {
      if (owner.has(p)) {
        console.log(`  ${p} is in both "${owner.get(p)}" and "${g.id}"`);
        bad++;
      }
      owner.set(p, g.id);
    }
  }
  const orphans = allStubs().filter((s) => !owner.has(s));
  for (const s of orphans) console.log(`  stub content/${s}.md is in no group`);
  bad += orphans.length;

  for (const g of groups) {
    const counts = { stub: 0, written: 0, 'to create': 0 };
    for (const p of g.pages) counts[status(p)]++;
    const missing = g.hubs.filter((h) => !existsSync(fileOf(h)));
    console.log(`${g.id.padEnd(22)} ${g.phase.padEnd(7)} ${String(counts.stub).padStart(3)} stubs, ` +
      `${counts.written} written, ${counts['to create']} to create` +
      (missing.length ? `   waiting on: ${missing.join(', ')}` : ''));
  }
  console.log(bad ? `\n${bad} problem(s).` : '\nEvery stub is in exactly one group.');
  return bad;
}

function show(g) {
  console.log(`${g.title} (${g.id}), phase: ${g.phase}\n\nPages you own:`);
  for (const p of g.pages) console.log(`  content/${p}.md  ${status(p)}`);
  console.log('\nHubs you rely on and must not repeat:');
  const missing = g.hubs.filter((h) => !existsSync(fileOf(h)));
  for (const h of g.hubs) console.log(`  content/${h}.md  ${existsSync(fileOf(h)) ? 'present' : 'MISSING'}`);
  console.log('\nNotes:');
  for (const n of g.notes) console.log(`  - ${n}`);
  if (missing.length) {
    console.log(`\n${missing.length} hub(s) missing. Do not start: this worktree may have branched from the wrong commit.`);
  }
  return missing.length;
}

// The branch the main checkout is on: a worktree branched from it, so the
// merge base with it is where this worktree's own changes begin.
function defaultBase() {
  const common = resolve(ROOT, git('rev-parse', '--git-common-dir'));
  const branch = execFileSync('git', ['rev-parse', '--abbrev-ref', 'HEAD'], { cwd: dirname(common), encoding: 'utf8' }).trim();
  return git('merge-base', 'HEAD', branch);
}

function changes(g) {
  const branch = opt('--branch');
  const lines = (s) => s.split('\n').filter(Boolean);
  let changed;
  if (branch) {
    changed = lines(git('diff', '--name-only', `HEAD...${branch}`));
  } else {
    const base = opt('--base') || defaultBase();
    changed = [...lines(git('diff', '--name-only', base)), ...lines(git('ls-files', '--others', '--exclude-standard'))];
  }
  const allowed = new Set(g.pages.map((p) => `content/${p}.md`));
  const outside = [...new Set(changed)].filter((f) => !allowed.has(f));
  for (const f of outside) console.log(`  ${f} is not in group "${g.id}"`);
  console.log(outside.length
    ? `\n${outside.length} file(s) changed outside the group. Revert them, and put what they held in the report.`
    : `${changed.length} file(s) changed, all in group "${g.id}".`);
  return outside.length;
}

let failures;
const id = opt('--group');
if (!id) {
  failures = coverage();
} else {
  const g = groups.find((x) => x.id === id);
  if (!g) {
    console.error(`no group "${id}". Groups: ${groups.map((x) => x.id).join(', ')}`);
    process.exit(1);
  }
  failures = args.includes('--changes') ? changes(g) : show(g);
}
process.exit(failures ? 1 : 0);
