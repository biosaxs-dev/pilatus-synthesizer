"""Tests for _keklib/basic_utils.py.

Original: test/test_000_BasicUtils.py  (nose → pytest)
"""

import os
import threading
import time

import pytest

from pilatus_synthesizer._keklib.basic_utils import (
    mkdirs_with_retry,
    rename_with_retry,
    exe_name,
)


# ── mkdirs_with_retry ────────────────────────────────────────────────────

def test_mkdirs_creates_directory(tmp_path):
    target = tmp_path / 'new_dir'
    assert not target.exists()
    mkdirs_with_retry(str(target))
    assert target.is_dir()


def test_mkdirs_idempotent(tmp_path):
    target = tmp_path / 'existing'
    target.mkdir()
    mkdirs_with_retry(str(target))   # should not raise
    assert target.is_dir()


def test_mkdirs_nested(tmp_path):
    target = tmp_path / 'a' / 'b' / 'c'
    mkdirs_with_retry(str(target))
    assert target.is_dir()


def _delete_after_creation(path, delay=0.1):
    """Helper thread: create path, sleep a bit, then *remove* it."""
    os.makedirs(path, exist_ok=True)
    time.sleep(delay)
    # Simulate a transient failure by removing the just-created dir;
    # mkdirs_with_retry watches for the dir to either exist or to create it.
    try:
        os.rmdir(path)
    except OSError:
        pass


def test_mkdirs_with_retry_concurrent(tmp_path):
    """mkdirs_with_retry must succeed even if the dir disappears transiently."""
    target = str(tmp_path / 'race')
    thr = threading.Thread(target=_delete_after_creation, args=(target,))
    thr.start()
    mkdirs_with_retry(target)
    thr.join()
    # We just check no exception was raised; the dir may or may not exist
    # depending on timing — that's fine.


# ── rename_with_retry ────────────────────────────────────────────────────

def test_rename_with_retry(tmp_path):
    src = tmp_path / 'source.txt'
    dst = tmp_path / 'dest.txt'
    src.write_text('hello')

    rename_with_retry(str(src), str(dst))

    assert not src.exists()
    assert dst.read_text() == 'hello'


# ── exe_name ─────────────────────────────────────────────────────────────

def test_exe_name_returns_string():
    name = exe_name()
    assert isinstance(name, str)
    assert len(name) > 0


def test_exe_name_strips_extensions():
    name = exe_name()
    assert not name.endswith('.py')
    assert not name.endswith('.exe')
