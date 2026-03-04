# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

import sys
import os
import time
import glob
from nose.tools     import eq_, assert_not_equal
from pyautogui      import typewrite

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from OurMock        import MagicMock
from OurTkinter     import Tk
from OurMessageBox  import check_last_message
from BasicUtils     import exe_name, Struct
from TestUtils      import clear_dirs_with_retry
import PersistentInfo
import GuiController
from PilatusImage   import PilatusImage
from Preferences    import set_preference, get_preference, reload_preferences
from Settings       import clear_settings, set_setting
from Development    import set_devel_info
from DebugQueue     import debug_queue_put

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

broken_folder   = env_dict['broken_folder']
syn_folder      = env_dict['test_syn_folder']
ENTER       = [ 'enter' ]

expected_syn_folder  = env_dict['expected_syn_folder']

tick = 500

assert_call_count = 0
assert_done_count = 0

def assert_exists( path ):
    global assert_call_count, assert_done_count

    assert_call_count += 1
    assert( os.path.exists( path ) )
    assert_done_count += 1

def setting_clear():
    clear_dirs_with_retry( [ syn_folder ] )

    # TODO: remove_settings
    pickle_file = PersistentInfo.make_pickle_file_path( 'settings.dump' )
    if os.path.exists( pickle_file ):
        os.remove( pickle_file )
    reload_preferences()
    clear_settings()

def test_setup():
    global root
    global gui
    global i
    i = 0

    time.sleep( 1 )

    setting_clear()
    set_devel_info( 'adj_output', 'NO' )
    set_setting( 'op_option', 'MANUAL' )
    set_devel_info( 'intermediate_results', 'NO' )
    set_devel_info( 'adj_algorithm', 'round' )

    root = Tk.Tk()
    root.title( __file__ )
    root.withdraw()

    opts = Struct( pandastable=False )
    gui = GuiController.Controller( root, opts )

def do_AutoRun( in_folder, assert_path ):
    global root
    global gui                                                                                                                                                                          
    global i

    i += 1; root.after( i*tick, lambda: gui.entry_frame.in_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.in_folder_entry.delete( 0, 'end') )
    i += 1; root.after( i*tick, lambda: typewrite( in_folder ) )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.log_file_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: typewrite( 'Y' ) )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.syn_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.syn_folder_entry.delete( 0, 'end') )
    i += 1; root.after( i*tick, lambda: typewrite( syn_folder ) )
    i += 1; root.after( i*tick, lambda: gui.refresh_button.focus_force() )
    i += 1; root.after( i*tick, lambda: gui.refresh_button.invoke() )
    i += 2; root.after( i*tick, lambda: gui.run_button.invoke() )
    i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )    # 
    i += 2; root.after( i*tick, lambda: typewrite( ENTER ) )    # 
    i += 1; root.after( i*tick, lambda: assert_exists( assert_path ) )

def test_two_changes():
    do_AutoRun( broken_folder + '/PILATUS1M', syn_folder + '/SiGe64201_syn.tif' )

def test_three_changes():
    do_AutoRun( broken_folder + '/AgBh_center',  syn_folder + '/AgBh002_syn.tif' )

def test_teardown():
    global root
    global gui
    global i

    i += 2; root.after( i*tick, lambda: gui.quit() )
    i += 1; root.after( i*tick, lambda: check_last_message( 'Do you want to quit' ) )
    i += 1; root.after( i*tick, lambda: typewrite( 'Y' ) )
    i += 1; root.after( i*tick, lambda: check_last_message( 'Do you want to save' ) )
    i += 1; root.after( i*tick, lambda: typewrite( 'N' ) )

    root.mainloop()

    fh = open( gui.entry_frame.logfile_path )
    logtext = fh.read()
    fh.close()
    assert( logtext.find( "error" ) <= 0 )
    gui.__del__()
    root.destroy()

    # Tkinter 中のエラーがキャッチされて認識されないため、
    # すべての assert 文が実行されたことを確認する。
    eq_( assert_call_count, assert_done_count )

if __name__ == '__main__':
    test_setup()
    test_two_changes()
    test_three_changes()
    test_teardown()
