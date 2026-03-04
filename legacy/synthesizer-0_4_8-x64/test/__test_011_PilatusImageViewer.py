# -*- coding: utf-8 -*-
"""
   tests for PilatusImageViewer.py

"""
from __future__ import unicode_literals

import sys
import os
import time
from nose.tools import eq_
import numpy as np

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from OurTkinter         import Tk
from SAnglerMask        import SAnglerMask
from PilatusImage       import PilatusImage
from PilatusImageViewer import PilatusImageViewer
from Preferences        import set_preference, get_preference

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

in_folder       = env_dict['in_folder1_AgBh_center']
tif_file        = in_folder + '/AgBh002_0_00000.tif'
tif_file1       = in_folder + '/AgBh002_1_00000.tif'
tif_file2       = in_folder + '/AgBh002_2_00000.tif'
mask_file       = in_folder + '/20151019cent01_0_00000.mask'
mask_array      = SAnglerMask( mask_file ).mask_array
empty_folder    = env_dict['empty_folder']
out_file        = empty_folder + '/saved.tif'
expected_adj_folder = env_dict[ 'expected_adj_folder' ]

tick            = 500
sample_id       = 'AgBh002'
color_map       = 'color_map'

def test_setup():
    global orig_cmap
    global root

    orig_cmap   = get_preference( color_map )
    root = Tk.Tk()
    root.iconify()

def show_image():
    pim         = PilatusImage( tif_file )
    im_array    = pim.image_array()
    exec_params = [ [ 'AgBh002_0_00000.tif', im_array ] ]
    viewer      = PilatusImageViewer( 1, sample_id, exec_params )
    time.sleep( 0.5 )
    # root.after( tick, lambda: viewer.quit_button.invoke() )
    viewer.quit_button.invoke()

def test_AlbulaLike():
    set_preference( color_map, 'ALBULA')
    show_image()

def test_Diverging():
    set_preference( color_map, 'Diverging')
    show_image()

def test_teardown():
    global root
    root.destroy()
    root = None
    set_preference( color_map, orig_cmap)

if __name__ == '__main__':
    test_setup()
    test_AlbulaLike()
    test_Diverging()
    test_teardown()

