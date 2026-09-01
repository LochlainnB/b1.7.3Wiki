"""Load Babric tiny-v2 mappings: client-obfuscated <-> intermediary <-> named."""
import io
import re


def load(intermediary_path, barn_path):
    """Return an object able to translate obfuscated client names to readable ones."""
    # ---- intermediary.tiny : c <intermediary> <glue> <server> <client>
    cls_obf2int = {}
    mem_obf2int = {}          # (client_class_obf, name, desc_obf) -> intermediary member name
    cur = None
    with io.open(intermediary_path, encoding='utf-8') as fh:
        for line in fh:
            p = line.rstrip('\n').split('\t')
            if p and p[0] == 'c' and len(p) >= 5:
                cur = p[4]
                cls_obf2int[p[4]] = p[1]
            elif len(p) >= 2 and p[0] == '' and cur:
                kind = p[1]
                if kind in ('m', 'f') and len(p) >= 7:
                    # '', kind, desc, intermediary, glue, server, client
                    mem_obf2int[(cur, p[6], p[2])] = p[3]

    # ---- barn.tiny : c <intermediary> <named>
    cls_int2named = {}
    mem_int2named = {}        # (intermediary_class, intermediary_member) -> named
    cur = None
    with io.open(barn_path, encoding='utf-8') as fh:
        for line in fh:
            p = line.rstrip('\n').split('\t')
            if p and p[0] == 'c' and len(p) >= 3:
                cur = p[1]
                cls_int2named[p[1]] = p[2]
            elif len(p) >= 2 and p[0] == '' and cur:
                kind = p[1]
                if kind in ('m', 'f') and len(p) >= 5:
                    mem_int2named[(cur, p[3])] = p[4]

    def obf_desc_to_int(desc):
        """Rewrite Lxx; class tokens in a descriptor into intermediary form."""
        return re.sub(r'L([^;]+);',
                      lambda mo: 'L%s;' % cls_obf2int.get(mo.group(1), mo.group(1)),
                      desc)

    class M:
        def cls(self, obf):
            i = cls_obf2int.get(obf)
            n = cls_int2named.get(i) if i else None
            return n or i or obf

        def simple(self, obf):
            return self.cls(obf).rsplit('/', 1)[-1]

        def member(self, cls_obf, name, desc):
            """Readable name for a method/field of an obfuscated class."""
            i_cls = cls_obf2int.get(cls_obf)
            i_mem = mem_obf2int.get((cls_obf, name, obf_desc_to_int(desc)))
            if i_cls and i_mem:
                return mem_int2named.get((i_cls, i_mem)) or i_mem
            return name

        def find_class(self, named):
            """Obfuscated client class name for a fully-qualified named class."""
            for i, n in cls_int2named.items():
                if n == named:
                    for o, ii in cls_obf2int.items():
                        if ii == i:
                            return o
            return None
    return M()
