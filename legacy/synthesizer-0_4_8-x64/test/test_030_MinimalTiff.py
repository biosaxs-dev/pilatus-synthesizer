# coding: utf-8
"""
   tests for MinimalTiff.py

"""
from __future__ import division, print_function, unicode_literals

import sys
import os
import shutil
from nose.tools import eq_
import numpy    as np
import fabio
from PIL        import Image

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from BasicUtils         import mkdirs_with_retry
from MinimalTiff        import MinimalTiff

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

tif_folder = env_dict[ 'tif_folder' ]
pilatus_tif_file = tif_folder + '/AgBh0_0_00000.tif'
minimal_tif_file1 = 'temp/minimal-temp1.tif'
pillow_tif_file = 'temp/pillow-temp.tif'
float_tif_file  = 'temp/pillow-float.tif'

def test_load():
    pass

def test_setup():
    mkdirs_with_retry( 'temp' )

def test_PilatusImage():
    m_image = MinimalTiff( pilatus_tif_file )
    print( 'm_image.data.shape=',  m_image.data.shape )
    print( 'm_image.data.dtype=',  m_image.data.dtype )
    print( m_image.pre_ifd_texts )
    f_image = fabio.open( pilatus_tif_file )

    print( 'f_image.data.shape=',  f_image.data.shape )
    eq_( ( m_image.data == f_image.data ).all(), True )

    m_image.save( minimal_tif_file1 )
    m_image = MinimalTiff( minimal_tif_file1 )
    eq_( ( m_image.data == f_image.data ).all(), True )

    # print( m_image.data.flags )
    try:
        m_image.data[ 0, 0 ] = 0
        assert( False )
    except:
        assert( True )
    # m_image.data.flags[ 'WRITEABLE' ] = True
    # m_image.data[ 0, 0 ] = 0
    data = np.array(m_image.data)
    data[ 0, 0 ] = 0

def test_PillowImage():
    global p_imarray
    p_image = Image.open( pilatus_tif_file )
    p_image.save( pillow_tif_file )

    print( 'int tiff by pillow' )
    m_image = MinimalTiff( pillow_tif_file )
    p_imarray = np.array( p_image )
    eq_( ( m_image.data == p_imarray ).all(), True )

    m_image.save( minimal_tif_file1 )
    print( 'int tiff by minimal' )
    m_image = MinimalTiff( minimal_tif_file1 )
    eq_( ( m_image.data == p_imarray ).all(), True )

def test_FloatType():
    global p_imarray
    print( 'p_imarray.dtype=', p_imarray.dtype )
    imarray_float = np.array( p_imarray, dtype=float )
    print( 'imarray_float.dtype=', imarray_float.dtype )
    im = Image.fromarray( imarray_float )
    im.save( float_tif_file )
    # TODO:
    print( 'float tiff by pillow' )
    m_image_float = MinimalTiff( float_tif_file )
    eq_( ( m_image_float.data == imarray_float ).all(), True )

    print( 'm_image_float.data.dtype=', m_image_float.data.dtype )

def ___memo():
    image = MinimalTiff( fabio_tif_file )
    print( 'pre_ifd_texts=', image.pre_ifd_texts )
    pillow_tif_file = './temp-pil.tif'
    image = MinimalTiff( pillow_tif_file )
    print( 'pre_ifd_texts=', image.pre_ifd_texts )

def test_teardown():
    shutil.rmtree( 'temp' )

if __name__ == '__main__':
    test_setup()
    test_PilatusImage()
    test_PillowImage()
    test_FloatType()
    test_teardown()
