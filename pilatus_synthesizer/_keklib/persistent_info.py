"""Persistent dictionary storage via pickle.

Stores per-application config in ~/.KekTools/pilatus-synthesizer/.

Original: KekLib/PersistentInfo.py
Copyright (c) 2016-2020, Masatsuyo Takahashi, KEK-PF
"""

import pickle
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_APP_NAME = "pilatus-synthesizer"


def _get_app_config_dir() -> Path:
    config_dir = Path.home() / ".KekTools" / _APP_NAME
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


class PersistentInfo:
    def __init__(self, filename, defaults=None):
        if defaults is None:
            defaults = {}
        self.pickle_file = _get_app_config_dir() / filename
        self.dictionary = self._load()
        for k, v in defaults.items():
            if self.dictionary.get(k) is None:
                self.dictionary[k] = v

    def _load(self):
        path = self.pickle_file
        if path.exists() and path.stat().st_size > 0:
            try:
                with open(path, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                logger.warning(
                    "Broken settings file %s — resetting to defaults.", path
                )
                path.unlink(missing_ok=True)
        return {}

    def get_dictionary(self):
        return self.dictionary

    def set_dictionary(self, dictionary):
        self.dictionary = dictionary

    def save(self, file=None):
        path = Path(file) if file else self.pickle_file
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.dictionary, f)
