# -*- coding: utf-8 -*-
"""
   tests for preferences.py

"""
from __future__ import division, print_function, unicode_literals

import sys
import os
import shutil
from nose.tools import eq_

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from Preferences import  ( clear_preferences, get_preference, set_preference, save_preferences,
                        reload_preferences, temporary_preferences_begin, temporary_preferences_end,
                        get_usual_preference
                      )

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

global log_file
global mask_file

syn_method1  = 'syn_method1'
syn_method2  = 'syn_method2'

def test_setup():
    clear_preferences()
    save_preferences()

def test_basics():
    eq_( get_preference( 'syn_method' ), None )
    set_preference( 'syn_method', syn_method1 )
    eq_( get_preference( 'syn_method' ), syn_method1 )
    save_preferences()
    set_preference( 'syn_method', syn_method2 )
    eq_( get_preference( 'syn_method' ), syn_method2 )
    reload_preferences()
    eq_( get_preference( 'syn_method' ), syn_method1 )

def test_temporary_preferences():
    set_preference( 'syn_method', syn_method1 )
    eq_( get_preference( 'syn_method' ), syn_method1 )
    temporary_preferences_begin()
    set_preference( 'syn_method', syn_method2 )
    eq_( get_preference( 'syn_method' ), syn_method2 )
    eq_( get_usual_preference( 'syn_method' ), syn_method1 )
    temporary_preferences_end()
    eq_( get_preference( 'syn_method' ), syn_method1 )

def test_teardown():
    test_setup()

if __name__ == '__main__':
    test_setup()
    test_teardown()
