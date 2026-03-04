# -*- coding: utf-8 -*-
"""
   tests for Settings.py

"""
from __future__ import division, print_function, unicode_literals

import sys
import os
import shutil
from nose.tools import eq_

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from SynthesizerSettings import  ( clear_settings, get_setting, set_setting, save_settings,
                        reload_settings, temporary_settings_begin, temporary_settings_end,
                        set_mask
                      )

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

in_folder1  = 'in_folder1'
in_folder2  = 'in_folder2'

def test_setup():
    clear_settings()
    save_settings()

def test_basics():
    eq_( get_setting( 'in_folder' ), None )
    set_setting( 'in_folder', in_folder1 )
    eq_( get_setting( 'in_folder' ), in_folder1 )
    save_settings()
    set_setting( 'in_folder', in_folder2 )
    eq_( get_setting( 'in_folder' ), in_folder2 )
    reload_settings()
    eq_( get_setting( 'in_folder' ), in_folder1 )

def test_temporary_settings():
    set_setting( 'in_folder', in_folder1 )
    eq_( get_setting( 'in_folder' ), in_folder1 )
    temporary_settings_begin()
    set_setting( 'in_folder', in_folder2 )
    eq_( get_setting( 'in_folder' ), in_folder2 )
    temporary_settings_end()
    eq_( get_setting( 'in_folder' ), in_folder1 )

def test_set_mask():
    in_folder_  = env_dict[ 'in_folder1_AgBh_center' ]
    maskfile    = in_folder_ + '/20151019cent01_0_00000.mask'
    logfile     = in_folder_ + '/measurement_AgBh_center.log'
    emptyfile   = env_dict[ 'test_syn_folder' ] + '/emptyfile'
    fh = open( emptyfile, "w" )
    fh.close()

    eq_( set_mask( maskfile ),  True )
    eq_( set_mask( logfile ),   False )
    eq_( set_mask( emptyfile ), False )

def test_teardown():
    test_setup()

if __name__ == '__main__':
    test_setup()
    test_teardown()
