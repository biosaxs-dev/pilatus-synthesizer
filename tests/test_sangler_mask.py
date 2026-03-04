"""Tests for core/sangler_mask.py.

Original: test/test_006_SAnglerMask.py  (nose → pytest)
Requires external measurement data — auto-skipped when unavailable.
"""

import os
import pytest
import numpy as np

pytestmark = pytest.mark.requires_data


@pytest.fixture(scope='module')
def mask(in_folder1):
    from pilatus_synthesizer.core.sangler_mask import SAnglerMask
    mask_file = os.path.join(in_folder1, '20151019cent01_0_00000.mask')
    return SAnglerMask(mask_file)


def test_mask_is_ndarray(mask):
    assert isinstance(mask.mask_array, np.ndarray)


def test_mask_shape(mask):
    row, col = mask.mask_array.shape
    assert row == 1043
    assert col == 981


def test_mask_first_row(mask):
    a = mask.mask_array
    assert a[0,   0] == 0
    assert a[0, 486] == 0
    assert a[0, 487] == 1
    assert a[0, 493] == 1
    assert a[0, 494] == 0


def test_mask_chip_gap_rows(mask):
    a = mask.mask_array
    assert a[830,   0] == 0
    assert a[831,   0] == 1
    assert a[831,   1] == 1
    assert a[831, 980] == 1
    assert a[847,   0] == 1
    assert a[847,   1] == 1
    assert a[847, 980] == 1
    assert a[848,   0] == 0
    assert a[848, 486] == 0
    assert a[848, 487] == 1


def test_mask_last_row(mask):
    a = mask.mask_array
    assert a[1042, 265] == 1
    assert a[1042, 493] == 1
    assert a[1042, 980] == 0
