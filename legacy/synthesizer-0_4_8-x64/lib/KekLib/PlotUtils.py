# coding: utf-8
"""
    PlotUtils.py

    Copyright (c) 2016, Masatsuyo Takahashi, KEK-PF
"""
import numpy                as np

def get_wider_range( vmin, vmax, ratio ):
    vmin_   = vmin * ( 1 + ratio ) + vmax * ( -ratio )
    vmax_   = vmin * ( -ratio ) + vmax * ( 1 + ratio )
    return vmin_, vmax_

def convert_to_the_level( yval, ymin, ymax, posf, post, vmin=None, vmax=None ):
    # print( 'convert_to_the_level: vmin, vmax=', vmin, vmax )
    if vmin is None:
        vmin = np.min( yval )
    if vmax is None:
        vmax = np.max( yval )
    ymin_ = ymin * ( 1 - posf ) + ymax * posf
    ymax_ = ymin * ( 1 - post ) + ymax * post
    ratio = ( ymax_ - ymin_ ) / ( vmax - vmin )
    return ( yval - vmin ) * ratio + ymin_

def plot_line( ax, x, y, rec, color, label=None, plot_qrg=False ):
    Rg, a, b, f, t = rec

    a_ = - ( Rg**2 / 3 )
    y0 = b + a_ * x[f]
    y1 = b + a_ * x[t]

    print( 'plot_line: Rg=', Rg, '; a=', a )
    print( [ x[f], x[t] ], [ y0, y1 ] )

    ax.plot( [ x[f], x[t] ], [ y0, y1 ], marker='o', color=color, label=label )
