"""A small concrete JVM interpreter.

Enough of the JVM to *run* Beta 1.7.3's recipe registration code instead of
pattern-matching it.

CraftingManager writes about a third of the game's recipes out one call at a
time, which a straight-line stack simulation can read. It hands the rest to
seven generator classes that build them in loops over material tables:

    for(int var2 = 0; var2 < this.recipeItems[0].length; ++var2) {
        Object var3 = this.recipeItems[0][var2];
        for(int var4 = 0; var4 < this.recipeItems.length - 1; ++var4) {
            Item var5 = (Item)this.recipeItems[var4 + 1][var2];
            var1.addRecipe(new ItemStack(var5), this.recipePatterns[var4],
                           '#', Item.stick, 'X', var3);
        }
    }

Those arguments do not exist anywhere in the bytecode as constants -- they only
exist once the loops have run. So we run them.

What is modelled: locals, the operand stack, 32-bit int and float
arithmetic, double arithmetic, arrays, branches, instance fields, calls into
other game classes, and the few JDK calls game code makes (see _jdk). What
is not: class initialisers, exceptions, threads, most string methods, long
arithmetic.

Every value is one entry on the operand stack, where the JVM gives a long or
a double two slots. Those two are tagged instead (Wide, WideLong), which is
what the stack-shuffling instructions need: dup2 copies one double or two
floats, and only the tag says which.

Static fields of game classes stay *symbolic*. `Block.stone` evaluates to
Ref('uu', 'ba'), which is exactly what a recipe wants to know, so Block's
enormous <clinit> never has to run. The caller resolves Refs to ids afterwards.

Anything outside that is a hard error rather than a guess -- a wrong recipe is
worse than a missing one, and a silent one is worse than both.
"""
import math
import struct

from disasm import disassemble, params_of, u2


class Unsupported(Exception):
    """The bytecode did something this interpreter deliberately does not model."""


class Ref(object):
    """A static field of a game class, left unevaluated. `Block.stone`."""
    __slots__ = ('owner', 'name', 'desc')

    def __init__(self, owner, name, desc):
        self.owner = owner
        self.name = name
        self.desc = desc

    def __repr__(self):
        return 'Ref(%s.%s)' % (self.owner, self.name)


class ArrayRef(object):
    """An element of a symbolic static array. `Item.itemsList[35]`."""
    __slots__ = ('base', 'index')

    def __init__(self, base, index):
        self.base = base
        self.index = index

    def __repr__(self):
        return 'ArrayRef(%s.%s[%r])' % (self.base.owner, self.base.name, self.index)


class Obj(object):
    """An instance created by `new`.

    Fields are keyed by (declaring class, name), not by name alone: an
    obfuscated hierarchy reuses letters freely, so BlockStairs.a (the block it
    copies) and Block.a would otherwise be the same slot.
    """
    __slots__ = ('cls', 'fields')

    def __init__(self, cls):
        self.cls = cls
        self.fields = {}

    def __repr__(self):
        return 'Obj(%s)' % self.cls


class Stub(Obj):
    """An object with nothing behind it.

    Every method called on one returns the default of its type -- zero,
    false or null -- unless a hook answers it, and every field read does the
    same, unless something was stored there. It stands in for whatever the code under study needs
    to hold but never really asks anything of: the world an entity is built
    in, the Minecraft instance a renderer keeps a reference to.
    """


class Wide(float):
    """A double: one entry on this stack, where the JVM would use two slots."""


class WideLong(int):
    """A long, likewise."""


def widen(value, kind):
    """Tag a value of descriptor type `kind` ('D', 'J', or anything else)."""
    if kind == 'D' and isinstance(value, (int, float)) and not isinstance(value, Wide):
        return Wide(value)
    if kind == 'J' and isinstance(value, int) and not isinstance(value, WideLong):
        return WideLong(value)
    return value


# Boxing. valueOf hands back the raw value, so a boxed number is usually just
# the number; one made with `new` is an object holding it.
BOXES = ('java/lang/Byte', 'java/lang/Short', 'java/lang/Integer', 'java/lang/Long',
         'java/lang/Float', 'java/lang/Double', 'java/lang/Character', 'java/lang/Boolean')
BOXED = ('java/lang/Number', 'value')
UNBOX = ('byteValue', 'shortValue', 'intValue', 'longValue', 'floatValue', 'doubleValue',
         'charValue', 'booleanValue')


def unbox(value):
    if isinstance(value, Obj) and BOXED in value.fields:
        return value.fields[BOXED]
    return value


def slots(value):
    return 2 if isinstance(value, (Wide, WideLong)) else 1


class Arr(list):
    """A Java array. A plain list, tagged so arraylength can refuse a Ref."""


def i32(v):
    """Wrap to a signed 32-bit int, the way every Java int operation does."""
    v &= 0xFFFFFFFF
    return v - 0x100000000 if v & 0x80000000 else v


def f32(v):
    """Round to the nearest 32-bit float, the way every Java float op does.

    Block.setHardness raises a block's blast resistance to hardness * 5 in
    float arithmetic, so doing the multiply in Python's doubles would drift
    away from the number the game actually holds.
    """
    return struct.unpack('<f', struct.pack('<f', v))[0]


def arg_slots(desc):
    """Operand-stack entries a call's arguments occupy.

    One per argument. The JVM gives a long or a double two slots, but this
    stack holds every value as one Python object, so counting two popped an
    extra value and misaligned the rest: Vertex's constructor hands three
    doubles to Vec3D.createVector, and that underflowed.
    """
    return len(params_of(desc))


DEFAULTS = {'V': None, 'I': 0, 'Z': 0, 'B': 0, 'C': 0, 'S': 0,
            'J': 0, 'F': 0.0, 'D': 0.0}


def default_for(desc):
    ret = desc[desc.rindex(')') + 1:]
    return DEFAULTS.get(ret, None)


# Comparisons for the if<cond> / if_icmp<cond> families, keyed by opcode.
IFCOND = {0x99: lambda a: a == 0, 0x9a: lambda a: a != 0, 0x9b: lambda a: a < 0,
          0x9c: lambda a: a >= 0, 0x9d: lambda a: a > 0, 0x9e: lambda a: a <= 0}
ICMP = {0x9f: lambda a, b: a == b, 0xa0: lambda a, b: a != b,
        0xa1: lambda a, b: a < b, 0xa2: lambda a, b: a >= b,
        0xa3: lambda a, b: a > b, 0xa4: lambda a, b: a <= b}
# fadd/fsub/fmul/fdiv/frem, and the d-prefixed opcode of each is exactly one
# higher, so the double family reuses this table. Java answers infinity or NaN
# where Python raises, which is what `zero` covers.
FLOAT_OPS = {
    0x62: lambda a, b: a + b,
    0x66: lambda a, b: a - b,
    0x6a: lambda a, b: a * b,
    0x6e: lambda a, b: a / b if b else zero_div(a),
    0x72: lambda a, b: math.fmod(a, b) if b else float('nan'),
}


def zero_div(a):
    return float('nan') if a == 0 else math.copysign(float('inf'), a)


def trunc(v):
    """Java's float-to-int cast: toward zero, NaN to 0, saturating at the ends."""
    if v != v:
        return 0
    if v >= 2147483647.0:
        return 2147483647
    if v <= -2147483648.0:
        return -2147483648
    return int(v)


class JavaRandom(object):
    """java.util.Random: the 48-bit linear congruential generator, exactly."""

    MULTIPLIER = 0x5DEECE66D
    MASK = (1 << 48) - 1

    def __init__(self, seed):
        self.seed = (seed ^ self.MULTIPLIER) & self.MASK

    def next(self, bits):
        self.seed = (self.seed * self.MULTIPLIER + 0xB) & self.MASK
        return self.seed >> (48 - bits)

    def next_int(self, bound):
        if bound <= 0:
            raise Unsupported('Random.nextInt(%d)' % bound)
        if bound & -bound == bound:                  # a power of two
            return (bound * self.next(31)) >> 31
        while True:
            bits = self.next(31)
            value = bits % bound
            if bits - value + (bound - 1) < (1 << 31):
                return value

    def next_float(self):
        return self.next(24) / float(1 << 24)


# The java.lang.Math calls game code makes, by name; each takes one argument.
MATH = {'sin': math.sin, 'cos': math.cos, 'sqrt': math.sqrt, 'atan': math.atan,
        'abs': abs, 'floor': math.floor, 'ceil': math.ceil}


# The type each load family reads: iload, lload, fload, dload, aload.
LOAD_KIND = 'IJFDA'
# dup, dup_x1, dup_x2, dup2, dup2_x1, dup2_x2: (slots copied, slots they go under).
DUPS = {0x59: (1, 0), 0x5a: (1, 1), 0x5b: (1, 2), 0x5c: (2, 0), 0x5d: (2, 1), 0x5e: (2, 2)}

ICONST = {0x02: -1, 0x03: 0, 0x04: 1, 0x05: 2, 0x06: 3, 0x07: 4, 0x08: 5}
FCONST = {0x0b: 0.0, 0x0c: 1.0, 0x0d: 2.0}
LCONST = {0x09: WideLong(0), 0x0a: WideLong(1)}
DCONST = {0x0e: Wide(0.0), 0x0f: Wide(1.0)}


class Interp(object):
    """Runs methods of the loaded game classes.

    loader(name) -> ClassFile or None. Hooks intercept a call by (owner, name,
    desc); a hook returning NOTHING means "handled, no value". field_hook
    resolves getfield on a symbolic Ref, which is how `Block.cloth.blockID`
    becomes the number 35 without running Block's initialiser.
    """

    NOTHING = object()

    def __init__(self, loader, budget=2000000):
        self.loader = loader
        self.budget = budget
        self.hooks = {}
        self.field_hook = None
        self.statics = {}
        self._classes = {}
        self._owners = {}
        self._refs = {}
        self._tried_clinit = set()

    # -- class loading -----------------------------------------------------
    def cls(self, name):
        if name not in self._classes:
            self._classes[name] = self.loader(name)
        return self._classes[name]

    def _find(self, owner, name, desc):
        """Resolve a method against the class and its superclasses."""
        seen = set()
        cur = owner
        while cur and cur not in seen:
            seen.add(cur)
            cf = self.cls(cur)
            if cf is None:
                return None, None
            m = cf.method(name, desc)
            if m is not None:
                return cf, m
            cur = cf.super
        return None, None

    # -- calling -----------------------------------------------------------
    def call(self, owner, name, desc, recv, args, static=False, virtual=False):
        """Run a method. `virtual` dispatches on the receiver's actual class.

        The constant pool names the class the *caller* saw, so Block's
        `getBlockTextureFromSideAndMetadata` calling `this.getBlockTextureFromSide`
        reads as a call on Block. Resolving there would hand every block the
        base implementation and quietly lose the furnace its front face.
        """
        hook = self.hooks.get((owner, name, desc))
        if virtual and isinstance(recv, Obj):
            hook = self.hooks.get((recv.cls, name, desc), hook)
            owner = recv.cls
        if hook is not None:
            return hook(self, recv, args)
        if isinstance(recv, Stub) and not static:
            return default_for(desc)
        if owner.startswith('java/') or owner.startswith('['):
            return self._jdk(owner, name, desc, recv, args)
        cf, m = self._find(owner, name, desc)
        if m is None:
            # A game method we cannot see (an interface, or a class the jar
            # does not hold). Returning a default would invent a recipe.
            raise Unsupported('no method %s.%s%s' % (owner, name, desc))
        code = cf.code_of(m)
        if code is None:
            raise Unsupported('abstract/native %s.%s%s' % (owner, name, desc))
        local = {}
        slot = 0
        if not static:
            local[0] = recv
            slot = 1
        for kind, val in zip(params_of(desc), args):
            local[slot] = widen(val, kind)
            slot += 2 if kind in ('J', 'D') else 1
        return self.run(cf, m, code, local)

    @staticmethod
    def _text(v):
        if isinstance(v, str):
            return v
        if v is None:
            return 'null'
        if isinstance(v, bool):
            return 'true' if v else 'false'
        if isinstance(v, (int, float)):
            return repr(v) if isinstance(v, float) else str(v)
        raise Unsupported('cannot stringify %r' % (v,))

    def _jdk(self, owner, name, desc, recv, args):
        """The handful of JDK calls this code actually makes."""
        if owner == 'java/lang/StringBuilder':
            # Real concatenation: getItemNameIS builds a stack's translation
            # key this way ("tile.cloth" + "." + "magenta"), and the answer is
            # the whole point of running it.
            key = (owner, 'value')
            if name == '<init>':
                if isinstance(recv, Obj):
                    recv.fields[key] = args[0] if args and isinstance(args[0], str) else ''
                return self.NOTHING
            if name == 'append':
                if isinstance(recv, Obj):
                    recv.fields[key] = recv.fields.get(key, '') + self._text(args[0])
                return recv
            if name == 'toString':
                return recv.fields.get(key, '') if isinstance(recv, Obj) else ''
        if owner == 'java/util/Random':
            # ModelGhast seeds one to pick its nine tentacles' lengths, so the
            # sequence has to be Java's, bit for bit. Block's initialiser
            # makes an unseeded one it never draws from; drawing from one
            # would be a different answer every run, and is refused.
            key = (owner, 'state')
            if name == '<init>':
                if desc == '(J)V' and isinstance(recv, Obj):
                    recv.fields[key] = JavaRandom(args[0])
                return self.NOTHING
            if name == 'setSeed' and desc == '(J)V' and isinstance(recv, Obj):
                recv.fields[key] = JavaRandom(args[0])
                return self.NOTHING
            rand = recv.fields.get(key) if isinstance(recv, Obj) else None
            if rand is not None and name == 'nextInt' and desc == '(I)I':
                return rand.next_int(args[0])
            if rand is not None and name == 'nextFloat' and desc == '()F':
                return rand.next_float()
            raise Unsupported('JDK call %s.%s%s' % (owner, name, desc))
        if owner == 'java/lang/Math' and name in MATH and len(args) == 1:
            value = MATH[name](args[0])              # ModelSquid places its tentacles
            return f32(value) if desc.endswith(')F') else value
        if owner in BOXES and name == '<init>' and len(args) == 1 and isinstance(recv, Obj):
            recv.fields[BOXED] = args[0]             # new Byte(b), new Integer(i)
            return self.NOTHING
        if name == '<init>':
            return self.NOTHING                      # new ArrayList(), new HashMap()
        if name == 'valueOf' and len(args) == 1:
            return args[0]                           # Character/Integer boxing
        if name in UNBOX and not args:
            return unbox(recv)
        if owner == 'java/util/Collections' and name == 'sort':
            return self.NOTHING                      # recipe ordering, not content
        if owner in ('java/util/List', 'java/util/ArrayList', 'java/util/Map',
                     'java/util/HashMap'):
            return default_for(desc)                 # collection plumbing
        if owner == 'java/io/PrintStream':
            return self.NOTHING
        if owner == 'java/lang/String':
            if name == 'length' and isinstance(recv, str):
                return len(recv)
            if name == 'charAt' and isinstance(recv, str):
                return ord(recv[args[0]])
            if name == 'equals':
                return 1 if recv == args[0] else 0
            if name == 'valueOf':
                return self._text(args[0])
            if name == 'concat':
                return self._text(recv) + self._text(args[0])
        raise Unsupported('JDK call %s.%s%s' % (owner, name, desc))

    # -- execution ---------------------------------------------------------
    def run(self, cf, m, code, local):
        ins = list(disassemble(code))
        index = {pc: n for n, (pc, _, _) in enumerate(ins)}
        stack = []
        n = 0
        steps = 0

        def span(end, n):
            """Where the entries holding the top `n` JVM slots below `end` start."""
            k = end
            while n > 0:
                k -= 1
                n -= slots(stack[k])
            if n < 0:
                raise Unsupported('stack shuffle splits a long or double in %s.%s'
                                  % (cf.this, m['name']))
            return k

        def pop(k=1):
            if k == 0:
                return []
            if len(stack) < k:
                raise Unsupported('stack underflow in %s.%s' % (cf.this, m['name']))
            vals = stack[-k:]
            del stack[-k:]
            return vals

        while n < len(ins):
            steps += 1
            if steps > self.budget:
                raise Unsupported('step budget exhausted in %s.%s -- infinite loop?'
                                  % (cf.this, m['name']))
            pc, op, operand = ins[n]
            n += 1

            if op == 0x00:                                          # nop
                pass
            elif op == 0x01:  stack.append(None)                    # aconst_null
            elif op in ICONST: stack.append(ICONST[op])
            elif op in LCONST: stack.append(LCONST[op])
            elif op in FCONST: stack.append(FCONST[op])
            elif op in DCONST: stack.append(DCONST[op])
            elif op == 0x10:  stack.append(struct.unpack_from('>b', operand)[0])
            elif op == 0x11:  stack.append(struct.unpack_from('>h', operand)[0])
            elif op in (0x12, 0x13):
                stack.append(cf.const(operand[0] if op == 0x12 else u2(operand)))
            elif op == 0x14:                                         # ldc2_w
                stack.append(widen(cf.const(u2(operand)),
                                   'D' if cf.cp[u2(operand)][0] == 'double' else 'J'))

            # loads
            elif op in (0x15, 0x16, 0x17, 0x18, 0x19):
                stack.append(widen(local.get(operand[0]), LOAD_KIND[op - 0x15]))
            elif 0x1a <= op <= 0x2d:
                stack.append(widen(local.get((op - 0x1a) % 4), LOAD_KIND[(op - 0x1a) // 4]))
            # array load
            elif 0x2e <= op <= 0x35:
                arr, idx = pop(2)
                stack.append(widen(self._aload(arr, idx), 'J' if op == 0x2f else
                                   'D' if op == 0x31 else ''))

            # stores
            elif op in (0x36, 0x37, 0x38, 0x39, 0x3a):
                local[operand[0]] = pop(1)[0]
            elif 0x3b <= op <= 0x4e:
                local[(op - 0x3b) % 4] = pop(1)[0]
            # array store
            elif 0x4f <= op <= 0x56:
                arr, idx, val = pop(3)
                if not isinstance(arr, list):
                    raise Unsupported('store into non-array %r' % (arr,))
                if not isinstance(idx, int) or not 0 <= idx < len(arr):
                    raise Unsupported('array store out of range: %r' % (idx,))
                arr[idx] = val

            # stack shuffling
            elif op in (0x57, 0x58):                                 # pop, pop2
                del stack[span(len(stack), op - 0x56):]
            elif op in DUPS:
                n_copy, n_under = DUPS[op]
                top = span(len(stack), n_copy)
                under = span(top, n_under)
                stack[under:under] = stack[top:]
            elif op == 0x5f:                                         # swap
                stack[-1], stack[-2] = stack[-2], stack[-1]

            # int arithmetic
            elif op == 0x60:  a, b = pop(2); stack.append(i32(a + b))
            elif op == 0x64:  a, b = pop(2); stack.append(i32(a - b))
            elif op == 0x68:  a, b = pop(2); stack.append(i32(a * b))
            elif op == 0x6c:
                a, b = pop(2)
                stack.append(i32(abs(a) // abs(b) * (1 if (a < 0) == (b < 0) else -1)))
            elif op == 0x70:
                a, b = pop(2)
                stack.append(i32(a - (abs(a) // abs(b) * (1 if (a < 0) == (b < 0) else -1)) * b))
            elif op == 0x74:  stack.append(i32(-pop(1)[0]))
            elif op == 0x78:  a, b = pop(2); stack.append(i32(a << (b & 31)))
            elif op == 0x7a:  a, b = pop(2); stack.append(i32(a >> (b & 31)))
            elif op == 0x7c:
                a, b = pop(2)
                stack.append(i32((a & 0xFFFFFFFF) >> (b & 31)))
            elif op == 0x7e:  a, b = pop(2); stack.append(i32(a & b))
            elif op == 0x80:  a, b = pop(2); stack.append(i32(a | b))
            elif op == 0x82:  a, b = pop(2); stack.append(i32(a ^ b))
            # float and double arithmetic
            elif op in FLOAT_OPS:
                a, b = pop(2)
                stack.append(f32(FLOAT_OPS[op](a, b)))
            elif op - 1 in FLOAT_OPS:
                a, b = pop(2)
                stack.append(Wide(FLOAT_OPS[op - 1](a, b)))
            elif op == 0x76:  stack.append(f32(-pop(1)[0]))          # fneg
            elif op == 0x77:  stack.append(Wide(-pop(1)[0]))         # dneg
            elif op in (0x86, 0x90):                                 # i2f, d2f
                stack.append(f32(pop(1)[0]))
            elif op in (0x87, 0x8d):                                 # i2d, f2d
                stack.append(Wide(pop(1)[0]))
            elif op in (0x8b, 0x8e):                                 # f2i, d2i
                stack.append(trunc(pop(1)[0]))
            elif op in (0x95, 0x96, 0x97, 0x98):                     # f/dcmpl, f/dcmpg
                a, b = pop(2)
                if a != a or b != b:                                 # NaN
                    stack.append(-1 if op in (0x95, 0x97) else 1)
                else:
                    stack.append((a > b) - (a < b))

            elif op == 0x84:                                         # iinc
                idx = operand[0]
                local[idx] = i32(local.get(idx, 0) + struct.unpack_from('>b', operand, 1)[0])
            elif op == 0x91:                                         # i2b
                v = pop(1)[0] & 0xFF
                stack.append(v - 0x100 if v & 0x80 else v)
            elif op in (0x92, 0x93):                                 # i2c, i2s
                v = pop(1)[0] & 0xFFFF
                stack.append(v if op == 0x92 else (v - 0x10000 if v & 0x8000 else v))

            # branches
            elif op in IFCOND:
                if IFCOND[op](pop(1)[0]):
                    n = index[pc + struct.unpack_from('>h', operand)[0]]
            elif op in ICMP:
                a, b = pop(2)
                if ICMP[op](a, b):
                    n = index[pc + struct.unpack_from('>h', operand)[0]]
            elif op in (0xa5, 0xa6):                                 # if_acmpeq/ne
                a, b = pop(2)
                same = a is b
                if same if op == 0xa5 else not same:
                    n = index[pc + struct.unpack_from('>h', operand)[0]]
            elif op in (0xc6, 0xc7):                                 # ifnull/ifnonnull
                v = pop(1)[0]
                if (v is None) if op == 0xc6 else (v is not None):
                    n = index[pc + struct.unpack_from('>h', operand)[0]]
            elif op == 0xa7:
                n = index[pc + struct.unpack_from('>h', operand)[0]]
            elif op == 0xc8:
                n = index[pc + struct.unpack_from('>i', operand)[0]]

            # returns
            elif op == 0xb1:  return None
            elif op in (0xac, 0xad, 0xae, 0xaf, 0xb0):
                return pop(1)[0]

            # fields
            elif op == 0xb2:                                         # getstatic
                owner, name, desc = cf.ref(u2(operand))
                stack.append(widen(self._getstatic(owner, name, desc), desc))
            elif op == 0xb3:                                         # putstatic
                owner, name, desc = cf.ref(u2(operand))
                self.statics[(self._declares(owner, name), name)] = pop(1)[0]
            elif op == 0xb4:                                         # getfield
                owner, name, desc = cf.ref(u2(operand))
                obj = pop(1)[0]
                stack.append(widen(self._getfield(obj, owner, name, desc), desc))
            elif op == 0xb5:                                         # putfield
                owner, name, desc = cf.ref(u2(operand))
                obj, val = pop(2)
                if not isinstance(obj, Obj):
                    raise Unsupported('putfield on %r' % (obj,))
                obj.fields[(self._declares(owner, name), name)] = val

            # objects and calls
            elif op == 0xbb:                                         # new
                stack.append(Obj(cf.cls_name(u2(operand))))
            elif op == 0xbc:                                         # newarray
                stack.append(Arr([0] * self._len(pop(1)[0])))
            elif op == 0xbd:                                         # anewarray
                stack.append(Arr([None] * self._len(pop(1)[0])))
            elif op == 0xbe:                                         # arraylength
                arr = pop(1)[0]
                if not isinstance(arr, list):
                    raise Unsupported('arraylength of %r' % (arr,))
                stack.append(len(arr))
            elif op == 0xc0:  pass                                   # checkcast
            elif op == 0xc1:                                         # instanceof
                stack.append(self._instanceof(pop(1)[0], cf.cls_name(u2(operand))))
            elif op in (0xb6, 0xb7, 0xb8, 0xb9):
                owner, name, desc = cf.ref(u2(operand))
                args = pop(arg_slots(desc))
                recv = pop(1)[0] if op != 0xb8 else self.NOTHING
                res = self.call(owner, name, desc, recv, args,
                                static=(op == 0xb8), virtual=op in (0xb6, 0xb9))
                if not desc.endswith(')V') and res is not self.NOTHING:
                    stack.append(widen(res, desc[desc.rindex(')') + 1:]))
            else:
                raise Unsupported('opcode 0x%02x at %d in %s.%s'
                                  % (op, pc, cf.this, m['name']))
        return None

    # -- helpers -----------------------------------------------------------
    # Constant tables worth evaluating: a class initialiser that only fills in
    # String[] or int[] literals is safe to run. Block's and Item's are not --
    # they build the whole game -- and their arrays are [LBlock; / [LItem;, so
    # this rule leaves them symbolic, which is what the callers want anyway.
    CONST_TABLES = ('[Ljava/lang/String;', '[I', '[[I')

    def _declares(self, owner, name):
        """The class a field is really declared on.

        A constant pool names the class the code said, not the one holding the
        field: BlockContainer's constructor writes `isBlockContainer[id]`,
        which is Block's array. Stopping at the named class would hand back a
        symbolic Ref for a field we are already holding a value for, and would
        let two classes in one hierarchy share an instance field slot.
        """
        hit = self._owners.get((owner, name))
        if hit is not None:
            return hit
        hit, seen, cur = owner, set(), owner
        while cur and cur not in seen:
            seen.add(cur)
            cf = self.cls(cur)
            if cf is None:
                break
            if any(f['name'] == name for f in cf.fields):
                hit = cur
                break
            cur = cf.super
        self._owners[(owner, name)] = hit
        return hit

    def _getstatic(self, owner, name, desc):
        owner = self._declares(owner, name)
        key = (owner, name)
        if key in self.statics:
            return self.statics[key]
        if desc in self.CONST_TABLES and owner not in self._tried_clinit:
            self._tried_clinit.add(owner)
            cf = self.cls(owner)
            if cf is not None and cf.method('<clinit>') is not None:
                sub = Interp(self.loader, budget=100000)
                sub.loader = self.loader
                sub.field_hook = self.field_hook
                sub._refs = self._refs
                sub._tried_clinit = self._tried_clinit
                try:
                    sub.call(owner, '<clinit>', '()V', None, [], static=True)
                except Exception:
                    pass                     # not a constant table after all
                else:
                    for k, v in sub.statics.items():
                        self.statics.setdefault(k, v)
                if key in self.statics:
                    return self.statics[key]
        if key not in self._refs:
            # One static field is one value however often it is read, so the
            # symbol standing in for it has to be the same object every time:
            # BlockFluid picks its texture with `material == Material.lava`,
            # and two freshly built Refs are never the same object, which gave
            # lava the water tile.
            self._refs[key] = Ref(owner, name, desc)
        return self._refs[key]

    def _instanceof(self, value, target):
        """`value instanceof target`, for the values this interpreter makes.

        null is an instance of nothing. An object answers by its class, its
        superclasses and every interface they declare. Anything else -- a
        symbolic Ref, a string -- keeps the old answer of yes, since nothing
        here can tell what class a Ref would have held.
        """
        if value is None:
            return 0
        if not isinstance(value, Obj):
            return 1
        todo, seen = [value.cls], set()
        while todo:
            cur = todo.pop()
            if cur == target:
                return 1
            if cur in seen or cur.startswith('java/'):
                continue
            seen.add(cur)
            cf = self.cls(cur)
            if cf is not None:
                todo.extend(c for c in [cf.super] + cf.interfaces if c)
        return 0

    @staticmethod
    def _len(v):
        if not isinstance(v, int) or not 0 <= v < 65536:
            raise Unsupported('array length %r' % (v,))
        return v

    @staticmethod
    def _aload(arr, idx):
        if isinstance(arr, Ref):
            return ArrayRef(arr, idx)          # Item.itemsList[n], left symbolic
        if not isinstance(arr, list):
            raise Unsupported('array load from %r' % (arr,))
        if not isinstance(idx, int) or not 0 <= idx < len(arr):
            raise Unsupported('array index %r out of range' % (idx,))
        return arr[idx]

    def _getfield(self, obj, owner, name, desc):
        if isinstance(obj, Obj):
            key = (self._declares(owner, name), name)
            return obj.fields.get(key, default_for('()' + desc))
        if isinstance(obj, (Ref, ArrayRef)) and self.field_hook is not None:
            v = self.field_hook(obj, name, desc)
            if v is not self.NOTHING:
                return v
        raise Unsupported('getfield %s.%s on %r' % (owner, name, obj))
