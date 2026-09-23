"""Locating the Beta 1.7.3 client jar and the Babric mappings.

The jar is Mojang's, shipped without a licence, so it is never vendored into
this repository - the same rule the decompiled source lives under. It sits
outside, is read strictly read-only, and is found by:

  1. the B173_JAR and B173_CACHE environment variables,
  2. "jarPath" and "cachePath" in wiki.local.json (gitignored).

The mappings cache is one directory holding intermediary.tiny and barn.tiny,
and the jar normally sits beside them, so pointing at the cache is usually
enough; jarPath is only for a jar kept somewhere else. AGENTS.md says where to
download all three.

This follows tools/lib/source.mjs, with two differences. A missing source tree
is not an error - the wiki builds and validates without it. These files are
what the extractors are made of, so not finding them is fatal, and the message
says how to point at them. And there is no conventional directory to fall back
on: a path nobody configured is not guessed at.
"""
import collections
import io
import json
import os

CACHE_FILES = ('intermediary.tiny', 'barn.tiny')
JAR_NAME = 'client.jar'

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


def _cache_dir(root):
    """The configured cache directory, the environment first, or None."""
    env = os.environ.get('B173_CACHE')
    if env:
        return Found(os.path.abspath(env), 'B173_CACHE')
    cfg = _local_config(root).get('cachePath')
    if cfg:
        return Found(os.path.normpath(os.path.join(root, cfg)),
                     'wiki.local.json "cachePath"')
    return None


def _search(root, wanted):
    """The configured cache directory, if it holds every name in `wanted`.

    None when no directory is configured at all. One that is configured but
    lacks a file is an error, named for the setting that points at it.
    """
    cand = _cache_dir(root)
    if cand is None:
        return None
    absent = [f for f in wanted if not os.path.exists(os.path.join(cand.path, f))]
    if absent:
        raise Missing('%s points at %s, which has no %s'
                      % (cand.origin, cand.path, ' or '.join(absent)))
    return cand


def _nowhere(wanted, env, key):
    return Missing('no %s found. Set %s, or "%s" in wiki.local.json; '
                   '"Regenerating data and assets" in AGENTS.md lists the '
                   'downloads.' % (' or '.join(wanted), env, key))


def find_cache(root=REPO_ROOT):
    """The directory holding intermediary.tiny and barn.tiny."""
    hit = _search(root, CACHE_FILES)
    if hit is None:
        raise _nowhere(CACHE_FILES, 'B173_CACHE', 'cachePath')
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
        raise _nowhere((JAR_NAME,), 'B173_JAR', 'jarPath')
    return Found(os.path.join(hit.path, JAR_NAME), hit.origin)
