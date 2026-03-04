# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

import sys
import os
import time
from nose.tools     import eq_
from pyautogui      import typewrite, moveTo, click, keyDown, keyUp, scroll, dragRel

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from OurMock        import MagicMock
from OurTkinter     import Tk
from OurMessageBox  import check_last_message
from BasicUtils     import exe_name
from TestUtils      import clear_dirs_with_retry
import PersistentInfo
import GuiController
from PilatusImage   import PilatusImage
from Preferences    import set_preference, get_preference, reload_preferences
from SynthesizerSettings    import clear_settings, set_setting
from Development    import set_devel_info
from DebugQueue     import debug_queue_put
from TestTkUtils    import split_geometry

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

in_folder   = env_dict['in_folder1_AgBh_center']
adj_folder  = env_dict['test_adj_folder']
syn_folder  = env_dict['test_syn_folder']
syn_folder2 = env_dict['test_syn_folder2']
ENTER       = [ 'enter' ]

expected_adj_folder  = env_dict['expected_adj_folder']
expected_syn_folder  = env_dict['expected_syn_folder']

tick = 500

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
    set_devel_info( 'adj_output', 'YES' )
    set_setting( 'op_option', 'MANUAL' )
    set_devel_info( 'intermediate_results', 'YES' )

    # ここでは、fast で確認する。
    set_devel_info( 'adj_algorithm', 'fast' )

    root = Tk.Tk()
    root.title( __file__ )
    root.withdraw()

    i = 0
    gui = None

def show_data_cursor():
    global gui
    viewer = gui.synthesizer.viewer
    w, h, x, y = split_geometry( viewer.winfo_geometry() )
    x_ = x + w/8
    y_ = y + h/2
    moveTo( x_, y_ )
    keyDown( 'shift' )
    click()
    keyUp( 'shift' )
    t = tick/1000
    for key in [ ['up'], ['down'], ['left'], ['right'], ['escape'] ]:
        time.sleep( t )
        viewer.update()
        typewrite( key )

def show_zoom_pan():
    global gui

    t = tick/1000

    viewer = gui.synthesizer.viewer

    viewer.focus()
    scroll( 100 )
    viewer.update()
    time.sleep( t )
    scroll( -100 )
    viewer.update()

    w, h, x, y = split_geometry( viewer.winfo_geometry() )
    x_ = x + w/8
    y_ = y + h/2
    moveTo( x_, y_ )
    dragRel( 50, 50 )
    viewer.update()

    time.sleep( t )
    dragRel( -50, -50 )


def test_NormalSynthesis():
    global root
    global gui                                                                                                                                                                          
    global i

    gui = GuiController.Controller( root )

    i += 1; root.after( i*tick, lambda: gui.entry_frame.in_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: typewrite( in_folder ) )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.log_file_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: typewrite( 'Y' ) )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.adj_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: typewrite( adj_folder ) )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.syn_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: typewrite( syn_folder ) )
    i += 1; root.after( i*tick, lambda: gui.refresh_button.focus_force() )
    i += 1; root.after( i*tick, lambda: gui.refresh_button.invoke() )

    # 合成前の表示の実行
    i += 1; root.after( i*tick, lambda: gui.image_info_table.table.selection_set( 'topleft' ) )
    i += 1; root.after( i*tick, lambda: gui.image_info_table.test_select_row( 0 ) )
    i += 1; root.after( i*tick, lambda: gui.image_info_table.do_action( 1 ) )
    # gui.synthesizer.viewer が設定されるまでに十分な時間が必要
    i += 6; root.after( i*tick, lambda: gui.synthesizer.viewer.quit_button.invoke() )
    i += 1; root.after( i*tick, lambda: gui.image_info_table.do_action( 2 ) )
    # gui.synthesizer.viewer が設定されるまでに十分な時間が必要
    i += 6; root.after( i*tick, lambda: gui.synthesizer.viewer.quit_button.invoke() )

    # 合成の実行
    def exec_systhsis( change=False ):
        global i
        i += 1; root.after( i*tick, lambda: gui.image_info_table.table.selection_set( 'topleft' ) )
        i += 1; root.after( i*tick, lambda: gui.image_info_table.test_select_row( 0 ) )
        if change:
            i += 1; root.after( i*tick, lambda: gui.image_info_table.do_action( 3, change ) )
        else:
            i += 1; root.after( i*tick, lambda: gui.run_button.invoke() )
        i += 1; root.after( i*tick, lambda: check_last_message( 'You are making sythesized images' ) )
        i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )
        if change:
            # とりあえず通す意味で、変更しないで、OK。
            i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )
        i += 4; root.after( i*tick, lambda: typewrite( ENTER ) )
        i += 1; root.after( i*tick, lambda: assert_equal_adj( 'AgBh002_1_adj.tif' ) )
        i += 1; root.after( i*tick, lambda: assert_equal_adj( 'AgBh002_2_adj.tif' ) )
    exec_systhsis()
    i += 1; root.after( i*tick, lambda: assert_equal_syn( 'AgBh002_1_syn.tif' ) )
    i += 1; root.after( i*tick, lambda: assert_equal_syn( 'AgBh002_syn.tif' ) )

    # 合成後の表示の実行
    i += 1; root.after( i*tick, lambda: gui.image_info_table.table.selection_set( 'topleft' ) )
    i += 1; root.after( i*tick, lambda: gui.image_info_table.test_select_row( 0 ) )
    i += 1; root.after( i*tick, lambda: gui.image_info_table.do_action( 2 ) )
    # gui.synthesizer.viewer が設定されるまでに十分な時間が必要
    i += 6; root.after( i*tick, lambda: gui.synthesizer.viewer.quit_button.invoke() )
    i += 1; root.after( i*tick, lambda: gui.image_info_table.do_action( 1 ) )
    # gui.synthesizer.viewer が設定されるまでに十分な時間が必要
    i += 6; root.after( i*tick, lambda: show_data_cursor() )
    i += 10; root.after( i*tick, lambda: show_zoom_pan() )
    i += 12; root.after( i*tick, lambda: gui.synthesizer.viewer.quit_button.invoke() )

    # 出力フォルダの変更（ログ出力先の変更）
    i += 1; root.after( i*tick, lambda: gui.entry_frame.syn_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.syn_folder_entry.delete( 0, 'end') )
    i += 1; root.after( i*tick, lambda: typewrite( syn_folder2 ) )
    i += 1; root.after( i*tick, lambda: gui.refresh_button.focus_force() )
    i += 1; root.after( i*tick, lambda: gui.refresh_button.invoke() )
    exec_systhsis( change=True )
    i += 1; root.after( i*tick, lambda: assert_equal_syn2( 'AgBh002_1_syn.tif' ) )
    i += 1; root.after( i*tick, lambda: assert_equal_syn2( 'AgBh002_syn.tif' ) )
    # PilatusUtils の中でエラーを発生させるように設定
    i += 1; root.after( i*tick, lambda: debug_queue_put( 'PilatusUtils.die()' ) )
    i += 1; root.after( i*tick, lambda: gui.refresh_button.focus_force() )
    i += 1; root.after( i*tick, lambda: gui.refresh_button.invoke() )
    i += 4; root.after( i*tick, lambda: typewrite( ENTER ) )

    # 合成後の表示の実行
    orig_cmap = get_preference( 'color_map' )
    i += 1; root.after( i*tick, lambda: gui.image_info_table.table.selection_set( 'topleft' ) )
    i += 1; root.after( i*tick, lambda: gui.image_info_table.test_select_row( 0 ) )
    i += 1; root.after( i*tick, lambda: set_preference( 'color_map', 'Diverging' ) )
    i += 1; root.after( i*tick, lambda: gui.image_info_table.do_action( 2 ) )
    # gui.synthesizer.viewer が設定されるまでに十分な時間が必要
    i += 6; root.after( i*tick, lambda: gui.synthesizer.viewer.quit_button.invoke() )
    i += 1; root.after( i*tick, lambda: set_preference( 'color_map', orig_cmap ) )

    # 変更されたログの存在確認
    logname_ = exe_name() + '.log'
    changed_log = os.path.join( syn_folder2, logname_ )
    i += 1; root.after( i*tick, lambda: assert_exists_path( changed_log ) )

    # gui.mainloop()

def test_OperationErrors():
    global root
    global gui
    global i

    # 出力フォルダをクリアする。
    i += 1; root.after( i*tick, lambda: gui.entry_frame.syn_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: gui.entry_frame.syn_folder_entry.delete( 0, 'end') )

    # 入力が完了していないのに Refresh ボタンを押す。（disable 化により、不要）
    """
    i += 1; root.after( i*tick, lambda: gui.refresh_button.focus_force() )
    i += 1; root.after( i*tick, lambda: gui.refresh_button.invoke() )
    i += 1; root.after( i*tick, lambda: check_last_message( "Please fill in" ) )
    i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )
    """

    # 出力フォルダを元の値に戻す。
    i += 1; root.after( i*tick, lambda: gui.entry_frame.syn_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: typewrite( syn_folder ) )
    # ここでフォーカスを変えないと入力が終了しない。
    i += 1; root.after( i*tick, lambda: gui.image_info_table.table.focus_force() )

    # Refresh ボタンを押さないで実行しようとする。
    i += 1; root.after( i*tick, lambda: gui.image_info_table.table.selection_set( 'topleft' ) )
    i += 1; root.after( i*tick, lambda: gui.image_info_table.test_select_row( 0 ) )
    i += 1; root.after( i*tick, lambda: gui.image_info_table.do_action( 3 ) )
    i += 1; root.after( i*tick, lambda: check_last_message( "You can't do any action until" ) )
    i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )

    # このタイミングで Preferences の変更はできない。
    # TODO: 実際にメニューから実行すること。
    i += 1; root.after( i*tick, lambda: gui.preferences() )
    i += 1; root.after( i*tick, lambda: check_last_message( "You can't change preferences until" ) )
    i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )

    # Refresh ボタンを押せば Preferences ダイアログは開ける。
    # TODO: GuiPreferences の単体テスト
    i += 1; root.after( i*tick, lambda: gui.refresh_button.focus_force() )
    i += 1; root.after( i*tick, lambda: gui.refresh_button.invoke() )
    i += 1; root.after( i*tick, lambda: gui.preferences() )
    i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )

def test_ClearSettingEntries():
    global root
    global gui
    global i

    if gui == None:
        gui = GuiController.Controller( root )

    i += 1; root.after( i*tick, lambda: gui.clear_button.invoke() )
    i += 1; root.after( i*tick, lambda: check_last_message( 'Do you want to clear' ) )
    i += 1; root.after( i*tick, lambda: typewrite( 'Y' ) )

def test_teardown():
    global root
    global gui
    global i

    i += 1; root.after( i*tick, lambda: gui.quit() )
    i += 1; root.after( i*tick, lambda: check_last_message( 'Do you want to quit' ) )
    i += 1; root.after( i*tick, lambda: typewrite( 'N' ) )
    i += 1; root.after( i*tick, lambda: gui.quit() )
    i += 1; root.after( i*tick, lambda: check_last_message( 'Do you want to quit' ) )
    i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )
    i += 1; root.after( i*tick, lambda: check_last_message( 'Do you want to save' ) )
    i += 1; root.after( i*tick, lambda: typewrite( ENTER ) )

    root.mainloop()
    gui.__del__()
    root.destroy()

    # Tkinter 中のエラーがキャッチされて認識されないため、
    # すべての assert 文が実行されたことを確認する。
    eq_( assert_call_count, assert_done_count )

    time.sleep( 3 )

if __name__ == '__main__':
    test_setup()
    test_NormalSynthesis()
    test_OperationErrors()
    test_ClearSettingEntries()
    test_teardown()
