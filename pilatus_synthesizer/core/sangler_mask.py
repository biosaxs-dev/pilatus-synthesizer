"""SAngler mask file reader.

Reads .mask files produced by SAngler software, creating a binary pixel mask
array for Pilatus detector images.

Original: lib/SAnglerMask.py
Copyright (c) 2015-2025, SAXS Team, KEK-PF
"""

import re
import numpy as np

_comment_line_re = re.compile(r'^#\s+(\w+)=(.+)')


class SAnglerMask:
    def __init__(self, filename):
        width, height = 0, 0
        self.mask_array = []

        with open(filename) as fh:
            for line in fh.readlines():
                m1 = _comment_line_re.match(line)
                if m1:
                    key_word = m1.group(1)
                    value = m1.group(2)
                    if key_word == 'Width':
                        width = int(value)
                    elif key_word == 'Height':
                        height = int(value)
                    continue

                if width == 0 or height == 0:
                    raise ValueError('Wrong format: Width/Height not set before data')

                if len(self.mask_array) == 0:
                    self.mask_array = np.zeros([height, width])

                for pair in line.split("\t"):
                    parts = pair.split()
                    if len(parts) == 2:
                        c, r = parts
                        self.mask_array[int(r), int(c)] = 1

        if width == 0 or height == 0:
            raise ValueError('Wrong format: missing Width/Height in mask file')
