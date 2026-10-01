#!/usr/bin/env python3
"""PROTOTYPE: draw every mob the way the game's own model code draws it.

    python tools/extract/models.py --out DIR [--only Creeper Pig]

Writes DIR/portrait/<name>.png, a three-quarter view of the whole mob for an
infobox, DIR/icon/<name>.png, its head drawn as the inventory draws a block,
and a contact sheet of each. Nothing reads these yet: this is the proof of
concept behind docs/proposals/entity-images.md, and it is not wired into
sprites.py, data/ or the build.

A mob has no picture in the jar. It has a skin, mob/creeper.png, and code
that folds the skin around boxes. So rather than restate any of that, this
module runs the code:

    EntityRenderDispatcher.<init>     which renderer and which models each
                                      entity class gets
    the entity's constructor          which skin it wears (read, not run)
    EntityModel.animateModel, render  which parts are drawn, posed how, and
    ModelPart.render, Quad.render     every box, texture coordinate and
                                      normal, sent through the Tessellator

all executed by interp.py, with every GL11 call answered by softgl.py. The
boxes, their posing, the order they are drawn in and the light they are lit
by are the game's; only the rasterising is ours.

What is not run yet is the renderer around the model, because it asks the
entity questions -- how big is this slime, is this sheep sheared, how bright
is it here -- and there is no entity to ask. SPECIAL below holds the answers
for an idle mob in daylight, transcribed from each renderer with a citation.
Running LivingEntityRenderer.render against a real entity instead is the next
step; see the proposal.

The head is found the same way: the model is drawn twice with nothing
changed but the head-yaw argument, and the parts that moved are the head.
The game therefore decides that a chicken's head includes its bill and its
wattle, a cow's its horns, a sheep's its fleece cap. A ghast, a slime and a
squid turn their whole body, so for them the head is the body: the first
part drawn and whatever is drawn in the same place.
"""
import argparse
import io
import math
import os
import re
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import interp as jvm
import isometric
import png
from disasm import disassemble, u2
from gamedata import Jar, extract_entities
from interp import Interp, Obj, default_for
from mappings import load as load_mappings
from paths import Missing, find_cache, find_jar
from softgl import GL, Texture, apply, identity, mul, rotation, scaling, translation

# The camera, transcribed from GuiInventory.drawScreen, which draws the player
# in the inventory: glScalef(-30, 30, 30), glRotatef(180, 0, 0, 1), the lamps
# switched on with a 135 degree turn about Y in force, then a tilt about X and
# a body turn that follow the mouse. YAW and PITCH are that mouse held above
# and to one side, well inside the range the inventory itself reaches
# (atan * 20, so up to 31 degrees either way).
YAW = 30.0
PITCH = -12.0

# What each renderer adds around its model, for an idle mob in daylight.
SPECIAL = {
    # RenderGhast.func_4014_a: attackCounter 0 gives (8 + 1) / 2 on each axis.
    'Ghast': {'scale': (4.5, 4.5, 4.5)},
    # RenderGiantZombie.preRenderScale; 6.0 is RenderManager's argument.
    'Giant': {'scale': (6.0, 6.0, 6.0)},
    # RenderSlime.scaleSlime with no squish. renderSlimePassModel then draws
    # the outer cube, blended, with the same skin.
    'Slime': {'scale': (2.0, 2.0, 2.0), 'pass': 'own', 'blend': True},
    # RenderSheep.setWoolColorAndRender: an unsheared sheep, white fleece,
    # full brightness.
    'Sheep': {'pass': 'renderPass', 'passTexture': '/mob/sheep_fur.png'},
    # RenderSquid.func_21007_a replaces rotateCorpse; pitch and yaw 0.
    'Squid': {'corpse': 'squid'},
    # RenderWolf.func_25004_a: EntityWolf.setTailRotation for a wild wolf.
    'Wolf': {'ticks': 0.62831855},
}
# Left out on purpose. RenderSpider's eye pass has alpha (1 - brightness) / 2,
# nothing in daylight. RenderPig's saddle and RenderCreeper's charge are
# variants, not the plain mob. RenderBiped's held item -- the skeleton's bow,
# the pig zombie's gold sword -- needs ItemRenderer, which is not run yet.


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def f32(v):
    return struct.unpack('<f', struct.pack('<f', v))[0]


class Runner(Interp):
    """The interpreter, plus an entity that answers every question with nothing.

    A model's animateModel asks its entity things: is the wolf angry, is it
    sitting, is it shaking. The stub's zeros make an idle, wild, standing mob.
    """

    STUB = Obj('<idle entity>')

    def call(self, owner, name, desc, recv, args, static=False, virtual=False):
        if recv is self.STUB:
            return default_for(desc)
        return Interp.call(self, owner, name, desc, recv, args, static, virtual)

    def _getfield(self, obj, owner, name, desc):
        if obj is self.STUB:
            return default_for('()' + desc)
        return Interp._getfield(self, obj, owner, name, desc)


class Models(object):
    """The game's entity renderers, live enough to draw with."""

    def __init__(self, jar_path, mp):
        self.jar = Jar(jar_path)
        self.zip = zipfile.ZipFile(jar_path)
        self.mp = mp
        find = mp.find_class
        self.c_dispatcher = find('net/minecraft/client/render/entity/EntityRenderDispatcher')
        self.c_living_renderer = find('net/minecraft/client/render/entity/LivingEntityRenderer')
        self.c_model = find('net/minecraft/client/render/entity/model/EntityModel')
        self.c_living = find('net/minecraft/entity/LivingEntity')
        self.c_player = find('net/minecraft/entity/player/PlayerEntity')
        self.f_model = self._field(self.c_living_renderer, 'model')
        self.f_pass_model = self._field(self.c_living_renderer, 'field_910')
        self.m_render = self._method(self.c_model, 'render', '(FFFFFF)V')
        self.m_animate = self._method(self.c_model, 'animateModel', '(L%s;FFF)V' % self.c_living)

        tess = find('net/minecraft/client/render/Tessellator')
        alloc = find('net/minecraft/client/util/GlAllocationUtils')
        vec = find('net/minecraft/util/math/Vec3d')
        self.gl_names = {
            'tessellator': tess,
            'startQuads': self._method(tess, 'startQuads', '()V'),
            'normal': self._method(tess, 'normal', '(FFF)V'),
            'vertexUV': self._method(tess, 'vertex', '(DDDDD)V'),
            'draw': self._method(tess, 'draw', '()V'),
            'glalloc': alloc,
            'generateDisplayLists': self._method(alloc, 'generateDisplayLists', '(I)I'),
        }

        self.interp = it = Runner(self.jar.cls, budget=20000000)
        it.field_hook = lambda _ref, _name, _desc: Interp.NOTHING
        self.lists = {'next': 1}
        GL(1, 1, self.lists).install(it, self.gl_names)

        # Vec3D.createVector hands out vectors from a pool held in a static
        # list; a fresh vector from createVectorHelper is the same value.
        pooled = '(DDD)L%s;' % vec
        cached, fresh = self._method(vec, 'createCached', pooled), self._method(vec, 'create', pooled)
        it.hooks[(vec, cached, pooled)] = lambda i, _r, args: i.call(
            vec, fresh, pooled, None, args, static=True)

        # MathHelper.sin and cos read a 65536-entry table its <clinit> fills.
        # Building it here is the same table, without interpreting the loop.
        helper = find('net/minecraft/util/math/MathHelper')
        table = [f32(math.sin(i * math.pi * 2.0 / 65536.0)) for i in range(65536)]
        scale = f32(10430.378)
        it.hooks[(helper, self._method(helper, 'sin', '(F)F'), '(F)F')] = \
            lambda _i, _r, a: table[jvm.trunc(f32(a[0] * scale)) & 65535]
        it.hooks[(helper, self._method(helper, 'cos', '(F)F'), '(F)F')] = \
            lambda _i, _r, a: table[jvm.trunc(f32(f32(a[0] * scale) + 16384.0)) & 65535]

        self.renderers = self._run_dispatcher()

    def _field(self, cls, named):
        for f in self.jar.cls(cls).fields:
            if self.mp.member(cls, f['name'], f['desc']) == named:
                return (cls, f['name'])
        raise jvm.Unsupported('no field %s on %s' % (named, cls))

    def _method(self, cls, named, desc):
        for m in self.jar.cls(cls).methods:
            if m['desc'] == desc and self.mp.member(cls, m['name'], desc) == named:
                return m['name']
        raise jvm.Unsupported('no method %s%s on %s' % (named, desc, cls))

    def _run_dispatcher(self):
        """EntityRenderDispatcher's constructor: entity class -> renderer.

        It stops at the snowball, whose renderer wants an item icon out of
        Item's registry; every living entity is registered before that, and
        `stopped` records where.
        """
        found = {}

        def put(_it, _recv, args):
            found[args[0]] = args[1]
            return None
        for owner in ('java/util/Map', 'java/util/HashMap'):
            self.interp.hooks[(owner, 'put', '(Ljava/lang/Object;Ljava/lang/Object;)'
                                             'Ljava/lang/Object;')] = put
        self.stopped = None
        try:
            self.interp.call(self.c_dispatcher, '<init>', '()V', Obj(self.c_dispatcher), [])
        except jvm.Unsupported as err:
            self.stopped = err
        return found

    def _ancestry(self, cls):
        while cls and not cls.startswith('java/'):
            yield cls
            cf = self.jar.cls(cls)
            cls = cf.super if cf else None

    def renderer(self, cls):
        """getEntityClassRenderObject: the class's own renderer, or its nearest ancestor's."""
        for c in self._ancestry(cls):
            if c in self.renderers:
                return self.renderers[c]
        return None

    def living(self, cls):
        r = self.renderer(cls)
        return r is not None and self.f_model in r.fields

    def skin(self, cls):
        """The texture an entity's constructor assigns, most derived class first."""
        for c in self._ancestry(cls):
            cf = self.jar.cls(c)
            for m in cf.methods:
                if m['name'] != '<init>':
                    continue
                last = None
                for _pc, op, operand in disassemble(cf.code_of(m)):
                    if op in (0x12, 0x13):
                        value = cf.const(operand[0] if op == 0x12 else u2(operand))
                        if isinstance(value, str) and value.startswith('/mob/'):
                            last = value
                if last:
                    return last
        return None

    def image(self, path):
        return png.decode(self.zip.read(path.lstrip('/')))

    def passes(self, name, cls):
        """(model, skin, blended) for each model the renderer draws, in order."""
        renderer = self.renderer(cls)
        spec = SPECIAL.get(name, {})
        skin = self.skin(cls)
        out = [(renderer.fields[self.f_model], skin, False)]
        if spec.get('pass') == 'renderPass':
            out.append((renderer.fields[self.f_pass_model], spec['passTexture'], False))
        elif spec.get('pass') == 'own':
            own = [v for (owner, _f), v in sorted(renderer.fields.items())
                   if owner == renderer.cls and isinstance(v, Obj)]
            out.append((own[0], skin, spec.get('blend', False)))
        return out

    def draw(self, gl, name, cls, head_yaw=0.0):
        """Every pass, as LivingEntityRenderer.render calls the model."""
        gl.install(self.interp, self.gl_names)
        ticks = SPECIAL.get(name, {}).get('ticks', 0.0)
        for model, skin, blend in self.passes(name, cls):
            gl.texture = skin                # recorded, and loaded when replayed
            gl.blend = blend
            self.interp.call(self.c_model, self.m_animate, '(L%s;FFF)V' % self.c_living,
                             model, [Runner.STUB, 0.0, 0.0, 1.0], virtual=True)
            self.interp.call(self.c_model, self.m_render, '(FFFFFF)V', model,
                             [0.0, 0.0, ticks, head_yaw, 0.0, 0.0625], virtual=True)


def entity_matrix(name, yaw):
    """LivingEntityRenderer.render, from rotateCorpse to the model's own scale."""
    spec = SPECIAL.get(name, {})
    m = identity()
    if spec.get('corpse') == 'squid':
        m = mul(m, translation(0.0, 0.5, 0.0))
        m = mul(m, rotation(180.0 - yaw, 0.0, 1.0, 0.0))
        m = mul(m, translation(0.0, -1.2, 0.0))
    else:
        m = mul(m, rotation(180.0 - yaw, 0.0, 1.0, 0.0))
    m = mul(m, scaling(-1.0, -1.0, 1.0))
    if 'scale' in spec:
        m = mul(m, scaling(*spec['scale']))
    return mul(m, translation(0.0, -24.0 * 0.0625 - 0.0078125, 0.0))


class Calls(GL):
    """A GL that draws nothing and records each display list called, and where.

    The model code runs once into one of these; framing and lighting are then
    worked out from the record, and the record is replayed into a real frame.
    """

    def __init__(self, lists):
        GL.__init__(self, 1, 1, lists)
        self.calls = []

    def call_list(self, ident):
        self.calls.append((ident, list(self.top), self.texture, self.blend))


def bounds(lists, calls):
    lo, hi = [1e30] * 3, [-1e30] * 3
    for ident, m, _skin, _blend in calls:
        for quad in lists[ident]:
            for x, y, z, _u, _v, _n in quad:
                p = apply(m, x, y, z)
                for k in range(3):
                    lo[k], hi[k] = min(lo[k], p[k]), max(hi[k], p[k])
    return lo, hi


def replay(models, calls, root, size, lights):
    """Draw recorded calls into a size x size frame, under `root`, lit by `lights`."""
    gl = GL(size, size, models.lists)
    gl.lighting, gl.lights = True, lights
    for ident, m, skin, blend in calls:
        gl.stack = [mul(root, m)]
        gl.texture = Texture(models.image(skin))
        gl.blend = blend
        gl.call_list(ident)
    return gl


def portrait(models, name, cls, size=256, ss=3, yaw=YAW, pitch=PITCH):
    """The whole mob, three-quarter view, fitted to the frame and antialiased."""
    rec = Calls(models.lists)
    gui = mul(scaling(-1.0, 1.0, 1.0), rotation(180.0, 0.0, 0.0, 1.0))
    rec.stack = [mul(gui, rotation(pitch, 1.0, 0.0, 0.0))]
    rec.multiply(entity_matrix(name, yaw))
    models.draw(rec, name, cls)
    lo, hi = bounds(models.lists, rec.calls)
    full = size * ss
    margin = 0.06 * full
    s = (full - 2 * margin) / max(hi[0] - lo[0], hi[1] - lo[1])
    root = mul(translation(full / 2.0 - s * (lo[0] + hi[0]) / 2.0,
                           full / 2.0 - s * (lo[1] + hi[1]) / 2.0, 0.0),
               scaling(s, s, s))
    # The lamps go on with GuiInventory's 135 degree turn in force, and the
    # turn is undone before the mob is drawn, so they sit where the inventory
    # puts them.
    lamps = GL(1, 1, models.lists)
    lamps.stack = [mul(mul(root, gui), rotation(135.0, 0.0, 1.0, 0.0))]
    lamps.enable_standard_lighting()
    return downsample(replay(models, rec.calls, root, full, lamps.lights), ss, size)


def head_calls(models, name, cls):
    """The display lists that turn when only the head-yaw argument changes."""
    runs = []
    for head_yaw in (0.0, 40.0):
        rec = Calls(models.lists)
        rec.stack = [entity_matrix(name, 0.0)]
        models.draw(rec, name, cls, head_yaw=head_yaw)
        runs.append(rec.calls)
    still, turned = runs
    moved = [a for a, b in zip(still, turned)
             if any(abs(x - y) > 1e-6 for x, y in zip(a[1], b[1]))]
    if moved:
        return moved
    first = still[0][1]
    return [c for c in still if c[1] == first]


def icon(models, name, cls, size=32):
    """The head, drawn the way RenderItem draws a block into a slot.

    The same projection and the same two lamps as isometric.py, and no
    antialiasing, so a mob's icon sits beside a block's without looking
    borrowed from somewhere else.
    """
    calls = head_calls(models, name, cls)
    lo, hi = bounds(models.lists, calls)
    span = max(hi[k] - lo[k] for k in range(3))
    fit = mul(scaling(1.0 / span, 1.0 / span, 1.0 / span),
              translation(-(lo[0] + hi[0]) / 2.0, -(lo[1] + hi[1]) / 2.0, -(lo[2] + hi[2]) / 2.0))
    columns = [isometric._eye(1, 0, 0), isometric._eye(0, 1, 0), isometric._eye(0, 0, 1)]
    eye = [columns[0][0], columns[1][0], columns[2][0], 0.0,
           columns[0][1], columns[1][1], columns[2][1], 0.0,
           columns[0][2], columns[1][2], columns[2][2], 0.0,
           0.0, 0.0, 0.0, 1.0]
    unit = 10.0 * size / 16.0
    root = mul(mul(translation(size / 2.0, size / 2.0, 0.0), scaling(unit, unit, unit)),
               mul(eye, fit))
    gl = replay(models, calls, root, size, isometric.LIGHTS)
    out = png.Image(size, size)
    out.px = gl.colour
    return out


def downsample(gl, ss, size):
    """Box-filter a supersampled frame, weighting each sample's colour by its alpha."""
    out = png.Image(size, size)
    full, n, src = size * ss, ss * ss, gl.colour
    for y in range(size):
        for x in range(size):
            r = g = b = a = 0
            for dy in range(ss):
                row = ((y * ss + dy) * full + x * ss) * 4
                for dx in range(ss):
                    at = row + dx * 4
                    alpha = src[at + 3]
                    r += src[at] * alpha
                    g += src[at + 1] * alpha
                    b += src[at + 2] * alpha
                    a += alpha
            if a:
                o = (y * size + x) * 4
                out.px[o:o + 4] = bytes((r // a, g // a, b // a, a // n))
    return out


def contact_sheet(images, columns, scale=1):
    """Images side by side on a light checkerboard, for looking at."""
    w = max(i.w for i in images) * scale
    h = max(i.h for i in images) * scale
    rows = (len(images) + columns - 1) // columns
    sheet = png.Image(columns * w, rows * h)
    for k, im in enumerate(images):
        ox, oy = (k % columns) * w, (k // columns) * h
        for y in range(h):
            for x in range(w):
                light = 0xF2 if ((x // 8 + y // 8) % 2) else 0xE4
                r = g = b = light
                sx, sy = x // scale, y // scale
                if sx < im.w and sy < im.h:
                    p = (sy * im.w + sx) * 4
                    a = im.px[p + 3] / 255.0
                    r = int(im.px[p] * a + r * (1 - a))
                    g = int(im.px[p + 1] * a + g * (1 - a))
                    b = int(im.px[p + 2] * a + b * (1 - a))
                o = ((oy + y) * sheet.w + ox + x) * 4
                sheet.px[o:o + 4] = bytes((r, g, b, 255))
    return sheet


def write(path, image):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as fh:
        fh.write(png.encode(image))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jar', help='client.jar; found automatically if omitted')
    ap.add_argument('--cache', help='directory holding intermediary.tiny and barn.tiny')
    ap.add_argument('--out', required=True, help='directory to write the pictures to')
    ap.add_argument('--size', type=int, default=256, help='portrait size in pixels')
    ap.add_argument('--ss', type=int, default=3, help='portrait supersampling factor')
    ap.add_argument('--icon', type=int, default=32, help='icon size in pixels')
    ap.add_argument('--only', nargs='*', help='entity names, as data/entities.json spells them')
    a = ap.parse_args()
    try:
        cache = a.cache or find_cache().path
        jar_path = a.jar or find_jar().path
    except Missing as err:
        raise SystemExit('error: %s' % err)
    mp = load_mappings(os.path.join(cache, 'intermediary.tiny'), os.path.join(cache, 'barn.tiny'))
    models = Models(jar_path, mp)
    _records, classes = extract_entities(models.jar, mp)
    # The player is not in EntityList, having no network id, but has a renderer.
    classes['Player'] = models.c_player

    portraits, icons = [], []
    for name, cls in sorted(classes.items()):
        if a.only and name not in a.only:
            continue
        if not models.living(cls):
            continue
        p = portrait(models, name, cls, a.size, a.ss)
        i = icon(models, name, cls, a.icon)
        write(os.path.join(a.out, 'portrait', slug(name) + '.png'), p)
        write(os.path.join(a.out, 'icon', slug(name) + '.png'), i)
        portraits.append(p)
        icons.append(i)
        print('%-10s %s' % (name, models.skin(cls)))
    if portraits:
        write(os.path.join(a.out, 'portraits.png'), contact_sheet(portraits, 6))
        write(os.path.join(a.out, 'icons.png'), contact_sheet(icons, 9, scale=3))


if __name__ == '__main__':
    main()
