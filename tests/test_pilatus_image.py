"""Tests for core/pilatus_image.py.

Consolidated from:
  - test/test_040_PilatusImageTIFF.py
  - test/test_042_PilatusImageCompare.py
  (nose → pytest)

Requires external measurement data — auto-skipped when unavailable.
"""

import os
import pytest
import numpy as np

pytestmark = pytest.mark.requires_data


# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture(scope='module')
def agbh_paths(env, in_folder1):
    return {
        'tif0':  os.path.join(in_folder1, 'AgBh002_0_00000.tif'),
        'tif1':  os.path.join(in_folder1, 'AgBh002_1_00000.tif'),
        'tif2':  os.path.join(in_folder1, 'AgBh002_2_00000.tif'),
        'mask':  os.path.join(in_folder1, '20151019cent01_0_00000.mask'),
        'expected_adj': env['expected_adj_folder'],
        'round_adj':    env['round_adj_folder'],
    }


@pytest.fixture(scope='module')
def mask_array(agbh_paths):
    from pilatus_synthesizer.core.sangler_mask import SAnglerMask
    return SAnglerMask(agbh_paths['mask']).mask_array


@pytest.fixture(scope='module')
def cbf_paths(env):
    return {
        'tif': os.path.join(env['in_folder_cbf_tif'], 'AgBh0_0_00000.tif'),
        'cbf': os.path.join(env['in_folder_cbf'],     'AgBh0_0_00000.cbf'),
    }


# ── Save / diff / equal ───────────────────────────────────────────────────

def test_save_and_equal(agbh_paths, tmp_path):
    from pilatus_synthesizer.core.pilatus_image import PilatusImage
    pim_a = PilatusImage(agbh_paths['tif0'])
    out_file = str(tmp_path / 'saved.tif')
    pim_a.save(out_file)

    pim_b = PilatusImage(out_file)
    pim_c = pim_a.diff(pim_b)
    assert (pim_c.image_array() == np.zeros(pim_a.image_array().shape)).all()
    assert pim_a.equal(pim_b)


# ── pixel_rounded_shift ───────────────────────────────────────────────────

def test_pixel_rounded_shift():
    from pilatus_synthesizer.core.pilatus_image import pixel_rounded_shift
    assert pixel_rounded_shift(  5074) ==  30
    assert pixel_rounded_shift(  5073) ==  29
    assert pixel_rounded_shift(  5000) ==  29
    assert pixel_rounded_shift(  4902) ==  29
    assert pixel_rounded_shift(  4901) ==  28
    assert pixel_rounded_shift( -4901) == -28
    assert pixel_rounded_shift( -4902) == -28
    assert pixel_rounded_shift( -5000) == -29
    assert pixel_rounded_shift( -5073) == -29
    assert pixel_rounded_shift( -5074) == -29
    assert pixel_rounded_shift( -5075) == -30


# ── Image adjustment algorithms ───────────────────────────────────────────

def test_slow_adjust(agbh_paths, mask_array):
    from pilatus_synthesizer.core.pilatus_image import PilatusImage
    from pilatus_synthesizer.config.development import set_devel_info
    set_devel_info('adj_algorithm', 'slow')

    adj = PilatusImage(agbh_paths['tif1'], mask_array, 5000, 3000)
    exp = PilatusImage(os.path.join(agbh_paths['expected_adj'], 'AgBh002_1_adj.tif'))
    assert adj.equal(exp)

    adj = PilatusImage(agbh_paths['tif2'], mask_array, -5000, -3000)
    exp = PilatusImage(os.path.join(agbh_paths['expected_adj'], 'AgBh002_2_adj.tif'))
    assert adj.equal(exp)


def test_fast_adjust(agbh_paths, mask_array):
    from pilatus_synthesizer.core.pilatus_image import PilatusImage
    from pilatus_synthesizer.config.development import set_devel_info
    set_devel_info('adj_algorithm', 'fast')

    adj = PilatusImage(agbh_paths['tif1'], mask_array, 5000, 3000)
    exp = PilatusImage(os.path.join(agbh_paths['expected_adj'], 'AgBh002_1_adj.tif'))
    assert adj.equal(exp)

    adj = PilatusImage(agbh_paths['tif2'], mask_array, -5000, -3000)
    exp = PilatusImage(os.path.join(agbh_paths['expected_adj'], 'AgBh002_2_adj.tif'))
    assert adj.equal(exp)


def test_round_adjust(agbh_paths, mask_array):
    from pilatus_synthesizer.core.pilatus_image import PilatusImage, pixel_rounded_shift
    from pilatus_synthesizer.config.development import set_devel_info
    set_devel_info('adj_algorithm', 'round')

    original_pim = PilatusImage(agbh_paths['tif1'])
    original_arr = original_pim.image_array()
    rows, cols = original_arr.shape

    ir_ = pixel_rounded_shift(5000)
    ic_ = pixel_rounded_shift(3000)

    adjusted_pim = PilatusImage(agbh_paths['tif1'], mask_array, 5000, 3000)
    adjusted_arr = adjusted_pim.image_array()

    # Top-left region must match shifted original
    for i in range(10):
        for j in range(10):
            assert original_arr[i + ir_, j + ic_] == adjusted_arr[i, j]

    # Bottom-right region (outside shift) must be filled with -2
    for i in range(rows - ir_, rows):
        for j in range(cols - ic_, cols):
            assert adjusted_arr[i, j] == -2


# ── TIF vs CBF comparison ─────────────────────────────────────────────────

def test_tif_matches_pillow(cbf_paths):
    from PIL import Image
    from pilatus_synthesizer.core.pilatus_image import PilatusImage
    tif_file = cbf_paths['tif']
    pim = PilatusImage(tif_file)
    pil_array = np.array(Image.open(tif_file))
    assert (pim.imarray == pil_array).all()


def test_cbf_close_to_tif(cbf_paths):
    from pilatus_synthesizer.core.pilatus_image import PilatusImage
    tif_pim = PilatusImage(cbf_paths['tif'])
    cbf_pim = PilatusImage(cbf_paths['cbf'])
    max_diff = np.max(np.abs(cbf_pim.imarray - tif_pim.imarray))
    assert max_diff < 1300
