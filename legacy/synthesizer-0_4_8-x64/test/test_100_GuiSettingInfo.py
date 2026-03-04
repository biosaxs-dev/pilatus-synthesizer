# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

import sys
import os
from nose.tools     import eq_
from pyautogui      import typewrite

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from OurMock        import MagicMock
from OurTkinter     import Tk
from OurMessageBox  import check_last_message
from Preferences    import set_preference
from SynthesizerSettings    import clear_settings, save_settings, reload_settings, get_setting, set_setting
from Development    import set_devel_info
from GuiSettingInfo import EntryFrame
from TestUtils      import dnd_from_to
from MachineTypes   import get_chassistype_name, get_display_resolution, get_monitors

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

ENTER       = [ 'enter' ]

assert_call_count = 0
assert_done_count = 0

def assert_suggested_folders_ok( in_folder ):
    global testee
    global assert_call_count
    global assert_done_count

    cwd_ = os.getcwd()
    drive_ = cwd_.split( '\\' )[0]

    assert_call_count += 1
    eq_( testee.suggested_folders( 'Adjusted' ), 
        [   in_folder + '/Adjusted',
            in_folder + '-Adjusted',
            drive_ + '/Adjusted',
        ]
        )
    assert_done_count += 1

def assert_eq_( a, b ):
    global assert_call_count
    global assert_done_count

    assert_call_count += 1
    eq_( a, b )
    assert_done_count += 1

def assert_check_last_message_ok( msg ):
    global assert_call_count
    global assert_done_count

    assert_call_count += 1
    check_last_message( msg )
    assert_done_count += 1


class MockGuicontroller:
    def __init__( self ):
        self.setting_entry = {}
        self.op_is_manual   = False
        self.image_info_table   = None
        self.refresh_button_suggestion  = MagicMock()
        self.refresh_button_enable      = MagicMock()
        self.auto_start     = MagicMock()
        self.auto_disable   = MagicMock()
        self.auto_enable    = MagicMock()
        pass

AutomaticSetting_is_done = False
tick = 200

def TkRootAndEntryFrameSetup( after=True ):
    global root
    global controller
    global testee

    root = Tk.Tk()
    root.title( __file__ )
    controller = MockGuicontroller()
    testee = EntryFrame( root, controller )
    testee.pack()
    if after:
        testee.after_construction_proc()

def test_setup():

    set_devel_info( 'adj_output', 'YES' )
    set_setting( 'op_option', 'MANUAL' )

def test_InitialEntryControl():
    clear_settings()
    TkRootAndEntryFrameSetup()

    i = 0
    i += 1;

    # 初期の入力促進文字列の確認
    if True:
        root.after( i*tick, lambda: assert_eq_( testee.in_folder.get(),  '<Folder>' ) )
        root.after( i*tick, lambda: assert_eq_( testee.log_file.get(),   '<File>'   ) )
        root.after( i*tick, lambda: assert_eq_( testee.mask_file.get(),  '<File>'   ) )
        root.after( i*tick, lambda: assert_eq_( testee.adj_folder.get(), '<Folder>' ) )
        root.after( i*tick, lambda: assert_eq_( testee.syn_folder.get(), '<Folder>' ) )

    # エラー示唆のための赤字確認
    for entry in (  testee.in_folder_entry,
                    testee.log_file_entry,
                    testee.mask_file_entry,
                    testee.adj_folder_entry,
                    testee.syn_folder_entry):
        root.after( i*tick, lambda: assert_eq_( entry.cget('fg'), 'red' ) )

    # フォーカス時の空欄化確認
    i += 1; root.after( i*tick, lambda: testee.in_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.in_folder.get(), '' ) )

    i += 1; root.after( i*tick, lambda: testee.log_file_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.in_folder.get(), '<Folder>' ) )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.log_file.get(), '' ) )

    i += 1; root.after( i*tick, lambda: testee.mask_file_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.log_file.get(), '<File>' ) )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.mask_file.get(), '' ) )

    i += 1; root.after( i*tick, lambda: testee.adj_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.mask_file.get(), '<File>' ) )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.adj_folder.get(), '' ) )

    i += 1; root.after( i*tick, lambda: testee.syn_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.adj_folder.get(), '<Folder>' ) )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.syn_folder.get(), '' ) )

    i += 1; root.after( i*tick, lambda: testee.in_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.syn_folder.get(), '<Folder>' ) )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.in_folder.get(), '' ) )

    i += 1; root.after( i*tick, lambda: root.destroy() )
    root.mainloop();


def test_CreateFolderDialog():
    global i

    # （遅いマシンでは）
    # このテストはエラーになりやすいので、ゆっくり動かす。
    global tick
    orig_tick = tick
    tick = 500

    clear_settings()
    TkRootAndEntryFrameSetup()

    in_folder   = env_dict['in_folder1_AgBh_center']
    i = 0
    i += 1; root.after( i*tick, lambda: testee.in_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: typewrite( in_folder ) )
    i += 1; root.after( i*tick, lambda: testee.log_file_entry.focus_force() )
    # ( tkinter の mainloop で処理していることから )
    # 下の assert_suggested_folders_ok のためには dialog を終了させてからの方がよい。
    i += 1; root.after( i*tick, lambda: typewrite( ENTER  ) )
    i += 1; root.after( i*tick, lambda: assert_suggested_folders_ok( in_folder ) )
    i += 1; root.after( i*tick, lambda: root.destroy() )
    root.mainloop();

    tick = orig_tick

def NormalSetting( save=False ):
    global i
    in_folder   = env_dict['in_folder1_AgBh_center']
    log_file    = in_folder + '/measurement_AgBh_center.log'
    mask_file   = in_folder + '/20151019cent01_0_00000.mask'
    adj_folder = env_dict['test_adj_folder']
    syn_folder = env_dict['test_syn_folder']
    # 入力フォルダに log または mask ファイルが存在し、自動設定を行うこと
    i += 1; root.after( i*tick, lambda: testee.in_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: typewrite( in_folder ) )
    i += 1; root.after( i*tick, lambda: testee.log_file_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.auto_set_asked, True ) )
    i += 1; root.after( i*tick, lambda: typewrite( 'Y' ) )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.auto_set_done, True ) )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.log_file.get(), log_file ) )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.mask_file.get(), mask_file ) )
    i += 1; root.after( i*tick, lambda: testee.adj_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: typewrite( adj_folder ) )
    i += 1; root.after( i*tick, lambda: testee.syn_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.adj_folder_entry.cget('fg'), 'black' ) )
    i += 1; root.after( i*tick, lambda: typewrite( syn_folder ) )
    i += 1; root.after( i*tick, lambda: testee.in_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.syn_folder_entry.cget('fg'), 'black' ) )
    i += 1;
    if True:
        root.after( i*tick, lambda: controller.refresh_button_suggestion.start.assert_called_with() )
        for entry in (  testee.in_folder_entry,
                        testee.log_file_entry,
                        testee.mask_file_entry ):
            root.after( i*tick, lambda: assert_eq_( entry.cget('fg'), 'black' ) )

    if save:
        i += 1; root.after( i*tick, lambda: save_settings() )

def test_AutomaticSetting():
    global i
    global AutomaticSetting_is_done

    # （遅いマシンでは）
    # このテストはエラーになりやすいので、ゆっくり動かす。
    global tick
    orig_tick = tick
    tick = 500

    AutomaticSetting_is_done = False

    clear_settings()

    in_folder2  = env_dict['in_folder2_Detector_move']
    empty_folder = env_dict['empty_folder']

    set_setting( 'op_option', 'MANUAL' )

    TkRootAndEntryFrameSetup()

    i = 0
    NormalSetting( save=True )

    # 別のフォルダを指定して、自動設定をキャンセル
    i += 1; root.after( i*tick, lambda: testee.in_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: testee.in_folder_entry.delete(0, 'end') )
    i += 1; root.after( i*tick, lambda: typewrite( in_folder2 ) )
    i += 1; root.after( i*tick, lambda: testee.log_file_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.auto_set_asked, True ) )
    i += 1; root.after( i*tick, lambda: typewrite( 'N' ) )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.auto_set_done, False ) )

    # 入力フォルダに log または mask ファイルが存在しないので、
    # 自動設定可否を問わない。
    i += 1; root.after( i*tick, lambda: testee.in_folder_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: testee.in_folder_entry.delete(0, 'end') )
    i += 1; root.after( i*tick, lambda: typewrite( empty_folder ) )
    i += 1; root.after( i*tick, lambda: testee.log_file_entry.focus_force() )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.auto_set_asked, False ) )
    i += 1; root.after( i*tick, lambda: assert_eq_( testee.auto_set_done, False ) )

    i += 1; root.after( i*tick, lambda: root.destroy() )
    root.mainloop();
    testee.__del__()        # 必要。ロガーの削除のため。
    # print( 'test_AutomaticSetting end' )
    AutomaticSetting_is_done = True

    tick = orig_tick

if get_chassistype_name() == 'Desktop':
    image_folder = 'images-desktop'
    interval_dnd = 12
else:
    image_folder = 'images-notebook'
    interval_dnd = 16

# print( get_display_resolution() )

def OpenAndDND_in_folder():
    global root

    in_folder       = env_dict['test_in_folder']
    open_folder     = os.path.dirname( in_folder ).replace( '/', '\\' )
    dnd_obj_image   = image_folder + '/AgBh_center.png'

    dnd_from_to( open_folder, dnd_obj_image, root, testee.in_folder_entry  )

def OpenAndDND_adj_folder():
    global root

    adj_folder       = env_dict['test_adj_folder']
    open_folder     = os.path.dirname( adj_folder ).replace( '/', '\\' )
    dnd_obj_image   = image_folder + '/Adjusted.png'

    dnd_from_to( open_folder, dnd_obj_image, root, testee.adj_folder_entry )

def OpenAndDND_syn_folder():
    global root

    syn_folder       = env_dict['test_syn_folder']
    open_folder     = os.path.dirname( syn_folder ).replace( '/', '\\' )
    dnd_obj_image   = image_folder + '/Synthesized.png'

    dnd_from_to( open_folder, dnd_obj_image, root, testee.syn_folder_entry )

def test_DND():
    global tick

    monitors = get_monitors()
    if len( monitors ) > 1:
        print( 'Skipping test_DND for multi-monitor environment.' )
        # return

    clear_settings()
    TkRootAndEntryFrameSetup()

    orig_tick = tick
    tick = 500

    i = 0
    i += 1; root.after( i*tick, lambda: OpenAndDND_in_folder() )
    i += interval_dnd; root.after( i*tick, lambda: typewrite( 'Y' ) )
    i += 4; root.after( i*tick, lambda: OpenAndDND_adj_folder() )
    i += interval_dnd; root.after( i*tick, lambda: OpenAndDND_syn_folder() )
    i += interval_dnd; root.after( i*tick, lambda: root.destroy() )

    root.mainloop();
    testee.__del__()        # 必要。ロガーの削除のため。
    tick = orig_tick

def test_EnvironmentNoChange():
    global i

    if not AutomaticSetting_is_done:
        test_AutomaticSetting()

    reload_settings()

    TkRootAndEntryFrameSetup( after=False )

    i = 0
    i += 1; root.after( i*tick, lambda: testee.after_construction_proc() )
    i += 2; root.after( i*tick, lambda: root.destroy() )
    root.mainloop();
    testee.__del__()        # 必要。ロガーの削除のため。

def test_EnvironmentChangeReplyYes():
    global i

    if not AutomaticSetting_is_done:
        test_AutomaticSetting()

    reload_settings()
    previous_in_folder = get_setting( 'in_folder' )
    # print( 'previous_in_folder=', previous_in_folder )
    set_setting( 'in_folder', previous_in_folder + 'XXX' )

    TkRootAndEntryFrameSetup( after=False )

    i = 0
    i += 1; root.after( i*tick, lambda: testee.after_construction_proc() )
    i += 1; root.after( i*tick, lambda: typewrite( 'Y' ) )
    i += 1; root.after( i*tick, lambda: assert_check_last_message_ok( 'changed' ) )
    i += 2; root.after( i*tick, lambda: root.destroy() )
    root.mainloop();
    testee.__del__()        # 必要。ロガーの削除のため。

def test_EnvironmentChangeReplyNo():
    global i

    if not AutomaticSetting_is_done:
        test_AutomaticSetting()

    reload_settings()
    previous_in_folder = get_setting( 'in_folder' )
    # print( 'previous_in_folder=', previous_in_folder )
    set_setting( 'in_folder', previous_in_folder + 'XXX' )

    TkRootAndEntryFrameSetup( after=False )

    i = 0
    i += 1; root.after( i*tick, lambda: testee.after_construction_proc() )
    i += 1; root.after( i*tick, lambda: assert_check_last_message_ok( 'changed' ) )
    i += 1; root.after( i*tick, lambda: typewrite( 'N' ) )
    i += 2; root.after( i*tick, lambda: root.destroy() )
    root.mainloop();
    testee.__del__()        # 必要。ロガーの削除のため。


def test_InputErrors():
    clear_settings()
    TkRootAndEntryFrameSetup()

    bad_input   = 'XXX'
    in_folder   = env_dict['in_folder1_AgBh_center']
    log_file    = in_folder + '/measurement_AgBh_center.log'

    i = 0

    entries = [
        testee.in_folder_entry,
        testee.log_file_entry,
        testee.mask_file_entry,
        testee.adj_folder_entry,
        testee.syn_folder_entry,
        ]

    test_cases = [
        [ 0, 1, bad_input, log_file ],      # in_folder_entry のエラー
        [ 1, 2, bad_input, in_folder ],     # log_file_entry のエラー
        [ 2, 3, bad_input, in_folder ],     # mask_file_entry のエラー
        [ 3, 4, bad_input, log_file ],      # adj_folder_entry のエラー
        [ 4, 0, bad_input, log_file ],      # syn_folder_entry のエラー
        ]

    for test_case in test_cases:
        t, n, input1, input2 = test_case
        testee_obj  = entries[t]
        next_obj    = entries[n]
        i += 1; root.after( i*tick, lambda testee_=testee_obj   : testee_.focus_force() )
        i += 1; root.after( i*tick, lambda input_=input1        : typewrite( input_  ) )
        i += 1; root.after( i*tick, lambda next_=next_obj       : next_.focus_force() )
        # TODO: get and check messagebox's text
        i += 1; root.after( i*tick, lambda                      : typewrite( ENTER  ) )
        i += 1; root.after( i*tick, lambda testee_=testee_obj   : assert_eq_( testee_.cget('fg'), 'red' ) )

        i += 1; root.after( i*tick, lambda testee_=testee_obj   : testee_.focus_force() )
        i += 1; root.after( i*tick, lambda testee_=testee_obj   : testee_.delete(0, 'end') )
        i += 1; root.after( i*tick, lambda input_=input2        : typewrite( input_  ) )
        i += 1; root.after( i*tick, lambda next_=next_obj       : next_.focus_force() )
        # TODO: get and check messagebox's text
        i += 1; root.after( i*tick, lambda                      : typewrite( ENTER  ) )
        i += 1; root.after( i*tick, lambda: assert_eq_( testee_obj.cget('fg'), 'red' ) )

        i += 1; root.after( i*tick, lambda testee_=testee_obj   : testee_.focus_force() )
        i += 1; root.after( i*tick, lambda testee_=testee_obj   : testee_.delete(0, 'end') )

    i += 1; root.after( i*tick, lambda: root.destroy() )
    root.mainloop();
    testee.__del__()        # 必要。ロガーの削除のため。

def test_teardown():
    eq_( assert_call_count, assert_done_count )

if __name__ == '__main__':
    test_setup()
    # test_InitialEntryControl()
    # test_CreateFolderDialog()
    # test_AutomaticSetting()
    test_DND()
    # test_EnvironmentNoChange()
    # test_EnvironmentChangeReplyYes()
    # test_EnvironmentChangeReplyNo()
    # test_InputErrors()
    test_teardown()
