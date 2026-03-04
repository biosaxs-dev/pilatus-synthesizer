# coding: utf-8
"""
    ThreeDimUtils.py

    Copyright (c) 2018, SAXS Tam, KEK-PF
"""
import numpy                as np

def compute_plane( A, B, C, x, y ):
    """
    base_plane = [
        [ A * x[0] + B * y[0], A * x[0] + B * y[1], A * x[0] + B * y[2] ],
        [ A * x[1] + B * y[0], A * x[1] + B * y[1], A * x[1] + B * y[2] ],
        [ A * x[2] + B * y[0], A * x[2] + B * y[1], A * x[2] + B * y[2] ],
        ...
        ] + C
                = np.dot( [
                            [ A * x[0], 1 ],
                            [ A * x[1], 1 ],
                            [ A * x[2], 1 ],
                              ...
                          ],
                          [
                            [ 1,        1,        1,        ... ],
                            [ B * y[0], B * y[1], B * y[2], ... ].
                            ...
                          ] )

    """
    return np.dot( np.vstack( [ A * x, np.ones( len(x) ) ] ).T, np.vstack( [ np.ones( len(y) ), B * y ] ) ) + C
