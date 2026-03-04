# coding: utf-8
"""
   tests for PilatusImagePIL.py

"""
from __future__ import unicode_literals

import sys
import os
from nose.tools import eq_
import numpy as np

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from PIL                    import Image    as ImagePIL
from PilatusImage           import PilatusImage

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def get_valid_index( X ):
    return np.logical_and( np.logical_not( np.isnan( X ) ), np.logical_not( np.isinf( X ) ) )

def test_load():
    assert True

def test_setup():
    global tif_file, cbf_file
    tif_dir     = env_dict[ 'in_folder_cbf_tif' ]
    tif_file    = tif_dir + '/' + 'AgBh0_0_00000.tif'
    cbf_dir     = env_dict[ 'in_folder_cbf' ]
    cbf_file    = cbf_dir + '/' + 'AgBh0_0_00000.cbf'
    pass

def test_tif_compare():
    global tif_file, tif_im_m
    tif_im_m = PilatusImage( tif_file )
    im = ImagePIL.open(tif_file  )
    im_array = np.array( im )

    eq_( ( tif_im_m.imarray == im_array ).all(), True )

def test_cbf_compare():
    global cbf_file, tif_im_m
    cbf_im_f = PilatusImage( cbf_file )
    max_ = np.max( np.abs( cbf_im_f.imarray - tif_im_m.imarray ) )
    # print( 'max_=', max_ )
    assert( max_ < 1300 )

def test_teardown():
    pass

if __name__ == '__main__':
    test_setup()
    test_tif_compare()
    test_cbf_compare()
    test_teardown()

