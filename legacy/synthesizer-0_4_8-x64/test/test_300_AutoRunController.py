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
from SynthesizerSettings    import clear_settings, set_setting
from Development    import set_devel_info
from TestDataGenerator import TestDataGenerator
from DebugQueue     import debug_queue_put

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

in_folder   = env_dict['test_in_folder']
syn_folder  = env_dict['test_syn_folder']
ENTER       = [ 'enter' ]

expected_syn_folder  = env_dict['expected_syn_folder']

tick = 500

assert_call_count = 0
assert_done_count = 0

def setting_clear():
    clear_dirs_with_retry( [ syn_folder ] )

    # TODO: remove_settings
    pickle_file = PersistentInfo.make_pickle_file_path( 'settings.dump' )
    if os.path.exists( pickle_file ):
        os.remove( pickle_file )
    reload_preferences()
    clear_settings()

def assert_equal_num_files( num_samples ):
    global assert_call_count
    global assert_done_count
    orig_dir = os.getcwd()

    time.sleep( 1 )

    test_phase = 0
    try:
        assert_call_count += 1
        # print( in_folder )
        os.chdir( in_folder )
        files = glob.glob( '*.tif' )
        test_phase += 1
        eq_( len( files ), num_samples * 3 )

        # print( syn_folder )
        os.chdir( syn_folder )
        files = glob.glob( '*.tif' )
        test_phase += 1
        eq_( len( files ), num_samples )

        assert_done_count += 1
    except:
        print( sys.exc_info[0] )
        print( 'Looks like failed in test_phase: ', test_phase )

    os.chdir( orig_dir )

def test_setup():
    global root
    global gui

    setting_clear()
    set_devel_info( 'adj_output', 'NO' )
    set_setting( 'op_option', 'AUTOMATIC' )
    set_devel_info( 'intermediate_results', 'NO' )
    set_devel_info( 'adj_algorithm', 'round' )

    root = Tk.Tk()
    root.title( __file__ )
    root.withdraw()

def test_AutoRun():
    global root
    global gui                                                                                                                                                                          
    global i

    mdg = TestDataGenerator( in_folder )
    mdg.restore_from_bak()

    opts = Struct( pandastable=True )

    gui = GuiController.Controller( root, opts )

    num_samples = 1

    i = 0
    i += 1; root.after( i*tick, lambda: gui.entry_frame.in_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: typewrite( in_folder ) )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.log_file_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: typewrite( 'Y' ) )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.syn_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: typewrite( syn_folder ) )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.watch_interval_box.focus_force() )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.watch_interval.set( '10' ) )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.autorun_button.focus_force() )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.autorun_button.invoke() )
    i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )
    # ログが開始されていることを確認する。
    i += 4; root.after( i*tick, lambda: assert_not_equal( gui.entry_frame.logfile_path, '' ) )
    i += 25; root.after( i*tick, lambda: mdg.add_mockcopy(3) ); num_samples += 3
    i += 25; root.after( i*tick, lambda: mdg.add_mockcopy(0) )
    i += 25; root.after( i*tick, lambda: mdg.add_mockcopy(3) ); num_samples += 3
    i += 25; root.after( i*tick, lambda: debug_queue_put( 'AutoRunController.die()' ) )
    i += 30; root.after( i*tick, lambda: gui.ar_controller.cancel() )
    i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )    # cancel dialog への OK
    i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )    # ActionWindow への OK
    i += 1; root.after( i*tick, lambda: assert_equal_num_files( num_samples ) )

def test_teardown():
    global root
    global gui
    global i

    i += 1; root.after( i*tick, lambda: gui.quit() )
    i += 1; root.after( i*tick, lambda: check_last_message( 'Do you want to quit' ) )
    i += 1; root.after( i*tick, lambda: typewrite( 'Y' ) )
    i += 1; root.after( i*tick, lambda: check_last_message( 'Do you want to save' ) )
    i += 1; root.after( i*tick, lambda: typewrite( 'N' ) )

    root.mainloop()

    fh = open( gui.entry_frame.logfile_path )
    logtext = fh.read()
    fh.close()
    assert( logtext.find( "NameError: name 'die' is not defined" ) > 0 )
    gui.__del__()
    root.destroy()

    # Tkinter 中のエラーがキャッチされて認識されないため、
    # すべての assert 文が実行されたことを確認する。
    eq_( assert_call_count, assert_done_count )

if __name__ == '__main__':
    test_setup()
    test_AutoRun()
    test_teardown()
