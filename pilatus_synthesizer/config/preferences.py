"""User preferences (synthesis method, output naming, display options).

Original: lib/Synthesizer/Preferences.py
Copyright (c) 2015-2020, SAXS Team, KEK-PF
"""

from pilatus_synthesizer._keklib.persistent_info import PersistentInfo

DEFAULT_PREFERENCES = {
    'syn_method': 'cover',
    'detection_counter': 'None',
    'postfix_syn': '_syn',
    'color_map': 'ALBULA',
    'save_policy': 'Ask',
    'syn_policy': 'all',
    'syn_flags': [1, 1, 1],
}

_preference_info = PersistentInfo('preferences.dump', DEFAULT_PREFERENCES)
_preferences = _preference_info.get_dictionary()


def reload_preferences():
    global _preference_info, _preferences
    _preference_info = PersistentInfo('preferences.dump', DEFAULT_PREFERENCES)
    _preferences = _preference_info.get_dictionary()


def clear_preferences():
    global _preferences
    _preferences = {}
    _preference_info.set_dictionary(_preferences)


def get_preference(item):
    assert item in DEFAULT_PREFERENCES
    return _preferences.get(item)


def set_preference(item, value):
    assert item in DEFAULT_PREFERENCES
    _preferences[item] = value


def temporary_preferences_begin():
    global _preferences_save
    _preferences_save = _preferences.copy()


def temporary_preferences_end():
    global _preferences_save, _preferences
    _preferences = _preferences_save
    _preference_info.set_dictionary(_preferences)


def get_usual_preference(item):
    global _preferences_save
    return _preferences_save.get(item)


def save_preferences():
    _preference_info.save()
