"""Pilatus image data utilities — folder inspection and data array construction.

Dispatches between old-style and new-style naming conventions.
Refactored to use absolute paths instead of os.chdir().

Original: lib/PilatusUtils.py
Copyright (c) 2020, 2025, SAXS Team, KEK-PF
"""

import os
import re
import glob
from . import pilatus_counter as pc_module
from .pilatus_utils_old_style import get_data_info as get_data_info_old_style
from .pilatus_utils_new_style import get_data_info as get_data_info_new_style, FILE_NAME_RE

NEW_STYLE_ONLY = True

_old_file_name_re = re.compile(r'(\w+)_(\d)_(\d{5})\.(\w{3})')


def get_in_folder_info(in_folder):
    """Find log and mask files in the input folder (no chdir)."""
    log_files = glob.glob(os.path.join(in_folder, 'measure*.log'))
    if len(log_files) == 0:
        log_files = glob.glob(os.path.join(in_folder, '*.log'))
    mask_files = glob.glob(os.path.join(in_folder, '*.mask'))

    log_file = os.path.basename(log_files[0]) if log_files else None
    mask_file = os.path.basename(mask_files[0]) if mask_files else None

    return log_file, mask_file


class FolderInfo:
    def __init__(self, path):
        self.path = path
        self.single_image = True
        self.new_style = None
        self._get_image_file_names(path)

    def _get_image_file_names(self, folder):
        for ext in ['tif', 'cbf']:
            self.image_files = []
            old_type_files = []
            for path in glob.glob(os.path.join(folder, '*.' + ext)):
                file = os.path.basename(path)
                m = FILE_NAME_RE.match(file)
                if m:
                    self.image_files.append(path)
                    if int(m.group(3)) > 0:
                        self.single_image = False
                else:
                    if _old_file_name_re.match(file):
                        old_type_files.append(path)

            if len(self.image_files) > 0 and len(old_type_files) == 0:
                if self.new_style is None:
                    self.new_style = True
                break
            else:
                if len(old_type_files) > 0:
                    self.new_style = False
                    break

    def is_new_style(self):
        return self.new_style


def get_data_info(in_folder,
                  adj_folder, syn_folder, pilatus_counter, counter_id,
                  log_file_path=None,
                  sample_complete=False, for_test_data=False,
                  logger=None):

    log_file = None
    mask_file = None

    if not in_folder or not os.path.exists(in_folder):
        return log_file, mask_file, [], pilatus_counter

    log_file, mask_file = get_in_folder_info(in_folder)

    if pilatus_counter is None:
        pilatus_counter = pc_module.Counter(in_folder)

    if log_file_path is None:
        log_file_path = in_folder + '/' + log_file

    folder_info = FolderInfo(in_folder)

    if NEW_STYLE_ONLY or folder_info.is_new_style():
        get_data_info_impl = get_data_info_new_style
    else:
        get_data_info_impl = get_data_info_old_style

    return get_data_info_impl(folder_info, log_file, mask_file,
                              adj_folder, syn_folder, pilatus_counter, counter_id,
                              log_file_path, sample_complete, for_test_data,
                              logger=logger)
