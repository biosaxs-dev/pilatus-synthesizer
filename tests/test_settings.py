"""Tests for config/settings.py.

Original: test/test_003_Settings.py  (nose → pytest)
Mask-related tests are skipped on machines without test data.
"""

import pytest

from pilatus_synthesizer.config.settings import (
    clear_settings,
    get_setting,
    save_settings,
    set_setting,
    reload_settings,
    temporary_settings_begin,
    temporary_settings_end,
)


@pytest.fixture(autouse=True)
def _clean_settings():
    """Reset settings before and after every test in this module."""
    clear_settings()
    save_settings()
    yield
    clear_settings()
    save_settings()


# ── basic get / set / save / reload ──────────────────────────────────────

def test_get_returns_none_for_unset_string_setting():
    assert get_setting('in_folder') is None


def test_get_default_for_numeric_setting():
    """watch_interval has a non-None default."""
    assert get_setting('watch_interval') == 180


def test_set_and_get():
    set_setting('in_folder', '/tmp/input')
    assert get_setting('in_folder') == '/tmp/input'


def test_save_and_reload():
    set_setting('in_folder', '/tmp/input')
    save_settings()

    set_setting('in_folder', '/tmp/other')
    assert get_setting('in_folder') == '/tmp/other'

    reload_settings()
    assert get_setting('in_folder') == '/tmp/input'


def test_clear_removes_values():
    set_setting('in_folder', '/tmp/input')
    clear_settings()
    assert get_setting('in_folder') is None


def test_set_multiple_items():
    set_setting('in_folder', '/tmp/in')
    set_setting('adj_folder', '/tmp/adj')
    set_setting('syn_folder', '/tmp/syn')
    assert get_setting('in_folder') == '/tmp/in'
    assert get_setting('adj_folder') == '/tmp/adj'
    assert get_setting('syn_folder') == '/tmp/syn'


def test_invalid_key_raises():
    with pytest.raises(AssertionError):
        set_setting('not_a_valid_key', 'value')

    with pytest.raises(AssertionError):
        get_setting('not_a_valid_key')


# ── temporary settings ────────────────────────────────────────────────────

def test_temporary_settings():
    set_setting('in_folder', '/tmp/input')
    save_settings()

    temporary_settings_begin()

    set_setting('in_folder', '/tmp/other')
    assert get_setting('in_folder') == '/tmp/other'

    temporary_settings_end()

    assert get_setting('in_folder') == '/tmp/input'


def test_temporary_settings_multiple_keys():
    set_setting('in_folder', '/tmp/in')
    set_setting('adj_folder', '/tmp/adj')
    save_settings()

    temporary_settings_begin()
    set_setting('in_folder', '/tmp/in2')
    set_setting('adj_folder', '/tmp/adj2')

    temporary_settings_end()

    assert get_setting('in_folder') == '/tmp/in'
    assert get_setting('adj_folder') == '/tmp/adj'
