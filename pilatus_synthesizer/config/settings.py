"""Application settings (folder paths, mask, operation mode).

Original: lib/Synthesizer/SynthesizerSettings.py
Copyright (c) 2015-2020, SAXS Team, KEK-PF
"""

import os
from pilatus_synthesizer._keklib.persistent_info import PersistentInfo
from pilatus_synthesizer.core.sangler_mask import SAnglerMask

ITEM_DEFAULTS = {
    'in_folder': None,
    'log_file': None,
    'mask_file': None,
    'adj_folder': None,
    'syn_folder': None,
    'op_option': 'MANUAL',
    'watch_interval': 180,
    'positive_direction': 'right',
}

_setting_info = PersistentInfo('settings.dump')
_settings = _setting_info.get_dictionary()
_mask = None


def reload_settings():
    global _setting_info, _settings
    _setting_info = PersistentInfo('settings.dump')
    _settings = _setting_info.get_dictionary()


def clear_settings():
    global _settings
    _settings = {}
    _setting_info.set_dictionary(_settings)


def get_setting(item):
    assert item in ITEM_DEFAULTS
    value = _settings.get(item)
    if value is None:
        value = ITEM_DEFAULTS.get(item)
        set_setting(item, value)
    return value


def set_setting(item, value):
    assert item in ITEM_DEFAULTS
    _settings[item] = value


def temporary_settings_begin():
    global _settings_save
    _settings_save = _settings.copy()


def temporary_settings_end():
    global _settings_save, _settings
    _settings = _settings_save
    _setting_info.set_dictionary(_settings)


def save_settings():
    _setting_info.save()


def set_mask(filepath):
    global _mask
    try:
        _mask = SAnglerMask(filepath)
        return True
    except Exception:
        return False


def get_mask():
    return _mask
