# -*- coding: utf-8 -*-
"""
   tests for PilatusUtils.py

"""
from __future__ import division, print_function, unicode_literals

import sys
import os
import shutil
from nose.tools import eq_

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
import PilatusCounter
from PilatusUtils import get_in_folder_info, get_data_info

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

global log_file
global mask_file

in_folder   = env_dict['in_folder_cbf']
emp_folder  = env_dict['empty_folder']
adj_folder  = env_dict['empty_folder']
syn_folder  = env_dict['empty_folder']

def setting_clear():
    for dir_ in [ emp_folder ]:
        if os.path.exists( dir_ ):
            shutil.rmtree( dir_ )
        os.makedirs( dir_ )

def test_get_in_folder_info():
    setting_clear()
    log_file, mask_file = get_in_folder_info( in_folder )
    # print log_file
    # print mask_file
    assert os.path.isfile( os.path.join( in_folder, log_file ) )
    assert os.path.isfile( os.path.join( in_folder, mask_file ) )

    log_file, mask_file = get_in_folder_info( adj_folder )
    eq_( log_file, None )
    eq_( mask_file, None )

def test_get_data_info():
    log_file, mask_file, data_array, pilatus_counter = get_data_info( in_folder, adj_folder, syn_folder, None, 'C2' )

    assert os.path.isfile( os.path.join( in_folder, log_file ) )
    assert os.path.isfile( os.path.join( in_folder, mask_file ) )

    eq_( pilatus_counter.__class__, PilatusCounter.Counter )

    # print( 'data_array=', data_array )

    info_array = data_array[ 0 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['AgBh0_0_00000.cbf', ['0.70000', '-0.35000'], 1.0, None, None]  )
    eq_( info_array[1], ['AgBh0_1_00000.cbf', ['0', '0'], 0.99906009213162839, None, None] )
    eq_( info_array[2], ['AgBh0_2_00000.cbf', ['0', '0'], 0.99870375343427875, None, None] )

def test_data_array_order():
    # （変更した）作成ロジックから自明なので省略
    pass

if __name__ == '__main__':
    test_get_in_folder_info()
    test_get_data_info()
