# -*- coding: utf-8 -*-
"""
   tests for Development.py

"""
from __future__ import division, print_function, unicode_literals

import sys
import os
import shutil
from nose.tools     import eq_
from pyautogui      import typewrite

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from OurTkinter     import Tk
from Development    import  ( DeveloperOptionsDialog, get_devel_info, set_devel_info )

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

i = 0
tick = 500

def test_setup():
    pass

def test_basics():
    global i

    eq_( get_devel_info( 'adj_algorithm' ), 'round' )

    root = Tk.Tk()
    root.iconify()
    i += 1; root.after( i*tick, lambda: typewrite( [ 'enter' ] ) )

    dialog = DeveloperOptionsDialog( root, 'Test' )

    root.destroy()

def test_temporary_preferences():
    pass

def test_teardown():
    pass

if __name__ == '__main__':
    test_setup()
    test_basics()
    test_teardown()
