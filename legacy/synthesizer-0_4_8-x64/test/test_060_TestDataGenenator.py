# -*- coding: utf-8 -*-
"""
   tests for TestDataGenerator.py

"""
from __future__ import division, print_function, unicode_literals

import sys
import os
import shutil
from nose.tools import eq_

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from TestDataGenerator import TestDataGenerator

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

test_in_folder   = env_dict['test_in_folder']

def test_setup():
    pass

def test_mockcopy():
    mdg = TestDataGenerator( test_in_folder )
    mdg.restore_from_bak()
    mdg.add_mockcopy()
    mdg.add_mockcopy(2)

def test_teardown():
    pass

if __name__ == '__main__':
    test_setup()
    test_mockcopy()
    test_teardown()
