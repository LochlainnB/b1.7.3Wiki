import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, mkdirSync, mkdtempSync, copyFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadViewers, expandBuild, validateMesh } from './lib/viewers.mjs';
import { renderTemplate } from './lib/templates.mjs';
import { visibleFaces, faceBatches, faceGeometry, blockEdges } from '../theme/viewer-mesh.js';

const root = fileURLToPath(new URL('../', import.meta.url));
const read = (file) => JSON.parse(readFileSync(new URL(`../${file}`, import.meta.url), 'utf8'));
const models = read('assets/viewer/block-models.json').models;
const creeper = read('assets/viewer/creeper.json');
const scenes = loadViewers(root);

test('scene files are discovered by filename without a shared catalog', (t) => {
  const fixture = mkdtempSync(join(tmpdir(), 'wiki-viewers-'));
  t.after(() => rmSync(fixture, { recursive: true, force: true }));
  const directory = join(fixture, 'viewer/scenes');
  mkdirSync(directory, { recursive: true });
  mkdirSync(join(fixture, 'assets/viewer'), { recursive: true });
  mkdirSync(join(fixture, 'assets/textures'), { recursive: true });
  for (const file of ['viewer/block-models.json', 'textures/terrain.png']) {
    copyFileSync(join(root, 'assets', file), join(fixture, 'assets', file));
  }
  const authored = { kind: 'build', title: 'First build', caption: 'Test fixture',
    mesh: 'block-models.json', blocks: [{ at: [-3, 2, 1], block: '1:0' }] };
  writeFileSync(join(directory, 'first-build.json'), JSON.stringify(authored));
  writeFileSync(join(directory, 'README.md'), 'Not a scene');
  assert.deepEqual([...loadViewers(fixture).keys()], ['first-build']);

  writeFileSync(join(directory, 'second-build.json'), JSON.stringify({ ...authored,
    title: 'Second build', blocks: [{ at: [4, -1, 2], block: '3:0' }] }));
  const loaded = loadViewers(fixture);
  assert.deepEqual([...loaded.keys()], ['first-build', 'second-build']);
  assert.equal(loaded.get('first-build').title, 'First build');
  assert.deepEqual(loaded.get('first-build').blocks, [{ at: [-3, 2, 1], block: '1:0' }]);
  assert.equal(loaded.get('second-build').title, 'Second build');
  assert.deepEqual(loaded.get('second-build').blocks, [{ at: [4, -1, 2], block: '3:0' }]);

  writeFileSync(join(directory, 'Bad-ID.json'), JSON.stringify(authored));
  assert.throws(() => loadViewers(fixture), /invalid viewer scene Bad-ID/);
});

test('machine matches the tested E6 fixture, not the other transmutation machine', () => {
  const scene = scenes.get('sapling-transmutation');
  assert.equal(scene.minY, -1);
  assert.equal(scene.layers, 5); // Includes the empty Y=1 layer.
  assert.equal(scene.blocks.length, 78);
  const at = new Map(scene.blocks.map((b) => [b.at.join(','), b.block]));
  assert.equal(at.get('0,-1,0'), '3:0');
  assert.equal(at.get('0,0,0'), '6:0');
  for (const sign of [-1, 1]) {
    assert.equal(at.get(`${sign * 2},2,-1`), '1:0');
    assert.equal(at.get(`${sign * 2},2,0`), '76:3');
    assert.equal(at.get(`${sign * 3},2,0`), '1:0');
    assert.equal(at.get(`${sign * 4},2,0`), sign === -1 ? '33:5' : '33:4');
    assert.equal(at.get(`${sign * 5},3,0`), '69:13');
  }
});

test('piston machine matches the armed E5 survival fixture', () => {
  const scene = scenes.get('piston-transmutation');
  assert.equal(scene.minY, -1);
  assert.equal(scene.layers, 3);
  assert.equal(scene.blocks.length, 39); // Cropped 5 × 6 floor and nine machine blocks.
  assert.deepEqual(scene.blocks.filter((b) => b.at[1] >= 0), [
    { at: [0, 0, 0], block: '76:5' },
    { at: [-1, 0, 0], block: '35:5' },
    { at: [-2, 0, 0], block: '33:5' },
    { at: [0, 0, -1], block: '17:0' },
    { at: [0, 0, -2], block: '29:3' },
    { at: [-2, 0, -2], block: '1:0' },
    { at: [-2, 1, -2], block: '1:0' },
    { at: [-1, 1, -2], block: '69:9' }, // East-mounted wall lever, on.
    { at: [-2, 0, 1], block: '69:6' }, // Floor lever, off.
  ]);
});

test('explicit placements override fills; fixed omissions stay omitted', () => {
  const build = { fills: [{ from: [-1, 2, 3], to: [1, 3, 3], block: '1:0' }],
    blocks: [{ at: [0, 2, 3], block: '3:0' }], omissions: [[-1, 3, 3]] };
  const scene = expandBuild(build, models);
  assert.equal(scene.blocks.length, 5);
  assert.equal(scene.blocks.find((b) => b.at.join(',') === '0,2,3').block, '3:0');
  assert.ok(!scene.blocks.some((b) => b.at.join(',') === '-1,3,3'));
  assert.equal(scene.minY, 2);
  assert.equal(scene.layers, 2);
});

test('authoring mistakes and unsupported blocks fail validation', () => {
  assert.throws(() => expandBuild({ blocks: [{ at: [0, 0, 0], block: '54:0' }] }, models), /unsupported block/);
  assert.throws(() => expandBuild({ blocks: [{ at: [0, 0.5, 0], block: '1:0' }] }, models), /integer/);
  assert.throws(() => expandBuild({ fills: [{ from: [0, 0, 0], to: [100, 100, 100], block: '1:0' }] }, models), /exceeds/);
  assert.throws(() => expandBuild({ blocks: [{ at: [0, 0, 0], block: '1:0' }, { at: [0, 0, 0], block: '3:0' }] }, models), /duplicate/);
  assert.throws(() => expandBuild({ blocks: [{ at: [0, 0, 0], block: '1:0' }], omissions: [[1, 0, 0]] }, models), /occupied/);
  const bad = structuredClone(creeper);
  bad.variants[0].faces[0].texture = '../terrain.png';
  assert.throws(() => validateMesh(bad, root), /texture/);
});

test('side culling keeps exposed slice tops and faces next to transparent plants', () => {
  const entries = [{ at: [0, 0, 0], block: '1:0' }, { at: [1, 0, 0], block: '1:0' },
    { at: [0, 1, 0], block: '1:0' }, { at: [0, 0, 1], block: '6:0' }];
  const occupied = new Map(entries.map((b) => [b.at.join(','), b]));
  const normals = visibleFaces(entries[0], occupied, models).map((f) => f.normal.join(','));
  assert.equal(normals.length, 5);
  assert.ok(!normals.includes('1,0,0'));
  assert.ok(normals.includes('0,1,0')); // A hidden upper layer must not erase this top.
  assert.ok(normals.includes('0,0,1')); // A sapling is not an opaque neighbor.
  assert.equal(visibleFaces(entries[3], occupied, models).length, 4);
});

test('metadata rotates the piston front and south-mounted torch correctly', () => {
  const tile = (face) => Math.floor(face.corners[0][3] * 16) + 16 * Math.floor(face.corners[0][4] * 16);
  // BlockPistonBase.getBlockTextureFromSideAndMetadata: the normal head is tile 107.
  for (const [id, normal] of [['33:4', '-1,0,0'], ['33:5', '1,0,0']]) {
    assert.equal(tile(models[id].faces.find((f) => f.normal.join(',') === normal)), 107);
  }
  // RenderTorchAtAngle's textured head cap is centred at z=0.25 for metadata
  // 3, not z=0.75 (opposite wall) or z=0.5 (standing). The side quads extend
  // farther because their transparent texels cover a whole atlas tile.
  const cap = models['76:3'].faces[0].corners;
  assert.ok(Math.abs(cap.reduce((sum, v) => sum + v[2], 0) / 4 - 0.25) < 1e-7);
  assert.equal(models['69:13'].opaque, false);
});

test('piston machine exports the sticky head, lime wool, wood and armed lever poses', () => {
  const tile = (face) => Math.floor(face.corners[0][3] * 16) + 16 * Math.floor(face.corners[0][4] * 16);
  // BlockPistonBase: the sticky head is tile 106; orientation 3 faces south.
  assert.equal(tile(models['29:3'].faces.find((f) => f.normal.join(',') === '0,0,1')), 106);
  // BlockCloth's metadata-5 lookup yields 146, not the white wool tile 64.
  assert.ok(models['35:5'].faces.every((f) => tile(f) === 146));
  for (const face of models['17:0'].faces) assert.equal(tile(face), face.normal[1] ? 21 : 20);
  const cap = models['76:5'].faces[0].corners;
  assert.deepEqual([0, 1, 2].map((i) => cap.reduce((sum, v) => sum + v[i], 0) / 4), [0.5, 0.625, 0.5]);
  // RenderBlockLever: the wall base touches x=0; the floor base touches y=0.
  const wallBase = models['69:9'].faces.slice(0, 6).flatMap((f) => f.corners);
  assert.equal(Math.min(...wallBase.map((v) => v[0])), 0);
  assert.equal(Math.max(...wallBase.map((v) => v[0])), 0.1875);
  const floorBase = models['69:6'].faces.slice(0, 6).flatMap((f) => f.corners);
  assert.equal(Math.min(...floorBase.map((v) => v[1])), 0);
  assert.equal(Math.max(...floorBase.map((v) => v[1])), 0.1875);
  // The powered wall handle points down; the unpowered floor handle leans east.
  assert.ok(models['69:9'].faces[7].corners.every((v) => v[1] < 0.2));
  assert.ok(models['69:6'].faces[7].corners.every((v) => v[0] > 0.8));
});

test('entity pass order, additive glow and texture-matrix UVs survive batching', () => {
  const [normal, charged] = creeper.variants;
  assert.equal(normal.faces.length, 36);
  assert.equal(charged.faces.length, 72);
  assert.deepEqual(charged.faces.slice(0, 36), normal.faces);
  const batches = faceBatches(charged.faces);
  assert.equal(batches.length, 2);
  assert.equal(batches[0].state.texture, 'mob/creeper.png');
  assert.equal(batches[1].state.texture, 'armor/power.png');
  assert.deepEqual(batches[1].state.blend_func, [1, 1]);
  assert.equal(batches[1].state.lit, false);
  assert.equal(batches[1].state.blend, true);
  const geometry = faceGeometry([charged.faces[36]]);
  assert.equal(geometry.attributes.position.count, 4);
  assert.deepEqual([...geometry.index.array], [0, 1, 2, 0, 2, 3]);
  assert.ok(Math.abs(geometry.attributes.uv.getX(0) - charged.faces[36].corners[0][3]) < 1e-7);
  assert.deepEqual([...geometry.attributes.tint.array.slice(0, 4)], [0.5, 0.5, 0.5, 1]);
  geometry.dispose();
});

test('geometry preserves asymmetric UVs, alpha and byte-space diffuse lighting', () => {
  const face = { ...models['1:0'].faces[0], lit: true, normal: [0, -1, 0], rgba: [0.8, 0.5, 0.2, 0.25] };
  const geometry = faceGeometry([face]);
  // Downward normals receive only RenderHelper's ambient term, 0.4.
  const tint = geometry.attributes.tint.array;
  for (const [i, expected] of [0.32, 0.2, 0.08, 0.25].entries()) assert.ok(Math.abs(tint[i] - expected) < 1e-7);
  assert.equal(geometry.attributes.uv.getX(0), 0.0625);
  assert.ok(Math.abs(geometry.attributes.uv.getY(0) - 0.0624609375) < 1e-7);
  assert.equal(geometry.attributes.position.getZ(0), 1);
  geometry.dispose();
});

test('ghost edges have no triangle diagonals and deduplicate adjacent block edges', () => {
  const edges = blockEdges([{ at: [-2, 3, 1] }, { at: [-1, 3, 1] }]);
  assert.equal(edges.attributes.position.count, 40); // 24 cube edges minus 4 shared.
  const position = edges.attributes.position;
  for (let i = 0; i < position.count; i += 2) {
    const lengths = ['X', 'Y', 'Z'].map((axis) => Math.abs(position[`get${axis}`](i) - position[`get${axis}`](i + 1)));
    assert.deepEqual(lengths.sort(), [0, 0, 1]);
  }
  edges.dispose();
});

test('template uses scene layer count and entity controls; rejects unknown scene IDs', () => {
  const errors = [];
  const ctx = { viewers: scenes, error: (s) => errors.push(s), warn: (s) => assert.fail(s) };
  const build = renderTemplate('viewer', ['sapling-transmutation'], {}, ctx);
  assert.match(build, /max="5" value="5"/);
  assert.match(build, /viewer-previous/);
  const entity = renderTemplate('viewer', ['creeper'], {}, ctx);
  assert.match(entity, /Normal/);
  assert.match(entity, /Charged/);
  assert.doesNotMatch(entity, /type="range"|viewer-layers/);
  renderTemplate('viewer', ['../../wrong'], {}, ctx);
  renderTemplate('viewer', ['creeper'], { mesh: 'arbitrary.json' }, ctx);
  assert.equal(errors.length, 2);
});
