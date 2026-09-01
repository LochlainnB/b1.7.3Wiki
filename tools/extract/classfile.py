"""Minimal Java .class parser: constant pool + method bytecode disassembly.

Only what we need to read Beta 1.7.3's Block/Item <clinit> static initialisers.
No third-party dependencies.
"""
import struct

CONSTANT_Utf8=1; CONSTANT_Integer=3; CONSTANT_Float=4; CONSTANT_Long=5
CONSTANT_Double=6; CONSTANT_Class=7; CONSTANT_String=8; CONSTANT_Fieldref=9
CONSTANT_Methodref=10; CONSTANT_InterfaceMethodref=11; CONSTANT_NameAndType=12
CONSTANT_MethodHandle=15; CONSTANT_MethodType=16; CONSTANT_InvokeDynamic=18


class Reader:
    def __init__(self, data):
        self.d = data; self.p = 0
    def u1(self):
        v = self.d[self.p]; self.p += 1; return v
    def u2(self):
        v = struct.unpack_from('>H', self.d, self.p)[0]; self.p += 2; return v
    def u4(self):
        v = struct.unpack_from('>I', self.d, self.p)[0]; self.p += 4; return v
    def raw(self, n):
        v = self.d[self.p:self.p+n]; self.p += n; return v


class ClassFile:
    def __init__(self, data):
        r = Reader(data)
        assert r.u4() == 0xCAFEBABE, 'not a class file'
        r.u2(); r.u2()                       # minor, major
        self.cp = self._const_pool(r)
        r.u2()                               # access flags
        self.this = self.cls_name(r.u2())
        self.super = self.cls_name(r.u2())
        for _ in range(r.u2()): r.u2()       # interfaces
        self.fields = self._members(r)
        self.methods = self._members(r)

    def _const_pool(self, r):
        n = r.u2(); cp = [None] * n; i = 1
        while i < n:
            tag = r.u1()
            if tag == CONSTANT_Utf8:
                cp[i] = ('utf8', r.raw(r.u2()).decode('utf-8', 'replace'))
            elif tag == CONSTANT_Integer:  cp[i] = ('int', struct.unpack('>i', r.raw(4))[0])
            elif tag == CONSTANT_Float:    cp[i] = ('float', struct.unpack('>f', r.raw(4))[0])
            elif tag == CONSTANT_Long:     cp[i] = ('long', struct.unpack('>q', r.raw(8))[0])
            elif tag == CONSTANT_Double:   cp[i] = ('double', struct.unpack('>d', r.raw(8))[0])
            elif tag == CONSTANT_Class:    cp[i] = ('class', r.u2())
            elif tag == CONSTANT_String:   cp[i] = ('string', r.u2())
            elif tag in (CONSTANT_Fieldref, CONSTANT_Methodref, CONSTANT_InterfaceMethodref):
                cp[i] = ('ref', r.u2(), r.u2())
            elif tag == CONSTANT_NameAndType: cp[i] = ('nat', r.u2(), r.u2())
            elif tag == CONSTANT_MethodHandle: cp[i] = ('mh', r.u1(), r.u2())
            elif tag == CONSTANT_MethodType:   cp[i] = ('mt', r.u2())
            elif tag == CONSTANT_InvokeDynamic: cp[i] = ('indy', r.u2(), r.u2())
            else: raise ValueError('bad cp tag %d at %d' % (tag, i))
            i += 2 if tag in (CONSTANT_Long, CONSTANT_Double) else 1
        return cp

    def utf8(self, i):  return self.cp[i][1]
    def cls_name(self, i):
        if i == 0: return None
        return self.utf8(self.cp[i][1])

    def const(self, i):
        """Value of a loadable constant, or None."""
        e = self.cp[i]
        if e is None: return None
        if e[0] in ('int', 'float', 'long', 'double'): return e[1]
        if e[0] == 'string': return self.utf8(e[1])
        if e[0] == 'class':  return self.utf8(e[1])
        return None

    def ref(self, i):
        """(owner, name, descriptor) for a Field/Methodref."""
        e = self.cp[i]
        owner = self.cls_name(e[1])
        nat = self.cp[e[2]]
        return owner, self.utf8(nat[1]), self.utf8(nat[2])

    def _members(self, r):
        out = []
        for _ in range(r.u2()):
            r.u2()                                   # access
            name = self.utf8(r.u2()); desc = self.utf8(r.u2())
            attrs = {}
            for _ in range(r.u2()):
                an = self.utf8(r.u2()); alen = r.u4(); attrs[an] = r.raw(alen)
            out.append({'name': name, 'desc': desc, 'attrs': attrs})
        return out

    def method(self, name, desc=None):
        for m in self.methods:
            if m['name'] == name and (desc is None or m['desc'] == desc):
                return m
        return None

    def code_of(self, m):
        """Extract the raw bytecode array from a method's Code attribute."""
        c = m['attrs'].get('Code')
        if c is None: return None
        r = Reader(c); r.u2(); r.u2()                # max_stack, max_locals
        return r.raw(r.u4())
