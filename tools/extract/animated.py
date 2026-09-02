"""The tiles Beta 1.7.3 draws for itself instead of shipping.

A handful of the sheets' tiles are placeholders. The game overwrites them in
the texture atlas at load with a TextureFX, and what is left behind in the file
is whatever the artist happened to leave there: the portal is a flat blue
square, the clock's dial is magenta, and the compass has no needle at all.

These three are reproduced here, from TexturePortalFX, TextureWatchFX and
TextureCompassFX, so a page shows the tile a player sees rather than the tile
the file holds.

Each of those classes animates: the portal cycles thirty-two frames, and the
clock and compass turn to follow the sun and the world spawn. A wiki page is
one picture, so each is generated in its rest state -- the portal's first
frame, and the needle and dial at the angle a TextureFX holds before any world
is loaded, which is what the class's own fields start at.

The water, lava and fire tiles are generated the same way, but by simulations
with no rest state to speak of: they are seeded from the shipped tile and
stirred every tick, so there is no one frame to call theirs. Those are left as
the sheet has them.
"""
import math
import struct

TILE = 16
GRID = 16


def f32(v):
    """Round to the nearest 32-bit float, as every Java float operation does."""
    return struct.unpack('<f', struct.pack('<f', v))[0]


class JavaRandom(object):
    """java.util.Random. The portal's noise is seeded, so it must match."""

    def __init__(self, seed):
        self.state = (seed ^ 0x5DEECE66D) & ((1 << 48) - 1)

    def _next(self, bits):
        self.state = (self.state * 0x5DEECE66D + 0xB) & ((1 << 48) - 1)
        return self.state >> (48 - bits)

    def next_float(self):
        return f32(self._next(24) / float(1 << 24))


_SIN_TABLE = None


def mh_sin(v):
    """MathHelper.sin: a 65536-entry lookup, not Math.sin.

    The portal's swirl is sampled from this table, and the table is coarse
    enough that using a real sine would move pixels.
    """
    global _SIN_TABLE
    if _SIN_TABLE is None:
        _SIN_TABLE = [f32(math.sin(i * math.pi * 2.0 / 65536.0)) for i in range(65536)]
    return _SIN_TABLE[int(v * f32(10430.378)) & 0xFFFF]


def _tile_origin(index):
    return index % GRID * TILE, index // GRID * TILE


def _read_tile(sheet, index):
    """One tile as a list of 256 (r, g, b, a) tuples, row-major."""
    x0, y0 = _tile_origin(index)
    out = []
    for y in range(TILE):
        row = ((y0 + y) * sheet.w + x0) * 4
        for x in range(TILE):
            out.append(tuple(sheet.px[row + x * 4:row + x * 4 + 4]))
    return out


def _write_tile(sheet, index, pixels):
    x0, y0 = _tile_origin(index)
    for y in range(TILE):
        row = ((y0 + y) * sheet.w + x0) * 4
        for x in range(TILE):
            sheet.px[row + x * 4:row + x * 4 + 4] = bytes(pixels[y * TILE + x])


def portal_tile():
    """TexturePortalFX's first frame.

    The class builds all thirty-two frames in its constructor from
    `new Random(100L)`, so the answer is fixed and the arithmetic below is the
    constructor's, byte truncation included.
    """
    rand = JavaRandom(100)
    frames = [[None] * (TILE * TILE) for _ in range(32)]
    for frame in range(32):
        for x in range(TILE):
            for y in range(TILE):
                total = 0.0
                for pass_ in range(2):
                    offset = f32(pass_ * 8)
                    dx = f32(f32(f32(x) - offset) / 16.0 * 2.0)
                    dy = f32(f32(f32(y) - offset) / 16.0 * 2.0)
                    if dx < -1.0:
                        dx = f32(dx + 2.0)
                    if dx >= 1.0:
                        dx = f32(dx - 2.0)
                    if dy < -1.0:
                        dy = f32(dy + 2.0)
                    if dy >= 1.0:
                        dy = f32(dy - 2.0)
                    dist = f32(f32(dx * dx) + f32(dy * dy))
                    angle = f32(math.atan2(dy, dx))
                    spin = f32(f32(f32(frame) / 32.0 * f32(3.1415927) * 2.0)
                               - f32(dist * 10.0) + f32(pass_ * 2))
                    angle = f32(angle + f32(spin * f32(pass_ * 2 - 1)))
                    value = f32(f32(mh_sin(angle) + 1.0) / 2.0)
                    value = f32(value / f32(dist + 1.0))
                    total = f32(total + f32(value * 0.5))
                total = f32(total + f32(rand.next_float() * 0.1))
                blue = int(f32(total * 100.0 + 155.0))
                red = int(f32(f32(total * total) * 200.0 + 55.0))
                green = int(f32(f32(f32(total * total) * f32(total * total)) * 255.0))
                alpha = int(f32(total * 100.0 + 155.0))
                frames[frame][y * TILE + x] = (red & 255, green & 255, blue & 255, alpha & 255)
    return frames[0]


def compass_tile(items_sheet, index):
    """TextureCompassFX with the needle at rest.

    Without a world the class's target angle is zero, and the angle it holds
    starts there, so the needle lies along the tile's vertical axis: a grey
    crossbar and a half-red pointer, drawn over the item's own tile.
    """
    pixels = list(_read_tile(items_sheet, index))
    sin_a, cos_a = 0.0, 1.0
    for step in range(-4, 5):
        x = int(8.5 + cos_a * step * 0.3)
        y = int(7.5 - sin_a * step * 0.3 * 0.5)
        pixels[y * TILE + x] = (100, 100, 100, 255)
    for step in range(-8, 17):
        x = int(8.5 + sin_a * step * 0.3)
        y = int(7.5 + cos_a * step * 0.3 * 0.5)
        pixels[y * TILE + x] = ((255, 20, 20, 255) if step >= 0 else (100, 100, 100, 255))
    return pixels


def clock_tile(items_sheet, dial, index):
    """TextureWatchFX with the dial at rest.

    The item's own tile carries a magenta mask -- red and blue equal, green
    zero -- marking the window the dial shows through. Every masked pixel is
    replaced by misc/dial.png, sampled at the dial's rotation and dimmed by how
    strong the mask was there. With no world the rotation is zero, so the
    sampling reduces to a horizontal mirror, which is the game's own doing.
    """
    face = _read_tile(items_sheet, index)
    dial_px = _read_tile(dial, 0)
    sin_a, cos_a = 0.0, 1.0
    out = []
    for i, (red, green, blue, alpha) in enumerate(face):
        if red == blue and green == 0 and blue > 0:
            u = -((i % TILE) / 15.0 - 0.5)
            v = (i // TILE) / 15.0 - 0.5
            sx = int((u * cos_a + v * sin_a + 0.5) * 16.0)
            sy = int((v * cos_a - u * sin_a + 0.5) * 16.0)
            dr, dg, db, da = dial_px[(sx & 15) + (sy & 15) * TILE]
            out.append((dr * red // 255, dg * red // 255, db * red // 255, da))
        else:
            out.append((red, green, blue, alpha))
    return out


def patch_sheets(terrain, items, dial, portal_index, compass_index, clock_index):
    """Overwrite the three placeholder tiles in place. Returns what was fixed."""
    fixed = []
    if portal_index is not None:
        _write_tile(terrain, portal_index, portal_tile())
        fixed.append('portal (terrain %d)' % portal_index)
    if compass_index is not None:
        _write_tile(items, compass_index, compass_tile(items, compass_index))
        fixed.append('compass (items %d)' % compass_index)
    if clock_index is not None and dial is not None:
        _write_tile(items, clock_index, clock_tile(items, dial, clock_index))
        fixed.append('clock (items %d)' % clock_index)
    return fixed
