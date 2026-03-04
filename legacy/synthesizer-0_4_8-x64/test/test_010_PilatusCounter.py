# -*- coding: utf-8 -*-
"""
   tests for PilatusCounter.py

"""
from __future__ import division, print_function, unicode_literals

import sys
import os

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from NoseTools import eq_
import PilatusCounter


sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

def test_get_counter_dict():
    in_folder   = env_dict['in_folder1_AgBh_center']
    pilatus_counter = PilatusCounter.Counter( in_folder )

    dict_ = pilatus_counter.get_counter_dict( 'C1' )
    assert len( dict_.keys() ) == 3
    eq_( dict_[ 'AgBh002_0' ], 0 )
    eq_( dict_[ 'AgBh002_1' ], 0 )
    eq_( dict_[ 'AgBh002_2' ], 0 )

    dict_ = pilatus_counter.get_counter_dict( 'C2' )
    assert len( dict_.keys() ) == 3
    eq_( dict_[ 'AgBh002_0' ], 193636 )
    eq_( dict_[ 'AgBh002_1' ], 193454 )
    eq_( dict_[ 'AgBh002_2' ], 193385 )

    dict_ = pilatus_counter.get_counter_dict( 'C8' )
    assert len( dict_.keys() ) == 3
    eq_( dict_[ 'AgBh002_0' ], 0 )
    eq_( dict_[ 'AgBh002_1' ], 0 )
    eq_( dict_[ 'AgBh002_2' ], 0 )

def test_get_counter_dict_older_format():
    # MAG2wk7210_0_00000-0
    in_folder   = env_dict['in_folder2']
    pilatus_counter = PilatusCounter.Counter( in_folder )

    dict_ = pilatus_counter.get_counter_dict( 'C1' )
    assert len( dict_.keys() ) >= 2
    eq_( dict_[ 'MAG2wk7210_0' ], 6489421 )
    eq_( dict_[ 'MAG2wk7210_1' ], 6475856 )

    dict_ = pilatus_counter.get_counter_dict( 'C3' )
    assert len( dict_.keys() ) >= 2
    eq_( dict_[ 'MAG2wk7241_0' ], 194128 )
    eq_( dict_[ 'MAG2wk7241_1' ], 192835 )

def test_available_counters():
    in_folder   = env_dict['in_folder2_Detector_move']
    pilatus_counter = PilatusCounter.Counter( in_folder )
    counters = pilatus_counter.available_counters()
    eq_( counters, [ 'C1', 'C2', 'C3' ] )

def test_20240927():
    in_folder = r"E:\TODO\20241001\Synthesizer"
    pilatus_counter = PilatusCounter.Counter( in_folder )
    dict_ = pilatus_counter.get_counter_dict( 'C1' )
    print(dict_['casec292saxs_001_c0_8500eV_n0_d0'])

if __name__ == "__main__":
    # test_load()
    # test_get_counter_dict()
    # test_get_counter_dict_older_format()
    # test_available_counters()
    test_20240927()
    print( 'OK' )
