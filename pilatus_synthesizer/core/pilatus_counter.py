"""Pilatus detector counter file reader.

Reads PilatusCounter_*.txt files to extract photon count data
per image, used for intensity ratio normalization.

Original: lib/PilatusCounter.py
Copyright (c) 2015-2024, Masatsuyo Takahashi, KEK-PF
"""

import os
import glob
import re
import pandas as pd
from collections import defaultdict


class Counter:
    def __init__(self, in_folder):
        self.in_folder = in_folder
        self.counter_tables = []

        counter_files = glob.glob(os.path.join(in_folder, 'PilatusCounter_*.txt'))

        for file in counter_files:
            counter_table = pd.read_table(file)
            self.counter_tables.append(counter_table)

    def get_counter_dict(self, counter_id):
        counter_dict = {}

        for counter_table in self.counter_tables:
            if counter_id == 'None':
                counter = None
            else:
                counter = counter_table[counter_id]
            for i in range(counter_table.File.size):
                file_id = re.sub(r'\.\w+$', '', counter_table.File[i])
                fkey = file_id

                if counter_id == 'None':
                    count = 1
                else:
                    count = counter[i]
                counter_dict[fkey] = count

        return counter_dict

    def available_counters(self):
        available_keys = defaultdict(lambda: 0)
        for counter_table in self.counter_tables:
            for colname, series in counter_table.items():
                if colname[0] != 'C':
                    continue
                available = True
                for num in series:
                    if num <= 0:
                        available = False
                        break
                if available:
                    available_keys[colname] += 1

        return sorted(available_keys.keys())
