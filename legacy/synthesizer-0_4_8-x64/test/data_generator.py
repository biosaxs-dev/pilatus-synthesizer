# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

import sys
import os
import time
from nose.tools     import eq_

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from TestDataGenerator import TestDataGenerator

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

in_folder   = env_dict['test_in_folder']

tdg = TestDataGenerator( in_folder )
tdg.restore_from_bak()

while (True):
    time.sleep( 70 )
    tdg.add_mockcopy(3)
