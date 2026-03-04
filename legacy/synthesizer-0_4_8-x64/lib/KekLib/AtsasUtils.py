# coding: utf-8
"""
    AtsasUtils.py

    Copyright (c) 2016-2020, SAXS Team, KEK-PF
"""
import os
import glob

def get_dirs_in_later_order(pattern):
    paths = glob.glob(pattern)
    paths.sort(reverse=True)
    return paths

def get_autorg_exe_paths():
    dir_patterns = [r'C:\Program Files (x86)\ATSAS*', r'C:\atsas*']
    autorg_exe_array = []
    for dir_ in get_dirs_in_later_order(dir_patterns[0]) + get_dirs_in_later_order(dir_patterns[1]):
        for sub_dir in [ r'\bin', '' ]:
            exe_path = dir_ + sub_dir + r'\autorg.exe'
            if os.path.exists( exe_path ):
                autorg_exe_array.append( exe_path )
                break
    return autorg_exe_array
