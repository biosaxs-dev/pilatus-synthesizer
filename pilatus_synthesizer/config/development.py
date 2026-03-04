"""Developer options (algorithm tuning, debug flags).

Data-model only. The DeveloperOptionsDialog GUI is deferred to Phase 4.

Original: lib/Synthesizer/Development.py
Copyright (c) 2015-2020, SAXS Team, KEK-PF
"""

from pilatus_synthesizer._keklib.persistent_info import PersistentInfo

DEFAULT_DEVELOPER_OPTIONS = {
    'adj_algorithm': 'round',
    'min_ratio': 0.5,
    'adj_output': 'NO',
    'postfix_adj': '_adj',
    'intermediate_results': 'NO',
    'defaultfont': ('TkDefaultFont', 10),
    'fixedfont': ('TkFixedFont', 10),
    'debug': False,
}

_development_info = PersistentInfo('development.dump', DEFAULT_DEVELOPER_OPTIONS)
_development = _development_info.get_dictionary()


def get_devel_info(item):
    assert item in DEFAULT_DEVELOPER_OPTIONS
    return _development.get(item)


def set_devel_info(item, value):
    assert item in DEFAULT_DEVELOPER_OPTIONS
    _development[item] = value


def save_development():
    _development_info.save()
