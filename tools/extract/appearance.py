"""What the game draws for a block or item in the player's inventory.

The wiki used to show a block as a single raw terrain.png tile, picked by hand
whenever the constructor did not carry the answer. That is not what a player
sees. The inventory draws most blocks as a small three-quarter cube with a
different tile on each face, and it picks an item's tile from the stack's
damage value -- which is why every wool used to look white and every dye shared
one icon.

Rather than restate any of that, this module runs the game. Block's and Item's
static initialisers are executed by interp.py, which leaves behind a registry
of real block and item objects; each is then asked exactly what
RenderItem.drawItemIntoGui asks:

    Block.getRenderType()                        a cube, or a flat icon?
    Block.getBlockTextureFromSideAndMetadata()   the tile on each face
    Block.setBlockBoundsForItemRender()          how big the cube is
    Block.getRenderColor(metadata)               the cube's tint
    Item.getIconFromDamage(damage)               the tile for a flat icon
    Item.getColorFromDamage(damage)              its tint

Neither initialiser runs to completion: both end in statistics bookkeeping
this interpreter has no business modelling. Both get all the way through
registration first, so `stopped` records where each one gave up and the caller
checks that the ids it wanted are all present.

Method identification
---------------------
barn.tiny leaves Block's and Item's methods unnamed, so each is found by what
it is rather than what it is called, and every rule below is one the jar can
be checked against:

    getBlockTextureFromSideAndMetadata  Block's only (II)I
    getRenderColor / getColorFromDamage the (I)I that returns 0xFFFFFF
    getIconFromDamage                   the Item (I)I that returns iconIndex
    getRenderType                       the ()I whose overrides span 1..17
    setBlockBounds                      the only (FFFFFF)V
    setBlockBoundsForItemRender         the ()V that Block's <clinit> never calls
"""
import collections

from disasm import disassemble, u2
from interp import Arr, Interp, Obj, Ref, Unsupported, default_for

# RenderBlocks.renderItemIn3d: every other render type falls back to a flat
# tile drawn straight from the sheet.
RENDER_IN_3D = (0, 10, 11, 13, 16)

STAIRS, FENCE, CACTUS, PISTON = 10, 11, 13, 16

# The shapes renderBlockOnInventory assembles by hand, transcribed from it.
# Everything else is the one box the block reports for an item render.
STAIR_BOXES = ((0.0, 0.0, 0.0, 1.0, 1.0, 0.5),
               (0.0, 0.0, 0.5, 1.0, 0.5, 1.0))
FENCE_BOXES = ((0.375, 0.0, 0.0, 0.625, 1.0, 0.25),
               (0.375, 0.0, 0.75, 0.625, 1.0, 1.0),
               (0.4375, 0.8125, -0.125, 0.5625, 0.9375, 1.125),
               (0.4375, 0.3125, -0.125, 0.5625, 0.4375, 1.125))
# A cactus draws its four sides a sixteenth of a block inside the box.
CACTUS_INSET = 0.0625

WHITE = 0xFFFFFF

Box = collections.namedtuple('Box', 'bounds faces inset')


def _const_return(cf, m):
    """The constant a method returns, if its whole body is `push n; ireturn`."""
    code = cf.code_of(m)
    if code is None:
        return None
    ins = list(disassemble(code))
    if len(ins) != 2 or ins[1][1] != 0xac:
        return None
    _pc, op, operand = ins[0]
    if 0x02 <= op <= 0x08:
        return op - 0x03
    if op == 0x10:
        return int.from_bytes(operand[:1], 'big', signed=True)
    if op == 0x11:
        return int.from_bytes(operand[:2], 'big', signed=True)
    if op in (0x12, 0x13):
        return cf.const(operand[0] if op == 0x12 else u2(operand))
    return None


def _returned_field(cf, m):
    """The field a method returns, if its whole body is `this.x; ireturn`."""
    code = cf.code_of(m)
    if code is None:
        return None
    ins = list(disassemble(code))
    if len(ins) == 3 and ins[0][1] == 0x2a and ins[1][1] == 0xb4 and ins[2][1] == 0xac:
        return cf.ref(u2(ins[1][2]))[1]
    return None


def _putfields(cf, m):
    """Fields a method assigns, in the order it assigns them."""
    return [cf.ref(u2(o))[1] for _pc, op, o in disassemble(cf.code_of(m)) if op == 0xb5]


def _one(cands, what):
    if len(cands) != 1:
        raise Unsupported('expected one %s, found %r' % (what, cands))
    return cands[0]


class Appearance(object):
    """The game's block and item registries, live enough to be asked questions."""

    def __init__(self, jar, mp):
        self.jar = jar
        self.block_cls = mp.find_class('net/minecraft/block/Block')
        self.item_cls = (mp.find_class('net/minecraft/Item')
                         or mp.find_class('net/minecraft/item/Item'))
        bcf = jar.cls(self.block_cls)
        icf = jar.cls(self.item_cls)
        self._identify(jar, mp, bcf, icf)
        self._run(jar, bcf, icf)

    # -- what the methods are called ---------------------------------------
    def _identify(self, jar, mp, bcf, icf):
        block, item = self.block_cls, self.item_cls

        # Block(id, texture, material) is `this(id, material); this.tex = texture`,
        # so its lone assignment names the texture field.
        ctors = sorted((m['desc'] for m in bcf.methods if m['name'] == '<init>'))
        self.ctor_plain = _one([d for d in ctors if not d.startswith('(II')], 'Block(id, material)')
        self.ctor_tex = _one([d for d in ctors if d.startswith('(II')], 'Block(id, texture, material)')
        self.f_texture = (block, _one(_putfields(bcf, bcf.method('<init>', self.ctor_tex)),
                                      'texture assignment'))
        self.f_block_id = (block, _one([f['name'] for f in bcf.fields if f['desc'] == 'I'
                                        and mp.member(block, f['name'], 'I') == 'id'],
                                       'Block.id'))
        self.f_item_id = (item, _one([f['name'] for f in icf.fields if f['desc'] == 'I'
                                      and mp.member(item, f['name'], 'I') == 'id'],
                                     'Item.id'))
        self.f_blocks = _one([f['name'] for f in bcf.fields
                              if mp.member(block, f['name'], f['desc']) == 'BLOCKS'], 'Block.BLOCKS')
        self.f_items = _one([f['name'] for f in icf.fields
                             if mp.member(item, f['name'], f['desc']) == 'ITEMS'], 'Item.ITEMS')

        self.m_tex_meta = _one([m['name'] for m in bcf.methods if m['desc'] == '(II)I'],
                               'getBlockTextureFromSideAndMetadata')
        self.m_block_tint = _one([m['name'] for m in bcf.methods if m['desc'] == '(I)I'
                                  and _const_return(bcf, m) == WHITE], 'getRenderColor')
        self.m_set_bounds = _one([m['name'] for m in bcf.methods if m['desc'] == '(FFFFFF)V'],
                                 'setBlockBounds')
        self.bound_fields = [(block, f) for f in
                             _putfields(bcf, bcf.method(self.m_set_bounds, '(FFFFFF)V'))]
        if len(self.bound_fields) != 6:
            raise Unsupported('setBlockBounds assigns %d fields' % len(self.bound_fields))

        # setIconCoord(x, y) has iconIndex as its only assignment.
        self.f_icon = (item, _one(_putfields(icf, _one(
            [m for m in icf.methods if m['desc'] == '(II)L%s;' % item], 'setIconCoord')),
            'iconIndex assignment'))
        self.m_icon_damage = _one([m['name'] for m in icf.methods if m['desc'] == '(I)I'
                                   and _returned_field(icf, m) == self.f_icon[1]],
                                  'getIconFromDamage')
        self.m_item_tint = _one([m['name'] for m in icf.methods if m['desc'] == '(I)I'
                                 and _const_return(icf, m) == WHITE], 'getColorFromDamage')

        # getRenderType is the ()I whose overrides carry the widest set of
        # constants: RenderBlocks knows seventeen of them, and nothing else on
        # Block is answered so many different ways.
        subs = self._subclasses(jar, self.block_cls)
        ranked = []
        for m in bcf.methods:
            if m['desc'] != '()I':
                continue
            seen = set()
            for s in subs:
                cf = jar.cls(s)
                over = cf.method(m['name'], '()I')
                if over is not None:
                    seen.add(_const_return(cf, over))
            seen.discard(None)
            ranked.append((len(seen), m['name'], seen))
        ranked.sort(reverse=True)
        if not ranked or not set(range(1, 18)) <= ranked[0][2]:
            raise Unsupported('no ()I on Block answers with every render type')
        self.m_render_type = ranked[0][1]

        # Of Block's two empty ()V methods, initializeBlock is the one its own
        # <clinit> calls on each registered block; the other is the one
        # renderBlockOnInventory calls before measuring the cube.
        clinit = bcf.code_of(bcf.method('<clinit>'))
        called = {bcf.ref(u2(o))[1] for _pc, op, o in disassemble(clinit)
                  if op in (0xb6, 0xb7, 0xb8) and bcf.ref(u2(o))[::2] == (block, '()V')}
        self.m_item_bounds = _one([m['name'] for m in bcf.methods
                                   if m['desc'] == '()V' and m['name'] != '<clinit>'
                                   and m['name'] not in called],
                                  'setBlockBoundsForItemRender')

    @staticmethod
    def _subclasses(jar, root):
        out = []
        for name in jar.classes():
            seen = set()
            cf = jar.cls(name)
            cur = cf.super if cf else None
            while cur and cur not in seen:
                seen.add(cur)
                if cur == root:
                    out.append(name)
                    break
                parent = jar.cls(cur)
                cur = parent.super if parent else None
        return out

    # -- building the registries -------------------------------------------
    def _run(self, jar, bcf, icf):
        """Execute both static initialisers and keep what they registered.

        The constructors are intercepted rather than run. Block's real one
        checks the slot is free, asks the material questions and files the
        block in half a dozen lookup tables -- registration bookkeeping that
        would need a modelled Material to answer and that nothing here reads.
        What it leaves on the object is an id, a texture and a unit cube, and
        those are set directly.
        """
        interp = Interp(jar.cls, budget=50000000)
        self.interp = interp
        tried = set()

        def field_hook(ref, name, desc):
            """A static of a helper class, by running that class's initialiser.

            EnumToolMaterial and the sound tables are ordinary little classes
            whose <clinit> is safe to run; Block's and Item's are already
            running, so they are never reached this way.
            """
            if not isinstance(ref, Ref):
                return Interp.NOTHING
            if ref.owner not in tried:
                tried.add(ref.owner)
                try:
                    interp.call(ref.owner, '<clinit>', '()V', None, [], static=True)
                except Exception:
                    pass
            holder = interp.statics.get((ref.owner, ref.name))
            if isinstance(holder, Obj):
                return holder.fields.get((interp._declares(holder.cls, name), name),
                                         default_for('()' + desc))
            return Interp.NOTHING

        interp.field_hook = field_hook

        # Block's <clinit> files its custom ItemBlocks into Item.itemsList
        # before Item's <clinit> has made the array, so it is made here.
        block_items = Arr([None] * 32000)
        interp.statics[(self.item_cls, self.f_items)] = block_items

        def register(key, ident, obj, size):
            table = interp.statics.get(key)
            if not isinstance(table, list):
                table = Arr([None] * size)
                interp.statics[key] = table
            if isinstance(ident, int) and 0 <= ident < len(table):
                table[ident] = obj

        def new_block(_it, recv, args):
            recv.fields[self.f_block_id] = args[0]
            register((self.block_cls, self.f_blocks), args[0], recv, 256)
            interp.call(self.block_cls, self.m_set_bounds, '(FFFFFF)V', recv,
                        [0.0, 0.0, 0.0, 1.0, 1.0, 1.0])
            return Interp.NOTHING

        def new_textured_block(it, recv, args):
            new_block(it, recv, args)
            recv.fields[self.f_texture] = args[1]
            return Interp.NOTHING

        def new_item(_it, recv, args):
            recv.fields[self.f_item_id] = args[0] + 256
            register((self.item_cls, self.f_items), args[0] + 256, recv, 32000)
            return Interp.NOTHING

        interp.hooks[(self.block_cls, '<init>', self.ctor_plain)] = new_block
        interp.hooks[(self.block_cls, '<init>', self.ctor_tex)] = new_textured_block
        for m in icf.methods:
            if m['name'] == '<init>':
                interp.hooks[(self.item_cls, '<init>', m['desc'])] = new_item

        self.stopped = {}
        for owner, label in ((self.block_cls, 'Block'), (self.item_cls, 'Item')):
            try:
                interp.call(owner, '<clinit>', '()V', None, [], static=True)
                self.stopped[label] = None
            except Exception as err:
                self.stopped[label] = err
        self.blocks = interp.statics.get((self.block_cls, self.f_blocks)) or []
        # Item's initialiser installs a registry of its own, so the item forms
        # of the blocks -- filed by Block's initialiser, which ran first -- are
        # carried across into it.
        self.items = interp.statics.get((self.item_cls, self.f_items)) or []
        for ident, obj in enumerate(block_items):
            if obj is not None and self.items[ident] is None:
                self.items[ident] = obj

    def why_stopped(self):
        return '; '.join('%s.<clinit>: %s' % (k, v)
                         for k, v in sorted(self.stopped.items()) if v)

    # -- asking ------------------------------------------------------------
    def _obj(self, table, ident, what):
        obj = table[ident] if 0 <= ident < len(table) else None
        if obj is None:
            raise Unsupported('the game registered no %s %d (%s)'
                              % (what, ident, self.why_stopped() or 'no reason given'))
        return obj

    def _call(self, obj, method, desc, args):
        return self.interp.call(obj.cls, method, desc, obj, args, virtual=True)

    def render_type(self, block_id):
        return self._call(self._obj(self.blocks, block_id, 'block'), self.m_render_type, '()I', [])

    def _boxes(self, block, render_type, meta):
        faces = [self._call(block, self.m_tex_meta, '(II)I', [side, meta]) for side in range(6)]
        if render_type == STAIRS:
            return [Box(b, faces, 0.0) for b in STAIR_BOXES]
        if render_type == FENCE:
            return [Box(b, faces, 0.0) for b in FENCE_BOXES]
        self._call(block, self.m_item_bounds, '()V', [])
        bounds = tuple(block.fields.get(f, 0.0) for f in self.bound_fields)
        return [Box(bounds, faces, CACTUS_INSET if render_type == CACTUS else 0.0)]

    def icon(self, ident, damage=0):
        """How the inventory draws one stack.

        Either a cube of boxes carrying six terrain tiles each, or a flat tile
        from one of the two sheets. Both come with the colour the game
        multiplies them by, which is white for all but leaves.
        """
        if ident < 256:
            block = self._obj(self.blocks, ident, 'block')
            render_type = self._call(block, self.m_render_type, '()I', [])
            if render_type in RENDER_IN_3D:
                # A piston is always drawn retracted, whatever the stack says.
                meta = 1 if render_type == PISTON else damage
                return {'kind': 'cube', 'renderType': render_type,
                        'boxes': self._boxes(block, render_type, meta),
                        'tint': self._call(block, self.m_block_tint, '(I)I', [meta])}
        item = self._obj(self.items, ident, 'item')
        return {'kind': 'flat',
                'sheet': 'terrain' if ident < 256 else 'items',
                'tile': self._call(item, self.m_icon_damage, '(I)I', [damage]),
                'tint': self._call(item, self.m_item_tint, '(I)I', [damage])}
