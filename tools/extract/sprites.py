#!/usr/bin/env python3
"""Slice Beta 1.7.3's texture sheets and render every inventory icon.

    python tools/extract/sprites.py --out . [--contact-sheet F]

The jar is found automatically; see paths.py for how to say where it is.

Three things happen here, in order.

The sheets are decoded and the tiles the game generates for itself are put
back (see animated.py). A shipped terrain.png has a flat blue square where the
portal belongs, a red FIRE TEX! placard where the flames belong and rough
sketches of water and lava; gui/items.png has a compass with no needle and a
clock with a magenta hole for its dial.

Both sheets are then sliced tile by tile into assets/sprites/, which is what a
page reaching for a raw texture gets. The raw sheets are copied across
untouched, so what is under assets/textures/ is exactly what shipped.

Finally every block, item and metadata variant is asked what the game draws
for it (appearance.py) and the answer is rendered (isometric.py). Most blocks
come out as the little three-quarter cube a player sees rather than one flat
face of themselves, and a stack whose damage value picks its own tile -- all
sixteen wools, all sixteen dyes -- gets an icon of its own. Where a slot is
misleading the world wins; see the note above WORLD_TINTED.
"""
import argparse
import io
import json
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import animated
import isometric
import png
from appearance import WHITE, Appearance
from gamedata import Jar
from mappings import load as load_mappings
from paths import Missing, find_cache, find_jar

TILE = 16
GRID = 16

# Sheets copied through verbatim for pages that want the whole image.
RAW_TEXTURES = [
    'terrain.png', 'gui/items.png', 'gui/gui.png', 'gui/icons.png',
    'gui/crafting.png', 'gui/furnace.png', 'gui/inventory.png', 'gui/container.png',
    'gui/logo.png', 'gui/particles.png', 'gui/background.png', 'gui/slot.png',
    'gui/trap.png', 'font/default.png', 'achievement/icons.png', 'particles.png',
    'misc/grasscolor.png', 'misc/foliagecolor.png', 'misc/watercolor.png',
    'environment/clouds.png', 'environment/rain.png', 'environment/snow.png',
    'terrain/sun.png', 'terrain/moon.png', 'title/mclogo.png', 'pack.png',
    'item/arrows.png', 'item/boat.png', 'item/cart.png', 'item/door.png',
    'item/sign.png', 'art/kz.png',
]
MOB_PREFIX = 'mob/'
ARMOR_PREFIX = 'armor/'

# Two blocks a slot draws differently from the world. The wiki follows the
# world, because a slot is not where anyone meets either of them.
#
# Tall grass and the fern are grey in a slot and the biome's colour in the
# world. The colour is the game's own -- ColorizerGrass.getGrassColor against
# the shipped misc/grasscolor.png -- read at the middle of the table. Metadata
# 0 is the dead shrub, which BlockTallGrass.colorMultiplier leaves alone, and
# so does this.
#
# The grass block is worse off: BlockGrass overrides only the texture lookup
# that takes a world, so a slot falls back to grass_side on all six faces and
# the top of the cube is half dirt. getBlockTexture has grass up there and
# dirt underneath, and RenderBlocks singles Block.grass out to tint that top
# face and leave the other five alone.
GRASS = 'grass'
WORLD_TINTED = {'tallgrass': (1, 2)}
TOP = 1
DEFAULT_CLIMATE = (0.5, 1.0)


def slug(name):
    """Wiki slug shared with the site build: lowercase, hyphen separated."""
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def write_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as fh:
        fh.write(data)


def slice_sheet(img, outdir):
    """Write every non-blank tile as <outdir>/<index>.png; return the index set."""
    written = set()
    for idx in range(GRID * GRID):
        x, y = (idx % GRID) * TILE, (idx // GRID) * TILE
        tile = img.crop(x, y, TILE, TILE)
        if tile.is_blank():
            continue
        write_file(os.path.join(outdir, '%d.png' % idx), png.encode(tile))
        written.add(idx)
    return written


def grass_color(colorizer, climate=DEFAULT_CLIMATE):
    """ColorizerGrass.getGrassColor, against the shipped colour table."""
    temperature, humidity = climate
    humidity *= temperature
    x = int((1.0 - temperature) * 255.0)
    y = int((1.0 - humidity) * 255.0)
    at = (y * colorizer.w + x) * 4
    return (colorizer.px[at] << 16) | (colorizer.px[at + 1] << 8) | colorizer.px[at + 2]


def stacks(record):
    """(damage, display name) for a record: its own, plus any subtypes.

    A subtype whose name matches the record's own replaces it, which is how
    "Tall Grass" ends up as the growing plant at metadata 1 rather than the
    dead shrub the id happens to start with.
    """
    out = [(0, record['name'])]
    for damage, name in sorted((record.get('variants') or {}).items(), key=lambda kv: int(kv[0])):
        if (int(damage), name) not in out:
            out.append((int(damage), name))
    return out


def cube_look(game, record, icon, tint, world_tint):
    """The boxes and the tint to draw a cube block with.

    Every block but grass is drawn exactly as a slot draws it. Grass is asked
    getBlockTexture instead, and tinted the way RenderBlocks tints it: the top
    face only. See the note on GRASS above.
    """
    if record['key'] != GRASS:
        return icon['boxes'], tint
    faces = game.world_faces(record['id'])
    return ([box._replace(faces=faces) for box in icon['boxes']],
            tuple(world_tint if side == TOP else WHITE for side in range(6)))


def build_icons(game, sheets, records, out_dir, taken, kinds, world_tint, by_id=None,
                shared_by_id=None):
    """Render one file per named stack, and return its manifest entries.

    `by_id`, when given, also collects each record's own picture by id, which
    outlives the name if something else takes that name later.

    `shared_by_id`, when given, is the word for this kind of id ('item'). Two
    ids of the same name then no longer overwrite each other: the first keeps
    the name, and each later one is filed under its id, "item 2257", for a
    page that shows both. Without it the last one wins, as it does in the
    block pass, where the later of two twins is the lit torch or the still
    water.
    """
    entries, missing = {}, []
    by_id = {} if by_id is None else by_id
    for record in records:
        tinted = WORLD_TINTED.get(record['key'], ())
        for damage, name in stacks(record):
            key = slug(name)
            if key in taken and kinds.get(key) != 'flat':
                continue                     # a block already owns this name
            if shared_by_id and damage == 0 and key in entries:
                key = slug('%s %d' % (shared_by_id, record['id']))
            try:
                icon = game.icon(record['id'], damage)
            except Exception as err:
                missing.append('%s (%s)' % (name, err))
                continue
            tint = world_tint if damage in tinted else icon['tint']
            if icon['kind'] == 'cube':
                boxes, tint = cube_look(game, record, icon, tint, world_tint)
                image = isometric.render(sheets['terrain'], boxes, tint)
            elif tint == 0xFFFFFF:
                # Nothing to do to the tile, so point at the slice of it.
                index = icon['tile']
                entries[key] = {'sheet': icon['sheet'], 'index': index,
                                'file': 'assets/sprites/%s/%d.png' % (icon['sheet'], index)}
                kinds[key] = 'flat'
                if damage == 0:
                    by_id[record['id']] = entries[key]
                continue
            else:
                image = isometric.flat(sheets[icon['sheet']], icon['tile'], tint)
            write_file(os.path.join(out_dir, '%s.png' % key), png.encode(image))
            entries[key] = {'file': 'assets/sprites/icon/%s.png' % key}
            kinds[key] = icon['kind']
            if damage == 0:
                by_id[record['id']] = entries[key]
    return entries, missing


def prune(directory, keep):
    """Drop generated icons no longer named by anything, so renames leave nothing."""
    if not os.path.isdir(directory):
        return []
    gone = [f for f in sorted(os.listdir(directory)) if f.endswith('.png') and f not in keep]
    for name in gone:
        os.remove(os.path.join(directory, name))
    return gone


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jar', help='client.jar; found automatically if omitted')
    ap.add_argument('--cache', help='directory holding intermediary.tiny and '
                                    'barn.tiny; found automatically if omitted')
    ap.add_argument('--out', required=True, help='repository root')
    ap.add_argument('--contact-sheet', help='write an upscaled terrain sheet here')
    a = ap.parse_args()

    try:
        cache = a.cache or find_cache().path
        jar_path = a.jar or find_jar().path
    except Missing as err:
        raise SystemExit('error: %s' % err)

    root = a.out
    data_dir = os.path.join(root, 'data')
    blocks = json.load(io.open(os.path.join(data_dir, 'blocks.json'), encoding='utf-8'))
    itemdefs = json.load(io.open(os.path.join(data_dir, 'items.json'), encoding='utf-8'))

    z = zipfile.ZipFile(jar_path)
    terrain = png.decode(z.read('terrain.png'))
    items = png.decode(z.read('gui/items.png'))

    mp = load_mappings(os.path.join(cache, 'intermediary.tiny'),
                       os.path.join(cache, 'barn.tiny'))
    game = Appearance(Jar(jar_path), mp)

    # ---- the tiles the game draws for itself ---------------------------------
    # Every TextureFX names the tile it paints over in its own constructor,
    # out of the block's blockIndexInTexture or the item's icon, so the six
    # indices below are the game's and not this file's.
    by_key = {b['key']: b for b in blocks}
    item_by_key = {i['key']: i for i in itemdefs}
    icon_index = lambda rec: rec['icon']['y'] * GRID + rec['icon']['x'] if rec else None
    block_tile = lambda key: game.texture(by_key[key]['id']) if key in by_key else None
    fixed = animated.patch_sheets(
        terrain, items, png.decode(z.read('misc/dial.png')),
        {'portal': block_tile('portal'), 'water': block_tile('water'),
         'lava': block_tile('lava'), 'fire': block_tile('fire'),
         'compass': icon_index(item_by_key.get('compass')),
         'clock': icon_index(item_by_key.get('clock'))})
    print('regenerated %s' % ', '.join(fixed))

    # ---- raw tiles and raw sheets -------------------------------------------
    sprites_dir = os.path.join(root, 'assets', 'sprites')
    tex_dir = os.path.join(root, 'assets', 'textures')
    have_terrain = slice_sheet(terrain, os.path.join(sprites_dir, 'terrain'))
    have_items = slice_sheet(items, os.path.join(sprites_dir, 'items'))
    print('sliced %d terrain tiles, %d item tiles' % (len(have_terrain), len(have_items)))

    for name in RAW_TEXTURES:
        try:
            write_file(os.path.join(tex_dir, name.replace('/', os.sep)), z.read(name))
        except KeyError:
            pass
    mobs = 0
    for name in z.namelist():
        if (name.startswith(MOB_PREFIX) or name.startswith(ARMOR_PREFIX)) and name.endswith('.png'):
            write_file(os.path.join(tex_dir, name.replace('/', os.sep)), z.read(name))
            mobs += 1
    print('copied %d raw sheets, %d mob/armor textures' % (len(RAW_TEXTURES), mobs))

    if a.contact_sheet:
        write_file(a.contact_sheet, png.encode(terrain.scale(4)))
        print('contact sheet -> %s' % a.contact_sheet)

    # ---- inventory icons -----------------------------------------------------
    sheets = {'terrain': terrain, 'items': items}
    world_tint = grass_color(png.decode(z.read('misc/grasscolor.png')))
    icon_dir = os.path.join(sprites_dir, 'icon')

    kinds, block_own = {}, {}
    sprites, missing = build_icons(game, sheets, blocks, icon_dir, set(), kinds, world_tint,
                                   block_own)
    # An item of the same name wins over a block the inventory only ever draws
    # as a flat tile: a door, a sign, a bed and a repeater are all placed from
    # an item, and that item's icon is the picture a player would know.
    item_sprites, item_missing = build_icons(
        game, sheets, itemdefs, icon_dir, set(sprites), kinds, world_tint,
        shared_by_id='item')
    # The block keeps its own picture under its id, "block 83", for a page that
    # wants to show the thing as it stands in the world: sugar cane planted
    # rather than carried. An untinted tile is a slice of the sheet, which
    # nothing overwrites; a tinted one was rendered to the file the item's icon
    # has just replaced, so it is gone and is only reported.
    lost = []
    for block in blocks:
        own = block_own.get(block['id'])
        if own is None or slug(block['name']) not in item_sprites:
            continue
        if 'index' in own:
            sprites[slug('block %d' % block['id'])] = own
        else:
            lost.append('block %d' % block['id'])
    sprites.update(item_sprites)
    missing += item_missing

    dropped = prune(icon_dir, {os.path.basename(e['file']) for e in sprites.values()})

    out = {
        'tile': TILE,
        'note': 'Generated by tools/extract/sprites.py: what the inventory draws '
                'for each block, item and metadata variant. Entries with a sheet '
                'and an index are one raw tile; the rest are rendered into '
                'assets/sprites/icon/.',
        'sprites': dict(sorted(sprites.items())),
    }
    with io.open(os.path.join(data_dir, 'sprites.json'), 'w',
                 encoding='utf-8', newline='\n') as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write('\n')
    print('manifest: %d sprites, %d rendered' % (
        len(sprites), sum(1 for e in sprites.values() if 'index' not in e)))
    if dropped:
        print('  removed %d icon(s) nothing names any more' % len(dropped))
    if missing:
        print('  no icon: %s' % ', '.join(sorted(set(missing))))
    if lost:
        print('  no picture of its own kept for: %s' % ', '.join(lost))


if __name__ == '__main__':
    main()
