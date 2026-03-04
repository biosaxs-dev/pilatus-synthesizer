"""Tests for core/image_synthesizer.py.

Original: test/test_050_ImageSynthesizer.py  (nose → pytest)
Requires external measurement data — auto-skipped when unavailable.

Note: the legacy test used pyautogui/Tk event pumping to dismiss modal
dialogs.  The new package exposes ``exec_single_synthesis`` which can be
called headlessly, so we test that interface directly.
"""

import os
import pytest

pytestmark = pytest.mark.requires_data


@pytest.fixture(scope='module')
def synth_env(env, in_folder1, test_adj_folder, test_syn_folder):
    """Set up settings / preferences / mask and tear down afterwards."""
    from pilatus_synthesizer.config.settings import (
        set_setting, set_mask, clear_settings, save_settings)
    from pilatus_synthesizer.config.preferences import (
        set_preference, clear_preferences, save_preferences)
    from pilatus_synthesizer.config.development import set_devel_info

    mask_file = os.path.join(in_folder1, '20151019cent01_0_00000.mask')

    # Save originals
    from pilatus_synthesizer.config.preferences import get_preference
    orig_method = get_preference('syn_method')

    set_devel_info('min_ratio', 0.5)
    set_preference('syn_flags', [1, 1, 1, 1])
    set_devel_info('adj_output', 'YES')
    set_devel_info('intermediate_results', 'YES')
    set_devel_info('postfix_adj', '_adj')
    set_preference('postfix_syn', '_syn')

    set_setting('in_folder',  in_folder1)
    set_setting('adj_folder', test_adj_folder)
    set_setting('syn_folder', test_syn_folder)
    set_mask(mask_file)

    yield {
        'in_folder':    in_folder1,
        'adj_folder':   test_adj_folder,
        'syn_folder':   test_syn_folder,
    }

    # Restore
    set_preference('syn_method', orig_method)


def _make_exec_array():
    return [
        ['AgBh002', [
            ['AgBh002_0_00000.tif', ['0.70000', '-0.35000'], 1.0, None, 'AgBh002_syn.tif'],
            ['AgBh002_1_00000.tif', ['5', '3'],              1.0, 'AgBh002_1_adj.tif', 'AgBh002_syn.tif'],
            ['AgBh002_2_00000.tif', ['-5', '-3'],            1.0, 'AgBh002_2_adj.tif', 'AgBh002_syn.tif'],
        ]],
    ]


def test_cover_synthesis(synth_env):
    from pilatus_synthesizer.config.preferences import set_preference
    from pilatus_synthesizer.core.image_synthesizer import exec_single_synthesis
    set_preference('syn_method', 'cover')
    exec_array = _make_exec_array()
    exec_single_synthesis(len(exec_array[0][1]), exec_array)


def test_average_synthesis(synth_env):
    from pilatus_synthesizer.config.preferences import set_preference
    from pilatus_synthesizer.core.image_synthesizer import exec_single_synthesis
    set_preference('syn_method', 'average')
    exec_array = _make_exec_array()
    exec_single_synthesis(len(exec_array[0][1]), exec_array)
