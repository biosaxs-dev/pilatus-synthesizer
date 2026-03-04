# coding: utf-8
"""
    EnvironCheck.py

    Copyright (c) 2018, Masatsuyo Takahashi, KEK-PF
"""

def executables_check(parent):
    try:
        import numba
        numba_is_available = True
    except:
        numba_is_available = False

    if numba_is_available:
        ret = True
    else:
        import OurMessageBox as MessageBox
        yn = MessageBox.askyesno("Old executables warning",
            "It seems you are using an old version of executables.\n"
            "It would be desirable if you could take some to update.\n"
            "Or, extrapolation with smoothing will be significantly slow.\n"
            "Would you like to proceed anyway?",
            parent=parent)
        ret = yn
    return ret
