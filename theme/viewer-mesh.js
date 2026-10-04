// Geometry has no DOM dependency, so culling and layer boundaries can be tested.
import * as THREE from 'three';

export function visibleFaces(entry, occupied, models) {
  const model = models[entry.block];
  if (!model.opaque) return model.faces;
  return model.faces.filter((face) => {
    // Keep vertical faces: a lower block's top must survive a layer cut.
    const n = face.normal;
    if (Math.abs(n[1]) > 0.5) return true;
    const neighbor = occupied.get(entry.at.map((v, i) => v + Math.round(n[i])).join(','));
    return !neighbor || !models[neighbor.block].opaque;
  });
}

export function faceBatches(faces) {
  // Consecutive batches preserve entity part order and additional render passes.
  const batches = [];
  for (const face of faces) {
    const key = JSON.stringify([face.texture, face.textured, face.blend, face.blend_func,
      face.alpha_test, face.depth_test, face.depth_mask, face.depth_func]);
    let batch = batches.at(-1);
    if (!batch || batch.key !== key) {
      batch = { key, state: face, faces: [] };
      batches.push(batch);
    }
    batch.faces.push(face);
  }
  return batches;
}

export function faceGeometry(faces) {
  const positions = [], uvs = [], colors = [], indices = [];
  const lamps = [new THREE.Vector3(0.2, 1, -0.7).normalize(), new THREE.Vector3(-0.2, 1, 0.7).normalize()];
  for (const face of faces) {
    const first = positions.length / 3;
    let light = 1;
    if (face.lit) {
      // RenderHelper's ambient/diffuse lamps, with the game's recorded normals.
      const normal = new THREE.Vector3(...face.normal);
      light = 0.4 + lamps.reduce((n, lamp) => n + 0.6 * Math.max(0, normal.dot(lamp)), 0);
    }
    const tint = face.rgba.map((v, i) => i < 3 ? Math.min(1, v * light) : v);
    for (const [x, y, z, u, v] of face.corners) {
      positions.push(x, y, z);
      uvs.push(u, v);
      colors.push(...tint);
    }
    indices.push(first, first + 1, first + 2, first, first + 2, first + 3);
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  geometry.setAttribute('tint', new THREE.Float32BufferAttribute(colors, 4));
  geometry.setIndex(indices);
  return geometry;
}

export function blockEdges(blocks, topOnly = false) {
  const points = [], seen = new Set();
  const add = (a, b) => {
    const key = [a.join(','), b.join(',')].sort().join('|');
    if (seen.has(key)) return;
    seen.add(key);
    points.push(...a, ...b);
  };
  for (const { at: [x, y, z] } of blocks) {
    for (const h of topOnly ? [1] : [0, 1]) {
      add([x, y + h, z], [x + 1, y + h, z]);
      add([x + 1, y + h, z], [x + 1, y + h, z + 1]);
      add([x + 1, y + h, z + 1], [x, y + h, z + 1]);
      add([x, y + h, z + 1], [x, y + h, z]);
    }
    if (!topOnly) for (const dx of [0, 1]) for (const dz of [0, 1]) {
      add([x + dx, y, z + dz], [x + dx, y + 1, z + dz]);
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(points, 3));
  return geometry;
}
