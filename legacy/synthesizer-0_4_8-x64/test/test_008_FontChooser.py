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
from OurTix         import tix
from FontChooser    import askChooseFont

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

def test_setup():
    pass

def test_basics():
    root = tix.Tk( )
    # font = askChooseFont( root )
    root.destroy()

def test_teardown():
    pass

if __name__ == '__main__':
    test_setup()
    test_basics()
    test_teardown()
