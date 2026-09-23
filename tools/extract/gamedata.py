#!/usr/bin/env python3
"""Extract Minecraft Beta 1.7.3 game data from the shipped client.jar.

Everything here is derived from the real bytecode and the real en_US.lang, so
the wiki's IDs, sprites, hardness values and recipes are facts rather than
recollections. Run this once; the JSON it writes is committed to the repo and
the site build never needs the jar.

    python tools/extract/gamedata.py --out data

The jar and the Babric mappings are found automatically; see paths.py for how
to say where they are.

Setter identification
---------------------
barn.tiny does not name Block's builder methods, so they are identified by the
values they carry, each cross-checked against known Beta 1.7.3 behaviour:

    c(F)  hardness         stone 1.5, dirt 0.5, cobblestone 2.0
    b(F)  resistance       stone 10, bedrock 6000000  (blast resistance = f*3/5)
    a(F)  light emission   lava 1.0, glowstone 1.0
    g(I)  light opacity    water 3, lava 255, leaves 1
    a(String)  translation key -- every value is a key present in en_US.lang

setBlockUnbreakable is found rather than named: it is Block's only no-argument
builder that delegates to the hardness setter.

Where the builder calls are
---------------------------
Block's <clinit> is only half of the chain. A block may also call the same
builders from inside its own constructor, and six classes do: the three piston
blocks set their own hardness, a stair block copies whatever block it is cut
from, and stairs, slabs and farmland set their own light opacity. Reading the
<clinit> alone left six block ids with no hardness at all, so BlockCtor below
runs each constructor and records what it calls. See its docstring.

What an item does in a slot, a hit or a meal
--------------------------------------------
Stack size, durability, attack damage, healing and a mob's starting health
are not read here but asked of the game's own item objects, built by running
Item's initialiser (appearance.py). properties.py does the asking.
"""
import argparse
import hashlib
import io
import json
import os
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from appearance import Appearance
from classfile import ClassFile
from disasm import disassemble, trace_clinit, trace_calls, params_of, u2
from interp import ArrayRef, Interp, Obj, Ref, Unsupported, default_for
from mappings import load as load_mappings
from paths import Missing, find_cache, find_jar
from properties import Properties

# Block builder methods, by obfuscated name (see module docstring for evidence)
B_HARDNESS = 'c'
B_RESISTANCE = 'b'
B_LIGHT = 'a'
B_OPACITY = 'g'


def sha1(b):
    return hashlib.sha1(b).hexdigest()


class Jar:
    def __init__(self, path):
        self.z = zipfile.ZipFile(path)
        self._cache = {}

    def cls(self, obf):
        if obf not in self._cache:
            try:
                self._cache[obf] = ClassFile(self.z.read(obf + '.class'))
            except Exception:
                self._cache[obf] = None
        return self._cache[obf]

    def classes(self):
        return [n[:-6] for n in self.z.namelist()
                if n.endswith('.class') and '/' not in n]


def parse_lang(jar):
    """tile.stone.name=Stone  ->  {'tile.stone': 'Stone'}"""
    raw = jar.z.read('lang/en_US.lang').decode('utf-8', 'replace')
    names, descs = {}, {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or '=' not in line or line.startswith('#'):
            continue
        k, v = line.split('=', 1)
        if k.endswith('.name'):
            names[k[:-5]] = v
        elif k.endswith('.desc') and v:
            descs[k[:-5]] = v
    return names, descs


def const_calls(rec):
    """Index a record's builder calls as {(name, desc): [argsets]}."""
    out = {}
    for name, desc, args in rec['calls']:
        out.setdefault((name, desc), []).append(args)
    return out


def num(v, default=None):
    return v if isinstance(v, (int, float)) else default


def first_arg(argsets):
    return argsets[0][0] if argsets and argsets[0] else None


def light_level(v):
    """Block.setLightValue: lightValue[id] = (int)(15.0F * var1).

    A C-style cast truncates, so a redstone torch's 0.5 is light 7, not 8, and
    a brown mushroom's 0.125 is light 1, not 2. Rounding here would overstate
    half the light sources in the game. The multiply is done in float32 to
    match the JVM rather than Python's doubles.
    """
    if not v:
        return 0
    f32 = lambda x: struct.unpack('<f', struct.pack('<f', x))[0]
    return int(f32(15.0 * f32(v)))


def super_args(jar, cls_obf, parent_obf):
    """Constant arguments a subclass passes to its parent constructor."""
    cf = jar.cls(cls_obf)
    if cf is None:
        return None
    for c in trace_calls(cf, '<init>'):
        if c['name'] == '<init>' and c['owner'] == parent_obf and c['args']:
            if isinstance(c['args'][0], int):
                return c['args']
    return None


def load_name_overrides(out_dir):
    """Names for the few blocks/items en_US.lang never gives one, or gives twice.

    Subtypes are covered too. Wool and slabs name themselves, because the game
    picks a translation key per damage value and en_US.lang answers; tall grass
    does not, so the fern hiding at metadata 2 has no name to be found and one
    is supplied here.

    The other job is splitting. en_US.lang answers `tile.mushroom` and
    `item.clay` for two ids apiece, and a name is the wiki's identity for a
    thing, so without an override the brown and the red mushroom become one
    page with one sprite. See shared_names() below.

    Joining is the same move the other way. Item 331 is `item.redstone` and
    block 55 `tile.redstoneDust`, one thing under two names, so the override
    gives the item its block's name and the pair becomes one page.
    """
    path = os.path.join(out_dir, 'name-overrides.json')
    if not os.path.exists(path):
        return {}, {}, {}
    doc = json.load(io.open(path, encoding='utf-8'))
    return doc.get('byBlockId', {}), doc.get('byItemId', {}), doc.get('variantsByBlockId', {})


def shared_names(blocks, items, entities):
    """Display names claimed by more than one id, as {name: ['block 8', ...]}.

    Sharing is usually right: block 8 and 9 are the two halves of water, block
    63 and 68 the two ways a sign stands, and one page wants both. It is wrong
    when the ids are different things, because the loser vanishes -- it has no
    page of its own to be found on and no sprite of its own to be drawn with.
    Printing the list is the only way anyone notices which is which, so the
    extractor says it out loud every run and name-overrides.json settles it.
    """
    out = {}
    for kind, records in (('block', blocks), ('item', items), ('entity', entities)):
        for rec in records:
            if kind == 'block' and not rec.get('key'):
                continue                      # technical blocks are unnamed
            out.setdefault(rec['name'], []).append(
                '%s %d' % (kind, rec.get('id', rec.get('networkId'))))
    return {n: w for n, w in sorted(out.items()) if len(w) > 1}


class BlockCtor(object):
    """The builder calls a block makes from inside its own constructor.

    `new BlockStairs(53, planks)` carries no hardness of its own: the number
    comes from a `setHardness(var2.blockHardness)` inside the constructor,
    which the <clinit> replay never sees. Nor does it see the three pistons
    setting 0.5F, or stairs, slabs and farmland setting their light opacity.
    Those six blocks used to reach the wiki with no hardness and a blast
    resistance of zero, and every page showed a dash where a number belongs.

    Rather than pattern-match the constructors, run them, the way the recipe
    extractor runs the recipe registry. Three things make that cheap:

    - Block's own constructor is stubbed out. It is registration bookkeeping
      that wants a live Material, and nothing here reads what it leaves.
    - Every other Block builder is stubbed to return the receiver, so
      setStepSound and setTickOnLoad neither run nor need Block's static
      tables; the four that carry values are recorded instead of applied,
      leaving the caller to replay them in order against the <clinit> chain.
    - A field read of another block -- `var2.blockHardness` -- is answered
      from the blocks already extracted. Block's <clinit> always registers the
      model before the thing cut from it, so the answer is always in hand.

    Anything else a constructor does is allowed to run and allowed to fail:
    the calls recorded before a failure are still in order and still true, and
    what is lost is at worst what this class was written to recover. Nothing
    is invented -- a hardness read from a block that has not been extracted
    yet raises rather than defaulting to zero.
    """

    def __init__(self, jar, cf, obf):
        self.jar, self.obf = jar, obf
        self.f = '(F)L%s;' % obf
        self.i = '(I)L%s;' % obf
        self.v = '()L%s;' % obf
        self.record = {(B_HARDNESS, self.f), (B_RESISTANCE, self.f),
                       (B_LIGHT, self.f), (B_OPACITY, self.i)}
        # The hardness and resistance fields are the ones their setters write.
        self.f_hardness = putfields(cf, cf.method(B_HARDNESS, self.f))[0]
        self.f_resistance = set(putfields(cf, cf.method(B_RESISTANCE, self.f)))
        # setBlockUnbreakable: the no-argument builder that calls setHardness.
        self.unbreakable = {m['name'] for m in cf.methods if m['desc'] == self.v
                            and B_HARDNESS in invokes(cf, m)}
        self.ctors = [m['desc'] for m in cf.methods if m['name'] == '<init>']
        self.passthru = [(m['name'], m['desc']) for m in cf.methods
                         if m['desc'].endswith(')L%s;' % obf)
                         and (m['name'], m['desc']) not in self.record
                         and m['name'] not in self.unbreakable]
        self.tables = [f['name'] for f in cf.fields if f['desc'].startswith('[')]
        self.known = {}          # static field name -> (hardness, resistance)

    def learn(self, field, hardness, resistance):
        """Remember a finished block, so a stair cut from it can read it."""
        self.known[field] = (hardness if hardness is not None else 0.0, resistance)

    def calls(self, rec):
        """[(name, desc, args)] in execution order, or [] if there are none."""
        out = []
        interp = Interp(self.jar.cls)

        def recorder(nm, desc):
            def hook(_it, recv, args):
                out.append((nm, desc, list(args)))
                return recv
            return hook

        for nm, desc in self.record:
            hook = recorder(nm, desc)
            interp.hooks[(self.obf, nm, desc)] = hook
            interp.hooks[(rec['ctor'], nm, desc)] = hook
        # A virtual call is looked up on the receiver's own class, so a
        # subclass constructor calling this.setHardness needs both keys.
        for nm, desc in self.passthru:
            interp.hooks[(self.obf, nm, desc)] = _returns_self
            interp.hooks[(rec['ctor'], nm, desc)] = _returns_self
        for desc in self.ctors:
            interp.hooks[(self.obf, '<init>', desc)] = _nothing
        # Block's registration tables are static arrays its <clinit> has not
        # made here. BlockContainer files itself in one; give it somewhere to.
        for name in self.tables:
            interp.statics[(self.obf, name)] = [None] * 256

        def field_hook(ref, name, desc):
            if (isinstance(ref, Ref) and ref.owner == self.obf
                    and (name == self.f_hardness or name in self.f_resistance)):
                pair = self.known.get(ref.name)
                if pair is None:
                    return Interp.NOTHING            # never guess a hardness
                return pair[0] if name == self.f_hardness else pair[1]
            return default_for('()' + desc)

        interp.field_hook = field_hook
        args = [Ref(self.obf, a['ref'].split('.')[-1], a.get('desc'))
                if isinstance(a, dict) and 'ref' in a else a
                for a in (rec['args'] or [])]
        try:
            interp.call(rec['ctor'], '<init>', rec['ctor_desc'], Obj(rec['ctor']), args)
        except Exception:
            pass                                     # keep the prefix we got
        return out


def _returns_self(_interp, recv, _args):
    return recv


def _nothing(_interp, _recv, _args):
    return Interp.NOTHING


def putfields(cf, m):
    """Fields a method assigns, in the order it assigns them."""
    return [cf.ref(u2(o))[1] for _pc, op, o in disassemble(cf.code_of(m)) if op == 0xb5]


def invokes(cf, m):
    """Method names a method calls."""
    return [cf.ref(u2(o))[1] for _pc, op, o in disassemble(cf.code_of(m))
            if op in (0xb6, 0xb7, 0xb8, 0xb9)]


def extract_blocks(jar, mp, lang_names, lang_descs, overrides=None):
    obf = mp.find_class('net/minecraft/block/Block')
    cf = jar.cls(obf)
    recs = trace_clinit(cf)
    ctors = BlockCtor(jar, cf, obf)
    blocks, by_field = [], {}
    for r in recs:
        args = r['args'] or []
        if not args or not isinstance(args[0], int):
            # e.g. WoolBlock(), whose super(35, ...) call is inside its own <init>
            args = super_args(jar, r['ctor'], obf) or []
        if not args or not isinstance(args[0], int):
            continue
        bid = args[0]
        if not 0 < bid < 256:
            continue
        calls = const_calls(r)
        # args[1] is only a texture index when the constructor actually declares
        # a second int. StoneSlabBlock(int, boolean) would otherwise report its
        # flag as a texture.
        cparams = params_of(r['ctor_desc']) if r.get('ctor_desc') else []
        texture = (args[1] if len(args) > 1 and isinstance(args[1], int)
                   and len(cparams) > 1 and cparams[1] == 'I' else None)
        key = hardness = light = opacity = None
        # Beta 1.7.3 Block: setHardness raises blastResistance to hardness*5,
        # setResistance sets it to f*3, and explosions divide it by 5. Order of
        # the builder calls therefore matters, so replay them as written --
        # the constructor's first, since it finishes before the <clinit> chain
        # that is written onto its result begins.
        blast = 0.0
        for nm, desc, cargs in ctors.calls(r) + list(r['calls']):
            v = cargs[0] if cargs else None
            if desc.startswith('(Ljava/lang/String;)'):
                key = v
            elif desc == '(F)L%s;' % obf and isinstance(v, (int, float)):
                if nm == B_HARDNESS:
                    hardness = float(v)
                    blast = max(blast, hardness * 5.0)
                elif nm == B_RESISTANCE:
                    blast = float(v) * 3.0
                elif nm == B_LIGHT:
                    light = float(v)
            elif desc == '(I)L%s;' % obf and nm == B_OPACITY:
                opacity = num(v)
            elif nm in ctors.unbreakable and desc == '()L%s;' % obf:
                hardness = -1.0                   # setBlockUnbreakable
        ctors.learn(r['field'], hardness, blast)
        lang_key = 'tile.%s' % key if key else None
        entry = {
            'id': bid,
            'key': key,
            'name': ((overrides or {}).get(str(bid))
                     or lang_names.get(lang_key) or key or 'Block %d' % bid),
            'langKey': lang_key,
            'class': mp.simple(r['ctor']),
            'texture': texture,
            'hardness': round(hardness, 4) if hardness is not None else None,
            'blastResistance': round(blast / 5.0, 4),
            'lightEmission': light_level(light),
            'lightOpacity': opacity,
            'field': r['field'],
        }
        if lang_descs.get(lang_key):
            entry['desc'] = lang_descs[lang_key]
        blocks.append(entry)
        by_field[r['field']] = bid
    blocks.sort(key=lambda b: b['id'])
    return blocks, by_field, obf


def extract_items(jar, mp, lang_names, overrides=None):
    obf = (mp.find_class('net/minecraft/Item')
           or mp.find_class('net/minecraft/item/Item'))
    cf = jar.cls(obf)
    recs = trace_clinit(cf)
    items, by_field = [], {}
    for r in recs:
        args = r['args'] or []
        if not args or not isinstance(args[0], int):
            continue
        iid = args[0] + 256
        calls = const_calls(r)
        key = icon = None
        for (nm, desc), argsets in calls.items():
            if desc.startswith('(Ljava/lang/String;)'):
                key = first_arg(argsets)
            elif desc == '(II)L%s;' % obf:
                a = argsets[0]
                if len(a) == 2 and all(isinstance(x, int) for x in a):
                    icon = {'x': a[0], 'y': a[1]}
        lang_key = 'item.%s' % key if key else None
        items.append({
            'id': iid,
            'key': key,
            'name': ((overrides or {}).get(str(iid))
                     or lang_names.get(lang_key) or key or 'Item %d' % iid),
            'langKey': lang_key,
            'class': mp.simple(r['ctor']),
            'icon': icon,
            'field': r['field'],
        })
        by_field[r['field']] = iid
    items.sort(key=lambda i: i['id'])
    return items, by_field, obf


def extract_entities(jar, mp):
    """Find the registry class by the mob names in its constant pool.

    Returns the records and, separately, each one's obfuscated class, which
    the records do not carry but the health lookup in properties.py needs.
    """
    mobs = {'Pig', 'Sheep', 'Cow', 'Creeper', 'Skeleton', 'Zombie', 'Spider', 'Ghast'}
    for name in jar.classes():
        cf = jar.cls(name)
        if cf is None:
            continue
        strs = {e[1] for e in cf.cp if e and e[0] == 'utf8'}
        if len(mobs & strs) < 6:
            continue
        out, classes = [], {}
        for c in trace_calls(cf):
            a = c['args']
            if (len(a) == 3 and isinstance(a[0], str)
                    and isinstance(a[1], str) and isinstance(a[2], int)):
                out.append({'name': a[1], 'networkId': a[2], 'class': mp.simple(a[0])})
                classes[a[1]] = a[0]
        if out:
            return sorted(out, key=lambda e: e['networkId']), classes
    return [], {}


def add_properties(jar, mp, blocks, items, entities, entity_classes):
    """Stack size, durability, attack damage, healing and health. See properties.py.

    A block's stack size is its own item form's: every block id has one, made
    at the end of Block's <clinit>, and a player can hold any of them.
    """
    props = Properties(Appearance(jar, mp), jar, mp)
    for b in blocks:
        b['stackSize'] = props.of_item(b['id'])['stackSize']
    for i in items:
        i.update(props.of_item(i['id']))
    for e in entities:
        health = props.health(entity_classes[e['name']])
        if health is not None:
            e['health'] = health


def extract_biomes(jar, mp):
    """Biomes are anonymous singletons; the display name comes from a setter."""
    known = {'Rainforest', 'Swampland', 'Forest', 'Savanna', 'Shrubland',
             'Taiga', 'Desert', 'Plains', 'Tundra'}
    for name in jar.classes():
        cf = jar.cls(name)
        if cf is None:
            continue
        strs = {e[1] for e in cf.cp if e and e[0] == 'utf8'}
        if len(known & strs) < 5:
            continue
        out = []
        for r in trace_clinit(cf):
            label = color = None
            for nm, desc, cargs in r['calls']:
                v = cargs[0] if cargs else None
                if desc.startswith('(Ljava/lang/String;)') and isinstance(v, str):
                    label = v
                elif desc.startswith('(I)') and color is None and isinstance(v, int):
                    color = v
            if label:
                out.append({
                    'name': label,
                    'class': mp.simple(r['ctor']),
                    'color': '#%06X' % (color & 0xFFFFFF) if color is not None else None,
                    'field': r['field'],
                })
        if len(out) >= 5:
            return out
    return []


def resolve(v, bfield, ifield, block_obf, item_obf):
    """Turn a decoded bytecode value into {'block'|'item': id, ...}."""
    if isinstance(v, dict) and 'ref' in v:
        owner, field = v['ref'].split('.', 1)
        if owner == block_obf and field in bfield:
            return {'block': bfield[field]}
        if owner == item_obf and field in ifield:
            return {'item': ifield[field]}
        return None
    if isinstance(v, dict) and 'new' in v:            # ItemStack(thing, count[, damage])
        a = v.get('args') or []
        base = resolve(a[0], bfield, ifield, block_obf, item_obf) if a else None
        if base is None:
            return None
        if len(a) > 1 and isinstance(a[1], int):
            base['count'] = a[1]
        if len(a) > 2 and isinstance(a[2], int):
            base['damage'] = a[2]
        return base
    return None


def extract_recipes(jar, mp, bfield, ifield, block_obf, item_obf):
    """Every crafting recipe, by running CraftingManager's constructor.

    Most of the game's recipes are not constants anywhere in the bytecode.
    CraftingManager writes about sixty out one call at a time and hands the
    rest to seven generator classes that build them in loops over material
    tables -- every tool, weapon, armour piece, dye and ingot-block conversion.
    Recovering those statically means reimplementing the loops by hand;
    running them does not. See interp.py.

    Recipes come out in registration order (tools, weapons, ingots, food,
    crafting, armour, dyes, then CraftingManager's own). The game finishes by
    sorting the list with RecipeSorter, but that orders by matching priority --
    shaped before shapeless, larger recipes first -- which is a lookup detail,
    not something a reader wants, so the sort is skipped.
    """
    stack_obf = mp.find_class('net/minecraft/item/ItemStack')
    varargs = '(L%s;[Ljava/lang/Object;)V' % stack_obf

    manager = None
    for name in jar.classes():
        cf = jar.cls(name)
        if cf is not None and sum(1 for m in cf.methods
                                  if m['desc'] == varargs) >= 2:
            manager = name
            break
    if manager is None:
        return []

    # Of the two varargs registrars, the shaped one is much the larger: it is
    # the one that parses the pattern rows into a grid.
    mcf = jar.cls(manager)
    sizes = {m['name']: len(mcf.code_of(m) or b'')
             for m in mcf.methods if m['desc'] == varargs}
    shaped_name = max(sizes, key=sizes.get)

    # ItemStack's fields, by their mapped names, so the ints the constructors
    # leave behind can be read back without hard-coding obfuscated letters.
    scf = jar.cls(stack_obf)
    sfields = {mp.member(stack_obf, f['name'], f['desc']): f['name']
               for f in scf.fields}
    # Obj keys a field by the class that declares it, so an obfuscated
    # hierarchy cannot have two classes share one slot.
    F_ID = (stack_obf, sfields['itemId'])
    F_COUNT = (stack_obf, sfields['count'])
    F_DAMAGE = (stack_obf, sfields['damage'])

    def field_hook(ref, name, desc):
        """Resolve `Block.stone.blockID` and `Item.stick.shiftedIndex`.

        Both are the mapped name `id`. Answering here is what lets the recipe
        code run without ever executing Block's or Item's static initialiser.
        """
        if isinstance(ref, ArrayRef):
            # Item.itemsList[n] is the item form of block n, so its id is n.
            if isinstance(ref.index, int) and 0 <= ref.index < 256:
                return ref.index
            return Interp.NOTHING
        if desc == 'I' and mp.member(ref.owner, name, desc) == 'id':
            if ref.owner == block_obf and ref.name in bfield:
                return bfield[ref.name]
            if ref.owner == item_obf and ref.name in ifield:
                return ifield[ref.name]
        return Interp.NOTHING

    def value(v, ingredient=False):
        """A recipe argument as {'block'|'item': id, ...}, or None.

        An ingredient never carries a count. Both recipe classes match on
        itemID and damage alone and never look at stackSize, so the 9 in
        RecipesIngots' `new ItemStack(Item.ingotGold, 9)` is the *output* of
        the reverse recipe leaking into the forward one's ingredient slot --
        a grid cell still only ever takes one item. Damage -1 is the game's
        "any metadata" wildcard, which is the absence of a constraint.
        """
        if isinstance(v, Obj) and v.cls == stack_obf:
            ident = v.fields.get(F_ID)
            if not isinstance(ident, int):
                return None
            out = {'block': ident} if ident < 256 else {'item': ident}
            if not ingredient:
                out['count'] = v.fields.get(F_COUNT, 1)
            damage = v.fields.get(F_DAMAGE, 0)
            if damage and damage != -1:
                out['damage'] = damage
            return out
        if isinstance(v, Ref):
            if v.owner == block_obf and v.name in bfield:
                return {'block': bfield[v.name]}
            if v.owner == item_obf and v.name in ifield:
                return {'item': ifield[v.name]}
        if isinstance(v, ArrayRef) and isinstance(v.index, int) and v.index < 256:
            return {'block': v.index}
        return None

    recipes = []

    def register(shaped, args):
        out = value(args[0])
        arr = args[1]
        if out is None or not isinstance(arr, list):
            return
        if shaped:
            # The first vararg is either a String[] of rows (what the loop-
            # driven generators pass) or a run of loose row strings.
            if arr and isinstance(arr[0], list):
                rows, rest = [r for r in arr[0] if isinstance(r, str)], arr[1:]
            else:
                n = 0
                while n < len(arr) and isinstance(arr[n], str):
                    n += 1
                rows, rest = arr[:n], arr[n:]
            key = {}
            for i in range(0, len(rest) - 1, 2):
                ch, ing = rest[i], rest[i + 1]
                got = value(ing, ingredient=True)
                if isinstance(ch, int) and got:
                    key[chr(ch)] = got
            if rows and key:
                recipes.append({'type': 'shaped', 'output': out,
                                'pattern': rows, 'key': key})
        else:
            ings = [got for got in (value(x, ingredient=True) for x in arr) if got]
            if ings:
                recipes.append({'type': 'shapeless', 'output': out,
                                'ingredients': ings})

    interp = Interp(jar.cls)
    interp.field_hook = field_hook
    for nm in sizes:
        interp.hooks[(manager, nm, varargs)] = (
            lambda shaped: lambda it, recv, args: (register(shaped, args),
                                                   Interp.NOTHING)[1]
        )(nm == shaped_name)
    interp.call(manager, '<init>', '()V', Obj(manager), [])
    return recipes


def label_classes(jar, bfield, ifield, block_obf, item_obf):
    """Which class names each id's stacks: {('block'|'item', id): class}.

    An item's namer is simply the class its constructor made, straight out of
    Item's <clinit>. A block's is chosen separately, at the end of Block's
    <clinit>, by assigning into Item.itemsList:

        Item.itemsList[cloth.blockID] = new ItemCloth(...).setItemName("cloth")

    which is the only statement in the game that gives wool and slabs their
    per-metadata names, so it is read here rather than assumed.
    """
    out = {}
    icf = jar.cls(item_obf)
    for r in trace_clinit(icf):
        if r['field'] in ifield:
            out[('item', ifield[r['field']])] = r['ctor']

    bcf = jar.cls(block_obf)
    code = bcf.code_of(bcf.method('<clinit>'))
    items_list = '[L%s;' % item_obf
    into_items = last_block = last_new = None
    for _pc, op, operand in disassemble(code):
        if op == 0xb2:                                        # getstatic
            owner, name, desc = bcf.ref(u2(operand))
            if desc == items_list:
                into_items = True
            elif owner == block_obf and name in bfield:
                last_block = bfield[name]
        elif op == 0xbb:                                      # new
            last_new = bcf.cls_name(u2(operand))
        elif op == 0x53:                                      # aastore
            if into_items and last_block is not None and last_new is not None:
                out[('block', last_block)] = last_new
            into_items = last_new = None
    return out


def extract_variants(jar, mp, lang_names, blocks, items, bfield, ifield,
                     block_obf, item_obf, stack_obf):
    """Display names for the ids whose damage value selects a subtype.

    Wool, dye, slabs and coal all pack several things into one id and pick a
    translation key from the damage value -- `~damage & 15` for wool, a table
    index for slabs, a plain comparison for charcoal. Rather than restate any
    of that, run the game's own labelling method (getItemNameIS) once per
    damage value and look the answer up in en_US.lang.

    Ids whose sixteen answers are all the same have no subtypes, which is how
    the ordinary items fall out without being listed anywhere.
    """
    name_is = '(L%s;)Ljava/lang/String;' % stack_obf
    plain = '()Ljava/lang/String;'
    icf = jar.cls(item_obf)
    getter = next((m['name'] for m in icf.methods if m['desc'] == name_is), None)
    plain_getter = next((m['name'] for m in icf.methods
                         if m['desc'] == plain
                         and mp.member(item_obf, m['name'], plain) == 'getTranslationKey'),
                        None)
    if getter is None or plain_getter is None:
        return {}

    scf = jar.cls(stack_obf)
    sfields = {mp.member(stack_obf, f['name'], f['desc']): f['name']
               for f in scf.fields}
    ifields = {mp.member(item_obf, f['name'], f['desc']): f['name']
               for f in icf.fields}
    F_DAMAGE = (stack_obf, sfields['damage'])
    F_ID = (stack_obf, sfields['itemId'])
    F_KEY = (item_obf, ifields['translationKey']) if 'translationKey' in ifields else None

    owners = label_classes(jar, bfield, ifield, block_obf, item_obf)
    by_id = {('block', b['id']): b for b in blocks}
    by_id.update({('item', i['id']): i for i in items})

    variants = {}
    for ref, cls_obf in sorted(owners.items()):
        entry = by_id.get(ref)
        if entry is None or not entry.get('langKey'):
            continue
        cf = jar.cls(cls_obf)
        if cf is None or cf.method(getter, name_is) is None:
            continue                          # inherits the plain name

        interp = Interp(jar.cls)
        # getItemName() is the key of the stack's own kind. ItemBlock overrides
        # it to go through Block.blocksList, which is deliberately symbolic
        # here, so answer it outright for every class in the chain. An override
        # shares its parent's obfuscated name, and barn leaves ItemBlock's
        # members unmapped, so the name has to come from Item's mapping.
        chain, cur = [], cls_obf
        while cur and len(chain) < 8:
            chain.append(cur)
            c = jar.cls(cur)
            cur = c.super if c else None
        for c_obf in chain:
            interp.hooks[(c_obf, plain_getter, plain)] = (
                lambda key: lambda it, recv, args: key)(entry['langKey'])

        found = {}
        for damage in range(16):
            recv = Obj(cls_obf)
            if F_KEY:
                recv.fields[F_KEY] = entry['langKey']
            stack = Obj(stack_obf)
            stack.fields[F_ID] = entry['id']
            stack.fields[F_DAMAGE] = damage
            try:
                key = interp.call(cls_obf, getter, name_is, recv, [stack])
            except Unsupported:
                break                     # names this one a way we cannot follow
            label = lang_names.get(key) if isinstance(key, str) else None
            if label:
                found[damage] = label
        if len(set(found.values())) > 1:
            # Damage 0 is the default and always worth stating. Beyond it, a
            # value that lands back on the plain name says nothing a reader
            # cannot get from the fallback -- coal is coal at every damage but
            # 1 -- so only the ones that differ are kept.
            variants[ref] = {str(d): n for d, n in sorted(found.items())
                             if d == 0 or n != entry['name']}
    return variants


def extract_smelting(jar, mp, bfield, ifield, block_obf, item_obf):
    stack_obf = mp.find_class('net/minecraft/item/ItemStack')
    want = '(IL%s;)V' % stack_obf
    for name in jar.classes():
        cf = jar.cls(name)
        if cf is None or not any(m['desc'] == want for m in cf.methods):
            continue
        out = []
        for meth in ('<init>', '<clinit>'):
            for c in trace_calls(cf, meth):
                if c['desc'] != want:
                    continue
                src, dst = c['args'][0], c['args'][1]
                inp = ({'block': src} if isinstance(src, int) and src < 256
                       else {'item': src} if isinstance(src, int)
                       else resolve(src, bfield, ifield, block_obf, item_obf))
                res = resolve(dst, bfield, ifield, block_obf, item_obf)
                if inp and res:
                    out.append({'input': inp, 'output': res})
        if len(out) >= 3:
            return out
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jar', help='client.jar; found automatically if omitted')
    ap.add_argument('--cache', help='directory holding intermediary.tiny and '
                                    'barn.tiny; found automatically if omitted')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    try:
        cache = a.cache or find_cache().path
        jar_path = a.jar or find_jar().path
    except Missing as err:
        raise SystemExit('error: %s' % err)

    jar = Jar(jar_path)
    mp = load_mappings(os.path.join(cache, 'intermediary.tiny'),
                       os.path.join(cache, 'barn.tiny'))
    lang_names, lang_descs = parse_lang(jar)

    block_names, item_names, variant_names = load_name_overrides(a.out)
    blocks, bfield, block_obf = extract_blocks(jar, mp, lang_names, lang_descs, block_names)
    items, ifield, item_obf = extract_items(jar, mp, lang_names, item_names)
    entities, entity_classes = extract_entities(jar, mp)
    add_properties(jar, mp, blocks, items, entities, entity_classes)
    biomes = extract_biomes(jar, mp)
    recipes = extract_recipes(jar, mp, bfield, ifield, block_obf, item_obf)
    smelting = extract_smelting(jar, mp, bfield, ifield, block_obf, item_obf)

    stack_obf = mp.find_class('net/minecraft/item/ItemStack')
    variants = extract_variants(jar, mp, lang_names, blocks, items,
                                bfield, ifield, block_obf, item_obf, stack_obf)
    for ident, names in variant_names.items():
        variants.setdefault(('block', int(ident)), {}).update(names)
    for (kind, ident), names in variants.items():
        for entry in (blocks if kind == 'block' else items):
            if entry['id'] == ident:
                entry['variants'] = {k: names[k] for k in sorted(names, key=int)}

    os.makedirs(a.out, exist_ok=True)

    def write(nm, obj):
        with io.open(os.path.join(a.out, nm), 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(obj, fh, indent=2, ensure_ascii=False)
            fh.write('\n')
        print('  %-16s %d entries' % (nm, len(obj)))

    print('Extracted from %s' % jar_path)
    write('blocks.json', blocks)
    write('items.json', items)
    write('entities.json', entities)
    write('biomes.json', biomes)
    write('recipes.json', recipes)
    write('smelting.json', smelting)
    write('meta.json', {
        'version': 'Beta 1.7.3',
        'source': os.path.basename(jar_path),
        'sha1': sha1(io.open(jar_path, 'rb').read()),
        'generator': 'tools/extract/gamedata.py',
    })

    shared = shared_names(blocks, items, entities)
    if shared:
        print('\n%d names are claimed by more than one id. Each is one page and '
              'one sprite;\nsplit any that are two things in name-overrides.json.'
              % len(shared))
        for name, where in shared.items():
            print('  %-20s %s' % (name, ', '.join(where)))


if __name__ == '__main__':
    main()
