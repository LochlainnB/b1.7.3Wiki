// Authored scenes are separate from the generated game registries in data/.
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { gzipSync } from 'node:zlib';

const LIMIT = 10000;
const point = (v) => Array.isArray(v) && v.length === 3 && v.every(Number.isSafeInteger);
const assetName = (v) => typeof v === 'string' && /^[a-z0-9-]+\.json$/.test(v);

export function expandBuild(scene, models) {
  const occupied = new Map();
  const place = (at, block) => {
    if (!point(at)) throw new Error('block position must have three integer coordinates');
    if (!Object.hasOwn(models, block)) throw new Error(`unsupported block ${block}`);
    occupied.set(at.join(','), { at, block });
    if (occupied.size > LIMIT) throw new Error(`scene exceeds ${LIMIT} blocks`);
  };
  for (const fill of scene.fills || []) {
    if (!point(fill.from) || !point(fill.to) || fill.from.some((v, i) => v > fill.to[i])) {
      throw new Error('fill bounds must be ordered integer coordinates');
    }
    const volume = fill.from.reduce((n, v, i) => n * (fill.to[i] - v + 1), 1);
    if (volume > LIMIT) throw new Error(`fill exceeds ${LIMIT} blocks`);
    for (let x = fill.from[0]; x <= fill.to[0]; x++) {
      for (let y = fill.from[1]; y <= fill.to[1]; y++) {
        for (let z = fill.from[2]; z <= fill.to[2]; z++) place([x, y, z], fill.block);
      }
    }
  }
  const explicit = new Set();
  for (const entry of scene.blocks || []) {
    place(entry.at, entry.block); // Explicit placements override the floor/fills.
    const key = entry.at.join(',');
    if (explicit.has(key)) throw new Error(`duplicate authored block at ${key}`);
    explicit.add(key);
  }
  for (const at of scene.omissions || []) {
    if (!point(at) || !occupied.delete(at.join(','))) throw new Error('omission must name an occupied block');
  }
  const blocks = [...occupied.values()];
  if (!blocks.length) throw new Error('build has no blocks');
  const minY = Math.min(...blocks.map((b) => b.at[1]));
  const maxY = Math.max(...blocks.map((b) => b.at[1]));
  if (maxY - minY >= 32) throw new Error('build exceeds 32 vertical layers');
  return { blocks, minY, layers: maxY - minY + 1 };
}

// Legacy Alpha schematics store block IDs and metadata, not rendered geometry.
export function encodeSchematic({ blocks }) {
  const min = [0, 1, 2].map((i) => Math.min(...blocks.map((b) => b.at[i])));
  const size = min.map((v, i) => Math.max(...blocks.map((b) => b.at[i])) - v + 1);
  const [width, height, length] = size;
  const volume = width * height * length;
  // Sparse placements can have enormous bounds despite the occupied-block limit.
  if (size.some((v) => v > 32767) || volume > 1000000) {
    throw new Error('schematic bounds exceed 32767 per axis or 1000000 cells');
  }
  const ids = Buffer.alloc(volume), metadata = Buffer.alloc(volume);
  for (const { at, block } of blocks) {
    const [id, data] = block.split(':', 2).map(Number);
    if (!Number.isInteger(id) || id < 0 || id > 255 ||
        !Number.isInteger(data) || data < 0 || data > 15) {
      throw new Error(`unsupported schematic block ${block}`);
    }
    const [x, y, z] = at.map((v, i) => v - min[i]);
    const index = x + width * (z + length * y);
    ids[index] = id;
    metadata[index] = data;
  }

  const string = (text) => {
    const bytes = Buffer.from(text);
    const prefix = Buffer.alloc(2);
    prefix.writeUInt16BE(bytes.length);
    return Buffer.concat([prefix, bytes]);
  };
  const tag = (type, name, payload) => Buffer.concat([Buffer.from([type]), string(name), payload]);
  const short = (value) => {
    const bytes = Buffer.alloc(2);
    bytes.writeInt16BE(value);
    return bytes;
  };
  const byteArray = (bytes) => {
    const prefix = Buffer.alloc(4);
    prefix.writeInt32BE(bytes.length);
    return Buffer.concat([prefix, bytes]);
  };
  const emptyCompounds = Buffer.from([10, 0, 0, 0, 0]);
  return gzipSync(tag(10, 'Schematic', Buffer.concat([
    tag(2, 'Width', short(width)),
    tag(2, 'Height', short(height)),
    tag(2, 'Length', short(length)),
    tag(8, 'Materials', string('Alpha')),
    tag(7, 'Blocks', byteArray(ids)),
    tag(7, 'Data', byteArray(metadata)),
    tag(9, 'Entities', emptyCompounds),
    tag(9, 'TileEntities', emptyCompounds),
    Buffer.from([0]),
  ])));
}

export function validateMesh(mesh, root) {
  if (mesh.format !== 1) throw new Error('unsupported mesh format');
  const models = mesh.models ? Object.values(mesh.models) : mesh.variants;
  if (!Array.isArray(models) || !models.length) throw new Error('mesh has no models');
  for (const model of models) {
    if (!Array.isArray(model.faces) || !model.faces.length) throw new Error('model has no faces');
    for (const face of model.faces) {
      if (!Array.isArray(face.corners) || face.corners.length !== 4 ||
          face.corners.some((v) => !Array.isArray(v) || v.length !== 5 || !v.every(Number.isFinite)) ||
          !Array.isArray(face.normal) || face.normal.length !== 3 || !face.normal.every(Number.isFinite) ||
          !Array.isArray(face.rgba) || face.rgba.length !== 4 || !face.rgba.every(Number.isFinite)) {
        throw new Error('invalid mesh face');
      }
      for (const flag of ['lit', 'textured', 'blend', 'alpha_test', 'depth_test', 'depth_mask']) {
        if (typeof face[flag] !== 'boolean') throw new Error(`invalid mesh state ${flag}`);
      }
      if (![514, 515].includes(face.depth_func) ||
          !['1,1', '770,771'].includes(String(face.blend_func))) throw new Error('unsupported mesh pass');
      if (face.textured && (typeof face.texture !== 'string' ||
          !/^[a-zA-Z0-9_/-]+\.png$/.test(face.texture) || face.texture.includes('..') ||
          face.texture.startsWith('/') || !existsSync(join(root, 'assets/textures', face.texture)))) {
        throw new Error(`missing or invalid texture ${face.texture}`);
      }
    }
  }
}

export function loadViewers(root) {
  const directory = join(root, 'viewer/scenes');
  const scenes = new Map();
  for (const file of readdirSync(directory).filter((name) => name.endsWith('.json')).sort()) {
    const id = file.slice(0, -5);
    const authored = JSON.parse(readFileSync(join(directory, file), 'utf8'));
    if (!/^[a-z0-9-]+$/.test(id) || !['build', 'entity'].includes(authored.kind) ||
        !authored.title || !authored.caption || !assetName(authored.mesh)) {
      throw new Error(`invalid viewer scene ${id}`);
    }
    const mesh = JSON.parse(readFileSync(join(root, 'assets/viewer', authored.mesh), 'utf8'));
    validateMesh(mesh, root);
    const scene = { kind: authored.kind, title: authored.title, caption: authored.caption, mesh: authored.mesh };
    if (scene.kind === 'build') {
      if (!mesh.models) throw new Error(`${id} needs block models`);
      Object.assign(scene, expandBuild(authored, mesh.models));
    } else {
      if (!mesh.variants || mesh.variants.some((v) => typeof v.label !== 'string' || !v.label)) {
        throw new Error(`${id} needs labelled entity variants`);
      }
      scene.variants = mesh.variants.map((v) => v.label);
    }
    scenes.set(id, scene);
  }
  return scenes;
}
