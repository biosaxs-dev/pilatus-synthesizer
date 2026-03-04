"""Tests for config/preferences.py.

Original: test/test_002_Preferences.py  (nose → pytest)
"""

import pytest

from pilatus_synthesizer.config.preferences import (
    clear_preferences,
    get_preference,
    save_preferences,
    set_preference,
    reload_preferences,
    temporary_preferences_begin,
    temporary_preferences_end,
    get_usual_preference,
)


@pytest.fixture(autouse=True)
def _clean_prefs():
    """Reset preferences before and after every test in this module."""
    clear_preferences()
    save_preferences()
    yield
    clear_preferences()
    save_preferences()


# ── basic get / set / save / reload ──────────────────────────────────────

def test_get_returns_none_for_unset():
    assert get_preference('syn_method') is None


def test_set_and_get():
    set_preference('syn_method', 'cover')
    assert get_preference('syn_method') == 'cover'


def test_save_and_reload():
    set_preference('syn_method', 'cover')
    save_preferences()

    # Mutate in memory
    set_preference('syn_method', 'average')
    assert get_preference('syn_method') == 'average'

    # Reload should restore the saved value
    reload_preferences()
    assert get_preference('syn_method') == 'cover'


def test_clear_removes_values():
    set_preference('syn_method', 'cover')
    clear_preferences()
    assert get_preference('syn_method') is None


# ── temporary preferences ─────────────────────────────────────────────────

def test_temporary_preferences():
    set_preference('syn_method', 'cover')
    save_preferences()

    temporary_preferences_begin()

    set_preference('syn_method', 'average')
    assert get_preference('syn_method') == 'average'
    assert get_usual_preference('syn_method') == 'cover'

    temporary_preferences_end()

    assert get_preference('syn_method') == 'cover'


def test_temporary_preferences_multiple_keys():
    set_preference('syn_method', 'cover')
    set_preference('color_map', 'ALBULA')
    save_preferences()

    temporary_preferences_begin()

    set_preference('syn_method', 'average')
    set_preference('color_map', 'HEAT')
    assert get_preference('syn_method') == 'average'
    assert get_preference('color_map') == 'HEAT'
    assert get_usual_preference('syn_method') == 'cover'
    assert get_usual_preference('color_map') == 'ALBULA'

    temporary_preferences_end()

    assert get_preference('syn_method') == 'cover'
    assert get_preference('color_map') == 'ALBULA'
