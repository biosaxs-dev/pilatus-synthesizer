# coding: utf-8
"""

    ファイル名：   TkUtils.py

    処理内容：

    Copyright (c) 2016-2020, Masatsuyo Takahashi, KEK-PF

"""
import os
import sys
import re
from MultiMonitor import get_selected_monitor

DO_NO_ADJUST_GEOMETRY   = 'DO_NO_ADJUST_GEOMETRY'

def split_geometry( geometry ):
    n = geometry.split('+')
    s = n[0].split('x')
    w = int( s[0] )
    h = int( s[1] )
    x = 0 if len(n) < 2 else int( n[1] )
    y = 0 if len(n) < 3 else int( n[2] )
    return [ w, h, x, y ]

def join_geometry( w, h, x, y ):
    return '%dx%d+%d+%d' % ( w, h, x, y )

def geometry_fix( top, x, y ):
    W, H, X, Y = split_geometry( top.geometry() )
    top.geometry( join_geometry( W, H, x, y ) )
    top.update()

"""
    URL: http://effbot.org/tkinterbook/wm.htm
"""
def parsegeometry(geometry):
    m = re.match("(\d+)x(\d+)([-+]\d+)([-+]\d+)", geometry)
    if not m:
        raise ValueError("failed to parse geometry string")
    return map(int, m.groups())

def convert_to_tkgeometry( monitor ):
    return re.sub( r'monitor\((.+)\)', '\g<1>', str( monitor ) )

do_not_adjust_geometry = os.environ.get( DO_NO_ADJUST_GEOMETRY )
"""
    TODO:
    some tests seem to go wrong with adjusted geometry.
    it may have been improved by self.udate() before applying adjusted geometry.
"""

def adjusted_geometry( geometry, monitor=None, width_margin=0, height_margin=0.15, loc=None, debug=False ):
    global max_monitor, monitors

    if do_not_adjust_geometry:
        return geometry

    if monitor is None:
        monitor = get_selected_monitor()

    try:
        w0, h0, x0, y0 = split_geometry( geometry )
        w1, h1, x1, y1 = monitor.width, monitor.height, monitor.x,  monitor.y
        if debug:
            print(w0, h0, x0, y0)
            print(w1, h1, x1, y1)

        w1_ = int(w1 * (1-width_margin) )
        h1_ = int( h1 * (1-height_margin) )

        if loc is None:
            pass
        elif loc == "center":
            x1 += w1//2 - w0//2
            y1 += h1//2 - h0//2
        else:
            assert False

        return join_geometry( min(w0, w1_), min(h0, h1_), x1, y1 )
    except:
        return geometry

def geometry_move( toplevel, parent, x=50, y=50 ):
    x_, y_ = (parent.winfo_rootx()+x, parent.winfo_rooty()+y)
    # print( 'geometry_move: x_, y_=',  x_, y_  )
    toplevel.geometry("+%d+%d" % ( x_, y_ ) )

def rational_geometry( self, parent, w_ratio=0.5, h_ratio=0.5 ):
    w, h, x, y = split_geometry( parent.geometry() )
    x_, y_ = (parent.winfo_rootx() + int(w*w_ratio), parent.winfo_rooty() + int(h*h_ratio))
    self.geometry("+%d+%d" % ( x_, y_ ) )

def is_low_resolution():
    try:
        monitor = get_selected_monitor()
        # print( monitor.width, monitor.height )
        return monitor.height < 800
    except:
        # it seems this can occur
        return False

def get_widget_geometry(widget):
    w = widget.winfo_width()
    h = widget.winfo_height()
    x = widget.winfo_rootx()
    y = widget.winfo_rooty()
    return (w, h, x, y)

def get_tk_root(loc=None, withdraw=True):
    import tkinter
    from DebugPlot import set_plot_env
    root = tkinter.Tk()
    adj_geometry = adjusted_geometry(root.geometry(), loc=loc)
    root.geometry(adj_geometry)
    if withdraw:
        root.withdraw()
    root.update()
    set_plot_env(root)
    return root
