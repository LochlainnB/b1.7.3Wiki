"""Just enough fixed-function OpenGL to draw what the game's model code asks for.

models.py runs ModelPart.render, Quad.render and the Tessellator calls under
them unchanged in interp.py. Every GL11 call they make lands here instead of
on a driver, so the matrices, the display lists and the quads are the game's
own, and only the rasterising is this file's.

The state kept is the state Beta's entity rendering uses: a modelview stack,
display lists, the current colour, the two lamps of
RenderHelper.enableStandardItemLighting, blending and the alpha test. Any
other GL call is a hard error, so a renderer reaching for something new is
noticed rather than drawn wrong.

Rasterising follows GL where it shows: a depth buffer tested GL_LEQUAL, as
EntityRenderer sets it; the alpha test at glAlphaFunc(GL_GREATER, 0.1);
GL_SRC_ALPHA / GL_ONE_MINUS_SRC_ALPHA blending; flat-shaded per-face
lighting, since every vertex of a model quad carries the one normal
Quad.render computes; textures sampled nearest-texel and repeating, as
RenderEngine sets them up. Faces are drawn in the order the game draws them,
so a translucent layer composites exactly as the game composites it -- the
slime's outer cube included.
"""
import math

from interp import Interp, Unsupported

GL11 = 'org/lwjgl/opengl/GL11'

# RenderHelper.enableStandardItemLighting.
AMBIENT = 0.4
DIFFUSE = 0.6
LAMPS = ((0.2, 1.0, -0.7), (-0.2, 1.0, 0.7))


def identity():
    return [1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0]


def mul(a, b):
    """a * b, both row-major 4x4."""
    return [a[r * 4] * b[c] + a[r * 4 + 1] * b[4 + c]
            + a[r * 4 + 2] * b[8 + c] + a[r * 4 + 3] * b[12 + c]
            for r in range(4) for c in range(4)]


def translation(x, y, z):
    m = identity()
    m[3], m[7], m[11] = x, y, z
    return m


def scaling(x, y, z):
    m = identity()
    m[0], m[5], m[10] = x, y, z
    return m


def rotation(degrees, x, y, z):
    """glRotatef's matrix."""
    length = math.sqrt(x * x + y * y + z * z)
    x, y, z = x / length, y / length, z / length
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    t = 1.0 - c
    return [t * x * x + c, t * x * y - s * z, t * x * z + s * y, 0.0,
            t * x * y + s * z, t * y * y + c, t * y * z - s * x, 0.0,
            t * x * z - s * y, t * y * z + s * x, t * z * z + c, 0.0,
            0.0, 0.0, 0.0, 1.0]


def apply(m, x, y, z, w=1.0):
    return (m[0] * x + m[1] * y + m[2] * z + m[3] * w,
            m[4] * x + m[5] * y + m[6] * z + m[7] * w,
            m[8] * x + m[9] * y + m[10] * z + m[11] * w)


def normalize(v):
    length = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) or 1.0
    return (v[0] / length, v[1] / length, v[2] / length)


def normal_matrix(m):
    """The inverse transpose of m's upper 3x3: what GL turns normals by."""
    a, b, c, d, e, f, g, h, i = m[0], m[1], m[2], m[4], m[5], m[6], m[8], m[9], m[10]
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    if not det:
        return (a, b, c, d, e, f, g, h, i)
    k = 1.0 / det
    # The transpose of the inverse is the cofactor matrix over the determinant.
    return ((e * i - f * h) * k, (f * g - d * i) * k, (d * h - e * g) * k,
            (c * h - b * i) * k, (a * i - c * g) * k, (b * g - a * h) * k,
            (b * f - c * e) * k, (c * d - a * f) * k, (a * e - b * d) * k)


class Texture(object):
    """An RGBA image, sampled nearest-texel and repeating."""

    def __init__(self, image):
        self.w, self.h, self.px = image.w, image.h, image.px

    def sample(self, u, v):
        x = int(math.floor(u * self.w)) % self.w
        y = int(math.floor(v * self.h)) % self.h
        at = (y * self.w + x) * 4
        return self.px[at], self.px[at + 1], self.px[at + 2], self.px[at + 3]


class GL(object):
    """The GL state machine, with a rasteriser behind it.

    `lists` is the display-list table. A ModelPart compiles its list the
    first time it is drawn and only calls it after that, so every frame
    drawn from one set of models has to share one table.
    """

    def __init__(self, width, height, lists):
        self.width, self.height = width, height
        self.colour = bytearray(width * height * 4)
        self.depth = [-1e30] * (width * height)
        self.stack = [identity()]
        self.lists = lists
        self.recording = None
        self.rgba = (1.0, 1.0, 1.0, 1.0)
        self.lighting = False
        self.lights = ()
        self.blend = False
        self.alpha_test = True
        self.texture = None
        self.pending = []
        self.normal = (0.0, 0.0, 1.0)

    # -- matrices --------------------------------------------------------------
    @property
    def top(self):
        return self.stack[-1]

    def multiply(self, m):
        self.stack[-1] = mul(self.stack[-1], m)

    def push(self):
        self.stack.append(list(self.stack[-1]))

    def pop(self):
        self.stack.pop()

    def enable_standard_lighting(self):
        """RenderHelper.enableStandardItemLighting.

        A light's position goes through the modelview in force when glLight
        is called, so the lamps are fixed in eye space from here on and
        whatever is drawn later turns under them.
        """
        self.lighting = True
        self.lights = tuple(normalize(apply(self.top, *normalize(lamp), w=0.0))
                            for lamp in LAMPS)

    # -- the Tessellator -------------------------------------------------------
    def vertex(self, x, y, z, u, v):
        self.pending.append((x, y, z, u, v, self.normal))

    def draw(self):
        if len(self.pending) % 4:
            raise Unsupported('Tessellator.draw with %d vertices' % len(self.pending))
        quads = [self.pending[k:k + 4] for k in range(0, len(self.pending), 4)]
        self.pending = []
        if self.recording is not None:
            self.lists[self.recording].extend(quads)
        else:
            for quad in quads:
                self.quad(quad)

    def call_list(self, ident):
        for quad in self.lists.get(ident, ()):
            self.quad(quad)

    # -- rasterising -----------------------------------------------------------
    def shade(self, normal):
        if not self.lighting:
            return 1.0
        n = normal_matrix(self.top)
        x, y, z = normal
        n = normalize((n[0] * x + n[1] * y + n[2] * z,
                       n[3] * x + n[4] * y + n[5] * z,
                       n[6] * x + n[7] * y + n[8] * z))
        total = AMBIENT
        for lx, ly, lz in self.lights:
            total += DIFFUSE * max(0.0, n[0] * lx + n[1] * ly + n[2] * lz)
        return min(1.0, total)

    def quad(self, quad):
        light = self.shade(quad[0][5])
        r, g, b, a = self.rgba
        tint = (r * light, g * light, b * light, a)
        corners = [apply(self.top, x, y, z) + (u, v) for x, y, z, u, v, _n in quad]
        self.triangle(corners[0], corners[1], corners[2], tint)
        self.triangle(corners[0], corners[2], corners[3], tint)

    def triangle(self, p, q, r, tint):
        """Fill one triangle of (x, y, depth, u, v) eye-space vertices.

        The projection is orthographic, so screen x and y are eye x and y, and
        depth and texture coordinates interpolate affinely.
        """
        (ax, ay, az, au, av), (bx, by, bz, bu, bv), (cx, cy, cz, cu, cv) = p, q, r
        area = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
        if abs(area) < 1e-12:
            return
        inv = 1.0 / area
        lo_x = max(0, int(math.floor(min(ax, bx, cx))))
        hi_x = min(self.width - 1, int(math.ceil(max(ax, bx, cx))))
        lo_y = max(0, int(math.floor(min(ay, by, cy))))
        hi_y = min(self.height - 1, int(math.ceil(max(ay, by, cy))))
        sample = self.texture.sample
        tr, tg, tb, ta = tint
        blend, alpha_test = self.blend, self.alpha_test
        width, depth, colour = self.width, self.depth, self.colour
        for py in range(lo_y, hi_y + 1):
            y = py + 0.5
            for px in range(lo_x, hi_x + 1):
                x = px + 0.5
                w1 = ((x - ax) * (cy - ay) - (y - ay) * (cx - ax)) * inv
                w2 = ((bx - ax) * (y - ay) - (by - ay) * (x - ax)) * inv
                w0 = 1.0 - w1 - w2
                if w0 < 0.0 or w1 < 0.0 or w2 < 0.0:
                    continue
                z = az * w0 + bz * w1 + cz * w2
                slot = py * width + px
                if z < depth[slot]:                       # GL_LEQUAL; nearer is larger
                    continue
                sr, sg, sb, sa = sample(au * w0 + bu * w1 + cu * w2,
                                        av * w0 + bv * w1 + cv * w2)
                fa = sa / 255.0 * ta
                if alpha_test and fa <= 0.1:
                    continue
                at = slot * 4
                fr, fg, fb = sr * tr, sg * tg, sb * tb
                if blend:
                    keep = 1.0 - fa
                    fr = fr * fa + colour[at] * keep
                    fg = fg * fa + colour[at + 1] * keep
                    fb = fb * fa + colour[at + 2] * keep
                    out_a = fa * 255.0 + colour[at + 3] * keep
                else:
                    out_a = 255.0
                colour[at] = min(255, int(fr + 0.5))
                colour[at + 1] = min(255, int(fg + 0.5))
                colour[at + 2] = min(255, int(fb + 0.5))
                colour[at + 3] = min(255, int(out_a + 0.5))
                depth[slot] = z

    # -- wiring into the interpreter ---------------------------------------------
    def install(self, interp, names):
        """Answer GL11, GlAllocation and the Tessellator from this context.

        `names` carries the jar's names for the Tessellator and GlAllocation.
        Installing again moves the hooks to another context; the display
        lists stay where they are.
        """
        nothing = Interp.NOTHING
        hooks = interp.hooks

        def hook(owner, name, desc, fn):
            hooks[(owner, name, desc)] = lambda _it, _recv, args: (fn(*args), nothing)[1]

        def new_list(ident, _mode):
            self.recording = ident
            self.lists[ident] = []

        def end_list():
            self.recording = None

        def gen_lists(_it, _recv, args):
            ident = self.lists['next']
            self.lists['next'] += args[0]
            return ident

        def normal(x, y, z):
            self.normal = (x, y, z)

        hook(GL11, 'glPushMatrix', '()V', lambda: self.push())
        hook(GL11, 'glPopMatrix', '()V', lambda: self.pop())
        hook(GL11, 'glTranslatef', '(FFF)V', lambda x, y, z: self.multiply(translation(x, y, z)))
        hook(GL11, 'glScalef', '(FFF)V', lambda x, y, z: self.multiply(scaling(x, y, z)))
        hook(GL11, 'glRotatef', '(FFFF)V',
             lambda deg, x, y, z: self.multiply(rotation(deg, x, y, z)))
        hook(GL11, 'glNewList', '(II)V', new_list)
        hook(GL11, 'glEndList', '()V', end_list)
        hook(GL11, 'glCallList', '(I)V', lambda ident: self.call_list(ident))
        hooks[(names['glalloc'], names['generateDisplayLists'], '(I)I')] = gen_lists

        t = names['tessellator']
        hook(t, names['startQuads'], '()V', lambda: None)
        hook(t, names['normal'], '(FFF)V', normal)
        hook(t, names['vertexUV'], '(DDDDD)V', lambda x, y, z, u, v: self.vertex(x, y, z, u, v))
        hook(t, names['draw'], '()V', lambda: self.draw())
