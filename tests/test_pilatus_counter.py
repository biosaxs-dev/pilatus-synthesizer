"""Tests for core/pilatus_counter.py.

Original: test/test_010_PilatusCounter.py  (nose → pytest)
Requires external measurement data — auto-skipped when unavailable.
"""

import pytest

pytestmark = pytest.mark.requires_data


@pytest.fixture(scope='module')
def counter_agbh(in_folder1):
    from pilatus_synthesizer.core.pilatus_counter import Counter
    return Counter(in_folder1)


@pytest.fixture(scope='module')
def counter_mag2(env):
    from pilatus_synthesizer.core.pilatus_counter import Counter
    return Counter(env['in_folder2'])


@pytest.fixture(scope='module')
def counter_detector_move(env):
    from pilatus_synthesizer.core.pilatus_counter import Counter
    return Counter(env['in_folder2_Detector_move'])


# ── AgBh dataset (newer format) ──────────────────────────────────────────

def test_get_counter_C1_agbh(counter_agbh):
    d = counter_agbh.get_counter_dict('C1')
    assert len(d) == 3
    assert d['AgBh002_0'] == 0
    assert d['AgBh002_1'] == 0
    assert d['AgBh002_2'] == 0


def test_get_counter_C2_agbh(counter_agbh):
    d = counter_agbh.get_counter_dict('C2')
    assert len(d) == 3
    assert d['AgBh002_0'] == 193636
    assert d['AgBh002_1'] == 193454
    assert d['AgBh002_2'] == 193385


def test_get_counter_C8_agbh(counter_agbh):
    d = counter_agbh.get_counter_dict('C8')
    assert len(d) == 3
    assert d['AgBh002_0'] == 0
    assert d['AgBh002_1'] == 0
    assert d['AgBh002_2'] == 0


# ── MAG2 dataset (older format) ──────────────────────────────────────────

def test_get_counter_C1_mag2(counter_mag2):
    d = counter_mag2.get_counter_dict('C1')
    assert len(d) >= 2
    assert d['MAG2wk7210_0'] == 6489421
    assert d['MAG2wk7210_1'] == 6475856


def test_get_counter_C3_mag2(counter_mag2):
    d = counter_mag2.get_counter_dict('C3')
    assert len(d) >= 2
    assert d['MAG2wk7241_0'] == 194128
    assert d['MAG2wk7241_1'] == 192835


# ── available_counters ────────────────────────────────────────────────────

def test_available_counters(counter_detector_move):
    counters = counter_detector_move.available_counters()
    assert counters == ['C1', 'C2', 'C3']
