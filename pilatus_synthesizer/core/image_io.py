"""Image I/O abstraction for Pilatus detector files.

Supports TIFF (.tif) via MinimalTiff and CBF (.cbf) via fabio.

Original: lib/OurImageIO.py
Copyright (c) 2016, Masatsuyo Takahashi, KEK-PF
"""

import re
from .minimal_tiff import MinimalTiff
import fabio

_extension_dict = {
    'tiff': 'tif',
}

_extension_re = re.compile(r'\.(\w+)$')


class Image:
    def __init__(self, path):
        m = _extension_re.search(path)
        if m:
            ext_ = m.group(1).lower()
        else:
            raise ValueError(f"Cannot determine file extension: {path}")

        if len(ext_) != 3:
            ext_ = _extension_dict.get(ext_)
            if ext_ is None:
                raise ValueError(f"Unsupported extension: {m.group(1)}")

        self.__ext = ext_

        if ext_ == 'tif':
            self.__image = MinimalTiff(path)
            self.__header = self.__image.header
            self.__data = self.__image.data
        elif ext_ == 'cbf':
            self.__image = fabio.open(path)
            self.__data = self.__image.data
        else:
            raise ValueError(f"Unsupported image format: {ext_}")

    def get_header(self):
        return self.__header

    def set_header(self):
        raise AttributeError("header is read-only")

    header = property(get_header, set_header)

    def get_data(self):
        return self.__data

    def set_data(self, data, force=False):
        self.__data = data
        self.__image.data = data

    data = property(get_data, set_data)

    def get_ext(self):
        return self.__ext

    def set_ext(self):
        raise AttributeError("ext is read-only")

    ext = property(get_ext, set_ext)

    def save(self, path):
        self.__image.save(path)
