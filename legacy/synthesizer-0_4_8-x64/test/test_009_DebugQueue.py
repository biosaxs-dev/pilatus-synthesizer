# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

import sys
import os
import shutil
from nose.tools import eq_

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from DebugQueue import debug_queue_put, debug_queue_get

def test_load():
    assert( True )

def test_basics():
    eq_( debug_queue_get(), None )
    debug_queue_put( 'ANY' )
    eq_( debug_queue_get(), 'ANY' )

if __name__ == '__main__':
    test_basics()


