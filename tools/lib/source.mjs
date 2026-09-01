// Locating the decompiled Beta 1.7.3 source tree.
//
// The source is Mojang's code with no licence attached, so it is never vendored
// into this repository. It lives outside, is read-only, and is found by:
//
//   1. the B173_SOURCE environment variable,
//   2. "sourceDir" in wiki.local.json (gitignored),
//   3. a sibling directory named b1.7.3Source.
//
// Everything here treats the tree as strictly read-only. Nothing in this
// repository ever writes to it.
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join, resolve } from 'node:path';

/** Where the client tree's flat package lives, relative to the source root. */
export const CLIENT_SRC = join('minecraft', 'net', 'minecraft', 'src');
export const SERVER_SRC = join('minecraft_server', 'net', 'minecraft', 'src');

const VERSION_MARKER = 'Minecraft Beta 1.7.3';

/**
 * Resolve the source tree.
 *
 * Returns { dir, ok, reason }. A missing tree is not an error: the wiki builds
 * and validates without it, and only the source-backed checks are skipped.
 */
export function findSource(root) {
  const candidates = [];
  if (process.env.B173_SOURCE) {
    candidates.push({ dir: resolve(process.env.B173_SOURCE), from: 'B173_SOURCE' });
  }
  const localConfig = join(root, 'wiki.local.json');
  if (existsSync(localConfig)) {
    try {
      const local = JSON.parse(readFileSync(localConfig, 'utf8'));
      if (local.sourceDir) {
        candidates.push({ dir: resolve(root, local.sourceDir), from: 'wiki.local.json' });
      }
    } catch (err) {
      return { dir: null, ok: false, reason: `wiki.local.json is not valid JSON (${err.message})` };
    }
  }
  candidates.push({ dir: resolve(root, '..', 'b1.7.3Source'), from: 'sibling directory' });

  for (const { dir, from } of candidates) {
    if (!existsSync(join(dir, CLIENT_SRC, 'Block.java'))) {
      // An explicitly configured path that is not there is worth saying out
      // loud; the conventional sibling simply not existing is not.
      if (from !== 'sibling directory') {
        const want = join(CLIENT_SRC, 'Block.java').replace(/\\/g, '/');
        return { dir, ok: false, reason: `${from} points at ${dir}, which has no ${want}` };
      }
      continue;
    }
    const marker = join(dir, 'minecraft', 'net', 'minecraft', 'client', 'Minecraft.java');
    if (existsSync(marker) && !readFileSync(marker, 'utf8').includes(VERSION_MARKER)) {
      return { dir, ok: false, reason: `${dir} is a decompile of a different version (no "${VERSION_MARKER}" in Minecraft.java)` };
    }
    return { dir, ok: true, from, reason: null };
  }
  return {
    dir: null,
    ok: false,
    reason: 'no decompiled source found (set B173_SOURCE or wiki.local.json "sourceDir")',
  };
}

/** Read one class from the client tree, falling back to the server tree. */
export function readClass(source, name, { side = 'client' } = {}) {
  const order = side === 'server' ? [SERVER_SRC, CLIENT_SRC] : [CLIENT_SRC, SERVER_SRC];
  for (const pkg of order) {
    const file = join(source.dir, pkg, `${name}.java`);
    if (existsSync(file)) return readFileSync(file, 'utf8');
  }
  return null;
}

/** Class names present in a tree, without the .java suffix. */
export function listClasses(source, pkg = CLIENT_SRC) {
  const dir = join(source.dir, pkg);
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((f) => f.endsWith('.java'))
    .map((f) => f.slice(0, -5))
    .sort();
}
