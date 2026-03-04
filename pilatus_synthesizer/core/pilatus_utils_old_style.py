"""Old-style log file parsing and data array construction.

Handles the original Pilatus naming convention (prefix_N_NNNNN.ext).

Original: lib/PilatusUtilsOldStyle.py
Copyright (c) 2015-2020, 2025, SAXS Team, KEK-PF
"""

import os
import glob
import re

_separator_line = re.compile(r'^\s*$')
_exec_date_re = re.compile(r'^#Execution date:\s+(.+)$')
_prefix_re = re.compile(r'^#\s+Pilatus1 fileprefix:\s+(\w+)')
_num_cycles_re = re.compile(r'^#\s+Pilatus1 Number of cycles:\s+(\d+)')
_num_changes_re = re.compile(r'^#\s+Pilatus1 Detector position:\s+Change\s+(\d+)')
_position_re = re.compile(
    r'^#\s+Pilatus1 Detector position(\(original\)|\d+):\s+([+-]?\d+\.?\d*),([+-]?\d+\.?\d*)'
)
_wave_length_re = re.compile(r'^#\s+Wavelength:\starget=(\d+\.\d+)')
_energy_re = re.compile(r'^#\s+Energy:\s+target=(\d+)')
_image_ext_re = re.compile(r'\.(tif|cbf)$', flags=re.I)


def _get_ext(file):
    m = _image_ext_re.search(file)
    if m:
        return m.group(1)
    return None


def _regex_glob(folder, regex):
    """Glob files matching regex in folder (no chdir)."""
    globbed_extension = None
    files = []
    for file in glob.glob(os.path.join(folder, '*.*')):
        basename = os.path.basename(file)
        m = regex.search(basename)
        if m:
            globbed_extension = m.group(1)
            files.append(basename)
    return files, globbed_extension


def get_data_info(folder_info, log_file, mask_file,
                  adj_folder, syn_folder, pilatus_counter, counter_id,
                  log_file_path,
                  sample_complete=False, for_test_data=False,
                  logger=None):

    in_folder = folder_info.path
    dict_info = _get_dict_info(in_folder, adj_folder, syn_folder, pilatus_counter, counter_id)

    prefix_info_list, text_dict = get_prefix_info_list(in_folder, log_file_path)
    prefix_dict = {}
    for info in prefix_info_list:
        prefix_dict[info[0]] = info

    image_data_info = []

    for info in prefix_info_list:
        fkey_type_is_old = _get_a_prefix_record_old_style(
            counter_id, dict_info, sample_complete, info, image_data_info
        )
        if not fkey_type_is_old:
            _get_a_prefix_record_new_style(
                counter_id, dict_info, sample_complete, info, image_data_info
            )

    data_array = make_data_array(image_data_info, prefix_dict)

    if for_test_data:
        return data_array, text_dict
    else:
        return log_file, mask_file, data_array, pilatus_counter


def get_prefix_info_list(in_folder, log_file_path):
    prefix = None
    measurement_text = ''
    text_dict = {}
    exec_date = None
    info_exec_date = None

    prefix_info_list = []

    with open(log_file_path) as fh:
        for line in fh.readlines():
            if _separator_line.match(line):
                if prefix != '':
                    text_dict[prefix] = measurement_text
                measurement_text = ''
                exec_date = None
            else:
                measurement_text += line

            me = _exec_date_re.match(line)
            if me:
                exec_date = me.group(1)

            m0 = _prefix_re.match(line)
            if m0:
                if prefix is not None:
                    info_rec = [prefix, num_cycles, num_changes, pos_array, wave_lengths, energies, info_exec_date]
                    prefix_info_list.append(info_rec)

                prefix = m0.group(1)
                info_exec_date = exec_date
                if prefix[-1] == '_':
                    prefix = prefix[:-1]

                pos_info_counter = 0
                num_cycles = 0
                num_changes = 0
                pos_array = []
                wave_lengths = []
                energies = []
                continue

            m1 = _num_cycles_re.match(line)
            if m1:
                num_cycles = int(m1.group(1))

            m2 = _num_changes_re.match(line)
            if m2:
                num_changes = int(m2.group(1))
                continue

            m3 = _position_re.match(line)
            if m3:
                x = m3.group(2)
                y = m3.group(3)
                pos_array.append([x, y])
                continue

            m4 = _wave_length_re.match(line)
            if m4:
                wave_lengths.append('_' + str(int(float(m4.group(1)) * 1000)) + 'A')

            m5 = _energy_re.match(line)
            if m5:
                energies.append('_' + m5.group(1) + 'eV')

    if prefix is not None:
        prefix_info_list.append([prefix, num_cycles, num_changes, pos_array, wave_lengths, energies, info_exec_date])

    if measurement_text != '':
        text_dict[prefix] = measurement_text

    return prefix_info_list, text_dict


def _get_dict_info(in_folder, adj_folder, syn_folder, pilatus_counter, counter_id):
    counter_dict = pilatus_counter.get_counter_dict(counter_id)

    globbed_extension = None
    org_file_dict = {}
    if in_folder and os.path.exists(in_folder):
        files, globbed_extension = _regex_glob(in_folder, _image_ext_re)
        for file in files:
            fkey = re.sub(r'_\d+\.\w+$', '', file, flags=re.I)
            org_file_dict[fkey] = file

    if globbed_extension:
        restricted_image_ext_re = re.compile(r'\.(' + globbed_extension + ')$')
    else:
        restricted_image_ext_re = _image_ext_re

    adj_file_dict = {}
    if adj_folder and os.path.exists(adj_folder):
        files, _ = _regex_glob(adj_folder, restricted_image_ext_re)
        for file in files:
            fkey = re.sub(r'_[^_]+\.\w+$', '', file, flags=re.I)
            adj_file_dict[fkey] = file

    syn_file_dict = {}
    if syn_folder and os.path.exists(syn_folder):
        files, _ = _regex_glob(syn_folder, restricted_image_ext_re)
        for file in files:
            fkey = re.sub(r'_[^_]+\.\w+$', '', file, flags=re.I)
            syn_file_dict[fkey] = file

    return [counter_dict, org_file_dict, adj_file_dict, syn_file_dict]


def _get_a_prefix_record_old_style(counter_id, dict_info, sample_complete, info, image_data_info):
    old_result = True

    counter_dict, org_file_dict, adj_file_dict, syn_file_dict = dict_info
    prefix, num_cycles, num_changes, pos_array, wave_lengths, energies, exec_date = info

    info_array = []
    for i in range(num_changes):
        fkey = '%s_%d' % (prefix, i)
        if i == 0:
            if num_cycles == 1:
                new_prefix_ = prefix
            else:
                new_prefix_ = '%s_%d' % (prefix, i)
            new_fkey = '%s_d%d' % (new_prefix_, i)

            orig_file_count = counter_dict.get(fkey, 0)
            orig_file_count_new = counter_dict.get(new_fkey, 0)
            if orig_file_count == 0 or orig_file_count_new > 0:
                old_result = False
                break
            else:
                ratio = 1.0
        else:
            if counter_id == 'None':
                ratio = 1.0
            else:
                if orig_file_count > 0:
                    ratio = counter_dict.get(fkey) / orig_file_count
                else:
                    ratio = None
        org_file = org_file_dict.get(fkey)
        syn_file = syn_file_dict.get(prefix)
        if not syn_file:
            syn_file = syn_file_dict.get(fkey)
        if org_file and syn_file:
            org_ext = _get_ext(org_file)
            syn_ext = _get_ext(syn_file)
            assert syn_ext == org_ext

        info_array.append([org_file, pos_array[i], ratio, adj_file_dict.get(fkey), syn_file])

    if len(info_array):
        if not sample_complete or len(info_array) == num_changes:
            image_data_info.append([prefix, info_array])

    return old_result


def _get_a_prefix_record_new_style(counter_id, dict_info, sample_complete, info, image_data_info):
    counter_dict, org_file_dict, adj_file_dict, syn_file_dict = dict_info
    prefix, num_cycles, num_changes, pos_array, wave_lengths, energies, exec_date = info

    for suppress_limit in [2, 1]:
        wave_length_list = [''] if len(wave_lengths) < suppress_limit else wave_lengths
        energy_list = [''] if len(energies) < suppress_limit else energies

        num_key_oks = 0
        for wave_length in wave_length_list:
            for energy in energy_list:
                for j in range(num_cycles):
                    if num_cycles == 1:
                        cycle = ''
                    else:
                        cycle = '_%d' % (j)

                    info_array = []
                    for k in range(num_changes):
                        new_prefix_ = prefix + wave_length + energy + cycle
                        fkey = '%s_d%d' % (new_prefix_, k)
                        if k == 0:
                            orig_file_count = counter_dict.get(fkey, 0)
                            if orig_file_count == 0:
                                break
                            else:
                                ratio = 1.0
                                num_key_oks += 1
                        else:
                            if counter_id == 'None':
                                ratio = 1.0
                            else:
                                if orig_file_count > 0:
                                    changed_file_count = counter_dict.get(fkey, 0)
                                    if changed_file_count > 0:
                                        ratio = counter_dict.get(fkey) / orig_file_count
                                    else:
                                        continue
                                else:
                                    assert False
                        syn_file = syn_file_dict.get(new_prefix_)

                        info_array.append([org_file_dict.get(fkey), pos_array[k], ratio,
                                           adj_file_dict.get(fkey), syn_file])

                    if len(info_array):
                        if not sample_complete or len(info_array) == num_changes:
                            image_data_info.append([new_prefix_, info_array, prefix])

        if num_key_oks > 0:
            break


def make_data_array(image_data_info, prefix_dict):
    data_array = []

    for info in image_data_info:
        if len(info) == 2:
            prefix, info_rec = info
            dict_key = prefix
        elif len(info) == 3:
            prefix, info_rec, dict_key = info
        else:
            assert False

        is_lacking = False
        for rec in info_rec:
            if rec[0] is None:
                is_lacking = True

        if is_lacking:
            continue

        prefix_info = prefix_dict.get(dict_key)
        num_changes = prefix_info[2]
        data_array.append([prefix, info_rec, num_changes])

    return data_array
