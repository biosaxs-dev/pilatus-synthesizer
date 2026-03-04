# coding: utf-8

import sys
import os
from time import sleep
from subprocess import Popen

this_dir, this_file = os.path.split( os.path.abspath( __file__ ) )
sys.path.append( this_dir + '/../lib' )
import KekLib

def run():
    from Build.PyCashe import clean_all_pycashes
    clean_all_pycashes()

if __name__ == '__main__':
    run()
