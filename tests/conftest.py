"""pytest configuration and shared fixtures.

Test data strategy
------------------
Many integration tests require real X-ray measurement data that cannot be
committed to the repository (large binary files, beamline-specific paths).

The helper module ``SynthesizerTestEnv.py`` maps environment keys to local
data paths.  If it is present anywhere on ``sys.path`` (or in a parent of
this file), tests that need data will run; otherwise they are automatically
skipped.

Typical ``SynthesizerTestEnv.py`` layout::

    env_dict = {
        'in_folder1_AgBh_center': r'E:/TestData/AgBh_center',
        'in_folder2':             r'E:/TestData/MAG2wk7210',
        'in_folder2_Detector_move': r'E:/TestData/Detector_move',
        'in_folder_cbf':          r'E:/TestData/cbf',
        'in_folder_cbf_tif':      r'E:/TestData/cbf_tif',
        'tif_folder':             r'E:/TestData/tif',
        'empty_folder':           r'E:/TestData/tmp/empty',
        'test_adj_folder':        r'E:/TestData/tmp/adj',
        'test_syn_folder':        r'E:/TestData/tmp/syn',
        'test_syn_folder2':       r'E:/TestData/tmp/syn2',
        'expected_adj_folder':    r'E:/TestData/expected/adj',
        'expected_syn_folder':    r'E:/TestData/expected/syn',
        'round_adj_folder':       r'E:/TestData/expected/round_adj',
        'round_syn_folder':       r'E:/TestData/expected/round_syn',
    }

To make test data available, either:
  (a) place ``SynthesizerTestEnv.py`` one directory above the repo root, or
  (b) set the environment variable ``SYNTH_TEST_ENV`` to its full path.
"""

import os
import sys
import importlib
import importlib.util
import pytest


# ── Locate SynthesizerTestEnv ──────────────────────────────────────────

def _find_test_env():
    """Try to locate SynthesizerTestEnv.py.  Returns the module or None."""
    # 1. Honour explicit env variable
    env_path = os.environ.get('SYNTH_TEST_ENV')
    if env_path and os.path.isfile(env_path):
        spec = importlib.util.spec_from_file_location('SynthesizerTestEnv', env_path)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    # 2. Search parent directories (up to 3 levels)
    here = os.path.dirname(os.path.abspath(__file__))
    for _ in range(3):
        candidate = os.path.join(here, 'SynthesizerTestEnv.py')
        if os.path.isfile(candidate):
            spec = importlib.util.spec_from_file_location('SynthesizerTestEnv', candidate)
            mod  = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
        here = os.path.dirname(here)

    # 3. Try importing from sys.path
    try:
        return importlib.import_module('SynthesizerTestEnv')
    except ImportError:
        return None


_test_env_module = _find_test_env()
_env_dict        = getattr(_test_env_module, 'env_dict', None) or {}

has_test_data = bool(_env_dict)

# ── Markers ─────────────────────────────────────────────────────────────

def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'requires_data: mark test as requiring external measurement data'
    )


def pytest_collection_modifyitems(config, items):
    if has_test_data:
        return
    skip_marker = pytest.mark.skip(reason='test data not available '
                                           '(set SYNTH_TEST_ENV or place '
                                           'SynthesizerTestEnv.py above repo root)')
    for item in items:
        if 'requires_data' in item.keywords:
            item.add_marker(skip_marker)


# ── Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(scope='session')
def env():
    """Return the environment dictionary (skips if data is absent)."""
    if not has_test_data:
        pytest.skip('test data not available')
    return _env_dict


@pytest.fixture(scope='session')
def in_folder1(env):
    return env['in_folder1_AgBh_center']


@pytest.fixture(scope='session')
def in_folder2(env):
    return env['in_folder2']


@pytest.fixture(scope='session')
def tif_folder(env):
    return env['tif_folder']


@pytest.fixture(scope='session')
def empty_folder(env, tmp_path_factory):
    """Writable scratch folder (uses tmp_path so it is always clean)."""
    return str(tmp_path_factory.mktemp('empty'))


@pytest.fixture(scope='session')
def test_adj_folder(env, tmp_path_factory):
    return str(tmp_path_factory.mktemp('adj'))


@pytest.fixture(scope='session')
def test_syn_folder(env, tmp_path_factory):
    return str(tmp_path_factory.mktemp('syn'))
