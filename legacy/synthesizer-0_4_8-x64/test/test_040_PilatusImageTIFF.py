# -*- coding: utf-8 -*-
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
from SAnglerMask    import SAnglerMask
from PilatusImage   import PilatusImage, pixel_rounded_shift
from Development    import get_devel_info, set_devel_info
from PIL            import Image as ImagePIL
from TestUtils      import OldPilatusImage

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

in_folder           = env_dict['in_folder1_AgBh_center']
tif_file           = in_folder + '/AgBh002_0_00000.tif'
tif_file1          = in_folder + '/AgBh002_1_00000.tif'
tif_file2          = in_folder + '/AgBh002_2_00000.tif'
mask_file           = in_folder + '/20151019cent01_0_00000.mask'
mask_array          = SAnglerMask( mask_file ).mask_array
empty_folder        = env_dict['empty_folder']
out_file            = empty_folder + '/saved.tif'
expected_adj_folder = env_dict[ 'expected_adj_folder' ]
round_adj_folder    = env_dict[ 'round_adj_folder' ]


adj_algo = 'adj_algorithm'

def test_setup():
    global orig_algo
    orig_algo = get_devel_info( adj_algo )

def test_save():
    pim_a = PilatusImage( tif_file )
    pim_a.save( out_file ) 

def test_diff():
    pim_a = PilatusImage( tif_file )
    pim_b = PilatusImage( out_file )

    pim_c = pim_a.diff( pim_b )
    assert( ( pim_c.image_array() == np.zeros( pim_a.image_array().shape ) ).all() )

    assert( pim_a.equal( pim_b ) )

    os.remove( out_file )

size_of_pixel   = 172
minus_escape    = 1000

def gaussian_division( x ):
    assert -minus_escape * size_of_pixel < x and x < minus_escape * size_of_pixel
    if x >= 0:
        ix = x // size_of_pixel
        dx = x %  size_of_pixel
    else:
        x += size_of_pixel * minus_escape
        ix = x // size_of_pixel
        dx = x %  size_of_pixel
        ix -= minus_escape
    return ix, dx

"""
    整数の割り算がガウス記号の整数部分と一致することを確認する。
"""
def test_division():
    x = 5000
    ix = x // size_of_pixel
    dx = x %  size_of_pixel
    eq_( ix, 29 )
    eq_( dx, 12 )
    x = -5000
    ix = x // size_of_pixel
    dx = x %  size_of_pixel
    eq_( ix, -30 )
    eq_( dx, 160 )
    ix, dx = gaussian_division( -5000 )
    eq_( ix, -30 )
    eq_( dx, 160 )

def test_pixel_rounded_shift():
    eq_( pixel_rounded_shift(  5074 ),  30 )
    eq_( pixel_rounded_shift(  5073 ),  29 )
    eq_( pixel_rounded_shift(  5000 ),  29 )
    eq_( pixel_rounded_shift(  4902 ),  29 )
    eq_( pixel_rounded_shift(  4901 ),  28 )
    eq_( pixel_rounded_shift( -4901 ), -28 )
    eq_( pixel_rounded_shift( -4902 ), -28 )    # not symmmetric between positive and negative
    eq_( pixel_rounded_shift( -5000 ), -29 )
    eq_( pixel_rounded_shift( -5073 ), -29 )
    eq_( pixel_rounded_shift( -5074 ), -29 )    # not symmmetric between positive and negative
    eq_( pixel_rounded_shift( -5075 ), -30 )

def test_slow_adjust():
    set_devel_info( adj_algo, 'slow' )
    adjusted_pim = PilatusImage( tif_file1, mask_array, 5000, 3000 )
    expected_pim = PilatusImage( expected_adj_folder + '/AgBh002_1_adj.tif' )
    assert( adjusted_pim.equal( expected_pim ) )

    adjusted_pim = PilatusImage( tif_file2, mask_array, -5000, -3000 )
    expected_pim = PilatusImage( expected_adj_folder + '/AgBh002_2_adj.tif' )
    assert( adjusted_pim.equal( expected_pim ) )

def test_fast_adjust():
    set_devel_info( adj_algo, 'fast' )
    adjusted_pim = PilatusImage( tif_file1, mask_array, 5000, 3000 )
    expected_pim = PilatusImage( expected_adj_folder + '/AgBh002_1_adj.tif' )
    assert( adjusted_pim.equal( expected_pim ) )

    # print( 'adjusted_pim.imarray.dtype=', adjusted_pim.imarray.dtype )

    adjusted_pim = PilatusImage( tif_file2, mask_array, -5000, -3000 )
    expected_pim = PilatusImage( expected_adj_folder + '/AgBh002_2_adj.tif' )
    assert( adjusted_pim.equal( expected_pim ) )

def test_round_adjust():
    set_devel_info( adj_algo, 'round' )
    original_pim = PilatusImage( tif_file1 )
    original_im_array = original_pim.image_array()
    rows, cols = original_im_array.shape

    # np.savetxt("original_im_array_TL.csv", original_im_array[0:100,0:100], delimiter=",")
    # np.savetxt("original_im_array_BR.csv", original_im_array[-100:,-100:], delimiter=",")

    ir_ = pixel_rounded_shift( 5000 )
    ic_ = pixel_rounded_shift( 3000 )

    adjusted_pim = PilatusImage( tif_file1, mask_array, 5000, 3000 )
    adjusted_im_array = adjusted_pim.image_array()

    # np.savetxt("adjusted_im_array_TL.csv", adjusted_im_array[0:100,0:100], delimiter=",")
    # np.savetxt("adjusted_im_array_BR.csv", adjusted_im_array[-100:,-100:], delimiter=",")

    # 左上隅の確認
    for i in range(10):
        for j in range(10):
            eq_( original_im_array[i+ir_,j+ic_], adjusted_im_array[i,j] )

    # 右下隅（無効値 -2）の確認
    for i in range(rows-ir_,rows):
        for j in range(cols-ic_, cols):
            eq_( adjusted_im_array[i,j], -2 )

    # 有効値右下隅の確認
    rows -= ir_
    cols -= ic_
    for i in range(rows-10,rows):
        for j in range(cols-10, cols):
            eq_( original_im_array[i+ir_,j+ic_], adjusted_im_array[i,j] )

    # expected_pim = PilatusImage( round_adj_folder + '/AgBh002_1_adj.tif' )
    expected_pim = OldPilatusImage( round_adj_folder + '/AgBh002_1_adj.tif', original_image=adjusted_pim )
    assert( adjusted_pim.equal( expected_pim ) )

    adjusted_pim = PilatusImage( tif_file2, mask_array, -5000, -3000 )
    # expected_pim = PilatusImage( round_adj_folder + '/AgBh002_2_adj.tif' )
    expected_pim = OldPilatusImage( round_adj_folder + '/AgBh002_2_adj.tif', original_image=adjusted_pim )

    assert( adjusted_pim.equal( expected_pim ) )

def test_teardown():
    set_devel_info( adj_algo, orig_algo )

if __name__ == '__main__':
    test_setup()
    test_save()
    test_diff()
    # test_slow_adjust()
    test_fast_adjust()
    test_round_adjust()
    test_teardown()
