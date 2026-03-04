# -*- coding: utf-8 -*-
"""
   tests for ImageSynthesizer.py

"""
from __future__ import division, print_function, unicode_literals

import sys
import os
import time
import numpy as np
from nose.tools     import eq_
from pyautogui      import typewrite, moveTo, click, keyDown, keyUp, scroll, dragRel

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )

import KekLib, Synthesizer
from OurTkinter         import Tk
from PilatusImage       import PilatusImage
from PilatusImageViewer import PilatusImageViewer
from TestTkUtils        import split_geometry

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

def test_load():
    assert True

in_folder           = env_dict['in_folder1_AgBh_center']

syn_method  = 'syn_method'

ENTER       = [ 'enter' ]
tick        = 500

def test_setup():
    pass

def show_image():
    global viewer
    global exec_params

    viewer = PilatusImageViewer( 1, 'AgBh002', exec_params )

def show_data_cursor():
    global viewer
    w, h, x, y = split_geometry( viewer.winfo_geometry() )
    x_ = x + w/2
    y_ = y + h/2
    moveTo( x_, y_ )
    keyDown( 'shift' )
    click()
    keyUp( 'shift' )
    viewer.update()
    time.sleep( 0.5 )
    typewrite( [ 'escape' ] )

def show_zoom_pan():
    global viewer

    viewer.focus()
    scroll( 100 )
    viewer.update()
    time.sleep( 0.5 )
    scroll( -100 )
    viewer.update()

    w, h, x, y = split_geometry( viewer.winfo_geometry() )
    x_ = x + w/2
    y_ = y + h/2
    moveTo( x_, y_ )
    dragRel( 50, 50 )
    viewer.update()

    time.sleep( 0.5 )
    dragRel( -50, -50 )
    viewer.update()

    time.sleep( 0.5 )
    scroll( -100 )
    viewer.update()
    scroll( -100 )

    time.sleep( 0.5 )
    keyDown( 'ctrl' )
    viewer.update()
    time.sleep( 0.1 )
    scroll( 100 )
    viewer.update()

    time.sleep( 0.5 )
    scroll( -100 )
    viewer.update()
    keyUp( 'ctrl' )

def test_viewer():
    global viewer
    global exec_params

    in_folder   = env_dict['in_folder1_AgBh_center']
    file        = 'AgBh002_0_00000.tif'
    pim         = PilatusImage( in_folder + '/' + file )
    exec_params = []
    exec_params.append( [ file, pim.image_array() ] )

    root = Tk.Tk()
    # root.withdraw()
    i = 0
    i += 1; root.after( i*tick, lambda: show_image() )
    i += 6; root.after( i*tick, lambda: show_data_cursor() )
    i += 6; root.after( i*tick, lambda: show_zoom_pan() )
    i += 12; root.after( i*tick, lambda: viewer.quit_button.invoke() )
    i += 1; root.after( i*tick, lambda: root.destroy() )
    root.mainloop()

    viewer = None

def test_teardown():
    pass

if __name__ == '__main__':
    test_setup()
    test_viewer()
    test_teardown()
