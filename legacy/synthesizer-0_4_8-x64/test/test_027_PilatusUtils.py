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

in_folder   = env_dict['in_folder_20180221']
emp_folder  = env_dict['empty_folder']
adj_folder  = env_dict['empty_folder']
syn_folder  = env_dict['empty_folder']
logfile_name = 'measurement_20180221.log'

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

    # print( 'data_array=', data_array )

    # 0     test.tif
    info_array = data_array[ 0 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test_1552A_0_d0_00000.tif', ['-16.00000', '166.00000'], 1.0, None, None] )
    eq_( info_array[1], ['test_1552A_0_d1_00000.tif', ['10', '6'], 1.0000143769049399, None, None] )
    eq_( info_array[2], ['test_1552A_0_d2_00000.tif', ['-10', '-6'], 0.99735464949105757, None, None] )

    # 1     test.tif
    info_array = data_array[ 1 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test_1552A_1_d0_00000.tif', ['-16.00000', '166.00000'], 1.0, None, None] )
    eq_( info_array[1], ['test_1552A_1_d1_00000.tif', ['10', '6'], 1.0176810358764825, None, None] )
    eq_( info_array[2], ['test_1552A_1_d2_00000.tif', ['-10', '-6'], 1.0155939975602228, None, None] )

    # 2     test.tif
    info_array = data_array[ 2 ][ 1 ]
    eq_( len( info_array ), 2 )
    eq_( info_array[0], ['test_1552A_2_d0_00000.tif', ['-16.00000', '166.00000'], 1.0, None, None] )
    eq_( info_array[1], ['test_1552A_2_d1_00000.tif', ['10', '6'], 1.0000869729079391, None, None] )

    # 3-6   test2.tif
    info_array = data_array[ 3 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test2_1552A_0_d0_00000.tif', ['-16.00000', '166.00000'], 1.0, None, None] )
    eq_( info_array[1], ['test2_1552A_0_d1_00000.tif', ['10', '6'], 0.99837173802427859, None, None] )
    eq_( info_array[2], ['test2_1552A_0_d2_00000.tif', ['-10', '-6'], 0.99841535218434252, None, None] )
    info_array = data_array[ 6 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test2_1552A_3_d0_00000.tif', ['-16.00000', '166.00000'], 1.0, None, None] )
    eq_( info_array[1], ['test2_1552A_3_d1_00000.tif', ['10', '6'], 0.99849437216781167, None, None] )
    eq_( info_array[2], ['test2_1552A_3_d2_00000.tif', ['-10', '-6'], 0.99663791843297767, None, None] )

    # 7-10   test2.tif
    info_array = data_array[ 7 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test2_1551A_0_d0_00000.tif', ['-16.00000', '166.00000'], 1.0, None, None] )
    eq_( info_array[1], ['test2_1551A_0_d1_00000.tif', ['10', '6'], 0.99934970427027525, None, None] )
    eq_( info_array[2], ['test2_1551A_0_d2_00000.tif', ['-10', '-6'], 0.99603629269501126, None, None] )
    info_array = data_array[ 10 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test2_1551A_3_d0_00000.tif', ['-16.00000', '166.00000'], 1.0, None, None] )
    eq_( info_array[1], ['test2_1551A_3_d1_00000.tif', ['10', '6'], 0.98411023622047245, None, None] )
    eq_( info_array[2], ['test2_1551A_3_d2_00000.tif', ['-10', '-6'], 0.99399999999999999, None, None] )

    # 11-14   test2.tif
    info_array = data_array[ 11 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test2_1550A_0_d0_00000.tif', ['-16.00000', '166.00000'], 1.0, None, None] )
    eq_( info_array[1], ['test2_1550A_0_d1_00000.tif', ['10', '6'], 0.99802164355765977, None, None] )
    eq_( info_array[2], ['test2_1550A_0_d2_00000.tif', ['-10', '-6'], 0.99570510652688538, None, None] )
    info_array = data_array[ 14 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test2_1550A_3_d0_00000.tif', ['-16.00000', '166.00000'], 1.0, None, None] )
    eq_( info_array[1], ['test2_1550A_3_d1_00000.tif', ['10', '6'], 0.99908426490661228, None, None] )
    eq_( info_array[2], ['test2_1550A_3_d2_00000.tif', ['-10', '-6'], 0.99600877723448, None, None] )

    # 15-18 test3.tif
    info_array = data_array[ 15 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test3_7999eV_0_d0_00000.tif', ['-16.00000', '166.00000'], 1.0, None, None] )
    eq_( info_array[1], ['test3_7999eV_0_d1_00000.tif', ['10', '6'], 0.99849352742305608, None, None] )
    eq_( info_array[2], ['test3_7999eV_0_d2_00000.tif', ['-10', '-6'], 0.99393907544624871, None, None] )
    info_array = data_array[ 18 ][ 1 ]
    eq_( info_array[0], ['test3_7999eV_3_d0_00000.tif', ['-16.00000', '166.00000'], 1.0, None, None] )
    eq_( info_array[1], ['test3_7999eV_3_d1_00000.tif', ['10', '6'], 0.99815200229654089, None, None] )
    eq_( info_array[2], ['test3_7999eV_3_d2_00000.tif', ['-10', '-6'], 0.99389981340605715, None, None] )

    # 19-22 test3.tif
    info_array = data_array[ 19 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test3_8000eV_0_d0_00000.tif', ['-16.00000', '166.00000'], 1.0, None, None] )
    eq_( info_array[1], ['test3_8000eV_0_d1_00000.tif', ['10', '6'], 0.99726615537044516, None, None] )
    eq_( info_array[2], ['test3_8000eV_0_d2_00000.tif', ['-10', '-6'], 0.99530292466331516, None, None] )
    info_array = data_array[ 22 ][ 1 ]
    eq_( info_array[0], ['test3_8000eV_3_d0_00000.tif', ['-16.00000', '166.00000'], 1.0, None, None] )
    eq_( info_array[1], ['test3_8000eV_3_d1_00000.tif', ['10', '6'], 0.99874074352516629, None, None] )
    eq_( info_array[2], ['test3_8000eV_3_d2_00000.tif', ['-10', '-6'], 0.99492538435514788, None, None] )

    # 23-26 test3.tif
    info_array = data_array[ 23 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test3_8001eV_0_d0_00000.tif', ['-16.00000', '166.00000'], 1.0, None, None] )
    eq_( info_array[1], ['test3_8001eV_0_d1_00000.tif', ['10', '6'], 0.99829076243518344, None, None] )
    eq_( info_array[2], ['test3_8001eV_0_d2_00000.tif', ['-10', '-6'], 0.99637027078932205, None, None] )
    info_array = data_array[ 26 ][ 1 ]
    eq_( info_array[0], ['test3_8001eV_3_d0_00000.tif', ['-16.00000', '166.00000'], 1.0, None, None] )
    eq_( info_array[1], ['test3_8001eV_3_d1_00000.tif', ['10', '6'], 0.99715546836684654, None, None] )
    eq_( info_array[2], ['test3_8001eV_3_d2_00000.tif', ['-10', '-6'], 0.99342815105443849, None, None] )

def test_data_array_order():
    # （変更した）作成ロジックから自明なので省略
    pass

if __name__ == '__main__':
    test_get_in_folder_info()
    test_get_data_info()
