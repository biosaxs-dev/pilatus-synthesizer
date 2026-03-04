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

in_folder   = env_dict['in_folder_20180307']
emp_folder  = env_dict['empty_folder']
adj_folder  = env_dict['empty_folder']
syn_folder  = env_dict['empty_folder']
logfile_name = 'measurement_20180307.log'

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
    eq_( log_file, logfile_name )

    log_file, mask_file = get_in_folder_info( adj_folder )
    eq_( log_file, None )
    eq_( mask_file, None )

def test_get_data_info():
    log_file_path_ = in_folder + '/' + logfile_name
    log_file, mask_file, data_array, pilatus_counter = get_data_info( in_folder, adj_folder, syn_folder, None, 'C2',
                                                            log_file_path=log_file_path_
                                                            )

    assert os.path.isfile( os.path.join( in_folder, log_file ) )
    assert os.path.isfile( os.path.join( in_folder, mask_file ) )

    eq_( pilatus_counter.__class__, PilatusCounter.Counter )

    # print( 'data_array[0:3]=', data_array[0:3] )

    # 0     ME67_0*.tif
    info_array = data_array[ 0 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['ME67_0_d0_00000.tif', ['0.00000000', '0.0000'], 1.0, None, None] )
    eq_( info_array[1], ['ME67_0_d1_00000.tif', ['5', '3'], 1.1271186440677967, None, None] )
    eq_( info_array[2], ['ME67_0_d2_00000.tif', ['-5', '-3'], 0.90677966101694918, None, None] )

    # 1     ME67_1*.tif
    info_array = data_array[ 1 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['ME67_1_d0_00000.tif', ['0.00000000', '0.0000'], 1.0, None, None] )
    eq_( info_array[1], ['ME67_1_d1_00000.tif', ['5', '3'], 1.1330472103004292, None, None] )
    eq_( info_array[2], ['ME67_1_d2_00000.tif', ['-5', '-3'], 1.0772532188841202, None, None] )

    # 8     ME67_8*.tif
    info_array = data_array[ 8 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['ME67_8_d0_00000.tif', ['0.00000000', '0.0000'], 1.0, None, None] )
    eq_( info_array[1], ['ME67_8_d1_00000.tif', ['5', '3'], 1.1638655462184875, None, None] )
    eq_( info_array[2], ['ME67_8_d2_00000.tif', ['-5', '-3'], 1.0042016806722689, None, None] )

    # 9-17      ME66_0*.tif
    info_array = data_array[ 9 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['ME66_0_d0_00000.tif', ['0.00000000', '0.0000'], 1.0, None, None] )
    eq_( info_array[1], ['ME66_0_d1_00000.tif', ['5', '3'], 0.98023715415019763, None, None] )
    eq_( info_array[2], ['ME66_0_d2_00000.tif', ['-5', '-3'], 1.0316205533596838, None, None] )
    info_array = data_array[ 17 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['ME66_8_d0_00000.tif', ['0.00000000', '0.0000'], 1.0, None, None] )
    eq_( info_array[1], ['ME66_8_d1_00000.tif', ['5', '3'], 1.0794979079497908, None, None] )
    eq_( info_array[2], ['ME66_8_d2_00000.tif', ['-5', '-3'], 1.0418410041841004, None, None] )

    # 18-22     HM39_0*.tif
    info_array = data_array[ 18 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['HM39_0_d0_00000.tif', ['0.00000000', '0.0000'], 1.0, None, None] )
    eq_( info_array[1], ['HM39_0_d1_00000.tif', ['5', '3'], 0.92213114754098358, None, None] )
    eq_( info_array[2], ['HM39_0_d2_00000.tif', ['-5', '-3'], 0.93852459016393441, None, None] )
    info_array = data_array[ 22 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['HM39_4_d0_00000.tif', ['0.00000000', '0.0000'], 1.0, None, None] )
    eq_( info_array[1], ['HM39_4_d1_00000.tif', ['5', '3'], 1.0344827586206897, None, None] )
    eq_( info_array[2], ['HM39_4_d2_00000.tif', ['-5', '-3'], 1.2025862068965518, None, None] )

def test_data_array_order():
    # （変更した）作成ロジックから自明なので省略
    pass

if __name__ == '__main__':
    test_get_in_folder_info()
    test_get_data_info()
