#!/usr/bin/env python3
"""What the game draws for an entity: a portrait, and a head icon for a mob.

    python tools/extract/models.py --preview DIR [--only Creeper Wolf]

sprites.py calls into this module for the wiki's pictures. Run on its own,
it writes every picture into DIR, with a contact sheet of each kind, for
looking at.

A mob has no picture in the jar. It has a skin, mob/creeper.png, and code
that folds the skin around boxes when the game draws it. So rather than
restate any of that, this module runs the code, in interp.py, on top of the
live block and item registries appearance.py builds:

    EntityRenderDispatcher.<init>   which renderer, and which models, each
                                    entity class gets
    the entity's own constructor    a real entity: its skin, its size, its
                                    DataWatcher, everything its renderer asks
    the renderer's render method    the whole draw -- rotateCorpse,
                                    preRenderCallback, the model, the extra
                                    passes, the held item -- exactly as the
                                    game calls it

Every GL11 call lands in softgl.py, which records the faces drawn; the
rasterising happens afterwards. The boxes, their pose, their order, the
textures bound, the light and the blending are all the game's.

The camera is the inventory's. GuiInventory.drawGuiContainerBackgroundLayer
draws the player: it scales and flips the GUI, turns 135 degrees about Y,
switches the lamps on, turns back, tilts about X by the pointer's height,
sets the player's body yaw, head yaw, head pitch and brightness from the
pointer, lifts by the player's yOffset and renders. models.py does the same
for every entity, with the body and head both turned YAW and the scene
tilted PITCH: the view the inventory gives when the pointer is below the
player and to one side, seen from above and from the mob's left.

Where the game itself gives an entity no world to stand in, a Stub does:
asked anything, it answers nothing. Five more things are answered here
rather than run, each for a reason given where it is done: the DataWatcher's
map, java.util.Random without a seed, Math.random, MathHelper's sine table
and the map renderer inside the held-item renderer.

The head is found by asking the game too. The entity is drawn twice with
nothing changed but its head yaw, and the faces that moved are the head.
That gives a chicken's head its bill and wattle, a cow's its horns, a sheep's
its fleece cap and a skeleton's its hat layer without a list. A ghast, a
slime and a squid turn their whole body, so for them the head is the body:
the first part drawn, and whatever is drawn in the same place.
"""
import argparse
import collections
import io
import json
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
from appearance import Appearance
from disasm import disassemble, u2
from gamedata import Jar, extract_entities
from interp import Interp, JavaRandom, Obj, Stub
from mappings import load as load_mappings
from paths import Missing, find_cache, find_jar
from softgl import (GL, Frame, bounds, identity, mul, normal_matrix, rotation, scaling,
                    translation, turn)

# The inventory's pointer, read as angles: GuiInventory turns the body by
# atan(dx / 40) * 20 and tilts the scene by atan(dy / 40) * 20, so each stays
# within 31 degrees. Positive PITCH is the pointer below the player, which
# puts the camera above it.
YAW = 30.0
PITCH = 12.0

PORTRAIT = 256          # pixels square
SUPERSAMPLE = 3
ICON = 32               # an inventory slot at GUI scale 2, as isometric.SIZE
MARGIN = 0.06

# Variants: an entity in a state the game puts it in, written the way the
# game writes it. Most state is in the DataWatcher, so most variants are
# values for its slots, each set by the method cited; the renderer then
# reads them back exactly as it would in a world. The first entry flagged
# `main` is the entity's own picture. A picture is drawn at the scale every
# picture of the same entity shares, so a size 1 slime is a quarter the
# height of a size 4.
SHEEP_COLOURS = 16


def _sheep(wool):
    """EntitySheep.setFleeceColor writes slot 16's low four bits, and
    setSheared its bit 16. A sheep drops wool of its fleece colour's damage
    value (EntitySheep.interact, dropFewItems), so the wool names name the
    colours."""
    out = [{'label': wool[0], 'main': True}]
    out += [{'label': wool[i], 'watch': {16: i}} for i in range(1, SHEEP_COLOURS)]
    out.append({'label': 'Sheared', 'watch': {16: 16}})
    return out


VARIANTS = {
    # EntityWolf: slot 16 is 1 sitting, 2 angry, 4 tamed; slot 18 its health,
    # which taming sets to 20 (EntityWolf.interact) and updateAITick copies
    # across. Taming sits a wolf down; the standing tame wolf is one told to
    # stand.
    'Wolf': [{'label': 'Wild', 'main': True},
             {'label': 'Tame', 'watch': {16: 4, 18: 20}},
             {'label': 'Tame, sitting', 'watch': {16: 5, 18: 20}},
             {'label': 'Angry', 'watch': {16: 2}}],
    # EntityCreeper.onStruckByLightning sets slot 17 to 1.
    'Creeper': [{'label': 'Normal', 'main': True},
                {'label': 'Charged', 'watch': {17: 1}}],
    # EntityPig.setSaddled: slot 16.
    'Pig': [{'label': 'Normal', 'main': True},
            {'label': 'Saddled', 'watch': {16: 1}}],
    # EntitySlime.setSlimeSize: slot 16. EntitySlime's constructor picks
    # 1 << nextInt(3), so these are the three sizes that spawn.
    'Slime': [{'label': 'Size 1', 'watch': {16: 1}},
              {'label': 'Size 2', 'watch': {16: 2}},
              {'label': 'Size 4', 'watch': {16: 4}, 'main': True}],
    # EntityGhast.updateEntityActionState counts attackCounter up to 20 while
    # it has a target, sets slot 16 while the count is past 10, and fires at
    # 20; onUpdate swaps the texture on slot 16. 19 is the tick before it
    # fires, when RenderGhast swells it most.
    'Ghast': [{'label': 'Idle', 'main': True},
              {'label': 'Shooting', 'watch': {16: 1}, 'attack': 19,
               'texture': '/mob/ghast_fire.png'}],
}

# Minecarts: EntityMinecart's own constructor takes the type, and
# EntityMinecart.attackEntityFrom drops each type's item, which names it.
MINECARTS = [(0, 'Minecart'), (1, 'Minecart with Chest'), (2, 'Minecart with Furnace')]


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def f32(v):
    return struct.unpack('<f', struct.pack('<f', v))[0]


def _code(cf, m):
    return list(disassemble(cf.code_of(m)))


class Game(object):
    """The game's entity renderers, and entities for them to draw.

    `textures` overrides what a texture path loads, for the sheets sprites.py
    has patched; anything else is read from the jar.
    """

    def __init__(self, jar_path, mp, textures=None):
        self.jar = Jar(jar_path)
        self.zip = zipfile.ZipFile(jar_path)
        self.mp = mp
        self.overrides = textures or {}
        self._images = {}
        find = mp.find_class
        self.c_dispatcher = find('net/minecraft/client/render/entity/EntityRenderDispatcher')
        self.c_renderer = find('net/minecraft/client/render/entity/EntityRenderer')
        self.c_living_renderer = find('net/minecraft/client/render/entity/LivingEntityRenderer')
        self.c_entity = find('net/minecraft/entity/Entity')
        self.c_living = find('net/minecraft/entity/LivingEntity')
        self.c_player = find('net/minecraft/entity/player/PlayerEntity')
        self.c_world = find('net/minecraft/world/World')
        self.c_minecraft = 'net/minecraft/client/Minecraft'
        self.c_textures = find('net/minecraft/client/texture/TextureManager')
        tess = find('net/minecraft/client/render/Tessellator')
        alloc = find('net/minecraft/client/util/GlAllocationUtils')
        self.gl_names = {
            'tessellator': tess,
            'startQuads': self._method(tess, 'startQuads', '()V'),
            'normal': self._method(tess, 'normal', '(FFF)V'),
            'vertexUV': self._method(tess, 'vertex', '(DDDDD)V'),
            'draw': self._method(tess, 'draw', '()V'),
            'glalloc': alloc,
            'generateDisplayLists': self._method(alloc, 'generateDisplayLists', '(I)I'),
            'textureManager': self.c_textures,
            'getTexture': self._method(self.c_textures, 'getTextureId', '(Ljava/lang/String;)I'),
            'getDownloadable': self._method(self.c_textures, 'method_1093',
                                            '(Ljava/lang/String;Ljava/lang/String;)I'),
            'bindTexture': self._method(self.c_textures, 'bindTexture', '(I)V'),
        }
        self.m_render = self._method(self.c_renderer, 'render', '(L%s;DDDFF)V' % self.c_entity)
        self.f_model = self._field(self.c_living_renderer, 'model')

        # Block's and Item's initialisers, already run: a skeleton's bow is
        # Item.bow, and the held-item renderer asks it for its icon.
        self.appearance = Appearance(self.jar, mp)
        self.interp = it = self.appearance.interp
        self.lists = {'next': 1}
        self.world = Stub(self.c_world)
        self._hooks()
        self.gl = GL(self.lists)
        self.gl.install(it, self.gl_names)
        self._inventory_screen()
        self.renderers = self._run_dispatcher()
        self.f_player = self._typed_field(self.c_dispatcher, self.c_living)
        self.f_world = self._typed_field(self.c_dispatcher, self.c_world)
        self._initialised = set()

    # -- names ---------------------------------------------------------------
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

    def _typed_field(self, cls, of):
        found = [f['name'] for f in self.jar.cls(cls).fields if f['desc'] == 'L%s;' % of]
        if len(found) != 1:
            raise jvm.Unsupported('%d fields of type %s on %s' % (len(found), of, cls))
        return (cls, found[0])

    def _ancestry(self, cls):
        while cls and not cls.startswith('java/'):
            yield cls
            cf = self.jar.cls(cls)
            cls = cf.super if cf else None

    # -- what is answered rather than run -------------------------------------
    def _hooks(self):
        it, find = self.interp, self.mp.find_class

        # Vec3D.createVector hands out vectors from a pool kept in a static
        # list; a fresh vector from createVectorHelper is the same value.
        vec = find('net/minecraft/util/math/Vec3d')
        pooled = '(DDD)L%s;' % vec
        cached = self._method(vec, 'createCached', pooled)
        fresh = self._method(vec, 'create', pooled)
        it.hooks[(vec, cached, pooled)] = lambda i, _r, args: i.call(
            vec, fresh, pooled, None, args, static=True)

        # MathHelper.sin and cos read a 65536-entry table its <clinit> fills.
        # Building it here is the same table without interpreting the loop.
        helper = find('net/minecraft/util/math/MathHelper')
        table = [f32(math.sin(i * math.pi * 2.0 / 65536.0)) for i in range(65536)]
        step = f32(10430.378)
        it.hooks[(helper, self._method(helper, 'sin', '(F)F'), '(F)F')] = \
            lambda _i, _r, a: table[jvm.trunc(f32(a[0] * step)) & 65535]
        it.hooks[(helper, self._method(helper, 'cos', '(F)F'), '(F)F')] = \
            lambda _i, _r, a: table[jvm.trunc(f32(f32(a[0] * step) + 16384.0)) & 65535]

        # An entity rolls its own Random and Math.random for things nothing
        # drawn depends on: a chicken's next egg, an idle mob's first yaw.
        # They are pinned so every run builds the same entity.
        def unseeded(_i, recv, _args):
            recv.fields[('java/util/Random', 'state')] = JavaRandom(0)
            return Interp.NOTHING
        it.hooks[('java/util/Random', '<init>', '()V')] = unseeded
        it.hooks[('java/lang/Math', 'random', '()D')] = lambda *_: 0.0

        # The DataWatcher keeps its slots in a HashMap of boxed values, read
        # back through getClass(); interp.py has neither. Its five accessors
        # are answered from a dict instead, which is all they amount to.
        self.c_watcher, self.f_watcher = self._datawatcher()
        key = (self.c_watcher, '<slots>')

        def put(_i, recv, args):
            recv.fields.setdefault(key, {})[args[0]] = jvm.unbox(args[1])
            return Interp.NOTHING

        def get(_i, recv, args):
            slots = recv.fields.get(key, {})
            if args[0] not in slots:
                raise jvm.Unsupported('DataWatcher slot %d was never added' % args[0])
            return slots[args[0]]
        for m in self.jar.cls(self.c_watcher).methods:
            if m['desc'] == '(ILjava/lang/Object;)V':
                it.hooks[(self.c_watcher, m['name'], m['desc'])] = put
            elif m['desc'] in ('(I)B', '(I)I', '(I)Ljava/lang/String;'):
                it.hooks[(self.c_watcher, m['name'], m['desc'])] = get

        # Minecraft.theMinecraft is null: no debug overlay, no name tags.
        it.statics[(self.c_minecraft, self._field(self.c_minecraft, 'INSTANCE')[1])] = None

        # EntityPlayer's constructor builds the inventory's crafting grid,
        # which looks up the recipe for an empty grid and so builds the whole
        # crafting registry. Nothing about it shows, so that constructor --
        # the one taking the player's inventory and a flag -- does nothing.
        # It then stands the player on the world's spawn point, which in a
        # world of nothing is the origin.
        point = find('net/minecraft/util/math/Vec3i')

        def spawn_point(i, _recv, _args):
            at = Obj(point)
            i.call(point, '<init>', '(III)V', at, [0, 0, 0])
            return at
        it.hooks[(self.c_world, self._method(self.c_world, 'getSpawnPos', '()L%s;' % point),
                  '()L%s;' % point)] = spawn_point
        # A painting asks the world how bright its wall is. World's only
        # (int, int, int) -> float is getLightBrightness; the answer is full
        # light, the brightness GuiInventory gives the player.
        bright = [m['name'] for m in self.jar.cls(self.c_world).methods if m['desc'] == '(III)F']
        if len(bright) != 1:
            raise jvm.Unsupported('World has %d (III)F methods' % len(bright))
        it.hooks[(self.c_world, bright[0], '(III)F')] = lambda *_: 1.0
        player_ctor = self.jar.cls(self.c_player).method('<init>', '(L%s;)V' % self.c_world)
        inventory = self.mp.find_class('net/minecraft/entity/player/PlayerInventory')
        cf = self.jar.cls(self.c_player)
        for _pc, op, o in _code(cf, player_ctor):
            if op == 0xb7 and cf.ref(u2(o))[1:] == ('<init>', '(L%s;Z)V' % inventory):
                it.hooks[(cf.ref(u2(o))[0], '<init>', '(L%s;Z)V' % inventory)] = \
                    lambda *_: Interp.NOTHING

    def _datawatcher(self):
        """Entity's DataWatcher field: the one whose class has a byte getter
        and two (int, Object) setters, addObject and updateObject."""
        for f in self.jar.cls(self.c_entity).fields:
            if not f['desc'].startswith('L'):
                continue
            cf = self.jar.cls(f['desc'][1:-1])
            if cf is None:
                continue
            descs = [m['desc'] for m in cf.methods]
            if descs.count('(ILjava/lang/Object;)V') == 2 and '(I)B' in descs:
                return f['desc'][1:-1], (self.c_entity, f['name'])
        raise jvm.Unsupported('no DataWatcher field on Entity')

    def _inventory_screen(self):
        """What GuiInventory sets on the player before drawing it.

        The method that loads /gui/inventory.png writes four floats on the
        player before it renders: body yaw, head yaw, head pitch,
        brightness. It then reads the player's yOffset to lift it, and writes
        one float on the dispatcher, playerViewY.
        """
        for name in self.jar.classes():
            cf = self.jar.cls(name)
            if cf is None or not any(e and e[0] == 'utf8' and e[1] == '/gui/inventory.png'
                                     for e in cf.cp):
                continue
            for m in cf.methods:
                code = cf.code_of(m)
                if code is None:
                    continue
                ins = list(disassemble(code))
                if not any(op in (0x12, 0x13) and cf.const(o[0] if op == 0x12 else u2(o))
                           == '/gui/inventory.png' for _pc, op, o in ins):
                    continue
                puts, reads = [], []
                for _pc, op, o in ins:
                    if op in (0xb4, 0xb5):
                        owner, fname, desc = cf.ref(u2(o))
                        if desc != 'F':
                            continue
                        declared = self.interp._declares(owner, fname)
                        (puts if op == 0xb5 else reads).append((declared, fname, len(puts)))
                players = []
                for declared, fname, _n in puts:
                    if declared == self.c_dispatcher:
                        self.f_view_y = (declared, fname)
                    elif (declared, fname) not in players:
                        players.append((declared, fname))
                self.f_body_yaw, self.f_yaw, self.f_pitch, self.f_brightness = players[:4]
                if self.f_yaw != self._field(self.c_entity, 'yaw'):
                    raise jvm.Unsupported('GuiInventory: second float written is not yaw')
                after = [(d, f) for d, f, n in reads if n >= 4 and d in (self.c_entity, self.c_living)]
                self.f_y_offset = after[0]
                return
        raise jvm.Unsupported('no inventory screen found')

    # -- the renderers ---------------------------------------------------------
    def _run_dispatcher(self):
        """EntityRenderDispatcher's constructor: entity class -> renderer.

        Its last act is to hand every renderer the dispatcher, in a loop over
        the map's values; interp.py keeps no maps, so that loop is the one
        thing done here instead. The dispatcher then gets what the game gives
        it once the client is up: a texture manager, and a held-item
        renderer made by its own constructor.
        """
        it, found = self.interp, {}

        def put(_it, _recv, args):
            found[args[0]] = args[1]
            return None
        for owner in ('java/util/Map', 'java/util/HashMap'):
            it.hooks[(owner, 'put', '(Ljava/lang/Object;Ljava/lang/Object;)'
                                    'Ljava/lang/Object;')] = put
        self.dispatcher = Obj(self.c_dispatcher)
        try:
            it.call(self.c_dispatcher, '<init>', '()V', self.dispatcher, [])
        except jvm.Unsupported as err:
            if not found:
                raise
            self.dispatcher_stopped = err
        set_dispatcher = self._method(self.c_renderer, 'setDispatcher', '(L%s;)V' % self.c_dispatcher)
        for renderer in found.values():
            it.call(self.c_renderer, set_dispatcher, '(L%s;)V' % self.c_dispatcher,
                    renderer, [self.dispatcher], virtual=True)

        textures = Obj(self.c_textures)
        minecraft = Obj(self.c_minecraft)
        minecraft.fields[self._field(self.c_minecraft, 'textureManager')] = textures
        # The held-item renderer's constructor also builds the map renderer,
        # from the font, the options and the texture manager; nothing here
        # holds a map, so that one constructor does nothing.
        maps = '(L%s;L%s;L%s;)V' % (self.mp.find_class('net/minecraft/client/font/TextRenderer'),
                                    self.mp.find_class('net/minecraft/client/option/GameOptions'),
                                    self.c_textures)
        by_minecraft = '(Lnet/minecraft/client/Minecraft;)V'
        for f in self.jar.cls(self.c_dispatcher).fields:
            if f['desc'] == 'L%s;' % self.c_textures:
                self.dispatcher.fields[(self.c_dispatcher, f['name'])] = textures
            held = f['desc'][1:-1] if f['desc'].startswith('L') else None
            cf = self.jar.cls(held) if held else None
            if cf is None or cf.method('<init>', by_minecraft) is None:
                continue
            for _pc, op, o in _code(cf, cf.method('<init>', by_minecraft)):
                if op == 0xb7 and cf.ref(u2(o))[1:] == ('<init>', maps):
                    it.hooks[(cf.ref(u2(o))[0], '<init>', maps)] = lambda *_: Interp.NOTHING
            renderer = Obj(held)
            it.call(held, '<init>', by_minecraft, renderer, [minecraft])
            self.dispatcher.fields[(self.c_dispatcher, f['name'])] = renderer
        return found

    def renderer(self, cls):
        """getEntityClassRenderObject: the class's own renderer, or its nearest ancestor's."""
        for c in self._ancestry(cls):
            if c in self.renderers:
                return self.renderers[c]
        return None

    def living(self, cls):
        r = self.renderer(cls)
        return r is not None and self.f_model in r.fields

    # -- entities ---------------------------------------------------------------
    def spawn(self, cls, desc='(L%s;)V', args=()):
        """A new entity, made by its own constructor in a world of nothing."""
        it = self.interp
        for c in reversed(list(self._ancestry(cls))):
            if c in self._initialised:
                continue
            self._initialised.add(c)
            if self.jar.cls(c).method('<clinit>'):
                it.call(c, '<clinit>', '()V', None, [], static=True)
        entity = Obj(cls)
        it.call(cls, '<init>', desc % self.c_world, entity, [self.world] + list(args))
        return entity

    def watch(self, entity, slots):
        watcher = entity.fields[self.f_watcher]
        watcher.fields.setdefault((self.c_watcher, '<slots>'), {}).update(slots)

    def ghast_attack(self, entity, count):
        """Set both of RenderGhast's counters: the two ints its preRenderCallback reads."""
        renderer = self.renderer(entity.cls)
        cf = self.jar.cls(renderer.cls)
        for m in cf.methods:
            ins = _code(cf, m) if cf.code_of(m) else []
            if not any(op == 0xb8 and cf.ref(u2(o))[1] == 'glScalef' for _pc, op, o in ins):
                continue
            fields = []
            for _pc, op, o in ins:
                if op == 0xb4:
                    owner, name, desc = cf.ref(u2(o))
                    if desc == 'I' and (owner, name) not in fields:
                        fields.append((owner, name))
            for owner, name in fields:
                entity.fields[(self.interp._declares(owner, name), name)] = count
            return
        raise jvm.Unsupported('no ghast counters')

    def set_texture(self, entity, path):
        """The skin a class switches to by itself, checked to be one it names."""
        if not any(e and e[0] == 'utf8' and e[1] == path
                   for c in self._ancestry(entity.cls) for e in self.jar.cls(c).cp):
            raise jvm.Unsupported('%s never names %s' % (entity.cls, path))
        entity.fields[self._field(self.c_living, 'texture')] = path

    # -- drawing ------------------------------------------------------------------
    def image(self, path):
        path = path.lstrip('/')
        if path in self.overrides:
            return self.overrides[path]
        if path not in self._images:
            self._images[path] = png.decode(self.zip.read(path))
        return self._images[path]

    def record(self, entity, camera, yaw, pitch=PITCH, head_yaw=None, lamps='inventory'):
        """Draw `entity` as GuiInventory draws the player; return the GL record.

        `camera` is what GuiInventory does before it switches the lamps on,
        less the pixel scale, which framing supplies later. `lamps` is
        'inventory' to switch them on where GuiInventory does, 'later' to
        draw lit and leave the lamps to whoever rasterises, or None to draw
        unlit.
        """
        it = self.interp
        gl = GL(self.lists)
        gl.install(it, self.gl_names)
        gl.stack = [camera]
        if lamps == 'inventory':
            gl.multiply(rotation(135.0, 0.0, 1.0, 0.0))
            gl.enable_standard_lighting()
            gl.multiply(rotation(-135.0, 0.0, 1.0, 0.0))
        elif lamps == 'later':
            gl.lighting = True
        gl.multiply(rotation(pitch, 1.0, 0.0, 0.0))
        living = self.f_body_yaw[0] in self._ancestry(entity.cls)
        if living:
            entity.fields[self.f_body_yaw] = yaw
            entity.fields[self.f_yaw] = yaw if head_yaw is None else head_yaw
            entity.fields[self.f_pitch] = 0.0
        entity.fields[self.f_brightness] = 1.0
        gl.multiply(translation(0.0, entity.fields.get(self.f_y_offset, 0.0), 0.0))
        self.dispatcher.fields[self.f_view_y] = 180.0
        self.dispatcher.fields[self.f_player] = entity
        self.dispatcher.fields[self.f_world] = self.world
        renderer = self.renderer(entity.cls)
        # renderEntityWithPosYaw(entity, 0, 0, 0, yaw, 1): a living entity
        # turns by its own body yaw and is passed 0, anything else by this.
        it.call(self.c_renderer, self.m_render, '(L%s;DDDFF)V' % self.c_entity, renderer,
                [entity, 0.0, 0.0, 0.0, 0.0 if living else yaw, 1.0], virtual=True)
        return gl


# GuiInventory: glScalef(-30, 30, 30), glRotatef(180, 0, 0, 1). The 30 is the
# pixel scale, which framing replaces.
GUI = mul(scaling(-1.0, 1.0, 1.0), rotation(180.0, 0.0, 0.0, 1.0))


def frame_scale(draws, size):
    lo, hi = bounds(draws)
    usable = size * (1.0 - 2.0 * MARGIN)
    return usable / max(hi[0] - lo[0], hi[1] - lo[1], 1e-9)


def portrait_frame(game, gl, scale, size=PORTRAIT, ss=SUPERSAMPLE):
    """Rasterise a recorded portrait, centred at `scale` pixels per unit."""
    full = size * ss
    lo, hi = bounds(gl.draws)
    s = scale * ss
    root = mul(translation(full / 2.0 - s * (lo[0] + hi[0]) / 2.0,
                           full / 2.0 - s * (lo[1] + hi[1]) / 2.0, 0.0),
               scaling(s, s, s))
    frame = Frame(full, full, game.image)
    frame.draw(gl.draws, root, [turn(normal_matrix(root), l) for l in gl.lights])
    return downsample(frame, ss, size)


def head(game, entity):
    """The faces that turn with the head, recorded in the entity's own space."""
    runs = [game.record(entity, identity(), 0.0, pitch=0.0, head_yaw=h, lamps='later').draws
            for h in (0.0, 40.0)]
    still, turned = runs
    if len(still) != len(turned):
        raise jvm.Unsupported('turning the head changed what was drawn')
    moved = [a for a, b in zip(still, turned)
             if any(abs(p - q) > 1e-6 for ca, cb in zip(a.corners, b.corners)
                    for p, q in zip(ca, cb))]
    if moved:
        return moved
    first = still[0].source
    return [d for d in still if d.source and first and d.source[1] == first[1]]


def eye_matrix():
    """isometric._eye as a matrix: the turn RenderItem gives a block in a slot."""
    cols = [isometric._eye(1, 0, 0), isometric._eye(0, 1, 0), isometric._eye(0, 0, 1)]
    return [cols[0][0], cols[1][0], cols[2][0], 0.0,
            cols[0][1], cols[1][1], cols[2][1], 0.0,
            cols[0][2], cols[1][2], cols[2][2], 0.0,
            0.0, 0.0, 0.0, 1.0]


def icon(game, entity, size=ICON):
    """The head, drawn the way RenderItem draws a block into a slot.

    The same projection and the same two lamps as isometric.py, fitted the
    way a block is -- its longest side one block -- and not antialiased, so
    a mob's icon sits beside a block's as one of a set.
    """
    draws = head(game, entity)
    lo, hi = bounds(draws)
    span = max(hi[k] - lo[k] for k in range(3))
    fit = mul(scaling(1.0 / span, 1.0 / span, 1.0 / span),
              translation(-(lo[0] + hi[0]) / 2.0, -(lo[1] + hi[1]) / 2.0,
                          -(lo[2] + hi[2]) / 2.0))
    unit = 10.0 * size / 16.0
    root = mul(mul(translation(size / 2.0, size / 2.0, 0.0), scaling(unit, unit, unit)),
               mul(eye_matrix(), fit))
    frame = Frame(size, size, game.image)
    frame.draw(draws, root, isometric.LIGHTS)
    out = png.Image(size, size)
    out.px = frame.colour
    return out


def downsample(frame, ss, size):
    """Box-filter a supersampled frame, weighting each sample's colour by its alpha."""
    out = png.Image(size, size)
    full, n, src = size * ss, ss * ss, frame.colour
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


def prepare(game, entity, variant):
    if 'watch' in variant:
        game.watch(entity, variant['watch'])
    if 'attack' in variant:
        game.ghast_attack(entity, variant['attack'])
    if 'texture' in variant:
        game.set_texture(entity, variant['texture'])


def entity_pictures(game, name, cls, wool=None):
    """Every picture of one entity: [(label or None, main?, portrait, icon or None)].

    The variants share one scale, so they compare. The icon is drawn for the
    main picture of a mob only.
    """
    variants = VARIANTS.get(name)
    if name == 'Sheep':
        variants = _sheep(wool)
    variants = variants or [{'label': None, 'main': True}]
    recorded = []
    for variant in variants:
        entity = game.spawn(cls)
        prepare(game, entity, variant)
        recorded.append((variant, entity, game.record(entity, GUI, YAW)))
    scale = min(frame_scale(gl.draws, PORTRAIT) for _v, _e, gl in recorded)
    out = []
    for variant, entity, gl in recorded:
        main = bool(variant.get('main'))
        out.append((variant['label'], main, portrait_frame(game, gl, scale),
                    icon(game, entity) if main and game.living(cls) else None))
    return out


def placed_pictures(game, classes):
    """Items as they stand in the world: each minecart type, and the boat."""
    out = []
    recorded = []
    for kind, item in MINECARTS:
        cart = game.spawn(classes['Minecart'], '(L%s;DDDI)V', [0.0, 0.0, 0.0, kind])
        recorded.append((item, game.record(cart, GUI, YAW)))
    scale = min(frame_scale(gl.draws, PORTRAIT) for _i, gl in recorded)
    for item, gl in recorded:
        out.append(Picture(item, None, True, portrait_frame(game, gl, scale), None, None))
    boat = game.record(game.spawn(classes['Boat']), GUI, YAW)
    out.append(Picture('Boat', None, True,
                       portrait_frame(game, boat, frame_scale(boat.draws, PORTRAIT)), None, None))
    return out


def motifs(game, painting):
    """EnumArt, run: [(enum value, title, width, height)] in the game's order.

    The painting's one enum-typed field holds its motif. EnumArt's
    constructor stores title, width, height and the two texture offsets, in
    that order, after the name and ordinal every enum constant gets.
    """
    jar, it = game.jar, game.interp
    for f in jar.cls(painting).fields:
        cls = f['desc'][1:-1] if f['desc'].startswith('L') else None
        cf = jar.cls(cls) if cls else None
        if cf is not None and cf.super == 'java/lang/Enum':
            art_field, art = (painting, f['name']), cls
            break
    else:
        raise jvm.Unsupported('no motif field on the painting')
    cf = jar.cls(art)
    ctor = next(m for m in cf.methods if m['name'] == '<init>')
    stored = [cf.ref(u2(o))[1] for _pc, op, o in _code(cf, ctor) if op == 0xb5]
    if len(stored) != 5:
        raise jvm.Unsupported('EnumArt stores %d fields' % len(stored))
    it.call(art, '<clinit>', '()V', None, [], static=True)
    values = next(it.statics[(art, f['name'])] for f in cf.fields
                  if f['desc'] == '[L%s;' % art)
    return art_field, [(v,) + tuple(v.fields[(art, n)] for n in stored[:3]) for v in values]


PAINTING_PIXELS = 16    # per block: one per texel of art/kz.png


def painting_pictures(game, cls):
    """Every motif, as RenderPainting draws it, face-on and at one pixel per texel.

    A painting in the world is lit by the two lamps from whichever way its
    wall faces, so a picture of the motif itself is drawn unlit, in full
    light.
    """
    art_field, arts = motifs(game, cls)
    out = []
    for value, title, width, height in arts:
        painting = game.spawn(cls)
        painting.fields[art_field] = value
        gl = game.record(painting, GUI, 180.0, pitch=0.0, lamps=None)
        lo, hi = bounds(gl.draws)
        s = float(PAINTING_PIXELS)
        root = mul(translation(width / 2.0 - s * (lo[0] + hi[0]) / 2.0,
                               height / 2.0 - s * (lo[1] + hi[1]) / 2.0, 0.0),
                   scaling(s, s, s))
        frame = Frame(width, height, game.image)
        frame.draw(gl.draws, root, ())
        image = png.Image(width, height)
        image.px = frame.colour
        out.append(Picture('Painting', title, False, image, None,
                           (width // PAINTING_PIXELS, height // PAINTING_PIXELS)))
    return out


# What sprites.py writes. `subject` is the name data/ gives the thing drawn;
# `label` names a variant, None for a thing with only one picture; `main` is
# the picture its infobox shows; `icon` is a mob's head; `blocks` is a
# painting's size, which is drawn pixel for pixel.
Picture = collections.namedtuple('Picture', 'subject label main image icon blocks')


def pictures(game, wool, only=None, log=None):
    """Every picture of every entity, item in the world and painting."""
    _records, classes = extract_entities(game.jar, game.mp)
    classes['Player'] = game.c_player
    out = []
    for name, cls in sorted(classes.items()):
        if (only and name not in only) or not game.living(cls):
            continue
        for label, main, image, head_icon in entity_pictures(game, name, cls, wool):
            out.append(Picture(name, label, main, image, head_icon, None))
        if log:
            log(name)
    if not only or 'Minecart' in only or 'Boat' in only:
        out += placed_pictures(game, classes)
    if not only or 'Painting' in only:
        out += painting_pictures(game, classes['Painting'])
    return out


def contact_sheet(images, columns, scale=1):
    """Images side by side on a light checkerboard, for looking at."""
    w = max(i.w for i in images) * scale
    h = max(i.h for i in images) * scale
    rows = (len(images) + columns - 1) // columns
    sheet = png.Image(columns * w, rows * h)
    sheet.px = bytearray(bytes((0xF2, 0xF2, 0xF2, 0xFF)) * (sheet.w * sheet.h))
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


def wool_names(root):
    """Wool's sixteen colour names, from data/: 'White' .. 'Black'."""
    blocks = json.load(io.open(os.path.join(root, 'data', 'blocks.json'), encoding='utf-8'))
    wool = next(b for b in blocks if b['key'] == 'cloth')
    names = {0: wool['name']}
    names.update({int(k): v for k, v in (wool.get('variants') or {}).items()})
    return [re.sub(r'\s*Wool$', '', names[i]) or 'White' for i in range(SHEEP_COLOURS)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jar', help='client.jar; found automatically if omitted')
    ap.add_argument('--cache', help='directory holding intermediary.tiny and barn.tiny')
    ap.add_argument('--preview', required=True, help='directory to write the pictures to')
    ap.add_argument('--only', nargs='*', help='entity names, as data/entities.json spells them')
    a = ap.parse_args()
    try:
        cache = a.cache or find_cache().path
        jar_path = a.jar or find_jar().path
    except Missing as err:
        raise SystemExit('error: %s' % err)
    mp = load_mappings(os.path.join(cache, 'intermediary.tiny'), os.path.join(cache, 'barn.tiny'))
    game = Game(jar_path, mp)
    found = pictures(game, wool_names(os.getcwd()), a.only, log=print)
    portraits = [p.image for p in found if not p.blocks]
    paintings = [p.image for p in found if p.blocks]
    icons = [p.icon for p in found if p.icon]
    for p in found:
        tag = slug(p.subject + (' ' + p.label if p.label else ''))
        write(os.path.join(a.preview, 'painting' if p.blocks else 'portrait', tag + '.png'), p.image)
        if p.icon:
            write(os.path.join(a.preview, 'icon', slug(p.subject) + '.png'), p.icon)
    if portraits:
        write(os.path.join(a.preview, 'portraits.png'), contact_sheet(portraits, 6))
    if icons:
        write(os.path.join(a.preview, 'icons.png'), contact_sheet(icons, 9, scale=3))
    if paintings:
        write(os.path.join(a.preview, 'paintings.png'), contact_sheet(paintings, 7, scale=2))


if __name__ == '__main__':
    main()
