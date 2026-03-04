# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

import sys
import os
import time
from nose.tools import eq_
import numpy as np

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from SAnglerMask import SAnglerMask

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

def test_Constructor():
    in_folder   = env_dict['in_folder1_AgBh_center']
    filepath    = '/'.join( [ in_folder, '20151019cent01_0_00000.mask' ] )
    mask = SAnglerMask( filepath )
    eq_( type(mask.mask_array), np.ndarray )

    # ヘッダ情報の確認
    row, col = mask.mask_array.shape
    eq_( row, 1043 )
    eq_( col,  981 )

    # 先頭行の確認
    eq_( mask.mask_array[   0,   0], 0 )
    eq_( mask.mask_array[   0, 486], 0 )
    eq_( mask.mask_array[   0, 487], 1 )
    eq_( mask.mask_array[   0, 493], 1 )
    eq_( mask.mask_array[   0, 494], 0 )

    # 幅が大きい行の確認
    eq_( mask.mask_array[ 830,   0], 0 )
    eq_( mask.mask_array[ 831,   0], 1 )
    eq_( mask.mask_array[ 831,   1], 1 )
    eq_( mask.mask_array[ 831, 980], 1 )
    eq_( mask.mask_array[ 847,   0], 1 )
    eq_( mask.mask_array[ 847,   1], 1 )
    eq_( mask.mask_array[ 847, 980], 1 )
    eq_( mask.mask_array[ 848,   0], 0 )
    eq_( mask.mask_array[ 848, 486], 0 )
    eq_( mask.mask_array[ 848, 487], 1 )

    # 末尾行の確認
    eq_( mask.mask_array[1042, 265], 1 )
    eq_( mask.mask_array[1042, 493], 1 )
    eq_( mask.mask_array[1042, 980], 0 )

if __name__ == '__main__':
    test_Constructor()
