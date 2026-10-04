#!/usr/bin/env python3
"""Export the placed block meshes used by the Three.js scene."""
import argparse
import io
import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from disasm import disassemble
from interp import Interp, Obj, Stub
from mappings import load as load_mappings
from models import Game
from paths import Missing, find_cache, find_jar
from softgl import GL


MODELS = ((1, 0), (3, 0), (6, 0), (76, 3), (33, 4), (33, 5), (69, 13),
          (17, 0), (29, 3), (35, 5), (76, 5), (69, 9), (69, 6))
OPAQUE = {(1, 0), (3, 0), (33, 4), (33, 5), (17, 0), (29, 3), (35, 5)}


def _normal(corners):
    a, b, c = corners[:3]
    u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    v = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2],
         u[0] * v[1] - u[1] * v[0])
    length = math.sqrt(sum(x * x for x in n)) or 1.0
    return [x / length for x in n]


def _clean(value):
    if isinstance(value, float):
        if abs(value) < 1e-14:
            return 0
        return round(value, 15)
    return value


def _select_tableswitch(cf, method, key):
    """Resolve the fixed metadata's switch branches in an in-memory copy.

    Interp does not implement tableswitch. Decode instruction boundaries so
    an operand byte equal to 0xaa cannot be mistaken for a switch opcode.
    No jar or source file is changed.
    """
    code = cf.code_of(method)
    patched = bytearray(code)
    for pc, op, _operand in disassemble(code):
        if op != 0xaa:
            continue
        at = (pc + 4) & ~3
        default, low, high = struct.unpack('>iii', code[at:at + 12])
        offsets = struct.unpack('>%di' % (high - low + 1),
                                code[at + 12:at + 16 + 4 * (high - low)])
        offset = offsets[key - low] if low <= key <= high else default
        target = pc + offset
        end = at + 12 + 4 * len(offsets)
        # Pop the switch operand, then jump from the following instruction.
        patched[pc:end] = bytes((0x57, 0xa7)) + struct.pack('>h', target - (pc + 1)) + \
            bytes(end - pc - 4)
    old = method['attrs']['Code']
    method['attrs']['Code'] = old[:8] + bytes(patched) + old[8 + len(code):]
    return old


def export(jar_path, cache):
    mp = load_mappings(os.path.join(cache, 'intermediary.tiny'),
                       os.path.join(cache, 'barn.tiny'))
    game = Game(jar_path, mp)
    it = game.interp
    block, view = game.appearance.block_cls, game.appearance.world_cls

    # RenderBlocks is deliberately located by its public shape, rather than an
    # unstable community name: it has a BlockView constructor and the placed
    # block dispatch method described at RenderBlocks.java:92.
    render = next(c for c in game.jar.classes() if game.jar.cls(c)
                  and game.jar.cls(c).method('<init>', '(L%s;)V' % view)
                  and any(m['desc'] == '(L%s;III)Z' % block for m in game.jar.cls(c).methods))
    placed = '(L%s;III)Z' % block
    # The interpreter intentionally has no tableswitch (the dispatch method's
    # only unsupported opcode), so call the exact branch selected there.
    branch_names = {0: 'method_76', 1: 'method_73', 2: 'method_62', 12: 'method_68'}
    branches = {kind: next(m['name'] for m in game.jar.cls(render).methods
                           if m['desc'] == placed
                           and game.mp.member(render, m['name'], m['desc']) == named)
                for kind, named in branch_names.items()}
    piston = next(m['name'] for m in game.jar.cls(render).methods
                  if m['desc'] == '(L%s;IIIZ)Z' % block)

    state = {'id': 0, 'meta': 0}
    world = Stub(view)
    nothing = Interp.NOTHING
    answers = {
        '(III)I': lambda a: state['id'] if tuple(a) == (0, 0, 0) else 0,
        '(IIII)F': lambda _a: 1.0,
        '(III)F': lambda _a: 1.0,
    }
    # Disambiguate the two (III)I methods by their mapped names.
    for m in game.jar.cls(view).methods:
        key = (view, m['name'], m['desc'])
        named = game.mp.member(view, m['name'], m['desc'])
        if named == 'getBlockId':
            it.hooks[key] = lambda _i, _r, a: state['id'] if tuple(a) == (0, 0, 0) else 0
        elif named == 'method_1778':
            it.hooks[key] = lambda _i, _r, a: state['meta'] if tuple(a) == (0, 0, 0) else 0
        elif m['desc'] in answers:
            it.hooks[key] = lambda _i, _r, a, fn=answers[m['desc']]: fn(a)
        elif m['desc'] == '(III)Z':
            it.hooks[key] = lambda _i, _r, _a: False
        elif m['desc'].startswith('(III)L') or m['desc'].startswith('()L'):
            result = m['desc'].split(')L', 1)[1][:-1]
            it.hooks[key] = lambda _i, _r, _a, cls=result: Stub(cls)

    renderer = Obj(render)
    it.call(render, '<init>', '(L%s;)V' % view, renderer, [world])
    tess = game.gl_names['tessellator']
    start, draw = game.gl_names['startQuads'], game.gl_names['draw']
    tess_obj = Stub(tess)
    result = {'format': 1, 'models': {}}
    for ident, meta in MODELS:
        state.update(id=ident, meta=meta)
        gl = GL(game.lists)
        gl.install(it, game.gl_names)
        gl.bind(gl.texture_id('/terrain.png'))

        # Tessellator colours are normally copied into its native vertex
        # buffer. softgl intercepts vertices earlier, so mirror those setters.
        def tess_colour(_i, _r, values, target=gl):
            if target.pending:
                target.draw()
            target.rgba = tuple(values) + (1.0,)
            return nothing

        for m in game.jar.cls(tess).methods:
            named = game.mp.member(tess, m['name'], m['desc'])
            if named == 'color' and m['desc'] == '(FFF)V':
                it.hooks[(tess, m['name'], m['desc'])] = tess_colour

        it.call(tess, start, '()V', tess_obj, [])
        block_obj = game.appearance.blocks[ident]
        kind = game.appearance.render_type(ident)
        if kind == 16:
            method = game.jar.cls(render).method(piston, '(L%s;IIIZ)Z' % block)
            old_code = _select_tableswitch(game.jar.cls(render), method, meta & 7)
            try:
                it.call(render, piston, '(L%s;IIIZ)Z' % block, renderer,
                        [block_obj, 0, 0, 0, False])
            finally:
                method['attrs']['Code'] = old_code
        else:
            it.call(render, branches[kind], placed, renderer, [block_obj, 0, 0, 0])
        it.call(tess, draw, '()V', tess_obj, [])
        faces = []
        for face in gl.draws:
            corners = [[_clean(x) for x in corner] for corner in face.corners]
            faces.append({
                'corners': corners, 'normal': [_clean(x) for x in _normal(corners)],
                'rgba': [_clean(x) for x in face.rgba], 'lit': face.lit,
                'texture': (face.texture or '').lstrip('/'), 'textured': face.textured,
                'blend': face.blend, 'blend_func': list(face.blend_func),
                'alpha_test': face.alpha_test, 'depth_test': face.depth_test,
                'depth_mask': face.depth_mask, 'depth_func': face.depth_func,
            })
        result['models']['%d:%d' % (ident, meta)] = {
            'opaque': (ident, meta) in OPAQUE, 'faces': faces}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jar', help='client.jar; found automatically if omitted')
    parser.add_argument('--cache', help='directory holding intermediary.tiny and barn.tiny')
    parser.add_argument('--out', default='assets/viewer/block-models.json')
    args = parser.parse_args()
    try:
        cache = args.cache or find_cache().path
        jar_path = args.jar or find_jar().path
    except Missing as err:
        raise SystemExit('error: %s' % err)
    data = export(jar_path, cache)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with io.open(args.out, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(data, fh, ensure_ascii=True, separators=(',', ':'), sort_keys=False)
        fh.write('\n')


if __name__ == '__main__':
    main()
