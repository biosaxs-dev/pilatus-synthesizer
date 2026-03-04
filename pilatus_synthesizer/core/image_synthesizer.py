"""Core image synthesis engine.

Pure computation: no GUI dependencies, no global config reads.
All parameters are passed explicitly.

Original: lib/ImageSynthesizer.py (computation extracted)
Copyright (c) 2015-2020, SAXS Team, KEK-PF
"""

import re
import logging
import numpy as np
from .pilatus_image import PilatusImage, pixel_rounded_shift

logger = logging.getLogger(__name__)


def synthesize_pair(original_path, shifted_path, mask_array,
                    dy, dx, direction, i_ratio=1.0, a_ratio=0.5,
                    algorithm='fast', method='cover',
                    counter_array=None, sum_array=None):
    """Synthesize two images: an original and a shifted secondary.

    Parameters
    ----------
    original_path : str or numpy.ndarray
        Path to the base image file, or an existing image array.
    shifted_path : str
        Path to the shifted (secondary) image file.
    mask_array : numpy.ndarray or None
        Pixel mask array (1 = masked).
    dy, dx : int
        Vertical / horizontal shift in μm.
    direction : str
        'left' (KEK-PF) or 'right' (SPring-8).
    i_ratio : float
        Intensity ratio for normalization.
    a_ratio : float
        Minimum coverage ratio for bilinear interpolation.
    algorithm : str
        Adjustment algorithm: 'fast', 'round', or 'slow'.
    method : str
        Synthesis method: 'cover' (gap-fill) or 'average'.
    counter_array : numpy.ndarray or None
        Running valid-pixel counter (for 'average' method).
    sum_array : numpy.ndarray or None
        Running intensity sum (for 'average' method).

    Returns
    -------
    result_array : numpy.ndarray
        Synthesized image data (int32).
    o_pim : PilatusImage
        The base PilatusImage (for saving).
    counter_array : numpy.ndarray or None
        Updated counter (only for 'average').
    sum_array : numpy.ndarray or None
        Updated sum (only for 'average').
    """
    # Load original
    if isinstance(original_path, np.ndarray):
        raise ValueError("For array input, use synthesize_pair_from_arrays()")

    o_pim = PilatusImage(original_path, mask_array if mask_array is not None else '',
                         algorithm=algorithm)
    oim_array = o_pim.image_array()

    if method == 'average' and counter_array is None:
        # Initialize running accumulators
        counter_array = np.zeros(oim_array.shape, dtype='i4')
        sum_array = np.zeros(oim_array.shape, dtype='f8')
        valid_cond = oim_array >= 0
        counter_array[valid_cond] += 1
        sum_array[valid_cond] += oim_array[valid_cond]

    # Load and adjust shifted image
    a_pim = PilatusImage(shifted_path,
                         mask_array if mask_array is not None else '',
                         dy, dx, i_ratio, a_ratio,
                         direction=direction, algorithm=algorithm)

    if method == 'cover':
        result_array = o_pim.fast_make_covered_array(a_pim)
    else:
        a_im_array = a_pim.image_array()
        valid_cond = a_im_array >= 0
        counter_array[valid_cond] += 1
        sum_array[valid_cond] += a_im_array[valid_cond]
        result_array = o_pim.fast_make_average_array(counter_array, sum_array)

    return result_array, o_pim, counter_array, sum_array


def exec_single_synthesis(sample_id, base_rec, fkey, sub_rec,
                          isfinal, mask_array, direction,
                          in_folder, adj_folder, syn_folder,
                          syn_method='cover', min_ratio=0.5,
                          adj_output=False, postfix_adj='_adj',
                          postfix_syn='_syn', algorithm='fast',
                          intermediate_results=False,
                          previous_im=None,
                          valid_value_sum_array=None,
                          valid_pixel_counter_array=None):
    """Execute a single synthesis step.

    Returns
    -------
    dict with keys: result_array, previous_im, valid_value_sum_array,
    valid_pixel_counter_array
    """
    o_file = base_rec[0]
    if not isinstance(o_file, np.ndarray):
        o_path = '%s/%s' % (in_folder, o_file)
        o_pim = PilatusImage(o_path, mask_array if mask_array is not None else '',
                             algorithm=algorithm)
        o_ext = o_pim.image.ext
        previous_im = o_pim

        if syn_method == 'average':
            oim_array = o_pim.image_array()
            valid_value_sum_array = np.zeros(oim_array.shape, dtype='f8')
            valid_pixel_counter_array = np.zeros(oim_array.shape, dtype='i4')

            valid_cond = oim_array >= 0
            valid_pixel_counter_array[valid_cond] += 1
            valid_value_sum_array[valid_cond] += oim_array[valid_cond]
    else:
        o_pim = PilatusImage(o_file, original_image=previous_im, algorithm=algorithm)
        o_ext = previous_im.image.ext

    s_file = sub_rec[0]
    s_path = '%s/%s' % (in_folder, s_file)
    s_delta = []
    for d in sub_rec[1]:
        s_delta.append(int(float(d) * 1000))

    i_ratio = sub_rec[2]
    a_ratio = min_ratio
    a_pim = PilatusImage(s_path,
                         mask_array if mask_array is not None else '',
                         s_delta[0], s_delta[1], i_ratio, a_ratio,
                         direction=direction, algorithm=algorithm)

    if adj_output and adj_folder:
        a_file = '%s%s.%s' % (fkey, postfix_adj, o_ext)
        w_path = '%s/%s' % (adj_folder, a_file)
        a_pim.save(w_path)

    if syn_method == 'cover':
        result_im_array = o_pim.fast_make_covered_array(a_pim)
    else:
        a_im_array = a_pim.image_array()
        valid_cond = a_im_array >= 0
        valid_pixel_counter_array[valid_cond] += 1
        valid_value_sum_array[valid_cond] += a_im_array[valid_cond]
        result_im_array = o_pim.fast_make_average_array(
            valid_pixel_counter_array, valid_value_sum_array
        )

    if isfinal:
        fkey_ = sample_id
    else:
        fkey_ = fkey

    if isfinal or intermediate_results:
        z_file = '%s%s.%s' % (fkey_, postfix_syn, o_ext)
        if syn_folder:
            w_path = '%s/%s' % (syn_folder, z_file)
            o_pim.image.set_data(result_im_array, force=True)
            o_pim.save(w_path)

    return {
        'result_array': result_im_array,
        'previous_im': previous_im,
        'valid_value_sum_array': valid_value_sum_array,
        'valid_pixel_counter_array': valid_pixel_counter_array,
    }
