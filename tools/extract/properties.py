"""What the game says an item or a mob is, beyond its name and picture.

For items: how many fit in a slot, how many uses a tool or armour piece has,
how hard it hits, and how much health eating it restores. For mobs: the health
one starts with. Pages used to type these by hand, where nothing could check
them.

Items are asked, not read. appearance.py leaves the game's item registry
behind as live objects, built by running Item's static initialiser, so every
constructor, every EnumToolMaterial lookup and every builder call has already
happened the way it does in the game. Each object is then asked what the game
asks it:

    getMaxCount()            the stack size
    getMaxDamage()           the durability; 0 means the item takes no wear
    getDamageVsEntity(e)     what a hit with it deals, where the item's class
                             overrides Item's flat 1 -- swords and tools
    use(stack, world, p)     run once on a stand-in player, recording what it
                             passes to heal(): what eating the item restores

Method identification
---------------------
barn.tiny names getMaxCount, getMaxDamage and use. The other two are found by
what they are:

    getDamageVsEntity   Item's only method taking an Entity and returning int
    heal                LivingEntity's (I)V that adds its argument to health,
                        where its other (I)V, damageEntity, subtracts it

Mob health is read rather than run. An entity constructor wants a live World,
a Random and a DataWatcher, and none of them bear on health, which in Beta is
set by plain assignments in the constructor chain: 10 in LivingEntity, 20 in
MobEntity, `health *= 10` in the giant. So the chain is walked from
LivingEntity down to the mob's own class and those assignments are replayed.
Anything else that touches health -- an assignment of a computed value, or a
call to a method that writes it -- leaves the mob with no figure at all. That
is the slime, whose constructor rolls a size and calls setSlimeSize, which
sets health to the size squared: 1, 4 or 16, and no one number is true.
"""
from disasm import disassemble, u2
from interp import Interp, Obj, Unsupported


def _one(cands, what):
    if len(cands) != 1:
        raise Unsupported('expected one %s, found %r' % (what, cands))
    return cands[0]


def _named(mp, cf, owner, name):
    return [(m['name'], m['desc']) for m in cf.methods
            if mp.member(owner, m['name'], m['desc']) == name]


def _field(mp, cf, owner, name):
    return _one([f['name'] for f in cf.fields
                 if mp.member(owner, f['name'], f['desc']) == name], '%s.%s' % (owner, name))


def _chain(jar, cls, stop):
    """cls and its superclasses up to and including `stop`, subclass first."""
    out, cur = [], cls
    while cur and len(out) < 12:
        out.append(cur)
        if cur == stop:
            return out
        cf = jar.cls(cur)
        cur = cf.super if cf else None
    return None


class Properties(object):
    """The numbers a slot, a hit or a meal reveal about each item."""

    def __init__(self, game, jar, mp):
        self.game = game
        self.jar = jar
        item = game.item_cls
        icf = jar.cls(item)
        self.item = item

        self.m_count = _one(_named(mp, icf, item, 'getMaxCount'), 'Item.getMaxCount')
        self.m_damage = _one(_named(mp, icf, item, 'getMaxDamage'), 'Item.getMaxDamage')
        self.m_use = _one(_named(mp, icf, item, 'use'), 'Item.use')

        self.entity = mp.find_class('net/minecraft/entity/Entity')
        self.living = mp.find_class('net/minecraft/entity/LivingEntity')
        self.m_attack = _one([(m['name'], m['desc']) for m in icf.methods
                              if m['desc'] == '(L%s;)I' % self.entity],
                             'getDamageVsEntity(Entity)')

        lcf = jar.cls(self.living)
        self.f_health = _field(mp, lcf, self.living, 'health')
        self.m_heal = _one([m['name'] for m in lcf.methods if m['desc'] == '(I)V'
                            and self._adds_to_health(lcf, m)], 'LivingEntity.heal')

        # use(stack, world, player): the three classes are its parameters.
        params = self.m_use[1][1:self.m_use[1].index(')')].split(';')[:3]
        self.stack_cls, self.world_cls, self.player_cls = (p[1:] for p in params)

    def _adds_to_health(self, cf, m):
        """True for the (I)V method whose body is `health += argument`."""
        ins = list(disassemble(cf.code_of(m) or b''))
        for a, b, c in zip(ins, ins[1:], ins[2:]):
            if (a[1] == 0xb4 and cf.ref(u2(a[2]))[1] == self.f_health
                    and b[1] == 0x1b and c[1] == 0x60):       # getfield; iload_1; iadd
                return True
        return False

    # -- items -------------------------------------------------------------
    def _ask(self, obj, method, args):
        name, desc = method
        return self.game.interp.call(obj.cls, name, desc, obj, args, virtual=True)

    def of_item(self, ident):
        """{'stackSize': n, ...} for the item (or a block's item form) at ident."""
        table = self.game.items
        obj = table[ident] if 0 <= ident < len(table) else None
        if obj is None:
            raise Unsupported('the game registered no item %d (%s)'
                              % (ident, self.game.why_stopped() or 'no reason given'))
        out = {'stackSize': self._ask(obj, self.m_count, [])}
        durability = self._ask(obj, self.m_damage, [])
        if durability:
            out['durability'] = durability
        owner, _m = self.game.interp._find(obj.cls, *self.m_attack)
        if owner is not None and owner.this != self.item:
            out['attackDamage'] = self._ask(obj, self.m_attack, [None])
        heal = self._heal_on_use(obj)
        if heal is not None:
            out['heal'] = heal
        return out

    def _heal_on_use(self, obj):
        """What using the item once passes to heal(), or None if it never does.

        Every item's use() is run against a stand-in stack, world and player.
        Most want far more of the world than a stand-in has and give up part
        way; that is harmless, because the only thing recorded is a heal()
        call, and a food item makes it before anything else can go wrong.
        """
        interp = self.game.interp
        healed = []

        def hook(_it, _recv, args):
            healed.append(args[0])
            return Interp.NOTHING

        keys = [(c, self.m_heal, '(I)V') for c in _chain(self.jar, self.player_cls, self.living) or []]
        for k in keys:
            interp.hooks[k] = hook
        try:
            self._ask(obj, self.m_use, [Obj(self.stack_cls), Obj(self.world_cls), Obj(self.player_cls)])
        except Exception:
            pass
        finally:
            for k in keys:
                interp.hooks.pop(k, None)
        if len(healed) > 1:
            raise Unsupported('item %s heals %d times on one use' % (obj.cls, len(healed)))
        return healed[0] if healed else None

    # -- mobs ----------------------------------------------------------------
    def health(self, cls):
        """The health a newly made mob of this class starts with.

        None for anything that is not a LivingEntity, and for a mob whose
        constructor leaves its health to chance.

        Entity's constructor is walked too. It has no health of its own, but
        it calls methods a mob may override, and an override that set health
        would run there.
        """
        if _chain(self.jar, cls, self.living) is None:
            return None
        chain = _chain(self.jar, cls, self.entity)
        if chain is None:
            return None
        health = None
        for c in reversed(chain):                     # base class first
            cf = self.jar.cls(c)
            ctor = cf.method('<init>', '(L%s;)V' % self.world_cls)
            if ctor is None:
                return None
            try:
                health = self._replay(cf, ctor, health, chain)
            except Unsupported:
                return None
        return health

    def _replay(self, cf, ctor, health, chain):
        """Apply one constructor's writes to health, in order.

        The two shapes Beta uses are `health = constant` and `health *= constant`
        (or +=). Any other write, and any call on `this` into a method that can
        write health, raises: the figure would be a guess.
        """
        ins = list(disassemble(cf.code_of(ctor)))
        for n, (_pc, op, operand) in enumerate(ins):
            if op == 0xb5 and cf.ref(u2(operand))[1] == self.f_health:        # putfield
                prev = ins[n - 1][1]
                const = _int_const(ins[n - 1])
                if const is not None and ins[n - 2][1] == 0x2a:              # aload_0; const
                    health = const
                    continue
                const = _int_const(ins[n - 2])
                if (prev in (0x60, 0x68) and const is not None and health is not None
                        and ins[n - 3][1] == 0xb4 and cf.ref(u2(ins[n - 3][2]))[1] == self.f_health):
                    health = health + const if prev == 0x60 else health * const
                    continue
                raise Unsupported('health is computed in %s' % cf.this)
            if op in (0xb6, 0xb7, 0xb9):
                owner, name, desc = cf.ref(u2(operand))
                if name != '<init>' and owner in chain and self._writes_health(chain, name, desc, set()):
                    raise Unsupported('%s.%s sets health' % (owner, name))
        return health

    def _writes_health(self, chain, name, desc, seen):
        """Whether the mob's own version of a method can assign its health."""
        if (name, desc) in seen:
            return False
        seen.add((name, desc))
        for c in chain:                               # the override nearest the mob
            cf = self.jar.cls(c)
            m = cf.method(name, desc)
            if m is None:
                continue
            code = cf.code_of(m)
            if code is None:
                return False
            for _pc, op, operand in disassemble(code):
                if op == 0xb5 and cf.ref(u2(operand))[1] == self.f_health:
                    return True
                if op in (0xb6, 0xb7, 0xb9):
                    owner, n2, d2 = cf.ref(u2(operand))
                    if owner in chain and n2 != '<init>' and self._writes_health(chain, n2, d2, seen):
                        return True
            return False
        return False


def _int_const(ins):
    """The int an instruction pushes, if it pushes a constant one."""
    _pc, op, operand = ins
    if 0x02 <= op <= 0x08:
        return op - 0x03
    if op == 0x10:
        return int.from_bytes(operand[:1], 'big', signed=True)
    if op == 0x11:
        return int.from_bytes(operand[:2], 'big', signed=True)
    return None
