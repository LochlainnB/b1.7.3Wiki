"""Drawing a block the way the player's inventory draws it.

RenderItem.drawItemIntoGui turns a block into a small three-quarter cube: ten
units across, spun forty-five degrees about the vertical and tipped back, lit
by two fixed lamps so the top face is bright and the two visible sides are not.
This reproduces that in software, at twice the size, which is exactly the
picture a player gets at the doubled GUI scale.

The transform, straight out of that method (the rotations compose to a single
-45 degree turn about Y, then 210 about X, then a Z flip), and the projection
is orthographic:

    glTranslatef(x - 2, y + 3, -3); glScalef(10, 10, 10)
    glTranslatef(1, 0.5, 1);        glScalef(1, 1, -1)
    glRotatef(210, 1, 0, 0);        glRotatef(45, 0, 1, 0)
    ... glRotatef(-90, 0, 1, 0);    renderBlockOnInventory(...)

which leaves the cube centred in its sixteen-pixel slot at ten units to the
block. Faces are drawn into a depth buffer rather than sorted, because a slab,
a stair and a fence all put more than one box on screen and only the depth
buffer gets the overlaps right in every case.

The face texture coordinates below are transcribed from RenderBlocks'
renderTopFace, renderEastFace and their four siblings. Two of the six read
their horizontal axis backwards -- that is what makes a texture face outwards
on both sides of the cube -- and the four upright faces read the vertical one
from the top down. The half-texel insets those methods apply are a guard for
GL's texture filtering and have no meaning for a rasteriser that samples the
nearest texel, so they are dropped.
"""
import math

from png import Image

TILE = 16
SIZE = 32                       # a 16-pixel inventory slot at GUI scale 2

_COS_Y, _SIN_Y = math.cos(math.radians(-45.0)), math.sin(math.radians(-45.0))
_COS_X, _SIN_X = math.cos(math.radians(210.0)), math.sin(math.radians(210.0))

# RenderHelper.enableStandardItemLighting, through the 120-degree turn about X
# that GuiContainer has in the matrix when it calls it.
AMBIENT = 0.4
DIFFUSE = 0.6
_LAMPS = ((0.2, 1.0, -0.7), (-0.2, 1.0, 0.7))


def _eye(x, y, z):
    """Model space to eye space. A rotation and a flip, so lengths survive."""
    ax = x * _COS_Y + z * _SIN_Y
    az = -x * _SIN_Y + z * _COS_Y
    return ax, y * _COS_X - az * _SIN_X, -(y * _SIN_X + az * _COS_X)


def _lights():
    out = []
    turn = math.radians(120.0)
    cos_t, sin_t = math.cos(turn), math.sin(turn)
    for x, y, z in _LAMPS:
        length = math.sqrt(x * x + y * y + z * z)
        x, y, z = x / length, y / length, z / length
        out.append((x, y * cos_t - z * sin_t, y * sin_t + z * cos_t))
    return tuple(out)


LIGHTS = _lights()


def _brightness(normal):
    """The flat-shaded intensity GL gives a face pointing this way."""
    ex, ey, ez = _eye(*normal)
    total = AMBIENT
    for lx, ly, lz in LIGHTS:
        total += DIFFUSE * max(0.0, ex * lx + ey * ly + ez * lz)
    return min(1.0, total)


def _faces(bounds, inset):
    """The six faces of one box: (side, corners, texture coordinates).

    Corners are model space; texture coordinates are in tile pixels, u across
    and v down. A cactus insets its four upright faces, which is the only use
    of the Tessellator translations renderBlockOnInventory makes.
    """
    x0, y0, z0, x1, y1, z1 = bounds
    e = inset
    t = 16.0
    down = lambda y: t - t * y
    return (
        (0, (0.0, -1.0, 0.0),
         ((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)),
         ((t * x0, t * z0), (t * x1, t * z0), (t * x1, t * z1), (t * x0, t * z1))),
        (1, (0.0, 1.0, 0.0),
         ((x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)),
         ((t * x0, t * z0), (t * x1, t * z0), (t * x1, t * z1), (t * x0, t * z1))),
        (2, (0.0, 0.0, -1.0),
         ((x0, y0, z0 + e), (x1, y0, z0 + e), (x1, y1, z0 + e), (x0, y1, z0 + e)),
         ((t * x1, down(y0)), (t * x0, down(y0)), (t * x0, down(y1)), (t * x1, down(y1)))),
        (3, (0.0, 0.0, 1.0),
         ((x0, y0, z1 - e), (x1, y0, z1 - e), (x1, y1, z1 - e), (x0, y1, z1 - e)),
         ((t * x0, down(y0)), (t * x1, down(y0)), (t * x1, down(y1)), (t * x0, down(y1)))),
        (4, (-1.0, 0.0, 0.0),
         ((x0 + e, y0, z0), (x0 + e, y0, z1), (x0 + e, y1, z1), (x0 + e, y1, z0)),
         ((t * z0, down(y0)), (t * z1, down(y0)), (t * z1, down(y1)), (t * z0, down(y1)))),
        (5, (1.0, 0.0, 0.0),
         ((x1 - e, y0, z0), (x1 - e, y0, z1), (x1 - e, y1, z1), (x1 - e, y1, z0)),
         ((t * z1, down(y0)), (t * z0, down(y0)), (t * z0, down(y1)), (t * z1, down(y1)))),
    )


class Canvas(object):
    """An RGBA buffer with a depth buffer behind it."""

    def __init__(self, size):
        self.size = size
        self.px = bytearray(size * size * 4)
        self.depth = [-1e9] * (size * size)

    def triangle(self, verts, sample):
        """Fill one screen-space triangle of (x, y, depth, u, v) vertices.

        The projection is orthographic, so depth and texture coordinates are
        affine in screen space and plain barycentric interpolation is exact.
        """
        (ax, ay, az, au, av), (bx, by, bz, bu, bv), (cx, cy, cz, cu, cv) = verts
        area = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
        if abs(area) < 1e-9:
            return
        lo_x = max(0, int(math.floor(min(ax, bx, cx))))
        hi_x = min(self.size - 1, int(math.ceil(max(ax, bx, cx))))
        lo_y = max(0, int(math.floor(min(ay, by, cy))))
        hi_y = min(self.size - 1, int(math.ceil(max(ay, by, cy))))
        for py in range(lo_y, hi_y + 1):
            y = py + 0.5
            for px in range(lo_x, hi_x + 1):
                x = px + 0.5
                w0 = ((bx - ax) * (y - ay) - (by - ay) * (x - ax)) / area
                w1 = ((x - ax) * (cy - ay) - (y - ay) * (cx - ax)) / area
                if w0 < 0.0 or w1 < 0.0 or w0 + w1 > 1.0:
                    continue
                w2 = 1.0 - w0 - w1
                depth = az * w2 + bz * w1 + cz * w0
                slot = py * self.size + px
                if depth <= self.depth[slot]:
                    continue
                texel = sample(au * w2 + bu * w1 + cu * w0,
                               av * w2 + bv * w1 + cv * w0)
                if texel is None:
                    continue                       # a hole in the texture
                self.depth[slot] = depth
                self.px[slot * 4:slot * 4 + 4] = texel


def _sampler(sheet, tile, shade):
    """Nearest texel of one sheet tile, pre-multiplied by the face's light."""
    x0 = tile % 16 * TILE
    y0 = tile // 16 * TILE
    red, green, blue = shade

    def sample(u, v):
        tx = int(u)
        ty = int(v)
        tx = 0 if tx < 0 else (TILE - 1 if tx > TILE - 1 else tx)
        ty = 0 if ty < 0 else (TILE - 1 if ty > TILE - 1 else ty)
        at = ((y0 + ty) * sheet.w + x0 + tx) * 4
        if not sheet.px[at + 3]:
            return None
        return bytes((int(sheet.px[at] * red), int(sheet.px[at + 1] * green),
                      int(sheet.px[at + 2] * blue), sheet.px[at + 3]))
    return sample


def _rgb(colour):
    return ((colour >> 16 & 255) / 255.0, (colour >> 8 & 255) / 255.0,
            (colour & 255) / 255.0)


def render(sheet, boxes, tint=0xFFFFFF, size=SIZE):
    """One inventory icon: the boxes, textured from `sheet`, into an Image.

    `boxes` are (bounds, six tile indices, inset) as appearance.py reports
    them. `tint` is the colour the game multiplies the block by -- white for
    everything but leaves -- or six of them, one per side, which is how the
    grass block gets a green top and plain grey sides.
    """
    scale = 10.0 * size / TILE
    centre = 8.0 * size / TILE
    tints = tint if isinstance(tint, tuple) else (tint,) * 6
    canvas = Canvas(size)
    for bounds, tiles, inset in boxes:
        for side, normal, corners, uvs in _faces(bounds, inset):
            light = _brightness(normal)
            shade = tuple(c * light for c in _rgb(tints[side]))
            sample = _sampler(sheet, tiles[side], shade)
            screen = []
            for (mx, my, mz), (u, v) in zip(corners, uvs):
                ex, ey, ez = _eye(mx - 0.5, my - 0.5, mz - 0.5)
                screen.append((scale * ex + centre, scale * ey + centre, ez, u, v))
            canvas.triangle((screen[0], screen[1], screen[2]), sample)
            canvas.triangle((screen[0], screen[2], screen[3]), sample)
    out = Image(size, size)
    out.px = canvas.px
    return out


def flat(sheet, tile, tint=0xFFFFFF):
    """One sheet tile as the inventory draws it: the tile, times its tint."""
    x0, y0 = tile % 16 * TILE, tile // 16 * TILE
    out = Image(TILE, TILE)
    red, green, blue = _rgb(tint)
    for y in range(TILE):
        src = ((y0 + y) * sheet.w + x0) * 4
        dst = y * TILE * 4
        for x in range(TILE):
            at = src + x * 4
            out.px[dst + x * 4:dst + x * 4 + 4] = bytes((
                int(sheet.px[at] * red), int(sheet.px[at + 1] * green),
                int(sheet.px[at + 2] * blue), sheet.px[at + 3]))
    return out
