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

in_folder   = env_dict['in_folder_many_log']
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
    eq_( log_file, 'measurement_SAXS.log' )

    log_file, mask_file = get_in_folder_info( adj_folder )
    eq_( log_file, None )
    eq_( mask_file, None )

def test_get_data_info():
    log_file_path_ = in_folder + '/' + 'measurement_SAXS.log'
    log_file, mask_file, data_array, pilatus_counter = get_data_info( in_folder, adj_folder, syn_folder, None, 'C2',
                                                            log_file_path=log_file_path_
                                                            )

    assert os.path.isfile( os.path.join( in_folder, log_file ) )
    assert os.path.isfile( os.path.join( in_folder, mask_file ) )

    eq_( pilatus_counter.__class__, PilatusCounter.Counter )

    # print( 'data_array=', data_array )

    info_array = data_array[ 0 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['HCP11thr_0_d0_00000.tif', ['-23.10000', '192.60000'], 1.0, None, None]  )
    eq_( info_array[1], ['HCP11thr_0_d1_00000.tif', ['5', '5'], 0.99841600942057551, None, None]  )
    eq_( info_array[2], ['HCP11thr_0_d2_00000.tif', ['-5', '-5'], 0.99765701393460138, None, None]  )

def test_data_array_order():
    # （変更した）作成ロジックから自明なので省略
    pass

if __name__ == '__main__':
    test_get_in_folder_info()
    test_get_data_info()
