---
title: Suppressing Chunk Saves
description: Sign-based chunk save suppression, repeated-text failures, measured sign-count boundaries, and a reproducible text generator.
type: guide
categories: [Guides]
---

**Suppressing chunk saves** with [[Sign|signs]] prevents a [[Chunk|chunk]] from saving its new state. A previously saved chunk returns to its last successful save when discarded and reloaded.

## Choosing text

Repeating one fixed line across every [[Sign|sign]] does not work in the tested sign-only fixtures. Punctuation and accented characters also fail when the same line is reused throughout the chunk. The working schemes vary text between signs.
<!-- verification: SignThreshold, original client.jar, OpenJDK 17,
     2026-10-04. The fixed-line trials below serialize all 32512 sign positions
     above a synthetic bedrock floor, not just a small sample of signs. -->

### Repeated-line tests

The following controlled NBT fixture contains 32,512 standing [[Sign|signs]] above a [[Bedrock|bedrock]] floor at y=0. Each sign has four copies of its line. All saves succeed; the rejection limit is 1,044,475 compressed bytes.

The fixture has zeroed lighting and height data and uses every position above the floor. It is not a survival excavation plan: naturally generated bedrock reduces the available space.

| Text | Compressed bytes |
|---|---|
| `qwertyuiopasdfg` on every sign | 135,231 |
| `!@#$%^&*()_+-=?` on every sign | 135,286 |
| `ÇüéâäàåçêëèïîìÄ` on every sign | 142,286 |
| One fresh random 15-character ASCII line per sign, repeated on all four lines | 852,186 |

<!-- verification: SignThreshold profiles qwerty, distinct15, unicode15,
     ascii1. Synthetic chunk (0,0), populated, bedrock at y=0, other terrain
     initially air, zero metadata/light/height arrays; signs y=1..127,
     metadata 8. Blocks, all arrays and all sign compounds are included.
     The synthetic maximum is an upper-capacity control, not a survival
     excavation plan: generated bedrock also occupies parts of y=1..4. -->

### Working text schemes

| Scheme | Lines on one [[Sign\|sign]] | Changes for the next sign |
|---|---|---|
| Two varied ASCII lines | A, B, A, B | Generate a fresh A and B. |
| Three varied ASCII lines | A, B, C, A | Generate a fresh A, B and C. |
| Four varied ASCII lines | A, B, C, D | Generate four fresh lines. |
| Shuffled keyboard letters | Four independently shuffled copies of `qwertyuiopasdfg` | Shuffle each line again. |

The ASCII schemes use 15 characters per line from the 94 printable ASCII characters accepted by the game. The backtick is excluded. The shuffled-letter scheme also uses 15 characters per line. Reusing A and B within one sign works; reusing the same pair throughout the chunk does not reproduce the working scheme.
<!-- src: GuiEditSign.java:58-62; ChatAllowedCharacters.java:10-27;
     original client.jar font.txt independently checked.
     verification: Java Random(173), uniform ASCII draws or Fisher-Yates
     shuffles. These are tested choices, not a proof of optimal compression. -->

The unmodified sign editor has no clipboard-paste handling. The generator below prepares text but does not add paste support or automate keyboard input. Paste modifications and keyboard automation are not tested here.
<!-- src: GuiEditSign.java:45-65; GuiScreen.java:31-49,119-124.
     Original client yc.a(CI)V independently disassembled: it invokes only
     String and StringBuilder methods, with no clipboard-helper call. -->

## Measured sign counts

Binary search gives the following boundaries in the controlled NBT fixture. Each count uses the same text sequence and bottom-up placement order. All [[Sign|signs]] share one rotation. Counts immediately below and above each boundary are also checked in a 33-count neighbourhood.

| Text scheme | Last passing count | Compressed bytes | First rejected count | Compressed bytes |
|---|---|---|---|---|
| Two varied ASCII lines | 26,524 | 1,044,440 | 26,525 | 1,044,480 |
| Three varied ASCII lines, A/B/C/A | 20,878 | 1,044,451 | 20,879 | 1,044,487 |
| Four varied ASCII lines | 17,250 | 1,044,451 | 17,251 | 1,044,511 |
| Four shuffled keyboard-letter lines | 23,266 | 1,044,466 | 23,267 | 1,044,501 |

<!-- verification: SignThreshold.boundary checks the empty and full fixtures,
     bisects the interval until the endpoints differ by one sign, then checks
     every count from N-16 to N+16. These are boundaries for these exact
     prefix fixtures, not a global minimum over all texts and placements. -->

### Generated chunks

The generated-chunk trials use three world seeds, four [[Chunk|chunk]] positions per seed, and both dimensions. Each chunk has a [[Stone|stone]] floor at y=5. Its chamber is cleared from y=6 to y=127 in the [[Overworld]], or y=122 in the [[Nether]]. Natural terrain below the floor and the Nether's [[Bedrock|bedrock]] roof remain. Lighting updates finish before measurement. No entities or other block entities are retained.
<!-- verification: ChunkThreshold.prepare, world seeds 173, 0, 8675309;
     chunk coordinates (0,0), (7,-3), (-20,17), (31250,-31250).
     A 5x5 surrounding chunk square is loaded and populated first.
     World.setBlockWithNotify prepares each chamber; World.updatingLighting
     drains its queued lighting work. -->

The ranges give the first rejected [[Sign|sign]] count in each sample. Signs share one rotation, and the text sequence starts again for each chunk. The three-line scheme is measured only in the controlled fixture.

| Text scheme | Overworld, 12 chunks | Nether, 12 chunks | All 24 chunks |
|---|---|---|---|
| Two varied ASCII lines | 26,480–26,541 | 26,471–26,521 | 26,471–26,541 |
| Four varied ASCII lines | 17,225–17,261 | 17,219–17,248 | 17,219–17,261 |
| Four shuffled keyboard-letter lines | 23,226–23,269 | 23,215–23,252 | 23,215–23,269 |

<details>
<summary>Individual chunk boundaries</summary>

Each count is the first rejected save for that prepared chunk and text scheme. One fewer sign saves successfully. Coordinates are chunk coordinates, not block coordinates.

| Dimension | World seed | Chunk (x, z) | Two ASCII lines | Four ASCII lines | Shuffled letters |
|---|---|---|---|---|---|
| Overworld | 173 | (0, 0) | 26,480 | 17,225 | 23,226 |
| Overworld | 173 | (7, −3) | 26,540 | 17,261 | 23,268 |
| Overworld | 173 | (−20, 17) | 26,496 | 17,235 | 23,241 |
| Overworld | 173 | (31,250, −31,250) | 26,531 | 17,253 | 23,248 |
| Overworld | 0 | (0, 0) | 26,511 | 17,246 | 23,253 |
| Overworld | 0 | (7, −3) | 26,540 | 17,261 | 23,269 |
| Overworld | 0 | (−20, 17) | 26,507 | 17,243 | 23,252 |
| Overworld | 0 | (31,250, −31,250) | 26,541 | 17,260 | 23,258 |
| Overworld | 8,675,309 | (0, 0) | 26,519 | 17,250 | 23,259 |
| Overworld | 8,675,309 | (7, −3) | 26,532 | 17,255 | 23,261 |
| Overworld | 8,675,309 | (−20, 17) | 26,509 | 17,244 | 23,253 |
| Overworld | 8,675,309 | (31,250, −31,250) | 26,539 | 17,258 | 23,257 |
| Nether | 173 | (0, 0) | 26,487 | 17,229 | 23,232 |
| Nether | 173 | (7, −3) | 26,506 | 17,239 | 23,240 |
| Nether | 173 | (−20, 17) | 26,484 | 17,228 | 23,233 |
| Nether | 173 | (31,250, −31,250) | 26,520 | 17,245 | 23,238 |
| Nether | 0 | (0, 0) | 26,507 | 17,243 | 23,249 |
| Nether | 0 | (7, −3) | 26,484 | 17,225 | 23,220 |
| Nether | 0 | (−20, 17) | 26,482 | 17,226 | 23,229 |
| Nether | 0 | (31,250, −31,250) | 26,492 | 17,228 | 23,215 |
| Nether | 8,675,309 | (0, 0) | 26,509 | 17,244 | 23,251 |
| Nether | 8,675,309 | (7, −3) | 26,521 | 17,248 | 23,252 |
| Nether | 8,675,309 | (−20, 17) | 26,471 | 17,219 | 23,220 |
| Nether | 8,675,309 | (31,250, −31,250) | 26,501 | 17,234 | 23,223 |

</details>

These measurements describe prepared chambers and the supplied text sequence. They are not universal limits for untouched terrain, other text, another placement order, or another Java/compression runtime. Each boundary is checked by saving N−1 signs through the original region writer, attempting N signs, and comparing the region file before and after the rejected save.
<!-- verification: ChunkThreshold.verifySave also decompresses the stored
     chunk and compares it byte-for-byte with the N-1 fixture. -->

## Building and calibrating

1. Make a backup and use a disposable world copy for calibration. Suppression rolls back every saved block, entity and block entity in the target [[Chunk|chunk]], including [[Sign|signs]] added since its last successful save. Player inventory saves separately.
2. Identify one chunk's exact 16×16 footprint. Prepare a solid floor and a chamber above it. Keep [[Bedrock|bedrock]] intact and allow room for access routes and scaffolding.
3. Place signs bottom-up. The tested layout fills each horizontal layer by traversing local x=0–15 within each local z=0–15 row. Standing signs can support the signs above them. Keep all signs inside the same chunk. Gaps for access change the layout and require recalibration.
4. Enter the selected text scheme in that placement order. Use a fresh pair or set of lines for every sign. Preserve spaces and punctuation in generated text; each ASCII line has exactly 15 characters.
5. Near the measured boundary, establish a successfully saved baseline. Add signs in small batches and make a distinctive block change. Save and actually discard the loaded chunk, then return. A successful save keeps the change; suppression restores the previous saved state. Restore the backup between trials when the test would otherwise consume signs or lose work.
6. Once calibrated, keep the chunk oversized until the intended rollback. Removing enough signs before the final save can make the new state save successfully instead.

<!-- src: ItemSign.java:9-47; BlockSign.java:10,80-103;
     Material.java:47-48,113; RegionFile.java:161-173;
     World.java:278-297; ChunkProvider.java:31-49,130-157 -->

Walking away does not unload a singleplayer chunk. Leaving the world or changing dimension does. On a server, the chunk must actually unload; another nearby player or spawn retention can prevent that. [[Chunk#Loading and unloading|Chunk loading rules]] determine whether the test has discarded its in-memory state.
<!-- src: ChunkProvider.java:11-188; Minecraft.java:1236-1248,1268-1279;
     minecraft_server/ChunkProviderServer.java:32-45,176-188;
     minecraft_server/PlayerInstance.java:44-54 -->

## Generating the measured text

Save the following Python 3 program as `signtext.py`. It reproduces the experiment's Java `Random(173)` sequence without requiring Java or the game jar. Each four-line group belongs to one [[Sign|sign]]; blank lines separate signs.

```python
import sys

count = int(sys.argv[1])
mode = sys.argv[2] if len(sys.argv) > 2 else "2"
state = (173 ^ 0x5DEECE66D) & ((1 << 48) - 1)


def next_int(bound):
    global state
    while True:
        state = (state * 0x5DEECE66D + 11) & ((1 << 48) - 1)
        bits = state >> 17
        if bound & (bound - 1) == 0:
            return bound * bits >> 31
        value = bits % bound
        if bits - value + bound - 1 < (1 << 31):
            return value


alphabet = "".join(chr(c) for c in range(32, 127) if c != 96)
assert mode in ("2", "3", "4", "permuted")
for _ in range(count):
    if mode == "permuted":
        lines = []
        for _ in range(4):
            chars = list("qwertyuiopasdfg")
            for i in range(len(chars) - 1, 0, -1):
                j = next_int(i + 1)
                chars[i], chars[j] = chars[j], chars[i]
            lines.append("".join(chars))
    else:
        unique = int(mode)
        lines = ["".join(alphabet[next_int(94)] for _ in range(15))
                 for _ in range(unique)]
        lines = [lines[i % unique] for i in range(4)]
    print("\n".join(lines) + "\n")
```

```bash
python3 signtext.py 27000 2 > two-line-signs.txt
python3 signtext.py 18000 4 > four-line-signs.txt
python3 signtext.py 24000 permuted > shuffled-letter-signs.txt
```

Mode `3` generates the three-line scheme. The Python output is compared against the Java generator for every line of 32,512 signs in each supported mode. The generated quantities are planning allowances, not guarantees for every chunk.
<!-- verification: GeneratorVerify checks all four lines and blank separator
     of every sign, and checks its portable alphabet against original font.txt. -->

## Evidence and limitations

The tests run headlessly on OpenJDK 17.0.20.1 against Mojang's original Beta 1.7.3 client jar, SHA-1 `43db9b498cb67058d2e12d394e6507722e71bb45`. The original chunk serializer, NBT writer and default deflater produce every measured payload. The original region writer checks every generated-chunk boundary.
<!-- verification: to.a(lm,fd,nu) / ChunkLoader.storeChunkInCompound;
     as.a(nu,DataOutput) / CompressedStreamTools.write;
     qj.b(II) / RegionFile.getChunkDataOutputStream uses default Java deflate.
     Binary-search snapshots start with fresh chunk tile-entity maps, insert
     signs in increasing index order, and use rotation metadata 8. -->

An additional placement test builds the two-line and four-line cases through the game's item-use code. In that run, the boundaries are 26,482 and 17,227 signs. The full chunk loader saves N−1 signs and restores that save after the attempt with N signs. Manual survival construction, GUI typing and dedicated-server execution are not tested.
<!-- verification: PlacementBoundary uses original iz.a(gs,fd,x,y-1,z,1),
     one-item sign stacks, and ld.a(fd,lm) / McRegionChunkLoader.saveChunk.
     Two-line: 26481 / 1044448 bytes saved; 26482 / 1044481 rejected.
     Four-line: 17226 / 1044462 bytes saved; 17227 / 1044522 rejected.
     Text is assigned to signText followed by onInventoryChanged; the GUI and
     player reach are not exercised. No patches replace gameplay or saving.
     Independent runs of the same seed/coordinates need not have the exact
     same prepared light/metadata/iteration state; only saved bytes set N. -->

The original jar is available from [Mojang](https://launcher.mojang.com/v1/objects/43db9b498cb67058d2e12d394e6507722e71bb45/client.jar).
