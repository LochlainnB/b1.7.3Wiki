"""Locating the Beta 1.7.3 client jar and the Babric mappings.

The jar is Mojang's, shipped without a licence, so it is never vendored into
this repository - the same rule the decompiled source lives under. It sits
outside, is read strictly read-only, and is found by:

  1. the B173_JAR and B173_CACHE environment variables,
  2. "jarPath" and "cachePath" in wiki.local.json (gitignored),
  3. a sibling directory named BabricKit/cache.

The mappings cache is one directory holding intermediary.tiny and barn.tiny,
and the jar normally sits beside them, so pointing at the cache is usually
enough; jarPath is only for a jar kept somewhere else.

This mirrors tools/lib/source.mjs, with one deliberate difference. A missing
source tree is not an error - the wiki builds and validates without it. These
files are what the extractors are made of, so not finding them is fatal, and
the message names all three ways to point at them.
"""
import collections
import io
import json
import os

CACHE_FILES = ('intermediary.tiny', 'barn.tiny')
JAR_NAME = 'client.jar'
SIBLING = os.path.join('..', 'BabricKit', 'cache')

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

Found = collections.namedtuple('Found', 'path origin')


class Missing(Exception):
    """Nothing to extract from. Carries a message that says what to set."""


def _local_config(root):
    """wiki.local.json as a dict, or {} when it is absent."""
    path = os.path.join(root, 'wiki.local.json')
    if not os.path.exists(path):
        return {}
    try:
        with io.open(path, encoding='utf-8') as fh:
            return json.load(fh)
    except ValueError as err:
        raise Missing('wiki.local.json is not valid JSON (%s)' % err)


def _dirs(root):
    """Directories to search, most explicit first, convention last."""
    out = []
    env = os.environ.get('B173_CACHE')
    if env:
        out.append(Found(os.path.abspath(env), 'B173_CACHE'))
    cfg = _local_config(root).get('cachePath')
    if cfg:
        out.append(Found(os.path.normpath(os.path.join(root, cfg)),
                         'wiki.local.json "cachePath"'))
    out.append(Found(os.path.normpath(os.path.join(root, SIBLING)), 'the conventional ' + SIBLING))
    return out


def _search(root, wanted):
    """First candidate directory holding every name in `wanted`.

    An explicitly configured directory that does not have them is worth saying
    out loud; the conventional sibling simply not being there is not, so the
    search moves on and the caller reports the whole list at the end.
    """
    for cand in _dirs(root):
        absent = [f for f in wanted if not os.path.exists(os.path.join(cand.path, f))]
        if not absent:
            return cand
        if not cand.origin.startswith('the conventional'):
            raise Missing('%s points at %s, which has no %s'
                          % (cand.origin, cand.path, ' or '.join(absent)))
    return None


def _nowhere(root, wanted, env, key):
    looked = '\n'.join('    %s  (%s)' % (c.path, c.origin) for c in _dirs(root))
    return Missing('no %s found. Looked in:\n%s\nSet %s, or "%s" in '
                   'wiki.local.json, or put the files in %s.'
                   % (' or '.join(wanted), looked, env, key, SIBLING))


def find_cache(root=REPO_ROOT):
    """The directory holding intermediary.tiny and barn.tiny."""
    hit = _search(root, CACHE_FILES)
    if hit is None:
        raise _nowhere(root, CACHE_FILES, 'B173_CACHE', 'cachePath')
    return hit


def find_jar(root=REPO_ROOT):
    """The client jar. An explicit path wins; otherwise it is found beside the mappings."""
    env = os.environ.get('B173_JAR')
    cfg = _local_config(root).get('jarPath')
    for value, origin in ((env, 'B173_JAR'), (cfg, 'wiki.local.json "jarPath"')):
        if not value:
            continue
        path = os.path.normpath(os.path.join(root, value))
        if not os.path.exists(path):
            raise Missing('%s points at %s, which does not exist' % (origin, path))
        return Found(path, origin)

    hit = _search(root, (JAR_NAME,))
    if hit is None:
        raise _nowhere(root, (JAR_NAME,), 'B173_JAR', 'jarPath')
    return Found(os.path.join(hit.path, JAR_NAME), hit.origin)
