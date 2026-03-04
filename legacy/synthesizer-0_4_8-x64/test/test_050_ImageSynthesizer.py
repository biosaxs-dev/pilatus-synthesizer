# -*- coding: utf-8 -*-
"""
   tests for ImageSynthesizer.py

"""
from __future__ import division, print_function, unicode_literals

import sys
import os
import time
from nose.tools         import eq_
import numpy as np
from pyautogui          import typewrite

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib/ExecutionWindow/bin' )

from Development        import set_devel_info
from Preferences        import get_preference, set_preference
from SynthesizerSettings    import get_setting, set_setting, set_mask
from OurTkinter         import Tk
from ImageSynthesizer   import ImageSynthesizer

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

in_folder           = env_dict['in_folder1_AgBh_center']
mask_file           = in_folder + '/20151019cent01_0_00000.mask'
expected_adj_folder = env_dict[ 'expected_adj_folder' ]
adj_folder          = env_dict['test_adj_folder']
syn_folder          = env_dict['test_syn_folder']

syn_method  = 'syn_method'

ENTER       = [ 'enter' ]
tick        = 500

def test_setup():
    global orig_method
    global orig_adj_folder
    global orig_syn_folder
    orig_method     = get_preference( syn_method )
    set_devel_info( 'min_ratio', 0.5 )
    set_preference( 'syn_flags', [ 1, 1, 1, 1 ] )
    set_devel_info( 'adj_output', 'YES' )
    set_devel_info( 'intermediate_results', 'YES' )
    set_devel_info( 'postfix_adj', '_adj' )
    set_preference( 'postfix_syn', '_syn' )
    set_setting( 'in_folder', in_folder )
    set_setting( 'adj_folder', adj_folder )
    set_setting( 'syn_folder', syn_folder )
    set_mask( mask_file )

def make_exec_array():
    global exec_array
    exec_array = []
    exec_rec= ['AgBh002', [
                    ['AgBh002_0_00000.tif', ['0.70000', '-0.35000'],    1.0, None, 'AgBh002_syn.tif'],
                    ['AgBh002_1_00000.tif', ['5', '3'],                 1.0, 'AgBh002_1_adj.tif', 'AgBh002_syn.tif'],
                    ['AgBh002_2_00000.tif', ['-5', '-3'],               1.0, 'AgBh002_2_adj.tif', 'AgBh002_syn.tif']
                    ]
              ]

    exec_array.append( exec_rec )

    return exec_array

def test_cover():
    set_preference( syn_method, 'cover' )

    exec_array = make_exec_array()

    root = Tk.Tk()
    root.withdraw()
    synthesizer = ImageSynthesizer( root )
    i = 0
    i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )
    i += 4; root.after( i*tick, lambda: typewrite( ENTER ) )
    synthesizer.execute( 3, exec_array )
    # TODO: expected result
    root.destroy()

def test_averege():
    set_preference( syn_method, 'average' )

    exec_array = make_exec_array()

    root = Tk.Tk()
    root.withdraw()
    synthesizer = ImageSynthesizer( root )
    i = 0
    i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )
    i += 4; root.after( i*tick, lambda: typewrite( ENTER ) )
    synthesizer.execute( 3, exec_array )
    # TODO: expected result
    root.destroy()

def test_teardown():
    set_preference( syn_method, orig_method )

if __name__ == '__main__':
    test_setup()
    test_cover()
    test_teardown()

