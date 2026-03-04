"""Minimal TIFF reader/writer for Pilatus detector images.

Reads uncompressed TIFF files preserving the original header byte-for-byte,
allowing data-only modifications and re-saving without header corruption.

Original: lib/MinimalTiff.py
Copyright (c) 2016, Masatsuyo Takahashi, KEK-PF
"""

import sys
import numpy as np


class IfdEntry:
    def __init__(self, buffer):
        assert len(buffer) == 12
        self.tag = '{:04x}'.format(int.from_bytes(buffer[0:2], 'little'))
        self.type = int.from_bytes(buffer[2:4], 'little')
        self.value1 = int.from_bytes(buffer[4:8], 'little')
        self.value2 = int.from_bytes(buffer[8:12], 'little')

    def __str__(self):
        return '[' + ','.join([self.tag, str(self.type), str(self.value1), str(self.value2)]) + ']'


class IFD:
    def __init__(self, block, num_entries):
        self.entry_dict = {}
        for i in range(num_entries):
            start = i * 12
            entry = IfdEntry(block[start:start + 12])
            self.entry_dict[entry.tag] = [entry.type, entry.value1, entry.value2]

    def __str__(self):
        return str(self.entry_dict)


class MinimalTiff:
    def __init__(self, path, header_info_only=False):
        with open(path, 'rb') as fh:
            header_length = 8
            self.header = fh.read(header_length)
            assert self.header[0:4] == b'\x49\x49\x2A\x00'

            offset = int.from_bytes(self.header[4:6], 'little')

            self.pre_ifd_texts = []

            to_read_bytes = offset - header_length
            block1 = b''
            if to_read_bytes > 0:
                block1 = fh.read(to_read_bytes)

                nonzero_bytes = ''
                for byte in block1[0:-2]:
                    if byte == 0:
                        if len(nonzero_bytes) > 0:
                            self.pre_ifd_texts.append(nonzero_bytes)
                            nonzero_bytes = ''
                    else:
                        nonzero_bytes += chr(byte)

            self.header += block1

            word = fh.read(2)
            self.header += word

            num_entries = int.from_bytes(word, 'little')

            to_read_bytes = num_entries * 12
            block2 = fh.read(to_read_bytes)
            self.header += block2

            self.ifd = ifd = IFD(block2, num_entries)

            # Baseline Tags
            self.cols = ifd.entry_dict['0100'][2]       # ImageWidth
            self.rows = ifd.entry_dict['0101'][2]       # ImageLength
            num_bits = ifd.entry_dict['0102'][2]        # BitsPerSample
            compression = ifd.entry_dict['0103'][2]     # Compression
            data_offset = ifd.entry_dict['0111'][2]     # StripOffsets
            data_size = ifd.entry_dict['0117'][2]       # StripByteCounts

            # Extension Tags
            tag_0153 = ifd.entry_dict.get('0153')       # SampleFormat
            data_type = tag_0153[2] if tag_0153 else None

            if compression != 1:
                sys.exit("Sorry, this module can't read compressed files!")

            to_read_bytes = data_offset - len(self.header)
            block3 = fh.read(to_read_bytes)
            self.header += block3

            data_buffer = fh.read()
            assert len(data_buffer) == data_size

            num_bytes = num_bits // 8

            dtype_ = 'i%d' % num_bytes
            if data_type == 2:
                pass
            elif data_type == 3:
                dtype_ = 'f%d' % num_bytes
            else:
                pass
            self.data = np.frombuffer(data_buffer, dtype=dtype_).copy()
            self.data.shape = (self.rows, self.cols)
            self.dtype = self.data.dtype

    def save(self, path):
        if self.data.shape != (self.rows, self.cols):
            sys.exit("You can't change the shape of the data.")

        if self.data.dtype != self.dtype:
            sys.exit("You can't change the dtype of the data.")

        with open(path, 'wb') as fh:
            fh.write(self.header)
            fh.write(self.data.tobytes())
