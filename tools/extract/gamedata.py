#!/usr/bin/env python3
"""Extract Minecraft Beta 1.7.3 game data from the shipped client.jar.

Everything here is derived from the real bytecode and the real en_US.lang, so
the wiki's IDs, sprites, hardness values and recipes are facts rather than
recollections. Run this once; the JSON it writes is committed to the repo and
the site build never needs the jar.

    python tools/extract/gamedata.py --jar <client.jar> --cache <BabricKit/cache> --out data

Setter identification
---------------------
barn.tiny does not name Block's builder methods, so they are identified by the
values they carry, each cross-checked against known Beta 1.7.3 behaviour:

    c(F)  hardness         stone 1.5, dirt 0.5, cobblestone 2.0
    b(F)  resistance       stone 10, bedrock 6000000  (blast resistance = f*3/5)
    a(F)  light emission   lava 1.0, glowstone 1.0
    g(I)  light opacity    water 3, lava 255, leaves 1
    a(String)  translation key -- every value is a key present in en_US.lang
"""
import argparse
import hashlib
import io
import json
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classfile import ClassFile
from disasm import trace_clinit, trace_calls, params_of
from mappings import load as load_mappings

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
    """Names for the few blocks/items en_US.lang never gives one."""
    path = os.path.join(out_dir, 'name-overrides.json')
    if not os.path.exists(path):
        return {}, {}
    doc = json.load(io.open(path, encoding='utf-8'))
    return doc.get('byBlockId', {}), doc.get('byItemId', {})


def extract_blocks(jar, mp, lang_names, lang_descs, overrides=None):
    obf = mp.find_class('net/minecraft/block/Block')
    cf = jar.cls(obf)
    recs = trace_clinit(cf)
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
        # the builder calls therefore matters, so replay them as written.
        blast = 0.0
        for nm, desc, cargs in r['calls']:
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
            elif nm == 'l' and desc == '()L%s;' % obf:
                hardness = -1.0                   # setUnbreakable
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
            'lightEmission': int(round(light * 15)) if light else 0,
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
    """Find the registry class by the mob names in its constant pool."""
    mobs = {'Pig', 'Sheep', 'Cow', 'Creeper', 'Skeleton', 'Zombie', 'Spider', 'Ghast'}
    for name in jar.classes():
        cf = jar.cls(name)
        if cf is None:
            continue
        strs = {e[1] for e in cf.cp if e and e[0] == 'utf8'}
        if len(mobs & strs) < 6:
            continue
        out = []
        for c in trace_calls(cf):
            a = c['args']
            if (len(a) == 3 and isinstance(a[0], str)
                    and isinstance(a[1], str) and isinstance(a[2], int)):
                out.append({'name': a[1], 'networkId': a[2], 'class': mp.simple(a[0])})
        if out:
            return sorted(out, key=lambda e: e['networkId'])
    return []


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
    stack_obf = mp.find_class('net/minecraft/item/ItemStack')
    shaped_desc = '(L%s;[Ljava/lang/Object;)V' % stack_obf

    manager = None
    for name in jar.classes():
        cf = jar.cls(name)
        if cf is not None and sum(1 for m in cf.methods
                                  if m['desc'] == shaped_desc) >= 2:
            manager = name
            break
    if manager is None:
        return []

    # The shaped variant is the larger method: it parses the pattern rows.
    mcf = jar.cls(manager)
    sizes = {m['name']: len(mcf.code_of(m) or b'')
             for m in mcf.methods if m['desc'] == shaped_desc}
    shaped_name = max(sizes, key=sizes.get) if sizes else None

    # The manager registers some recipes itself and delegates the rest.
    helper_desc = '(L%s;)V' % manager
    sources = [(manager, '<init>')]
    for name in jar.classes():
        cf = jar.cls(name)
        if cf is None or name == manager:
            continue
        for m in cf.methods:
            if m['desc'] == helper_desc:
                sources.append((name, m['name']))

    recipes = []
    for cls_name, meth in sources:
        cf = jar.cls(cls_name)
        for c in trace_calls(cf, meth):
            if c['desc'] != shaped_desc:
                continue
            out = resolve(c['args'][0], bfield, ifield, block_obf, item_obf)
            arr = c['args'][1]
            if out is None or not isinstance(arr, list):
                continue
            rows = [x for x in arr if isinstance(x, str)]
            rest = [x for x in arr if not isinstance(x, str)]
            if c['name'] == shaped_name and rows:
                key = {}
                for i in range(0, len(rest) - 1, 2):
                    ch, ing = rest[i], rest[i + 1]
                    if isinstance(ch, int):
                        r = resolve(ing, bfield, ifield, block_obf, item_obf)
                        if r:
                            key[chr(ch)] = r
                if key:
                    recipes.append({'type': 'shaped', 'output': out,
                                    'pattern': rows, 'key': key})
            else:
                ings = [resolve(x, bfield, ifield, block_obf, item_obf) for x in arr]
                ings = [i for i in ings if i]
                if ings:
                    recipes.append({'type': 'shapeless', 'output': out,
                                    'ingredients': ings})
    return recipes


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
    ap.add_argument('--jar', required=True)
    ap.add_argument('--cache', required=True,
                    help='directory holding intermediary.tiny and barn.tiny')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    jar = Jar(a.jar)
    mp = load_mappings(os.path.join(a.cache, 'intermediary.tiny'),
                       os.path.join(a.cache, 'barn.tiny'))
    lang_names, lang_descs = parse_lang(jar)

    block_names, item_names = load_name_overrides(a.out)
    blocks, bfield, block_obf = extract_blocks(jar, mp, lang_names, lang_descs, block_names)
    items, ifield, item_obf = extract_items(jar, mp, lang_names, item_names)
    entities = extract_entities(jar, mp)
    biomes = extract_biomes(jar, mp)
    recipes = extract_recipes(jar, mp, bfield, ifield, block_obf, item_obf)
    smelting = extract_smelting(jar, mp, bfield, ifield, block_obf, item_obf)

    os.makedirs(a.out, exist_ok=True)

    def write(nm, obj):
        with io.open(os.path.join(a.out, nm), 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(obj, fh, indent=2, ensure_ascii=False)
            fh.write('\n')
        print('  %-16s %d entries' % (nm, len(obj)))

    print('Extracted from %s' % os.path.basename(a.jar))
    write('blocks.json', blocks)
    write('items.json', items)
    write('entities.json', entities)
    write('biomes.json', biomes)
    write('recipes.json', recipes)
    write('smelting.json', smelting)
    write('meta.json', {
        'version': 'Beta 1.7.3',
        'source': os.path.basename(a.jar),
        'sha1': sha1(io.open(a.jar, 'rb').read()),
        'generator': 'tools/extract/gamedata.py',
    })


if __name__ == '__main__':
    main()
