"""Just enough fixed-function OpenGL to draw what the game's renderers ask for.

models.py runs the game's entity renderers unchanged in interp.py: the
renderer, the model, ModelPart, the Tessellator calls under them and the held
item. Every GL11 call they make lands here instead of on a driver, so the
matrices, the display lists, the quads, the textures bound and the state
switched on and off are the game's own. Only the rasterising is this file's.

The state kept is the state Beta's entity rendering touches: the modelview
and texture matrices, display lists, the current colour, the two lamps of
RenderHelper.enableStandardItemLighting, lighting, texturing, blending, the
alpha test and the depth test. Any GL call or mode not listed is a hard
error, so a renderer reaching for something new is noticed rather than drawn
wrong. Face culling is the one switch kept and not acted on: every renderer
here turns it off before it draws, and drawing with it on is refused.

Nothing is rasterised while the game's code runs. Every face it draws is
recorded, already transformed: its corners and normal in the space the
caller set up, its colour, whether it is lit, its texture, and the blend and
depth state in force. Frame then rasterises a record under any further
placement, so one run of the game's code can be measured, framed and drawn,
and the faces that make up a mob's head picked out and drawn alone.

Rasterising follows GL where it shows: the lighting equation with
GL_COLOR_MATERIAL, so a face is its colour times the light, clamped; a depth
buffer; the alpha test at glAlphaFunc(GL_GREATER, 0.1), which the game sets
once at start-up; texels sampled nearest and repeating, as RenderEngine sets
mob textures up; faces drawn in the order the game draws them, so a
translucent layer composites exactly as the game composites it.

Normals go through the same narrowing the game puts them through.
Tessellator.setNormal packs each into three signed bytes for a GL_BYTE
normal array, x times 128 and y and z times 127, so an x of exactly 1 comes
out as byte 128, which wraps to -128: -1. Every face pointing straight
along +x is lit as though it pointed the other way. That is how the game
lights its models, and checked against the running client it is the only
thing that makes those faces come out right.

One thing GL does has no equivalent in a picture with a transparent
background: additive blending onto nothing. Over a pixel nothing has been
drawn to, an additive layer keeps its own colour with the brightest of its
channels as its opacity, so it reads as a glow on any page colour.
"""
import math

from interp import Interp, Unsupported

GL11 = 'org/lwjgl/opengl/GL11'

# RenderHelper.enableStandardItemLighting.
AMBIENT = 0.4
DIFFUSE = 0.6
LAMPS = ((0.2, 1.0, -0.7), (-0.2, 1.0, 0.7))

# glEnable / glDisable capabilities, by the constant the game passes.
CAPS = {2896: 'lighting', 3042: 'blend', 3008: 'alpha_test', 3553: 'texture_2d',
        2884: 'cull_face', 2929: 'depth_test', 32826: 'rescale_normal', 2977: 'normalize'}
# Capabilities that change nothing a flat-shaded rasteriser could show:
# colour material (always on here, as RenderHelper has it), and the two lamps
# themselves.
INERT = {2903, 16384, 16385}

MODELVIEW, TEXTURE = 5888, 5890
ONE, SRC_ALPHA, ONE_MINUS_SRC_ALPHA = 1, 770, 771
EQUAL, LEQUAL = 514, 515


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


def packed_normal(x, y, z):
    """Tessellator.setNormal's bytes, read back as GL reads a GL_BYTE normal."""
    def byte(v):
        v = int(v) & 0xFF                     # Java's (byte)(int)f
        return v - 0x100 if v & 0x80 else v
    return tuple(max(c / 127.0, -1.0) for c in (byte(x * 128.0), byte(y * 127.0), byte(z * 127.0)))


def turn(n, v):
    """A direction through a normal matrix, renormalised."""
    x, y, z = v
    return normalize((n[0] * x + n[1] * y + n[2] * z,
                      n[3] * x + n[4] * y + n[5] * z,
                      n[6] * x + n[7] * y + n[8] * z))


class Texture(object):
    """An RGBA image, sampled nearest-texel and repeating."""

    def __init__(self, image):
        self.w, self.h, self.px = image.w, image.h, image.px

    def sample(self, u, v):
        x = int(math.floor(u * self.w)) % self.w
        y = int(math.floor(v * self.h)) % self.h
        at = (y * self.w + x) * 4
        return self.px[at], self.px[at + 1], self.px[at + 2], self.px[at + 3]


class Draw(object):
    """One face as the game drew it, ready to rasterise."""
    __slots__ = ('corners', 'normal', 'rgba', 'lit', 'texture', 'textured', 'blend',
                 'blend_func', 'alpha_test', 'depth_test', 'depth_mask', 'depth_func',
                 'source')

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


class GL(object):
    """The GL state machine, recording what is drawn into `draws`.

    `lists` is the display-list table, shared by every context drawing one
    set of models: a ModelPart compiles its list the first time it is drawn
    and only calls it after that. Texture ids handed out for paths live in it
    too, for the same reason.

    Each Draw carries `source`: the display list it came from and the
    modelview it was called under, or None for a face drawn directly. That
    is how one model part is told apart from the rest.
    """

    def __init__(self, lists):
        self.lists = lists
        self.draws = []
        self.source = None
        self.stack = [identity()]
        self.texture_matrix = identity()
        self.mode = MODELVIEW
        self.recording = None
        self.rgba = (1.0, 1.0, 1.0, 1.0)
        self.lights = ()
        self.lighting = False
        self.blend = False
        self.alpha_test = True
        self.texture_2d = True
        self.cull_face = False
        self.depth_test = True
        self.rescale_normal = False
        self.normalize = False
        self.depth_mask = True
        self.depth_func = LEQUAL
        self.blend_func = (SRC_ALPHA, ONE_MINUS_SRC_ALPHA)
        self.texture_path = None
        self.pending = []
        self.normal = (0.0, 0.0, 1.0)

    # -- matrices --------------------------------------------------------------
    @property
    def top(self):
        return self.stack[-1]

    def multiply(self, m):
        if self.mode == TEXTURE:
            self.texture_matrix = mul(self.texture_matrix, m)
        else:
            self.stack[-1] = mul(self.stack[-1], m)

    def load_identity(self):
        if self.mode != TEXTURE:
            raise Unsupported('glLoadIdentity on the modelview')
        self.texture_matrix = identity()

    def matrix_mode(self, mode):
        if mode not in (MODELVIEW, TEXTURE):
            raise Unsupported('glMatrixMode(%d)' % mode)
        self.mode = mode

    def push(self):
        if self.mode != MODELVIEW:
            raise Unsupported('glPushMatrix on the texture matrix')
        self.stack.append(list(self.stack[-1]))

    def pop(self):
        if self.mode != MODELVIEW:
            raise Unsupported('glPopMatrix on the texture matrix')
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

    # -- state -------------------------------------------------------------------
    def enable(self, cap, on):
        if cap in INERT:
            return
        if cap not in CAPS:
            raise Unsupported('gl%s(%d)' % ('Enable' if on else 'Disable', cap))
        setattr(self, CAPS[cap], bool(on))

    def set_blend_func(self, src, dst):
        if (src, dst) not in ((SRC_ALPHA, ONE_MINUS_SRC_ALPHA), (ONE, ONE)):
            raise Unsupported('glBlendFunc(%d, %d)' % (src, dst))
        self.blend_func = (src, dst)

    def set_depth_func(self, func):
        if func not in (EQUAL, LEQUAL):
            raise Unsupported('glDepthFunc(%d)' % func)
        self.depth_func = func

    def texture_id(self, path):
        ids = self.lists.setdefault('textures', {})
        if path not in ids:
            ids[path] = len(ids) + 1
        return ids[path]

    def bind(self, ident):
        for path, known in self.lists.get('textures', {}).items():
            if known == ident:
                self.texture_path = path
                return
        raise Unsupported('glBindTexture(%r): no such texture' % ident)

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
        self.source = (ident, tuple(self.top))
        for quad in self.lists.get(ident, ()):
            self.quad(quad)
        self.source = None

    def eye_normal(self, m, normal):
        """A normal as GL lights it: through the inverse transpose, then
        renormalised under GL_NORMALIZE, or under GL_RESCALE_NORMAL divided by
        the scale the modelview puts on z -- which leaves it unit length only
        where the modelview scales evenly. The ghast about to fire is
        stretched, and GL lights its tentacles with the longer normals."""
        n = normal_matrix(m)
        x, y, z = normal
        v = (n[0] * x + n[1] * y + n[2] * z, n[3] * x + n[4] * y + n[5] * z,
             n[6] * x + n[7] * y + n[8] * z)
        if self.normalize:
            return normalize(v)
        if self.rescale_normal:
            # The inverse modelview's third row is the third column of the
            # normal matrix.
            f = math.sqrt(n[2] * n[2] + n[5] * n[5] + n[8] * n[8]) or 1.0
            return (v[0] / f, v[1] / f, v[2] / f)
        return v

    def quad(self, quad):
        if self.cull_face:
            raise Unsupported('drawing with face culling on')
        if self.texture_2d and self.texture_path is None:
            raise Unsupported('drawing with no texture bound')
        m, tm = self.top, self.texture_matrix
        corners = []
        for x, y, z, u, v, _n in quad:
            tu, tv, _tw = apply(tm, u, v, 0.0)
            corners.append(apply(m, x, y, z) + (tu, tv))
        self.draws.append(Draw(
            corners=corners, normal=self.eye_normal(m, quad[0][5]), rgba=self.rgba,
            lit=self.lighting, texture=self.texture_path, textured=self.texture_2d,
            blend=self.blend, blend_func=self.blend_func, alpha_test=self.alpha_test,
            depth_test=self.depth_test, depth_mask=self.depth_mask,
            depth_func=self.depth_func, source=self.source))

    # -- wiring into the interpreter ---------------------------------------------
    def install(self, interp, names):
        """Answer GL11, GlAllocation, the Tessellator and RenderEngine from here.

        `names` carries the jar's names for the Tessellator's, GlAllocation's
        and RenderEngine's methods. Installing again moves the hooks to
        another context; display lists and texture ids stay where they are.
        """
        nothing = Interp.NOTHING
        hooks = interp.hooks

        def hook(owner, name, desc, fn):
            hooks[(owner, name, desc)] = lambda _it, _recv, args: (fn(*args), nothing)[1]

        def answer(owner, name, desc, fn):
            hooks[(owner, name, desc)] = lambda _it, _recv, args: fn(*args)

        def new_list(ident, _mode):
            self.recording = ident
            self.lists[ident] = []

        def end_list():
            self.recording = None

        def gen_lists(count):
            ident = self.lists['next']
            self.lists['next'] += count
            return ident

        def normal(x, y, z):
            self.normal = packed_normal(x, y, z)

        def colour(r, g, b, a=1.0):
            self.rgba = (r, g, b, a)

        def bind(target, ident):
            if target != 3553:
                raise Unsupported('glBindTexture(%d, ...)' % target)
            self.bind(ident)

        def depth_mask(flag):
            self.depth_mask = bool(flag)

        hook(GL11, 'glPushMatrix', '()V', lambda: self.push())
        hook(GL11, 'glPopMatrix', '()V', lambda: self.pop())
        hook(GL11, 'glTranslatef', '(FFF)V', lambda x, y, z: self.multiply(translation(x, y, z)))
        hook(GL11, 'glScalef', '(FFF)V', lambda x, y, z: self.multiply(scaling(x, y, z)))
        hook(GL11, 'glRotatef', '(FFFF)V',
             lambda deg, x, y, z: self.multiply(rotation(deg, x, y, z)))
        hook(GL11, 'glMatrixMode', '(I)V', lambda mode: self.matrix_mode(mode))
        hook(GL11, 'glLoadIdentity', '()V', lambda: self.load_identity())
        hook(GL11, 'glNewList', '(II)V', new_list)
        hook(GL11, 'glEndList', '()V', end_list)
        hook(GL11, 'glCallList', '(I)V', lambda ident: self.call_list(ident))
        hook(GL11, 'glEnable', '(I)V', lambda cap: self.enable(cap, True))
        hook(GL11, 'glDisable', '(I)V', lambda cap: self.enable(cap, False))
        hook(GL11, 'glColor3f', '(FFF)V', colour)
        hook(GL11, 'glColor4f', '(FFFF)V', colour)
        hook(GL11, 'glBlendFunc', '(II)V', lambda s, d: self.set_blend_func(s, d))
        hook(GL11, 'glDepthFunc', '(I)V', lambda f: self.set_depth_func(f))
        hook(GL11, 'glDepthMask', '(Z)V', depth_mask)
        hook(GL11, 'glBindTexture', '(II)V', bind)
        answer(names['glalloc'], names['generateDisplayLists'], '(I)I', gen_lists)

        t = names['tessellator']
        hook(t, names['startQuads'], '()V', lambda: None)
        hook(t, names['normal'], '(FFF)V', normal)
        hook(t, names['vertexUV'], '(DDDDD)V', lambda x, y, z, u, v: self.vertex(x, y, z, u, v))
        hook(t, names['draw'], '()V', lambda: self.draw())

        # RenderEngine: a texture's id stands for its path, and binding one
        # makes it current. A downloadable skin is never there, so the
        # fallback path is always the one used, as it is for any mob.
        e = names['textureManager']
        answer(e, names['getTexture'], '(Ljava/lang/String;)I', lambda path: self.texture_id(path))
        answer(e, names['getDownloadable'], '(Ljava/lang/String;Ljava/lang/String;)I',
               lambda _url, path: -1 if path is None else self.texture_id(path))
        hook(e, names['bindTexture'], '(I)V', lambda ident: self.bind(ident))


def bounds(draws):
    """([x0, y0, z0], [x1, y1, z1]) around every corner of `draws`."""
    lo, hi = [1e30] * 3, [-1e30] * 3
    for d in draws:
        for corner in d.corners:
            for k in range(3):
                if corner[k] < lo[k]:
                    lo[k] = corner[k]
                if corner[k] > hi[k]:
                    hi[k] = corner[k]
    return lo, hi


class Frame(object):
    """A colour and depth buffer that recorded draws are rasterised into.

    `textures` turns a texture path into an Image.
    """

    def __init__(self, width, height, textures):
        self.width, self.height = width, height
        self.colour = bytearray(width * height * 4)
        self.depth = [-1e30] * (width * height)
        self.textures = textures
        self._loaded = {}

    def texture(self, path):
        if path not in self._loaded:
            self._loaded[path] = Texture(self.textures(path))
        return self._loaded[path]

    def draw(self, draws, root, lights):
        """Rasterise draws in order, placed by `root` and lit by `lights`.

        `root` maps the recorded space to pixels, with depth in z, nearer
        larger; it may turn as well as scale. `lights` are the lamp
        directions in that final space.
        """
        # Framing scales evenly, and turns only an icon: its rotation is all it
        # does to a normal.
        rn = normal_matrix(root)
        k = math.sqrt(rn[0] * rn[0] + rn[3] * rn[3] + rn[6] * rn[6]) or 1.0
        rn = tuple(c / k for c in rn)
        for d in draws:
            r, g, b, a = d.rgba
            if d.lit:
                x, y, z = d.normal
                n = (rn[0] * x + rn[1] * y + rn[2] * z, rn[3] * x + rn[4] * y + rn[5] * z,
                     rn[6] * x + rn[7] * y + rn[8] * z)
                total = AMBIENT
                for lx, ly, lz in lights:
                    total += DIFFUSE * max(0.0, n[0] * lx + n[1] * ly + n[2] * lz)
                r, g, b = min(1.0, r * total), min(1.0, g * total), min(1.0, b * total)
            c = [apply(root, x, y, z) + (u, v) for x, y, z, u, v in d.corners]
            self.triangle(d, c[0], c[1], c[2], (r, g, b, a))
            self.triangle(d, c[0], c[2], c[3], (r, g, b, a))

    def triangle(self, d, p, q, r, tint):
        """Fill one triangle of (x, y, depth, u, v) vertices.

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
        sample = self.texture(d.texture).sample if d.textured else None
        tr, tg, tb, ta = tint
        additive = d.blend and d.blend_func == (ONE, ONE)
        blend, alpha_test = d.blend, d.alpha_test
        equal = d.depth_func == EQUAL
        test, write = d.depth_test, d.depth_mask
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
                if test:
                    held = depth[slot]
                    if (abs(z - held) > 1e-6) if equal else (z < held - 1e-9):
                        continue                          # nearer is larger
                if sample:
                    sr, sg, sb, sa = sample(au * w0 + bu * w1 + cu * w2,
                                            av * w0 + bv * w1 + cv * w2)
                else:
                    sr = sg = sb = sa = 255
                fa = sa / 255.0 * ta
                if alpha_test and fa <= 0.1:
                    continue
                at = slot * 4
                fr, fg, fb = sr * tr, sg * tg, sb * tb
                if additive:
                    if colour[at + 3]:
                        fr += colour[at]
                        fg += colour[at + 1]
                        fb += colour[at + 2]
                        out_a = colour[at + 3]
                    else:
                        out_a = max(fr, fg, fb)
                elif blend:
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
                if write:
                    depth[slot] = z
