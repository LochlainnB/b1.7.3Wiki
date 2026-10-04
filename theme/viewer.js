import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { visibleFaces, faceBatches, faceGeometry, blockEdges } from './viewer-mesh.js';

const BASE = new URL(window.WIKI_BASE || './', window.location.href);
const asset = (path) => new URL(`assets/${path}`, BASE).href;
const jsonCache = new Map();

function loadJSON(path) {
  if (!jsonCache.has(path)) jsonCache.set(path, fetch(asset(path)).then((response) => {
    if (!response.ok) throw new Error(`Could not load ${path}`);
    return response.json();
  }));
  return jsonCache.get(path);
}

export async function mountViewer(element) {
  const viewport = element.querySelector('.viewer-window');
  const status = element.querySelector('.viewer-status');
  let renderer, controls, resizeObserver, visibilityObserver, frame = 0;
  let disposed = false, visible = true, lost = false;
  const resources = new Set();
  const own = (resource) => {
    // A sibling texture request can finish after Promise.all has rejected.
    if (disposed) resource.dispose();
    else resources.add(resource);
    return resource;
  };
  let exitExpanded = () => {};

  function dispose() {
    if (disposed) return;
    disposed = true;
    cancelAnimationFrame(frame);
    resizeObserver?.disconnect();
    visibilityObserver?.disconnect();
    controls?.dispose();
    exitExpanded();
    for (const resource of resources) resource.dispose();
    renderer?.dispose();
    renderer?.domElement.remove();
    window.removeEventListener('pagehide', onPageHide);
  }
  function onPageHide(event) { if (!event.persisted) dispose(); }

  try {
    const data = await loadJSON(`viewer/${element.dataset.scene}-scene.json`);
    const mesh = await loadJSON(`viewer/${data.mesh}`);
    const faces = mesh.models ? Object.values(mesh.models).flatMap((m) => m.faces)
      : mesh.variants.flatMap((v) => v.faces);
    renderer = new THREE.WebGLRenderer({ antialias: false, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    viewport.prepend(renderer.domElement);
    const textures = new Map();
    const loader = new THREE.TextureLoader();
    await Promise.all([...new Set(faces.filter((f) => f.textured).map((f) => f.texture))].map(async (path) => {
      const texture = own(await loader.loadAsync(asset(`textures/${path}`)));
      texture.flipY = false;
      texture.magFilter = texture.minFilter = THREE.NearestFilter;
      texture.generateMipmaps = false;
      texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
      // The original fixed-function renderer multiplies byte-space colours.
      // Our shader deliberately preserves that rather than using PBR lighting.
      texture.colorSpace = THREE.NoColorSpace;
      textures.set(path, texture);
    }));

    const scene = new THREE.Scene();
    const model = new THREE.Group();
    scene.add(model);
    const materials = new Map();
    let order = 1;
    function addFaces(parent, list, batchBlocks = false) {
      const batches = faceBatches(list);
      // Blocks have no ordered overlay passes; combine their repeated states.
      const merged = new Map();
      if (batchBlocks) for (const batch of batches) {
        if (merged.has(batch.key)) merged.get(batch.key).faces.push(...batch.faces);
        else merged.set(batch.key, batch);
      }
      for (const { key, state, faces: batchFaces } of batchBlocks ? merged.values() : batches) {
        if (!materials.has(key)) {
          const additive = state.blend && state.blend_func[0] === 1;
          const material = own(new THREE.ShaderMaterial({
            uniforms: { map: { value: textures.get(state.texture) || null },
              textured: { value: state.textured }, alphaCut: { value: state.alpha_test ? 0.1 : -1 } },
            vertexShader: `attribute vec4 tint;
              varying vec2 vUv; varying vec4 vTint;
              void main() { vUv = uv; vTint = tint;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
            fragmentShader: `uniform sampler2D map; uniform bool textured; uniform float alphaCut;
              varying vec2 vUv; varying vec4 vTint;
              void main() { vec4 pixel = textured ? texture2D(map, vUv) : vec4(1.0);
                vec4 colour = pixel * vTint;
                if (colour.a <= alphaCut) discard;
                gl_FragColor = colour; }`,
            side: THREE.DoubleSide, forceSinglePass: true,
            transparent: state.blend,
            blending: state.blend ? THREE.CustomBlending : THREE.NoBlending,
            blendEquation: THREE.AddEquation,
            blendSrc: additive ? THREE.OneFactor : THREE.SrcAlphaFactor,
            blendDst: additive ? THREE.OneFactor : THREE.OneMinusSrcAlphaFactor,
            depthTest: state.depth_test, depthWrite: state.depth_mask,
            depthFunc: state.depth_func === 514 ? THREE.EqualDepth : THREE.LessEqualDepth,
          }));
          materials.set(key, material);
        }
        const part = new THREE.Mesh(own(faceGeometry(batchFaces)), materials.get(key));
        part.renderOrder = order++;
        parent.add(part);
      }
    }

    const layers = [], variants = [];
    if (data.kind === 'build') {
      const occupied = new Map(data.blocks.map((b) => [b.at.join(','), b]));
      const ghostMaterial = own(new THREE.LineBasicMaterial({ color: 0xc0d4dd,
        transparent: true, opacity: 0.22, depthWrite: false }));
      const selectionMaterial = own(new THREE.LineBasicMaterial({ color: 0x58d786,
        transparent: true, opacity: 0.75, depthWrite: false }));
      for (let i = 0; i < data.layers; i++) {
        const blocks = data.blocks.filter((b) => b.at[1] === data.minY + i);
        const solid = new THREE.Group();
        const list = blocks.flatMap((block) => visibleFaces(block, occupied, mesh.models).map((face) => ({
          ...face, corners: face.corners.map((corner) => corner.map((v, j) => j < 3 ? v + block.at[j] : v)),
        })));
        addFaces(solid, list, true);
        const ghost = new THREE.LineSegments(own(blockEdges(blocks)), ghostMaterial);
        const selected = new THREE.LineSegments(own(blockEdges(blocks.filter((b) => mesh.models[b.block].opaque), true)), selectionMaterial);
        ghost.renderOrder = selected.renderOrder = 1000;
        selected.position.y = 0.002;
        model.add(solid, ghost, selected);
        layers.push({ solid, ghost, selected, blocks: blocks.length });
      }
    } else {
      for (const variant of mesh.variants) {
        const group = new THREE.Group();
        addFaces(group, variant.faces);
        model.add(group);
        variants.push(group);
      }
    }

    const bounds = new THREE.Box3().setFromObject(model);
    const center = bounds.getCenter(new THREE.Vector3());
    const size = bounds.getSize(new THREE.Vector3());
    model.position.set(-center.x, -bounds.min.y, -center.z);
    const gridSize = data.kind === 'build' ? Math.ceil(Math.max(size.x, size.z) * 2) : 8;
    const grid = new THREE.GridHelper(gridSize, gridSize, 0x61727b, 0x61727b);
    own(grid.geometry); own(grid.material);
    grid.material.transparent = true;
    grid.material.opacity = 0.22;
    grid.material.depthWrite = false;
    grid.position.y = -0.012;
    scene.add(grid);

    const camera = new THREE.PerspectiveCamera(36, 1, 0.01, 1000);
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enablePan = false;
    controls.enableDamping = false;
    controls.maxPolarAngle = Math.PI * 0.94;
    controls.touches.ONE = THREE.TOUCH.ROTATE;
    controls.touches.TWO = THREE.TOUCH.DOLLY_ROTATE;
    controls.mouseButtons.RIGHT = controls.mouseButtons.MIDDLE = null;
    controls.target.set(0, size.y * 0.45, 0);
    const direction = new THREE.Vector3(data.kind === 'build' ? 0.55 : 0.8, 0.65, 1).normalize();
    let previousFit = 0;
    const axes = element.querySelector('.viewer-axes');
    const axisVectors = [[new THREE.Vector3(1, 0, 0), '#ef6849', 'X'],
      [new THREE.Vector3(0, 1, 0), '#7dda68', 'Y'], [new THREE.Vector3(0, 0, 1), '#7699ff', 'Z']];

    function draw() {
      frame = 0;
      if (disposed || lost || !visible || document.hidden) return;
      renderer.render(scene, camera);
      const inverse = camera.quaternion.clone().invert();
      axes.innerHTML = axisVectors.map(([vector, color, label]) => {
        const p = vector.clone().applyQuaternion(inverse);
        const x = 36 + p.x * 25, y = 42 - p.y * 25;
        return `<path d="M36 42L${x} ${y}" stroke="${color}" stroke-width="2"/>` +
          `<text x="${x + 3}" y="${y - 3}" fill="${color}">${label}</text>`;
      }).join('');
    }
    function invalidate() {
      if (!disposed && !frame) frame = requestAnimationFrame(draw);
    }
    function resize() {
      const { width, height } = viewport.getBoundingClientRect();
      if (!width || !height) return;
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      // Project the authored bounds, rather than fitting a large sphere around
      // a wide, low machine. Keep the user's relative zoom across size changes.
      const right = new THREE.Vector3().crossVectors(new THREE.Vector3(0, 1, 0), direction).normalize();
      const up = new THREE.Vector3().crossVectors(direction, right);
      const tanV = Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2);
      const tanH = tanV * camera.aspect;
      let distance = 0;
      const target = new THREE.Vector3(0, size.y * 0.45, 0);
      for (const x of [-size.x / 2, size.x / 2]) for (const y of [0, size.y]) for (const z of [-size.z / 2, size.z / 2]) {
        const corner = new THREE.Vector3(x, y, z).sub(target);
        distance = Math.max(distance, corner.dot(direction) +
          Math.max(Math.abs(corner.dot(right)) / tanH, Math.abs(corner.dot(up)) / tanV));
      }
      distance *= 1.12;
      if (!previousFit) {
        camera.position.copy(controls.target).addScaledVector(direction, distance);
      } else {
        camera.position.sub(controls.target).multiplyScalar(distance / previousFit).add(controls.target);
      }
      controls.minDistance = size.length() * 0.18;
      controls.maxDistance = distance * 4;
      previousFit = distance;
      controls.update();
      invalidate();
    }
    controls.addEventListener('change', invalidate);
    resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(viewport);
    visibilityObserver = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      if (visible) invalidate();
    });
    visibilityObserver.observe(element);
    const onVisibility = () => { if (!document.hidden) invalidate(); };
    document.addEventListener('visibilitychange', onVisibility);

    const slider = element.querySelector('input[type=range]');
    const previous = element.querySelector('.viewer-previous');
    const next = element.querySelector('.viewer-next');
    if (slider) {
      const setLayer = (value) => {
        const layer = Math.max(1, Math.min(data.layers, Number(value)));
        slider.value = layer;
        slider.style.setProperty('--layer-progress', `${(layer - 1) / Math.max(1, data.layers - 1) * 100}%`);
        for (let i = 0; i < layers.length; i++) {
          layers[i].solid.visible = i < layer;
          layers[i].ghost.visible = i >= layer;
          layers[i].selected.visible = i === layer - 1 && layer < data.layers;
        }
        element.querySelector('.viewer-layer-label').innerHTML = layer === data.layers
          ? 'Visible layers: <strong>All</strong>' : `Layer <strong>${layer}</strong> of ${data.layers}`;
        previous.disabled = layer === 1;
        next.disabled = layer === data.layers;
        element.dataset.layer = layer;
        element.dataset.solidBlocks = layers.slice(0, layer).reduce((n, l) => n + l.blocks, 0);
        element.dataset.ghostBlocks = layers.slice(layer).reduce((n, l) => n + l.blocks, 0);
        invalidate();
      };
      slider.disabled = false;
      slider.addEventListener('input', () => setLayer(slider.value));
      previous.addEventListener('click', () => setLayer(Number(slider.value) - 1));
      next.addEventListener('click', () => setLayer(Number(slider.value) + 1));
      setLayer(data.layers);
    } else {
      const buttons = [...element.querySelectorAll('[data-variant]')];
      const setVariant = (index) => {
        variants.forEach((group, i) => { group.visible = i === index; });
        buttons.forEach((button, i) => button.setAttribute('aria-pressed', String(i === index)));
        element.dataset.variant = mesh.variants[index].label;
        invalidate();
      };
      buttons.forEach((button, i) => {
        button.disabled = false;
        button.addEventListener('click', () => setVariant(i));
      });
      setVariant(0);
    }

    // Expand the entire figure so the layer/variant controls stay available.
    const fullscreen = element.querySelector('.viewer-fullscreen');
    let fallback = false, priorFocus, scrollY, bodyOverflow;
    const expanded = () => fallback || document.fullscreenElement === element;
    function fullscreenState() {
      const open = expanded();
      fullscreen.title = open ? 'Exit fullscreen' : 'Fullscreen';
      fullscreen.querySelector('path').setAttribute('d', open
        ? 'M3 9h6V3m6 0v6h6M9 21v-6H3m18 0h-6v6'
        : 'M9 3H3v6m12-6h6v6M3 15v6h6m12-6v6h-6');
      invalidate();
    }
    function finishExit() {
      if (priorFocus) {
        priorFocus.focus({ preventScroll: true });
        priorFocus = null;
      }
      fullscreenState();
    }
    function fallbackExit() {
      if (!fallback) return;
      fallback = false;
      element.classList.remove('viewer-expanded');
      document.body.style.overflow = bodyOverflow;
      window.scrollTo(0, scrollY);
      finishExit();
    }
    function fallbackEnter() {
      fallback = true;
      scrollY = window.scrollY;
      bodyOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      element.classList.add('viewer-expanded');
      fullscreenState();
    }
    async function toggleFullscreen() {
      if (fallback) { fallbackExit(); return; }
      if (document.fullscreenElement === element) { await document.exitFullscreen(); return; }
      priorFocus = document.activeElement;
      if (element.requestFullscreen) {
        try { await element.requestFullscreen(); fullscreenState(); return; } catch { /* Use page expansion. */ }
      }
      fallbackEnter();
    }
    const onFullscreen = () => {
      if (!expanded()) finishExit();
      else fullscreenState();
    };
    const onEscape = (event) => { if (event.key === 'Escape') fallbackExit(); };
    fullscreen.addEventListener('click', () => {
      toggleFullscreen().catch(() => { /* Native exit rejection leaves its exit button available. */ });
    });
    fullscreen.disabled = false;
    document.addEventListener('fullscreenchange', onFullscreen);
    document.addEventListener('keydown', onEscape);
    exitExpanded = () => {
      fallbackExit();
      document.removeEventListener('fullscreenchange', onFullscreen);
      document.removeEventListener('keydown', onEscape);
      document.removeEventListener('visibilitychange', onVisibility);
    };

    renderer.domElement.addEventListener('webglcontextlost', (event) => {
      event.preventDefault();
      lost = true;
      controls.enabled = false;
      status.hidden = false;
      status.textContent = '3D rendering paused. Waiting for graphics to recover…';
      element.dataset.viewerState = 'lost';
    });
    renderer.domElement.addEventListener('webglcontextrestored', () => {
      lost = false;
      controls.enabled = true;
      status.hidden = true;
      element.dataset.viewerState = 'ready';
      invalidate();
    });
    window.addEventListener('pagehide', onPageHide);
    status.hidden = true;
    element.dataset.viewerState = 'ready';
    resize();
    return dispose;
  } catch (error) {
    dispose();
    element.dataset.viewerState = 'error';
    status.hidden = false;
    status.textContent = 'The 3D viewer could not load. It requires WebGL 2 and enabled graphics. The article below is still available.';
    console.warn('Wiki 3D viewer:', error);
  }
}
