"""Tests for core/minimal_tiff.py.

Original: test/test_030_MinimalTiff.py  (nose → pytest)
Requires external measurement data — auto-skipped when unavailable.
"""

import os
import pytest
import numpy as np

pytestmark = pytest.mark.requires_data


@pytest.fixture(scope='module')
def pilatus_tif_path(tif_folder):
    return os.path.join(tif_folder, 'AgBh0_0_00000.tif')


def test_read_matches_fabio(pilatus_tif_path):
    fabio = pytest.importorskip('fabio')
    from pilatus_synthesizer.core.minimal_tiff import MinimalTiff
    m_image = MinimalTiff(pilatus_tif_path)
    f_image = fabio.open(pilatus_tif_path)
    assert (m_image.data == f_image.data).all()


def test_save_roundtrip(pilatus_tif_path, tmp_path):
    fabio = pytest.importorskip('fabio')
    from pilatus_synthesizer.core.minimal_tiff import MinimalTiff
    m_image = MinimalTiff(pilatus_tif_path)
    f_image = fabio.open(pilatus_tif_path)

    out_path = str(tmp_path / 'minimal_temp1.tif')
    m_image.save(out_path)
    m_reloaded = MinimalTiff(out_path)
    assert (m_reloaded.data == f_image.data).all()


def test_data_is_read_only(pilatus_tif_path):
    from pilatus_synthesizer.core.minimal_tiff import MinimalTiff
    m_image = MinimalTiff(pilatus_tif_path)
    with pytest.raises(Exception):
        m_image.data[0, 0] = 0


def test_data_writable_via_copy(pilatus_tif_path):
    from pilatus_synthesizer.core.minimal_tiff import MinimalTiff
    m_image = MinimalTiff(pilatus_tif_path)
    data = np.array(m_image.data)      # copy
    data[0, 0] = 0                     # must not raise


def test_read_pillow_written_tif(pilatus_tif_path, tmp_path):
    from PIL import Image
    from pilatus_synthesizer.core.minimal_tiff import MinimalTiff
    p_image = Image.open(pilatus_tif_path)
    pillow_path = str(tmp_path / 'pillow_temp.tif')
    p_image.save(pillow_path)

    m_image = MinimalTiff(pillow_path)
    p_array = np.array(p_image)
    assert (m_image.data == p_array).all()


def test_float_tif_roundtrip(pilatus_tif_path, tmp_path):
    from PIL import Image
    from pilatus_synthesizer.core.minimal_tiff import MinimalTiff
    p_image = Image.open(pilatus_tif_path)
    p_array = np.array(p_image, dtype=float)
    im = Image.fromarray(p_array)
    float_path = str(tmp_path / 'float_temp.tif')
    im.save(float_path)

    m_float = MinimalTiff(float_path)
    assert (m_float.data == p_array).all()
