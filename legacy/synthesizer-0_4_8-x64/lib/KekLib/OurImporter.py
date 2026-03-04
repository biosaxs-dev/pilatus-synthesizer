# coding: utf-8
"""

    OurImporter.py

    Copyright (c) 2019, Masatsuyo Takahashi, KEK-PF

"""
import imp

def import_module_from_file(name, path):
    fp, pathname, description = imp.find_module(name, path)
    try:
        return imp.load_module(name, fp, pathname, description)
    finally:
        # Since we may exit via an exception, close fp explicitly.
        if fp:
            fp.close()
