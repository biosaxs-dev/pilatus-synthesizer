# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

import sys
import os
import time
from nose.tools     import eq_
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
from PilatusImageFabIO   import PilatusImage
from Preferences    import set_preference, get_preference, reload_preferences
from Settings       import clear_settings, set_setting
from Development    import set_devel_info
from TestDataGenerator import TestDataGenerator

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

in_folder   = env_dict['test_in_folder']
adj_folder  = env_dict['test_adj_folder']
syn_folder  = env_dict['test_syn_folder']
syn_folder2 = env_dict['test_syn_folder2']
ENTER       = [ 'enter' ]

expected_adj_folder  = env_dict['expected_adj_folder']
expected_syn_folder  = env_dict['expected_syn_folder']

tick = 1000

assert_call_count = 0
assert_done_count = 0

def setting_clear():
    clear_dirs_with_retry( [ adj_folder, syn_folder, syn_folder2 ] )

    # TODO: remove_settings
    pickle_file = PersistentInfo.make_pickle_file_path( 'settings.dump' )
    if os.path.exists( pickle_file ):
        os.remove( pickle_file )
    reload_preferences()
    clear_settings()

def assert_equal_adj( filename ):
    global assert_call_count
    global assert_done_count

    assert_call_count += 1
    adjusted_file       = '/'.join( [ adj_folder, filename ] )
    expected_file       = '/'.join( [ expected_adj_folder, filename ] )
    adjusted_pim        = PilatusImage( adjusted_file )
    expected_pim        = PilatusImage( expected_file )
    assert( adjusted_pim.equal( expected_pim ) )
    assert_done_count += 1

def assert_equal_syn( filename ):
    global assert_call_count
    global assert_done_count

    assert_call_count += 1
    synthesized_file    = '/'.join( [ syn_folder, filename ] )
    expected_file       = '/'.join( [ expected_syn_folder, filename ] )
    synthesized_pim     = PilatusImage( synthesized_file )
    expected_pim        = PilatusImage( expected_file )
    assert( synthesized_pim.equal( expected_pim ) )
    assert_done_count += 1

def assert_equal_syn2( filename ):
    global assert_call_count
    global assert_done_count

    assert_call_count += 1
    synthesized_file    = '/'.join( [ syn_folder2, filename ] )
    expected_file       = '/'.join( [ expected_syn_folder, filename ] )
    synthesized_pim     = PilatusImage( synthesized_file )
    expected_pim        = PilatusImage( expected_file )
    assert( synthesized_pim.equal( expected_pim ) )
    assert_done_count += 1

def assert_exists_path( path ):
    global assert_call_count
    global assert_done_count

    assert_call_count += 1
    # print( 'assert_exists_path: path=', path )
    testlog = open( 'test.log', 'w' )
    testlog.write( path )
    testlog.close()
    assert( os.path.exists( path ) )
    assert_done_count += 1

def test_setup():
    global root
    global gui
    global i

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

    tdg = TestDataGenerator( in_folder )
    tdg.restore_from_bak()

    opts = Struct( pandastable=False )

    gui = GuiController.Controller( root, opts )

    i = 0
    i += 1; root.after( i*tick, lambda: gui.entry_frame.in_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: typewrite( in_folder ) )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.log_file_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: typewrite( 'Y' ) )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.syn_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: typewrite( syn_folder ) )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.watch_interval_box.focus_force() )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.watch_interval.set( '30' ) )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.autorun_button.focus_force() )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.autorun_button.invoke() )
    i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )
    i += 25; root.after( i*tick, lambda: tdg.add_mockcopy(3) )
    i += 25; root.after( i*tick, lambda: tdg.add_mockcopy(0) )
    i += 25; root.after( i*tick, lambda: tdg.add_mockcopy(3) )
    i += 25; root.after( i*tick, lambda: tdg.add_mockcopy(3) )
    # i += 30; root.after( i*tick, lambda: gui.ar_controller.cancel() )
    # i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )    # cancel dialog への OK
    # i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )    # ActionWindow への OK

def test_teardown():
    global root
    global gui
    global i

    """
    i += 1; root.after( i*tick, lambda: gui.quit() )
    i += 1; root.after( i*tick, lambda: check_last_message( 'Do you want to quit' ) )
    i += 1; root.after( i*tick, lambda: typewrite( 'Y' ) )
    i += 1; root.after( i*tick, lambda: check_last_message( 'Do you want to save' ) )
    i += 1; root.after( i*tick, lambda: typewrite( 'N' ) )
    """

    gui.mainloop()
    gui.__del__()

    # Tkinter 中のエラーがキャッチされて認識されないため、
    # すべての assert 文が実行されたことを確認する。
    eq_( assert_call_count, assert_done_count )

if __name__ == '__main__':
    test_setup()
    test_AutoRun()
    test_teardown()
