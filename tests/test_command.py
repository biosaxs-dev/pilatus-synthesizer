"""Tests for CLI command controller.

Original: test/test_400_CommandController.py  (nose → pytest)
Requires external measurement data — auto-skipped when unavailable.
"""

import os
import pytest

pytestmark = pytest.mark.requires_data


@pytest.fixture(scope='module')
def round_paths(env, in_folder1):
    return {
        'in_folder':       in_folder1,
        'syn_folder':      os.path.join(in_folder1, 'Synthesized'),
        'round_syn_folder': env['round_syn_folder'],
    }


@pytest.fixture(autouse=True, scope='module')
def _set_round_algorithm():
    from pilatus_synthesizer.config.development import set_devel_info
    set_devel_info('adj_algorithm', 'round')


class _Opts:
    """Minimal options object matching legacy ``Struct``."""
    def __init__(self, in_folder):
        self.command         = True
        self.in_folder       = in_folder
        self.adj_folder      = None
        self.autonum_folders = False
        self.out_folder      = None
        self.pandastable     = False


def _assert_equal_syn(filename, syn_folder, round_syn_folder):
    from pilatus_synthesizer.core.pilatus_image import PilatusImage
    synthesized_path = os.path.join(syn_folder, filename)
    expected_path    = os.path.join(round_syn_folder, filename)
    assert os.path.isfile(synthesized_path), f'Synthesized file missing: {synthesized_path}'
    assert os.path.isfile(expected_path),    f'Expected file missing: {expected_path}'
    assert PilatusImage(synthesized_path).equal(PilatusImage(expected_path))


def test_normal_synthesis(round_paths):
    from pilatus_synthesizer.config.development import set_devel_info
    from pilatus_synthesizer.cli.command import Controller
    set_devel_info('intermediate_results', 'YES')

    opts = _Opts(round_paths['in_folder'])
    cmd  = Controller(opts)
    cmd.execute()

    _assert_equal_syn('AgBh002_1_syn.tif',
                      round_paths['syn_folder'],
                      round_paths['round_syn_folder'])
    _assert_equal_syn('AgBh002_syn.tif',
                      round_paths['syn_folder'],
                      round_paths['round_syn_folder'])


def test_exception_logged(round_paths):
    from pilatus_synthesizer.config.development import set_devel_info
    from pilatus_synthesizer._keklib.debug_queue import debug_queue_put
    from pilatus_synthesizer.cli.command import Controller
    set_devel_info('intermediate_results', 'YES')
    debug_queue_put('PilatusUtils.die()')

    opts = _Opts(round_paths['in_folder'])
    cmd  = Controller(opts)
    cmd.execute()

    with open(cmd.logfile_path) as fh:
        log_text = fh.read()
    assert "NameError: name 'die' is not defined" in log_text
