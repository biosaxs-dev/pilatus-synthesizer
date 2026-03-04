"""Basic utility functions.

Original: KekLib/BasicUtils.py
Copyright (c) 2016-2020, Masatsuyo Takahashi, KEK-PF
"""

import os
import re
import sys
import time
import shutil


def mkdirs_with_retry(path, retry=3):
    retry_ = 0
    while not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError:
            if retry_ < retry:
                retry_ += 1
                time.sleep(1)
            else:
                raise


def clear_dirs_with_retry(dirs, retry=3):
    for dir_ in dirs:
        if os.path.exists(dir_):
            shutil.rmtree(dir_)
        mkdirs_with_retry(dir_, retry=retry)


def rename_with_retry(old_path, new_path, retry=3):
    retry_ = 0
    done_ = False
    while not done_:
        try:
            os.rename(old_path, new_path)
            done_ = True
        except OSError:
            if retry_ < retry:
                retry_ += 1
                time.sleep(1)
            else:
                raise


class Struct:
    """Simple attribute-access dict wrapper."""
    def __init__(self, **entries):
        self.__dict__.update(entries)


class AutoVivifiedDict(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


def print_exception():
    from pilatus_synthesizer._keklib.exception_traceback import ExceptionTracebacker
    etb = ExceptionTracebacker()
    print(etb)


def exe_name() -> str:
    """Return the current executable/script name without extension."""
    name = os.path.split(sys.argv[0])[-1]
    for ext in ('.exe', '.py'):
        name = name.replace(ext, '')
    return name
