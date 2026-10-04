---
title: Suppressing Chunk Saves
description: Working sign-text schemes, sign quantities, and steps for suppressing a chunk's saves.
type: guide
categories: [Guides]
---

**Suppressing chunk saves** with [[Sign|signs]] prevents a [[Chunk|chunk]] from saving its new state.
<!-- src: RegionFile.java:161-173; McRegionChunkLoader.java:42-57 -->

## Sign text and quantities

Fill all four lines of each [[Sign|sign]] with 15 characters. A–D below represent independently generated lines, not literal letters. Generate a fresh set for every sign.

| Scheme | Lines on each sign | Signs at first rejected save |
|---|---|---|
| Four varied ASCII lines | A, B, C, D | 17,219–17,261 |
| Two varied ASCII lines | A, B, A, B | 26,471–26,541 |
| Shuffled keyboard letters | Four independently shuffled copies of `qwertyuiopasdfg` | 23,215–23,269 |

These ranges come from automated tests of 24 cleared chunks in both dimensions. The count depends on the text, layout and other chunk data; test the target chunk rather than assuming a fixed threshold.
<!-- verification: ChunkThreshold, original client.jar, OpenJDK 17.0.20.1,
     2026-10-04. Three seeds (173, 0, 8675309), four chunk positions
     ((0,0), (7,-3), (-20,17), (31250,-31250)), both dimensions.
     Stone floor y=5; signs start y=6; cleared through y=127 Overworld /
     y=122 Nether; natural lower terrain/Nether roof retained; lighting
     drained; no entities/other tile entities; sign rotation metadata 8.
     Text is Java Random(173), restarting for each chunk. Binary search and
     +/-16 count checks; original region writer saves N-1, rejects N and
     leaves the previous region bytes unchanged. Manual construction untested.
     PlacementBoundary independently saves 17226 four-line signs and rejects
     17227 through ItemStack.useItem and McRegionChunkLoader. Jar SHA-1:
     43db9b498cb67058d2e12d394e6507722e71bb45. -->

Reusing one fixed line throughout the chunk compresses too well. A single fresh line per sign, repeated four times, also falls short in the tested fixtures.
<!-- verification: SignThreshold and RepeatedSave, 32512-sign synthetic
     fixture: qwerty 135231 bytes, punctuation 135286, accented 142286,
     one varied ASCII line/sign 852186; all save below the 1044475-byte limit. -->
<!-- src: GuiEditSign.java:58-62; ChatAllowedCharacters.java:10-27;
     original font.txt checked: 94 printable ASCII characters, no backtick. -->

## Building and testing

1. Back up the world and test on a copy. A rollback loses all chunk changes since the last successful save. Player inventory saves separately.
2. Mark one [[Chunk|chunk]]'s exact 16×16 footprint. Prepare a chamber with a solid floor near [[Bedrock|bedrock]] and room for access. Save the prepared chamber.
3. Place [[Sign|signs]] bottom-up, layer by layer, using the chosen text scheme. Signs can support signs above them. Keep their rotation consistent and all signs inside the same chunk.
4. Near the listed count, add signs in small batches. Make a distinctive block change, save, then unload and reload the chunk. If the change disappears, saving is suppressed. Restore the backup between trials as needed.
5. Keep the chunk oversized until the intended rollback. Removing enough signs can allow a later save to keep the new state instead.

<!-- src: ItemSign.java:9-47; BlockSign.java:10,80-103;
     Material.java:47-48,113; RegionFile.java:161-173;
     World.java:278-297; ChunkProvider.java:31-49,130-157 -->

In singleplayer, leave and reopen the world or change dimension; walking away does not unload the chunk. On a server, other nearby players or spawn retention can prevent unloading.
<!-- src: ChunkProvider.java:11-188; Minecraft.java:1236-1248,1268-1279;
     minecraft_server/ChunkProviderServer.java:32-45,176-188;
     minecraft_server/PlayerInstance.java:44-54 -->

## Preparing text

Save the Python 3 generator below as `signtext.py`. It produces four lines per [[Sign|sign]], with a blank line between signs. Preserve spaces and punctuation when entering the text.

<details>
<summary>Python text generator</summary>

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

</details>

```bash
python3 signtext.py 18000 4 > four-line-signs.txt
python3 signtext.py 27000 2 > two-line-signs.txt
python3 signtext.py 24000 permuted > shuffled-letter-signs.txt
```

The quantities provide spare text, not guaranteed thresholds. The vanilla sign editor has no clipboard-paste support; this program prepares text but does not enter it into the game.
<!-- src: GuiEditSign.java:45-65; GuiScreen.java:31-49,119-124.
     verification: GeneratorVerify compares every line and separator for
     32512 signs against the measured Java Random(173) sequence in all modes. -->
