#!/usr/bin/env python3
"""Slice Beta 1.7.3 texture sheets into per-tile sprites and build a manifest.

    python tools/extract/sprites.py --jar <client.jar> --out . [--contact-sheet F]

terrain.png and gui/items.png are both 256x256, i.e. a 16x16 grid of 16x16
tiles indexed row-major. Blocks record a terrain index and items record (x, y)
icon coordinates, so the manifest can map a page slug straight to a tile
without duplicating any image data.
"""
import argparse
import io
import json
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import png

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


def slug(name):
    """Wiki slug shared with the site build: lowercase, hyphen separated."""
    s = re.sub(r"[^a-z0-9]+", '-', name.lower())
    return s.strip('-')


def write_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as fh:
        fh.write(data)


def slice_sheet(img, outdir, prefix):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jar', required=True)
    ap.add_argument('--out', required=True, help='repository root')
    ap.add_argument('--contact-sheet', help='write an upscaled terrain sheet here')
    a = ap.parse_args()

    z = zipfile.ZipFile(a.jar)
    root = a.out
    sprites_dir = os.path.join(root, 'assets', 'sprites')
    tex_dir = os.path.join(root, 'assets', 'textures')

    terrain = png.decode(z.read('terrain.png'))
    items = png.decode(z.read('gui/items.png'))

    have_terrain = slice_sheet(terrain, os.path.join(sprites_dir, 'terrain'), 'terrain')
    have_items = slice_sheet(items, os.path.join(sprites_dir, 'items'), 'items')
    print('sliced %d terrain tiles, %d item tiles' % (len(have_terrain), len(have_items)))

    for name in RAW_TEXTURES:
        try:
            write_file(os.path.join(tex_dir, name.replace('/', os.sep)), z.read(name))
        except KeyError:
            pass
    mobs = 0
    for name in z.namelist():
        if name.startswith(MOB_PREFIX) or name.startswith(ARMOR_PREFIX):
            if name.endswith('.png'):
                write_file(os.path.join(tex_dir, name.replace('/', os.sep)), z.read(name))
                mobs += 1
    print('copied %d raw sheets, %d mob/armor textures' % (len(RAW_TEXTURES), mobs))

    if a.contact_sheet:
        write_file(a.contact_sheet, png.encode(terrain.scale(4)))
        print('contact sheet -> %s' % a.contact_sheet)

    # ---- manifest -------------------------------------------------------------
    data_dir = os.path.join(root, 'data')
    blocks = json.load(io.open(os.path.join(data_dir, 'blocks.json'), encoding='utf-8'))
    itemdefs = json.load(io.open(os.path.join(data_dir, 'items.json'), encoding='utf-8'))

    ov_path = os.path.join(data_dir, 'texture-overrides.json')
    overrides = {}
    if os.path.exists(ov_path):
        overrides = json.load(io.open(ov_path, encoding='utf-8')).get('byBlockId', {})

    sprites, missing = {}, []
    for b in blocks:
        key = slug(b['name'])
        idx = overrides.get(str(b['id']), b['texture'])
        if idx is None or idx not in have_terrain:
            missing.append(b['name'])
            continue
        sprites[key] = {'sheet': 'terrain', 'index': idx,
                        'file': 'assets/sprites/terrain/%d.png' % idx}
    for it in itemdefs:
        key = slug(it['name'])
        if key in sprites or not it['icon']:
            continue
        idx = it['icon']['y'] * GRID + it['icon']['x']
        if idx not in have_items:
            missing.append(it['name'])
            continue
        sprites[key] = {'sheet': 'items', 'index': idx,
                        'file': 'assets/sprites/items/%d.png' % idx}

    out = {
        'tile': TILE,
        'note': 'Generated by tools/extract/sprites.py. Fix a wrong block tile by '
                'setting its block id in data/texture-overrides.json, then re-run '
                'that script.',
        'sprites': dict(sorted(sprites.items())),
    }
    with io.open(os.path.join(data_dir, 'sprites.json'), 'w',
                 encoding='utf-8', newline='\n') as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write('\n')
    print('manifest: %d sprites, %d without a tile' % (len(sprites), len(missing)))
    if missing:
        print('  no tile yet: %s' % ', '.join(sorted(set(missing))))


if __name__ == '__main__':
    main()
