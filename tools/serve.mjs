#!/usr/bin/env node
// Dev server: serves site/ and rebuilds whenever content, theme, data or the
// build itself changes.
//
//   npm run dev            http://localhost:8173
//   npm run dev -- 9000    a different port
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { watch, existsSync } from 'node:fs';
import { join, extname, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const OUT = join(ROOT, 'site');
const PORT = Number(process.argv[2]) || Number(process.env.PORT) || 8173;

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.txt': 'text/plain; charset=utf-8',
};

let building = false;
let queued = false;

function build() {
  if (building) { queued = true; return; }
  building = true;
  const t0 = Date.now();
  const child = spawn(process.execPath, [join(ROOT, 'tools', 'build.mjs'), '--quiet'],
    { cwd: ROOT, stdio: ['ignore', 'pipe', 'pipe'] });
  let err = '';
  child.stdout.on('data', (d) => { err += d; });
  child.stderr.on('data', (d) => { err += d; });
  child.on('close', (code) => {
    building = false;
    const ms = Date.now() - t0;
    if (code === 0) {
      process.stdout.write(`  rebuilt in ${ms}ms${err.trim() ? '\n' + err.trimEnd() + '\n' : '\n'}`);
    } else {
      process.stdout.write(`  build failed:\n${err.trimEnd()}\n`);
    }
    if (queued) { queued = false; build(); }
  });
}

let timer = null;
const schedule = () => {
  clearTimeout(timer);
  timer = setTimeout(build, 80);          // coalesce editor save bursts
};

for (const dir of ['content', 'theme', 'data', 'tools']) {
  const full = join(ROOT, dir);
  if (!existsSync(full)) continue;
  watch(full, { recursive: true }, (_event, file) => {
    if (file && /\.(md|css|js|mjs|json)$/.test(file)) schedule();
  });
}
watch(join(ROOT, 'wiki.config.js'), schedule);

async function serveFile(res, path) {
  const body = await readFile(path);
  res.writeHead(200, {
    'Content-Type': TYPES[extname(path)] || 'application/octet-stream',
    'Cache-Control': 'no-cache',
  });
  res.end(body);
}

createServer(async (req, res) => {
  try {
    const url = decodeURIComponent(req.url.split('?')[0]);
    let path = join(OUT, url);
    // Directory URLs like /block/stone/ map to that directory's index.html.
    try {
      if ((await stat(path)).isDirectory()) path = join(path, 'index.html');
    } catch {
      if (!extname(path)) path = join(OUT, url, 'index.html');
    }
    await serveFile(res, path);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end('<h1>404</h1><p>Not built. Try <a href="/">the main page</a>.</p>');
  }
}).listen(PORT, () => {
  console.log(`\n  Beta 1.7.3 Wiki  ->  http://localhost:${PORT}`);
  console.log('  watching content/, theme/, data/, tools/ ...\n');
  build();
});
