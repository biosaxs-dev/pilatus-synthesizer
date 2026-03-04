"""Tests for core/pilatus_utils.py.

Original: test/test_020_PilatusUtils.py  (nose → pytest)
Requires external measurement data — auto-skipped when unavailable.
"""

import os
import pytest

from pilatus_synthesizer.core.pilatus_counter import Counter

pytestmark = pytest.mark.requires_data


def test_get_in_folder_info_with_data(in_folder1):
    from pilatus_synthesizer.core.pilatus_utils import get_in_folder_info
    log_file, mask_file = get_in_folder_info(in_folder1)
    assert log_file is not None
    assert mask_file is not None
    assert os.path.isfile(os.path.join(in_folder1, log_file))
    assert os.path.isfile(os.path.join(in_folder1, mask_file))


def test_get_in_folder_info_empty(empty_folder):
    from pilatus_synthesizer.core.pilatus_utils import get_in_folder_info
    log_file, mask_file = get_in_folder_info(empty_folder)
    assert log_file is None
    assert mask_file is None


def test_get_data_info(in_folder1, empty_folder):
    from pilatus_synthesizer.core.pilatus_utils import get_data_info
    log_file, mask_file, data_array, pilatus_counter = get_data_info(
        in_folder1, empty_folder, empty_folder, None, 'C2'
    )
    assert os.path.isfile(os.path.join(in_folder1, log_file))
    assert os.path.isfile(os.path.join(in_folder1, mask_file))
    assert isinstance(pilatus_counter, Counter)

    info_array = data_array[0][1]
    assert len(info_array) == 3
    assert info_array[0] == [
        'AgBh002_0_00000.tif', ['0.70000', '-0.35000'], 1.0, None, None
    ]
    assert info_array[1][0] == 'AgBh002_1_00000.tif'
    assert info_array[2][0] == 'AgBh002_2_00000.tif'
