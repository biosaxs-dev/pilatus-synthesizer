# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

import sys
import os
import shutil
import time
from nose.tools import eq_
import logging

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from TestUtils          import clear_dirs_with_retry
from ChangeableLogger   import Logger

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

syn_folder  = env_dict['test_syn_folder']
syn_folder2 = env_dict['test_syn_folder2']

def test_setup():
    clear_dirs_with_retry( [ syn_folder, syn_folder2 ] )

def test_basics():
    global clogger_
    path_       = os.path.join( syn_folder, 'test.log' )
    clogger_    = Logger( path_ )
    logging.info( 'This is an info massage' )
    assert( os.path.exists( path_ ) )

def test_changeto():
    path2_      = os.path.join( syn_folder2, 'test.log' )
    clogger_.changeto( path2_ )
    logging.warning( 'This is a warning massage' )
    assert( os.path.exists( path2_ ) )

def test_teardown():
    # clogger_ = None
    # time.sleep( 1 )
    # clear_dirs_with_retry( [ syn_folder, syn_folder2 ] )
    # TODO: clear syn_folder2
    # WindowsError: [Error 32] プロセスはファイルにアクセスできません。別のプロセスが
    # 使用中です。: 'F:/Development/Test/Synthesized2\\test.log'
    clear_dirs_with_retry( [ syn_folder ] )

if __name__ == '__main__':
    test_setup()
    test_basics()
    test_changeto()
    test_teardown()
