"""The tiles Beta 1.7.3 draws for itself instead of shipping.

A handful of the sheets' tiles are placeholders. The game overwrites them in
the texture atlas at load with a TextureFX, and what is left behind in the file
is whatever the artist happened to leave there: the portal is a flat blue
square, the clock's dial is magenta, and the compass has no needle at all.

All eight TextureFX classes the game registers are reproduced here, so a page
shows the tile a player sees rather than the tile the file holds.

Five of them have a rest state and are generated in it: the portal cycles
thirty-two frames and takes its first, and the clock and compass turn to
follow the sun and the world spawn, so each is drawn at the angle its own
fields start at, before any world is loaded.

Water, lava and fire have no rest state. They are stirred every tick from
Math.random(), which the game never seeds, so no frame is *the* frame and
none can be matched byte for byte. Each is instead run from a seed of this
module's own -- the index of the tile it paints -- for long enough to settle
into the texture it spends its life looking like. That is also why the float
rounding in those three is looser than the portal's: with the noise arbitrary
there is no exact answer to hit, so only the values that are stored round to
32 bits.
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

    def next_double(self):
        """Math.random(), which is one shared unseeded Random's nextDouble."""
        return ((self._next(26) << 27) + self._next(27)) / float(1 << 53)


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


# How long to stir the three unseeded textures before taking a frame. Lava is
# the slowest to fill -- a spark lands on one cell in two hundred per tick --
# and by here all three have stopped changing shape.
SETTLE = 240


def water_tile(index, flowing=False, ticks=SETTLE):
    """TextureWaterFX, or TextureWaterFlowFX when `flowing`.

    A field of springs. Each cell is pushed at random, the push fades, and the
    surface it leaves is blurred into its neighbours. The flowing tile blurs
    upwards only and scrolls what it has by a row a tick, which is what makes
    it look like it is running downhill.
    """
    rand = JavaRandom(index)
    surface, spare = [0.0] * 256, [0.0] * 256
    height, push = [0.0] * 256, [0.0] * 256
    spread = 3.2 if flowing else 3.3
    chance = 0.2 if flowing else 0.05
    fade = 0.3 if flowing else 0.1
    for _ in range(ticks):
        for x in range(TILE):
            for y in range(TILE):
                total = 0.0
                if flowing:
                    for v in range(y - 2, y + 1):
                        total += surface[x + (v & 15) * TILE]
                else:
                    for u in range(x - 1, x + 2):
                        total += surface[(u & 15) + y * TILE]
                spare[x + y * TILE] = f32(total / spread + height[x + y * TILE] * 0.8)
        for x in range(TILE):
            for y in range(TILE):
                at = x + y * TILE
                height[at] = f32(max(0.0, height[at] + push[at] * 0.05))
                push[at] = f32(push[at] - fade)
                if rand.next_double() < chance:
                    push[at] = 0.5
        surface, spare = spare, surface
    scroll = ticks * TILE if flowing else 0
    out = []
    for at in range(256):
        depth = min(1.0, max(0.0, surface[at - scroll & 255]))
        lit = f32(depth * depth)
        out.append((int(32.0 + lit * 32.0), int(50.0 + lit * 64.0), 255,
                    int(146.0 + lit * 50.0)))
    return out


def lava_tile(index, flowing=False, ticks=SETTLE):
    """TextureLavaFX, or TextureLavaFlowFX when `flowing`.

    The same springs as water, but the blur covers all eight neighbours and is
    fetched through an offset taken from MathHelper.sin of the *other*
    coordinate, which curdles the surface instead of rippling it.
    """
    rand = JavaRandom(index)
    heat, spare = [0.0] * 256, [0.0] * 256
    glow, push = [0.0] * 256, [0.0] * 256
    for _ in range(ticks):
        for x in range(TILE):
            for y in range(TILE):
                at = x + y * TILE
                across = int(mh_sin(f32(y * 3.1415927 * 2.0 / 16.0)) * 1.2)
                down = int(mh_sin(f32(x * 3.1415927 * 2.0 / 16.0)) * 1.2)
                total = 0.0
                for u in range(x - 1, x + 2):
                    for v in range(y - 1, y + 2):
                        total += heat[(u + across & 15) + (v + down & 15) * TILE]
                corners = (glow[at] + glow[(x + 1 & 15) + y * TILE]
                           + glow[(x + 1 & 15) + (y + 1 & 15) * TILE]
                           + glow[x + (y + 1 & 15) * TILE])
                spare[at] = f32(total / 10.0 + corners / 4.0 * 0.8)
                glow[at] = f32(max(0.0, glow[at] + push[at] * 0.01))
                push[at] = f32(push[at] - 0.06)
                if rand.next_double() < 0.005:
                    push[at] = 1.5
        heat, spare = spare, heat
    scroll = ticks // 3 * TILE if flowing else 0
    out = []
    for at in range(256):
        v = min(1.0, max(0.0, f32(heat[at - scroll & 255] * 2.0)))
        out.append((int(v * 100.0 + 155.0), int(v * v * 255.0),
                    int(v * v * v * v * 128.0), 255))
    return out


def flames_tile(index, ticks=SETTLE):
    """TextureFlamesFX: sixteen columns, twenty rows tall.

    The bottom four rows are off the tile. They are re-lit at random every
    tick and the heat is carried up the column, so what shows is the top
    sixteen rows of a fire whose base is out of frame. Alpha is all or nothing
    at half brightness, which is what gives a flame its ragged edge.
    """
    rand = JavaRandom(index)
    heat, spare = [0.0] * 320, [0.0] * 320
    for _ in range(ticks):
        for x in range(TILE):
            for y in range(20):
                # The weight starts at eighteen for the cell below and counts
                # the six it then samples, on the grid or not, so the divisor
                # always ends at twenty-four.
                weight = 18
                total = heat[x + (y + 1) % 20 * TILE] * weight
                for u in range(x - 1, x + 2):
                    for v in range(y, y + 2):
                        if 0 <= u < TILE and 0 <= v < 20:
                            total += heat[u + v * TILE]
                        weight += 1
                spare[x + y * TILE] = f32(total / (weight * 1.06))
                if y >= 19:
                    spare[x + y * TILE] = f32(
                        rand.next_double() * rand.next_double()
                        * rand.next_double() * 4.0 + rand.next_double() * 0.1 + 0.2)
        heat, spare = spare, heat
    out = []
    for at in range(256):
        v = min(1.0, max(0.0, f32(heat[at] * 1.8)))
        out.append((int(v * 155.0 + 100.0), int(v * v * 255.0),
                    int(v ** 10 * 255.0), 255 if v >= 0.5 else 0))
    return out


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


def patch_sheets(terrain, items, dial, tiles):
    """Overwrite every placeholder tile in place. Returns what was fixed.

    `tiles` gives the atlas index each TextureFX paints over, read out of the
    game rather than typed here: 'portal', 'water', 'lava' and 'fire' on the
    terrain sheet, 'compass' and 'clock' on the item sheet. One that is
    missing is skipped. The second tile of each pair is the flowing or second
    animation the game registers beside the first, at the offset that class's
    own constructor uses.
    """
    fixed = []

    def paint(sheet, index, pixels, size=1):
        """Write one tile, across the size x size block the game paints it
        into: flowing water and lava each cover four."""
        for dy in range(size):
            for dx in range(size):
                _write_tile(sheet, index + dx + dy * GRID, pixels)

    def done(what, sheet, *indices):
        fixed.append('%s (%s %s)' % (what, sheet, ', '.join(str(i) for i in indices)))

    if tiles.get('portal') is not None:
        paint(terrain, tiles['portal'], portal_tile())
        done('portal', 'terrain', tiles['portal'])
    if tiles.get('water') is not None:
        still, flow = tiles['water'], tiles['water'] + 1
        paint(terrain, still, water_tile(still))
        paint(terrain, flow, water_tile(flow, flowing=True), 2)
        done('water', 'terrain', still, flow)
    if tiles.get('lava') is not None:
        still, flow = tiles['lava'], tiles['lava'] + 1
        paint(terrain, still, lava_tile(still))
        paint(terrain, flow, lava_tile(flow, flowing=True), 2)
        done('lava', 'terrain', still, flow)
    if tiles.get('fire') is not None:
        low, high = tiles['fire'], tiles['fire'] + GRID
        paint(terrain, low, flames_tile(low))
        paint(terrain, high, flames_tile(high))
        done('fire', 'terrain', low, high)
    if tiles.get('compass') is not None:
        paint(items, tiles['compass'], compass_tile(items, tiles['compass']))
        done('compass', 'items', tiles['compass'])
    if tiles.get('clock') is not None and dial is not None:
        paint(items, tiles['clock'], clock_tile(items, dial, tiles['clock']))
        done('clock', 'items', tiles['clock'])
    return fixed
