# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

import sys
import os
import glob
import time
import shutil
import csv
from subprocess import call 
from nose.tools import eq_

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from PilatusImage   import PilatusImage
from Preferences    import set_preference
from Development    import set_devel_info
from BasicUtils     import clear_dirs_with_retry, Struct
from DebugQueue     import debug_queue_put
from TestUtils      import OldPilatusImage

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

in_folder   = env_dict['in_folder1_AgBh_center']
adj_folder  = env_dict['test_adj_folder']
syn_folder  = in_folder + '/Synthesized'
round_adj_folder  = env_dict['round_adj_folder']
round_syn_folder  = env_dict['round_syn_folder']

opts = Struct(
    command         = True,
    in_folder       = in_folder,
    adj_folder      = None,
    autonum_folders = False,
    out_folder      = None,
    pandastable     = False,
    )

assert_call_count = 0
assert_done_count = 0

def assert_equal_syn( filename ):
    global assert_call_count
    global assert_done_count

    assert_call_count += 1
    synthesized_file    = '/'.join( [ syn_folder, filename ] )
    expected_file       = '/'.join( [ round_syn_folder, filename ] )
    synthesized_pim     = PilatusImage( synthesized_file )
    expected_pim        = OldPilatusImage( expected_file, original_image=synthesized_pim )
    assert( synthesized_pim.equal( expected_pim ) )
    assert_done_count += 1

def test_load():
    assert True

def test_setup():
    # ここでは、round で確認する。
    # （デフォルトが変更されている場合があるので、
    # 念のため設定する）
    set_devel_info( 'adj_algorithm', 'round' )

def test_NormalSynthesis():
    from CommandController  import Controller
    set_devel_info( 'intermediate_results', 'YES' )

    try:
        cmd = Controller( opts )
        cmd.execute()
    except Exception as err:
        raise err

    assert_equal_syn( 'AgBh002_1_syn.tif' )
    assert_equal_syn( 'AgBh002_syn.tif' )

def test_Exception():
    from CommandController  import Controller
    set_devel_info( 'intermediate_results', 'YES' )
    debug_queue_put( 'PilatusUtils.die()' )

    try:
        cmd = Controller( opts )
        cmd.execute()
    except Exception as err:
        raise err

    fh = open( cmd.logfile_path )
    logtext = fh.read()
    fh.close()
    assert( logtext.find( "NameError: name 'die' is not defined" ) > 0 )

def SubprocessCallBat( exe_name ):
    clear_dirs_with_retry( [ syn_folder ] )

    run_dir = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
    ret = call( '%s/%s -c -i %s' % ( run_dir, exe_name, in_folder ), shell=True )

    eq_( ret, 0 )
    assert_equal_syn( 'AgBh002_syn.tif' )

def test_SubprocessCallExe():
    SubprocessCallBat( 'synthesizer.exe' )

def test_teardown():
    eq_( assert_call_count, assert_done_count )

if __name__ == '__main__':
    test_setup()
    test_NormalSynthesis()
    test_Exception()
    test_SubprocessCallExe()
    test_teardown()
