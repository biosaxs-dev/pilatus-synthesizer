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
from SynthesizerTestEnv import get_data_folder 

def test_load():
    assert True

global log_file
global mask_file

up_folder   = get_data_folder('20201012')
emp_folder  = get_data_folder('empty_folder')
adj_folder  = get_data_folder('empty_folder')
syn_folder  = get_data_folder('empty_folder')
logfile_name = 'measurement_test101.log'

def setting_clear():
    for dir_ in [ emp_folder ]:
        if os.path.exists( dir_ ):
            shutil.rmtree( dir_ )
        os.makedirs( dir_ )

def test_get_in_folder_info_101():
    setting_clear()
    in_folder = up_folder + '/test101' 
    log_file, mask_file = get_in_folder_info(in_folder)
    # print log_file
    # print mask_file
    assert os.path.isfile(os.path.join(in_folder, log_file))
    assert os.path.isfile(os.path.join(in_folder, mask_file))
    eq_( log_file, logfile_name )

    log_file, mask_file = get_in_folder_info( adj_folder )
    eq_( log_file, None )
    eq_( mask_file, None )

def test_20201012():
    in_folder = up_folder + '/test101' 

    log_file_path_ = in_folder + '/' + logfile_name
    log_file, mask_file, data_array, pilatus_counter = get_data_info( in_folder, adj_folder, syn_folder, None, 'C2',
                                                            log_file_path=log_file_path_
                                                            )

    assert os.path.isfile( os.path.join( in_folder, log_file ) )
    assert os.path.isfile( os.path.join( in_folder, mask_file ) )

    eq_( pilatus_counter.__class__, PilatusCounter.Counter )

    # print( 'data_array[0:3]=', data_array[0:3] )
    # print( 'data_array[-1]=', data_array[-1] )

    # 0     stest101_12000eV_n0_c0_d*_00000
    info_array = data_array[ 0 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['stest101_12000eV_n0_c0_d0_00000.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['stest101_12000eV_n0_c0_d1_00000.tif', ['0.5', '0.5'], 1.0, None, None] )
    eq_( info_array[2], ['stest101_12000eV_n0_c0_d2_00000.tif', ['-0.5', '-0.5'], 1.0138888888888888, None, None] )

    # 1     stest101_12000eV_n0_c0_d*_00001
    info_array = data_array[ 1 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['stest101_12000eV_n0_c0_d0_00001.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['stest101_12000eV_n0_c0_d1_00001.tif', ['0.5', '0.5'], 1.0, None, None] )
    eq_( info_array[2], ['stest101_12000eV_n0_c0_d2_00001.tif', ['-0.5', '-0.5'], 1.0138888888888888, None, None] )

    # 2     stest101_12000eV_n0_c0_d*_00002
    info_array = data_array[ 2 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['stest101_12000eV_n0_c0_d0_00002.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['stest101_12000eV_n0_c0_d1_00002.tif', ['0.5', '0.5'], 1.0, None, None] )
    eq_( info_array[2], ['stest101_12000eV_n0_c0_d2_00002.tif', ['-0.5', '-0.5'], 1.0138888888888888, None, None] )

def test_20201020_101():
    up_folder = get_data_folder('20201020')
    in_folder = os.path.join(up_folder, 'test101')

    log_file_path_ = os.path.join(in_folder, 'measurement_test101.log')
    log_file, mask_file, data_array, pilatus_counter = get_data_info( in_folder, adj_folder, syn_folder, None, 'C2',
                                                            log_file_path=log_file_path_
                                                            )

    # print( 'data_array[0:3]=', data_array[0:3] )

    # 0     test101_n0_c0_00000
    info_array = data_array[ 0 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test101_n0_c0_d0_00000.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['test101_n0_c0_d1_00000.tif', ['5', '3'], 0.9993102089081592, None, None] )
    eq_( info_array[2], ['test101_n0_c0_d2_00000.tif', ['-5', '-3'], 1.0006897910918409, None, None] )

    # -1    test101_n9_c1_d2_00002
    info_array = data_array[ -1 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test101_n9_c1_d0_00002.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['test101_n9_c1_d1_00002.tif', ['5', '3'], 1.0010190496540161, None, None] )
    eq_( info_array[2], ['test101_n9_c1_d2_00002.tif', ['-5', '-3'], 1.0008053779523676, None, None] )

def test_20201020_102():
    up_folder = get_data_folder('20201020')
    in_folder = os.path.join(up_folder, 'test102')

    log_file_path_ = os.path.join(in_folder, 'measurement_test102.log')
    log_file, mask_file, data_array, pilatus_counter = get_data_info( in_folder, adj_folder, syn_folder, None, 'C2',
                                                            log_file_path=log_file_path_
                                                            )

    # print( 'data_array[0:3]=', data_array[0:3] )

    # 0     test102_n0_c0_d0_00000
    info_array = data_array[ 0 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test102_n0_c0_d0_00000.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['test102_n0_c0_d1_00000.tif', ['5', '3'], 1.001084812623274, None, None] )
    eq_( info_array[2], ['test102_n0_c0_d2_00000.tif', ['-5', '-3'], 0.9999013806706114, None, None] )

    # -1    test102_n9_c1_d2_00002
    info_array = data_array[ -1 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test102_n9_c1_d0_00002.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['test102_n9_c1_d1_00002.tif', ['5', '3'], 1.0001313758334154, None, None] )
    eq_( info_array[2], ['test102_n9_c1_d2_00002.tif', ['-5', '-3'], 1.0003284395835386, None, None] )

def test_20201020_103():
    up_folder = get_data_folder('20201020')
    in_folder = os.path.join(up_folder, 'test103')

    log_file_path_ = os.path.join(in_folder, 'measurement_test103.log')
    log_file, mask_file, data_array, pilatus_counter = get_data_info( in_folder, adj_folder, syn_folder, None, 'C2',
                                                            log_file_path=log_file_path_
                                                            )

    # print( 'data_array[0:3]=', data_array[0:3] )

    # 0     test103_n0_d0_00000
    info_array = data_array[ 0 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test103_n0_d0_00000.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['test103_n0_d1_00000.tif', ['5', '3'], 1.0007883326763893, None, None] )
    eq_( info_array[2], ['test103_n0_d2_00000.tif', ['-5', '-3'], 1.0003613191433451, None, None] )

    # -1    test103_n9_d0_00000.tif
    info_array = data_array[ -1 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test103_n9_d0_00000.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['test103_n9_d1_00000.tif', ['5', '3'], 0.9992121331494977, None, None] )
    eq_( info_array[2], ['test103_n9_d2_00000.tif', ['-5', '-3'], 1.0002297944980632, None, None] )

def test_20201020_104():
    up_folder = get_data_folder('20201020')
    in_folder = os.path.join(up_folder, 'test104')

    log_file_path_ = os.path.join(in_folder, 'measurement_test104.log')
    log_file, mask_file, data_array, pilatus_counter = get_data_info( in_folder, adj_folder, syn_folder, None, 'C2',
                                                            log_file_path=log_file_path_
                                                            )

    # print( 'data_array[0:3]=', data_array[0:3] )

    # 0     test104_n0_d0_00000
    info_array = data_array[ 0 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test104_n0_d0_00000.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['test104_n0_d1_00000.tif', ['5', '3'], 0.9994745311832901, None, None] )
    eq_( info_array[2], ['test104_n0_d2_00000.tif', ['-5', '-3'], 0.9992610594765017, None, None] )

    # -1    test104_n9_d0_00000.tif
    info_array = data_array[ -1 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test104_n9_d0_00000.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['test104_n9_d1_00000.tif', ['5', '3'], 1.0002462326405988, None, None] )
    eq_( info_array[2], ['test104_n9_d2_00000.tif', ['-5', '-3'], 1.0002790636593453, None, None] )

def test_20201020_105():
    up_folder = get_data_folder('20201020')
    in_folder = os.path.join(up_folder, 'test105')

    log_file_path_ = os.path.join(in_folder, 'measurement_test105.log')
    log_file, mask_file, data_array, pilatus_counter = get_data_info( in_folder, adj_folder, syn_folder, None, 'C2',
                                                            log_file_path=log_file_path_
                                                            )

    # print( 'data_array[0:3]=', data_array[0:3] )

    # 0     test105_8266eV_n0_d0_00000
    info_array = data_array[ 0 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test105_8266eV_n0_d0_00000.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['test105_8266eV_n0_d1_00000.tif', ['5', '3'], 0.9995241611288866, None, None] )
    eq_( info_array[2], ['test105_8266eV_n0_d2_00000.tif', ['-5', '-3'], 0.9994585281811469, None, None] )

    # -1    test105_8269eV_n9_d0_00000.tif
    info_array = data_array[ -1 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test105_8269eV_n9_d0_00000.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['test105_8269eV_n9_d1_00000.tif', ['5', '3'], 0.9978823645287851, None, None] )
    eq_( info_array[2], ['test105_8269eV_n9_d2_00000.tif', ['-5', '-3'], 0.9999179211057668, None, None] )

def test_20201020_106():
    up_folder = get_data_folder('20201020')
    in_folder = os.path.join(up_folder, 'test106')

    log_file_path_ = os.path.join(in_folder, 'measurement_test106.log')
    log_file, mask_file, data_array, pilatus_counter = get_data_info( in_folder, adj_folder, syn_folder, None, 'C2',
                                                            log_file_path=log_file_path_
                                                            )

    # print( 'data_array[0:3]=', data_array[0:3] )

    # 0     test106_8266eV_n0_d0_00000
    info_array = data_array[ 0 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test106_8266eV_n0_d0_00000.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['test106_8266eV_n0_d1_00000.tif', ['5', '3'], 0.9991139261276931, None, None] )
    eq_( info_array[2], ['test106_8266eV_n0_d2_00000.tif', ['-5', '-3'], 0.999278013881824, None, None] )

    # -1    test106_8269eV_n9_d0_00000.tif
    info_array = data_array[ -1 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test106_8269eV_n9_d0_00000.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['test106_8269eV_n9_d1_00000.tif', ['5', '3'], 0.9999177320367902, None, None] )
    eq_( info_array[2], ['test106_8269eV_n9_d2_00000.tif', ['-5', '-3'], 1.0016124520789114, None, None] )

def test_20201020_107():
    up_folder = get_data_folder('20201020')
    in_folder = os.path.join(up_folder, 'test107')

    log_file_path_ = os.path.join(in_folder, 'measurement_test107.log')
    log_file, mask_file, data_array, pilatus_counter = get_data_info( in_folder, adj_folder, syn_folder, None, 'C2',
                                                            log_file_path=log_file_path_
                                                            )

    # print( 'data_array[0:3]=', data_array[0:3] )

    # 0     test107_1500A_n0_d0_00000
    info_array = data_array[ 0 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test107_1500A_n0_d0_00000.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['test107_1500A_n0_d1_00000.tif', ['5', '3'], 0.999589511189925, None, None] )
    eq_( info_array[2], ['test107_1500A_n0_d2_00000.tif', ['-5', '-3'], 1.000229873733642, None, None] )

    # -1    test107_1506A_n9_d0_00000.tif
    info_array = data_array[ -1 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test107_1506A_n9_d0_00000.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['test107_1506A_n9_d1_00000.tif', ['5', '3'], 1.0009439643246587, None, None] )
    eq_( info_array[2], ['test107_1506A_n9_d2_00000.tif', ['-5', '-3'], 0.9995931188255782, None, None] )

def test_20201020_108():
    up_folder = get_data_folder('20201020')
    in_folder = os.path.join(up_folder, 'test108')

    log_file_path_ = os.path.join(in_folder, 'measurement_test108.log')
    log_file, mask_file, data_array, pilatus_counter = get_data_info( in_folder, adj_folder, syn_folder, None, 'C2',
                                                            log_file_path=log_file_path_
                                                            )

    # print( 'data_array[0:3]=', data_array[0:3] )

    # 0     test108_1500A_n0_d0_00000
    info_array = data_array[ 0 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test108_1500A_n0_d0_00000.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['test108_1500A_n0_d1_00000.tif', ['5', '3'], 1.0014962183492273, None, None] )
    eq_( info_array[2], ['test108_1500A_n0_d2_00000.tif', ['-5', '-3'], 1.001035843472542, None, None] )

    # -1    test108_1506A_n9_d0_00000.tif
    info_array = data_array[ -1 ][ 1 ]
    eq_( len( info_array ), 3 )
    eq_( info_array[0], ['test108_1506A_n9_d0_00000.tif', ['-16.70000', '5.20000'], 1.0, None, None] )
    eq_( info_array[1], ['test108_1506A_n9_d1_00000.tif', ['5', '3'], 0.9993163506144705, None, None] )
    eq_( info_array[2], ['test108_1506A_n9_d2_00000.tif', ['-5', '-3'], 0.9999023358020672, None, None] )

if __name__ == '__main__':
    test_20201012()
    test_20201020_101()
    test_20201020_102()
    test_20201020_103()
    test_20201020_104()
    test_20201020_105()
    test_20201020_106()
    test_20201020_107()
    test_20201020_108()
