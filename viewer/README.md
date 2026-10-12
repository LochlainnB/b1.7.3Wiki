# Article models

Write `{{viewer|piston-transmutation}}`, `{{viewer|sapling-transmutation}}` or
`{{viewer|creeper}}` alone on a line.
Each authored scene lives in `viewer/scenes/<scene-id>.json`; `assets/viewer/`
contains generated meshes shared by scenes. The filename supplies the template
ID and must contain only lowercase letters, digits and hyphens. New scene files
are discovered automatically, without a catalog entry. The build validates scenes
and meshes and emits page-relative scene JSON. The bundled Three.js viewer loads
only when a model approaches the viewport. There are no CDN requests.

## Builds

A build has `kind: "build"`, `title`, `caption`, `mesh`, and these placements:

- `fills`: inclusive `from`/`to` integer coordinates and a `block` model key.
- `blocks`: explicit `{ "at": [x, y, z], "block": "id:metadata" }` placements,
  overriding fills. Duplicate explicit positions are errors.
- `omissions`: occupied coordinates to omit permanently for an authored cutaway.
  Camera rotation never changes these omissions.

Coordinates use east +X, up +Y, south +Z, in blocks. Layers start at the lowest
occupied Y; empty intervening layers still count. Layer N shows every block at
or below it solid, and higher blocks as translucent cube edges. The maximum is
All. Builds are limited to 10,000 blocks and 32 vertical layers. Unsupported
block/metadata pairs fail the build rather than becoming generic cubes.

The top-left download control saves the complete build as a legacy Alpha
`.schematic`, regardless of the selected layer or camera angle. The build emits
gzip-compressed NBT alongside the scene JSON, so downloading needs neither
JavaScript nor WebGL. Coordinates are shifted to a zero-based bounding box;
empty positions and fixed omissions are air. Rendering-only key suffixes such
as dust connections are excluded; numeric block IDs and metadata are preserved.
Schematic bounds may contain at most 1,000,000 cells and span at most 32,767 per
axis. Entities and tile entities are empty; scenes do not store their data.
Entity viewers have no schematic download.

The piston machine uses the E5 survival fixture in
`content/research/block-data-corruption.md`, Appendix C, after the upper wall
lever is switched on. Both pistons remain retracted and the floor lever is off.
It uses lime wool and oak wood, with the surrounding floor cropped to 5 × 6.

The sapling machine uses the E6 pre-growth fixture in
`content/research/block-data-corruption.md`, Appendix C. Its two powered levers
are frozen in the armed state, not a simulation of ordinary placement. The
surrounding test floor is cropped to a 13 × 5 platform; no machine part is omitted.

The dust order example is the worked example in
`content/guide/predicting-dust-update-order.md`, switched off. Its scene
coordinates are the guide's world coordinates minus (6, 63, 5), and it was
tested in the game as built.

Redstone dust draws itself from its neighbours, so a dust model's key carries
them: `55:<power level>:<n><e><s><w>`, north (−Z), east, south, west. Each side
is `-` for nothing to connect to, `f` for dust beside it (or one block lower,
which draws the same), or `u` for dust on top of a solid block beside it, which
draws the dust up that block's face. `DUST` in `tools/extract/viewer_blocks.py`
lists the shapes exported; add a key there and rerun the exporter.

## Entities and mesh extraction

An entity has `kind: "entity"`, `title`, `caption`, and `mesh`. The mesh lists
labelled frozen variants. Geometry is drawn by the client renderer, including
texture-matrix UVs, lighting normals, alpha tests, blend passes and depth state.
The Creeper's charged overlay remains additive and frozen at partial tick 1.

With the client jar and Babric mappings configured as described in `AGENTS.md`:

```sh
python tools/extract/viewer_blocks.py --out assets/viewer/block-models.json
python tools/extract/viewer_entities.py --out assets/viewer/creeper.json
npm run check
npm run build
```

Both extractors also accept `--jar PATH --cache DIRECTORY`. They execute the
existing JVM interpreter and GL recorder. The block exporter resolves the
piston renderer's metadata switches in memory because the interpreter has no
`tableswitch`; it never changes the jar or the external source.

Block meshes retain all faces. The browser removes horizontal faces between
opaque neighbors but retains vertical faces to expose each layer boundary.
Block faces are single-sided: plants already export paired front/back quads.
Nearest-filtered original textures and byte-space lighting preserve the Beta
appearance. Normal/charged variants share framing, including the overlay bounds.

The complete viewer expands through native fullscreen where available and uses
fixed-page expansion on rejection or unsupported browsers. The same button exits;
Escape exits page expansion. Closing restores the previous focus and page scroll.
Graphics loss pauses drawing until the context recovers. Load/graphics failures
leave the article available with an error message, without a static illustration.
