# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

import sys
import os
import shutil
import time
import threading
from nose.tools import eq_

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from BasicUtils import mkdirs_with_retry, rename_with_retry

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

required_env_keys = [
    'in_folder1_AgBh_center',
    'in_folder2',
    'in_folder2_Detector_move',
    'empty_folder',
    'test_adj_folder',
    'test_syn_folder',
    'test_syn_folder2',
    'expected_adj_folder',
    'expected_syn_folder',
    ]

def test_load():
    assert True

adj_folder  = env_dict['test_adj_folder']
syn_folder  = env_dict['test_syn_folder']
syn_folder2 = env_dict['test_syn_folder2']
emp_folder  = env_dict['empty_folder']

def make_and_remove_a_dir( path ):
    os.makedirs( path )
    time.sleep( 1 )
    os.remove( path )

def test_mkdirs_with_retry():
    for path_ in ( adj_folder, syn_folder, syn_folder2, emp_folder ):
        if os.path.exists( path_ ):
            shutil.rmtree( path_ )

        if path_ == adj_folder:
            thr_ = threading.Thread( None, lambda: make_and_remove_a_dir( path_ ), 'test', () )
            thr_.start()

        mkdirs_with_retry( path_ )

        if path_ == adj_folder:
            thr_.join()

        assert( os.path.exists( path_ ) )
        assert( os.path.isdir( path_ ) )

def make_a_file( path ):
    print( 'make_a_file: path=', path )
    fh = open( path, 'w' )
    time.sleep( 2 )
    fh.close()

def test_rename_with_retry():
    file = emp_folder + '/test.txt'

    # make a file in a different thread to force rename to fail.
    thr_ = threading.Thread( None, lambda: make_a_file( file ), 'test', () )
    thr_.start()
    time.sleep( 1 )
    assert( os.path.exists( file ) )
  
    bakfile = file.replace( '.txt', '.bak' )
    rename_with_retry( file, bakfile )
    thr_.join()
  
    assert( not os.path.exists( file ) )
    assert( os.path.exists( bakfile ) )
    os.remove( bakfile  )
    assert( not os.path.exists( bakfile ) )

def test_env_all_exist():
    for obj in required_env_keys:
        assert( obj in env_dict )
        try:
            assert( os.path.exists( env_dict[obj] ) )
        except:
            print( env_dict[obj], ' does not exist.' )
            assert( False )

if __name__ == '__main__':
    test_mkdirs_with_retry()
    test_rename_with_retry()
    test_env_all_exist()
