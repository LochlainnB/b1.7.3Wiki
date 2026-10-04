#!/usr/bin/env python3
"""Export frozen entity draws for the wiki's Three.js viewer."""
import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gamedata import extract_entities
from mappings import load as load_mappings
from models import Game, VARIANTS, prepare
from paths import Missing, REPO_ROOT, find_cache, find_jar
from softgl import identity


def face(draw):
    """Convert one softgl draw without changing its ordering or state."""
    return {
        'corners': [list(corner) for corner in draw.corners],
        'normal': list(draw.normal),
        'rgba': list(draw.rgba),
        'lit': draw.lit,
        'texture': draw.texture.lstrip('/') if draw.texture else None,
        'textured': draw.textured,
        'blend': draw.blend,
        'blend_func': list(draw.blend_func),
        'alpha_test': draw.alpha_test,
        'depth_test': draw.depth_test,
        'depth_mask': draw.depth_mask,
        'depth_func': draw.depth_func,
    }


def export_creeper(jar_path, cache):
    mp = load_mappings(os.path.join(cache, 'intermediary.tiny'),
                       os.path.join(cache, 'barn.tiny'))
    game = Game(jar_path, mp)
    _records, classes = extract_entities(game.jar, game.mp)
    creeper_class = classes['Creeper']
    variants = []
    for variant in VARIANTS['Creeper']:
        entity = game.spawn(creeper_class)
        prepare(game, entity, variant)
        # Entity/world space only: no GuiInventory reflection, pitch, or framing.
        draws = game.record(entity, identity(), 0.0, pitch=0.0, lamps='later').draws
        variants.append({'label': variant['label'],
                         'faces': [face(draw) for draw in draws]})
    return {'format': 1, 'variants': variants}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jar', help='client.jar; found automatically if omitted')
    ap.add_argument('--cache', help='directory holding intermediary.tiny and barn.tiny')
    ap.add_argument('--out', default=os.path.join(REPO_ROOT, 'assets', 'viewer', 'creeper.json'))
    args = ap.parse_args()
    try:
        cache = args.cache or find_cache().path
        jar_path = args.jar or find_jar().path
    except Missing as err:
        raise SystemExit('error: %s' % err)

    result = export_creeper(jar_path, cache)
    parent = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(parent, exist_ok=True)
    with io.open(args.out, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(result, fh, ensure_ascii=True, separators=(',', ':'), sort_keys=False)
        fh.write('\n')


if __name__ == '__main__':
    main()
