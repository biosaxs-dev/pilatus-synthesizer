# -*- coding: utf-8 -*-
"""
   tests for GuiPreferences.py

"""
from __future__ import division, print_function, unicode_literals

import sys
import os
import shutil
import time
from nose.tools     import eq_
from pyautogui      import typewrite

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from OurTkinter     import Tk
from PersistentInfo import get_pickle_file_path
from PilatusCounter import Counter
from Preferences    import preference_file, reload_preferences
from GuiPreferences import PreferencesDialog

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

    pickle_file_path = get_pickle_file_path( preference_file )
    if os.path.exists( pickle_file_path ):
        os.remove( pickle_file_path )

    reload_preferences()

    in_folder   = env_dict['in_folder1_AgBh_center']
    pilatus_counter = Counter( in_folder )

    root = Tk.Tk()
    root.withdraw()
    i += 1; root.after( i*tick, lambda: PreferencesDialog( root, 'Test', pilatus_counter ) )
    i += 1; root.after( i*tick, lambda: typewrite( [ 'enter' ] ) )
    i += 1; root.after( i*tick, lambda: root.destroy() )

    root.mainloop()

def test_teardown():
    time.sleep( 1 )
    pass

if __name__ == '__main__':
    test_setup()
    test_basics()
    test_teardown()
