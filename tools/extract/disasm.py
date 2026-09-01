"""Bytecode disassembly + a tiny abstract interpreter for static initialisers."""
import struct

# operand byte counts for each opcode (None = variable length, handled inline)
LEN = {}
for op in list(range(0x00, 0x10)) + list(range(0x1a, 0x36)) + list(range(0x3b, 0x84)) + \
         list(range(0x85, 0x99)) + list(range(0xac, 0xb2)) + [0xbe, 0xbf, 0xc2, 0xc3]:
    LEN[op] = 0
for op in [0x10, 0x12, 0x15, 0x16, 0x17, 0x18, 0x19, 0x36, 0x37, 0x38, 0x39, 0x3a, 0xa9, 0xbc]:
    LEN[op] = 1
for op in [0x11, 0x13, 0x14, 0x84, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xbb, 0xbd,
           0xc0, 0xc1, 0xc6, 0xc7] + list(range(0x99, 0xa9)):
    LEN[op] = 2
LEN[0xc5] = 3
for op in [0xb9, 0xba, 0xc8, 0xc9]:
    LEN[op] = 4

ICONST = {0x02: -1, 0x03: 0, 0x04: 1, 0x05: 2, 0x06: 3, 0x07: 4, 0x08: 5}
FCONST = {0x0b: 0.0, 0x0c: 1.0, 0x0d: 2.0}


def disassemble(code):
    """Yield (pc, opcode, operand_bytes)."""
    i = 0; n = len(code)
    while i < n:
        pc = i; op = code[i]; i += 1
        if op == 0xc4:                                   # wide
            sub = code[i]
            width = 4 if sub == 0x84 else 2
            yield pc, op, code[i:i + 1 + width]; i += 1 + width; continue
        if op in (0xaa, 0xab):                           # table/lookupswitch
            pad = (4 - (i % 4)) % 4; i += pad
            default = struct.unpack_from('>i', code, i)[0]; i += 4
            if op == 0xaa:
                lo = struct.unpack_from('>i', code, i)[0]; i += 4
                hi = struct.unpack_from('>i', code, i)[0]; i += 4
                i += 4 * (hi - lo + 1)
            else:
                npairs = struct.unpack_from('>i', code, i)[0]; i += 4
                i += 8 * npairs
            yield pc, op, b''; continue
        ln = LEN.get(op)
        if ln is None:
            raise ValueError('unknown opcode 0x%02x at %d' % (op, pc))
        yield pc, op, code[i:i + ln]; i += ln


def u2(b, off=0):
    return struct.unpack_from('>H', b, off)[0]


def trace_clinit(cf):
    """Walk <clinit>, returning a list of constructed-object records.

    Each record: {'ctor': class, 'args': [...], 'calls': [(method_name, [args])],
                  'field': static field the result was stored into}
    Chained builder calls (setHardness().setName() ...) are attributed to the
    object most recently created, which is how Block/Item clinits are written.
    """
    m = cf.method('<clinit>')
    if m is None: return []
    code = cf.code_of(m)
    records = []; cur = None; pending = []
    for pc, op, operand in disassemble(code):
        if op == 0xbb:                                    # new
            if cur is not None: records.append(cur)
            cur = {'ctor': cf.cls_name(u2(operand)), 'args': None, 'calls': [], 'field': None}
            pending = []
        elif op in ICONST:   pending.append(ICONST[op])
        elif op in FCONST:   pending.append(FCONST[op])
        elif op == 0x10:     pending.append(struct.unpack_from('>b', operand)[0])   # bipush
        elif op == 0x11:     pending.append(struct.unpack_from('>h', operand)[0])   # sipush
        elif op in (0x12, 0x13):
            idx = operand[0] if op == 0x12 else u2(operand)
            pending.append(cf.const(idx))
        elif op == 0x14:     pending.append(cf.const(u2(operand)))                  # ldc2_w
        elif op == 0xb2:                                                            # getstatic
            owner, name, desc = cf.ref(u2(operand))
            pending.append({'ref': '%s.%s' % (owner, name), 'desc': desc})
        elif op == 0xb7:                                                            # invokespecial
            owner, name, desc = cf.ref(u2(operand))
            if name == '<init>' and cur is not None and cur['args'] is None:
                cur['args'] = pending
            pending = []
        elif op in (0xb6, 0xb8, 0xb9):                                              # invoke*
            owner, name, desc = cf.ref(u2(operand))
            if cur is not None:
                cur['calls'].append((name, desc, pending))
            pending = []
        elif op == 0xb3:                                                            # putstatic
            owner, name, desc = cf.ref(u2(operand))
            if cur is not None:
                cur['field'] = name; cur['field_desc'] = desc
                records.append(cur); cur = None
            pending = []
        elif op in (0x59, 0x5a, 0x5b, 0x5c, 0x5d, 0x5e):                            # dup*
            pass
        elif op == 0x57 or op == 0x58:                                              # pop
            pending = []
    if cur is not None: records.append(cur)
    return records


class Arr(list):
    """Marker for a reconstructed Object[] literal."""


def trace_calls(cf, method_name='<clinit>', desc=None):
    """Walk a method, returning every invoke* as (owner, name, desc, args).

    Maintains a real operand stack so array literals (anewarray/dup/aastore)
    and `new X(...)` results are reconstructed as nested values.
    """
    m = cf.method(method_name, desc)
    if m is None: return []
    code = cf.code_of(m)
    if code is None: return []
    stack = []; out = []

    def pop(n):
        if n == 0: return []
        vals = stack[-n:] if len(stack) >= n else ([None] * (n - len(stack)) + stack[:])
        del stack[max(0, len(stack) - n):]
        return vals

    for pc, op, operand in disassemble(code):
        if op in ICONST:      stack.append(ICONST[op])
        elif op in FCONST:    stack.append(FCONST[op])
        elif op == 0x01:      stack.append(None)                                    # aconst_null
        elif op == 0x10:      stack.append(struct.unpack_from('>b', operand)[0])
        elif op == 0x11:      stack.append(struct.unpack_from('>h', operand)[0])
        elif op in (0x12, 0x13):
            stack.append(cf.const(operand[0] if op == 0x12 else u2(operand)))
        elif op == 0x14:      stack.append(cf.const(u2(operand)))
        elif op == 0xb2:                                                            # getstatic
            owner, name, d = cf.ref(u2(operand))
            stack.append({'ref': '%s.%s' % (owner, name), 'desc': d})
        elif op == 0xb3:      pop(1)                                                # putstatic
        elif op == 0xbb:      stack.append({'new': cf.cls_name(u2(operand))})       # new
        elif op in (0xbc, 0xbd):                                                    # newarray/anewarray
            n = pop(1)[0]
            stack.append(Arr([None] * (n if isinstance(n, int) and 0 <= n < 4096 else 0)))
        elif op == 0x53:                                                            # aastore
            arr, idx, val = pop(3)
            if isinstance(arr, Arr) and isinstance(idx, int) and 0 <= idx < len(arr):
                arr[idx] = val
        elif op == 0x59:                                                            # dup
            if stack: stack.append(stack[-1])
        elif op == 0x5a:                                                            # dup_x1
            if len(stack) >= 2: stack.insert(-2, stack[-1])
        elif op in (0x57, 0x58):  pop(1 if op == 0x57 else 2)
        elif op in (0xb6, 0xb7, 0xb8, 0xb9):                                        # invoke*
            owner, name, d = cf.ref(u2(operand))
            nargs = _arity(d); args = pop(nargs)
            recv = pop(1)[0] if op != 0xb8 else None
            if name == '<init>' and isinstance(recv, dict) and 'new' in recv:
                recv['args'] = args                    # visible through the dup'd reference
            out.append({'owner': owner, 'name': name, 'desc': d,
                        'args': args, 'recv': recv, 'pc': pc})
            if not d.endswith(')V'):
                if name == 'valueOf' and owner.startswith('java/lang/') and len(args) == 1:
                    stack.append(args[0])              # unwrap Character/Integer boxing
                else:
                    stack.append({'call': '%s.%s' % (owner, name), 'args': args, 'recv': recv})
        elif op == 0xc0:      pass                                                  # checkcast
        else:
            # any other opcode: conservatively clear what it would consume
            if 0x99 <= op <= 0xa8: pop(1)
    return out


def _arity(desc):
    """Count argument slots in a method descriptor (each arg = one stack value here)."""
    inner = desc[desc.index('(') + 1: desc.rindex(')')]
    n = 0; i = 0
    while i < len(inner):
        c = inner[i]
        if c == 'L':
            i = inner.index(';', i) + 1; n += 1
        elif c == '[':
            i += 1
            while i < len(inner) and inner[i] == '[': i += 1
            if inner[i] == 'L': i = inner.index(';', i) + 1
            else: i += 1
            n += 1
        else:
            i += 1; n += 1
    return n
