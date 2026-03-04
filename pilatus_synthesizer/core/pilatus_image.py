"""Pilatus detector image with sub-pixel shift and mask support.

Core image processing: shift-adjustment (bilinear interpolation or pixel-round),
mask application, gap-filling (cover), and multi-image averaging.

Pixel size: 172 μm.  Invalid values: -2 (masked), -3 (insufficient coverage).

Original: lib/PilatusImage.py
Copyright (c) 2015-2025, SAXS Team, KEK-PF
"""

import re
import numpy as np
from .image_io import Image
from .sangler_mask import SAnglerMask

SIZE_OF_PIXEL = 172
HALF_SIZE_OF_PIXEL = SIZE_OF_PIXEL // 2
INVALID_VALUE = -3

_comment_line_re = re.compile(r'^#\s+(\w+)=(.+)')


def pixel_rounded_shift(delta):
    """Convert a shift in μm to the nearest whole-pixel offset."""
    i_ = delta // SIZE_OF_PIXEL
    r_ = delta % SIZE_OF_PIXEL
    if r_ >= HALF_SIZE_OF_PIXEL:
        i_ += 1
    return i_


class PilatusImage:
    """Pilatus detector image with shift/mask adjustment.

    Parameters
    ----------
    file : str or numpy.ndarray
        File path to load, or pre-existing image array.
    mask_data : str or numpy.ndarray
        Path to .mask file, mask array, or '' for no mask.
    dy, dx : int
        Vertical / horizontal shift in μm.
    i_ratio : float
        Intensity ratio for normalization.
    a_ratio : float
        Minimum coverage ratio for bilinear interpolation.
    original_image : PilatusImage or None
        Reference image when ``file`` is an ndarray.
    direction : str or None
        'left' (KEK-PF) or 'right' (SPring-8). Controls sign of dx.
    algorithm : str
        Adjustment algorithm: 'fast' (default), 'round', or 'slow'.
    """

    def __init__(self, file, mask_data='', dy=0, dx=0,
                 i_ratio=1.0, a_ratio=0.5, original_image=None,
                 direction=None, algorithm='fast'):
        if direction is None:
            assert dx == 0
        else:
            if direction == 'right':
                dx = -dx
            else:
                assert direction == 'left'

        self.image = None

        if not isinstance(file, np.ndarray):
            self.image = Image(file)
            self.imarray = np.array(self.image.data)
        else:
            assert original_image is not None
            self.image = original_image.image
            self.imarray = file

        if isinstance(mask_data, np.ndarray):
            self.mask_array = mask_data
            self.has_mask = True
        elif mask_data not in ('', None):
            self._set_mask(mask_data)
            self.has_mask = True
        else:
            self.mask_array = None
            self.has_mask = False

        if self.has_mask:
            assert self.imarray.shape == self.mask_array.shape

        self.shifted = not (dy == 0 and dx == 0)
        if self.shifted:
            self.ir = dy // SIZE_OF_PIXEL
            self.dr = dy % SIZE_OF_PIXEL
            self.ic = dx // SIZE_OF_PIXEL
            self.dc = dx % SIZE_OF_PIXEL
            self.ir_rounded = pixel_rounded_shift(dy)
            self.ic_rounded = pixel_rounded_shift(dx)

        self.i_ratio = i_ratio

        if self.has_mask or self.shifted:
            if algorithm == 'round':
                self.round_adjust()
            elif algorithm == 'fast':
                self.fast_adjust(a_ratio)
            else:
                self.adjust(a_ratio)

    def image_array(self):
        return self.imarray

    def _set_mask(self, maskfile):
        mask_object = SAnglerMask(maskfile)
        self.mask_array = mask_object.mask_array

    def compute_cratios(self):
        self.cratios = []
        for p, q in ([0, 0], [0, 1], [1, 0], [1, 1]):
            v_prop = ((1 - p) * (SIZE_OF_PIXEL - self.dr) + p * self.dr) / SIZE_OF_PIXEL
            h_prop = ((1 - q) * (SIZE_OF_PIXEL - self.dc) + q * self.dc) / SIZE_OF_PIXEL
            self.cratios.append(v_prop * h_prop)

    # ------------------------------------------------------------------
    #   Slow bilinear adjustment (pixel-by-pixel Python loop)
    # ------------------------------------------------------------------
    def adjust(self, a_ratio):
        if self.shifted:
            self.compute_cratios()

        imarray_ = np.zeros(self.imarray.shape)

        numrows, numcols = self.imarray.shape
        for i in range(numrows):
            for j in range(numcols):
                imarray_[i, j] = self._intensity_rc(i, j, a_ratio)

        self.imarray = imarray_
        self.image.set_data(self.imarray, force=True)

    def _intensity_rc(self, r, c, a_ratio):
        if not self.shifted:
            intensity = self.imarray[r, c]
            if self.has_mask and self.mask_array[r, c]:
                intensity = -2
        else:
            intensity = 0
            cover_ratio = 0

            k = -1
            for p, q in ([0, 0], [0, 1], [1, 0], [1, 1]):
                k += 1
                i = r + self.ir + p
                if not (0 <= i < self.imarray.shape[0]):
                    continue
                j = c + self.ic + q
                if not (0 <= j < self.imarray.shape[1]):
                    continue
                value = self.imarray[i, j]
                if self.has_mask and self.mask_array[i, j]:
                    value = -2

                if value < 0:
                    continue

                ratio = self.cratios[k]
                intensity += value * ratio
                cover_ratio += ratio

            if cover_ratio < a_ratio:
                intensity = -3
            elif cover_ratio < 1.0:
                intensity /= cover_ratio

        if intensity > 0:
            intensity /= self.i_ratio

        return int(intensity)

    # ------------------------------------------------------------------
    #   Pixel-rounded adjustment (fastest — integer pixel shift)
    # ------------------------------------------------------------------
    def round_adjust(self):
        if self.has_mask:
            self.imarray[self.mask_array == 1] = -2

        if not self.shifted:
            return

        adjusted_array = np.ones(self.imarray.shape) * (-2)

        row, col = self.imarray.shape
        adj_min_r = max(0, 0 - self.ir_rounded)
        adj_max_r = min(row, row - self.ir_rounded)
        adj_min_c = max(0, 0 - self.ic_rounded)
        adj_max_c = min(col, col - self.ic_rounded)
        sft_min_r = max(0, 0 + self.ir_rounded)
        sft_max_r = min(row, row + self.ir_rounded)
        sft_min_c = max(0, 0 + self.ic_rounded)
        sft_max_c = min(col, col + self.ic_rounded)

        adjusted_array[adj_min_r:adj_max_r, adj_min_c:adj_max_c] = \
            self.imarray[sft_min_r:sft_max_r, sft_min_c:sft_max_c]
        self.imarray = adjusted_array.astype('i4')
        self.image.set_data(self.imarray, force=True)

    # ------------------------------------------------------------------
    #   Fast bilinear adjustment (numpy vectorized)
    # ------------------------------------------------------------------
    def fast_adjust(self, a_ratio):
        if self.has_mask:
            self.imarray[self.mask_array == 1] = -2

        if not self.shifted:
            return

        self.compute_cratios()

        numrows, numcols = self.imarray.shape
        extended_array = np.ones([numrows + 2, numcols + 2]) * INVALID_VALUE
        extended_array[1:numrows + 1, 1:numcols + 1] = self.imarray

        a00_r_min = max(0 + self.ir, 0)
        a00_r_max = min(numrows + self.ir + 1, numrows + 1)
        a00_c_min = max(0 + self.ic, 0)
        a00_c_max = min(numcols + self.ic + 1, numcols + 1)

        k = 0
        for p, q in ([0, 0], [0, 1], [1, 0], [1, 1]):
            carray_ = extended_array[
                (a00_r_min + p):(a00_r_max + p),
                (a00_c_min + q):(a00_c_max + q)
            ] * (self.cratios[k] / self.i_ratio)

            if k == 0:
                v_array = np.zeros(carray_.shape, dtype='f8')
                w_array = np.zeros(carray_.shape, dtype='f8')

            valid_cond_ = carray_ >= 0
            v_array[valid_cond_] += carray_[valid_cond_]
            w_array[valid_cond_] += self.cratios[k]

            k += 1

        v_array[w_array < a_ratio] = INVALID_VALUE

        valid_cond = w_array >= a_ratio
        v_array[valid_cond] /= w_array[valid_cond]

        b00_r_min = max(0 - self.ir, 0)
        if b00_r_min > 0:
            b00_r_min -= 1
            r_offset = 0
        else:
            r_offset = 1
        b00_r_max = b00_r_min + v_array.shape[0] - r_offset
        b00_c_min = max(0 - self.ic, 0)
        if b00_c_min > 0:
            b00_c_min -= 1
            c_offset = 0
        else:
            c_offset = 1
        b00_c_max = b00_c_min + v_array.shape[1] - c_offset

        imarray_ = np.ones(self.imarray.shape, dtype='i4') * INVALID_VALUE

        imarray_[b00_r_min:b00_r_max, b00_c_min:b00_c_max] = \
            v_array[r_offset:v_array.shape[0], c_offset:v_array.shape[1]]

        self.imarray = imarray_
        self.image.set_data(self.imarray, force=True)

    # ------------------------------------------------------------------
    #   Gap-filling: base image authoritative, shifted fills gaps
    # ------------------------------------------------------------------
    def fast_make_covered_array(self, other):
        assert self.imarray.shape == other.imarray.shape

        covered_array = self.imarray.copy()
        valid_cond = np.logical_and(self.imarray < 0, other.imarray >= 0)
        covered_array[valid_cond] = other.imarray[valid_cond]

        return covered_array.astype('i4')

    # ------------------------------------------------------------------
    #   Multi-image averaging
    # ------------------------------------------------------------------
    def fast_make_average_array(self, counter_array, sum_array):
        im_array = np.ones(counter_array.shape, dtype='i4') * INVALID_VALUE

        valid_cond = counter_array > 0
        im_array[valid_cond] = sum_array[valid_cond] / counter_array[valid_cond]

        return im_array

    # ------------------------------------------------------------------
    #   Test / utility methods
    # ------------------------------------------------------------------
    def diff(self, other):
        diff_imarray = np.zeros(self.imarray.shape)
        diff_imarray[self.imarray != other.imarray] = 10000
        return PilatusImage(diff_imarray, original_image=self, algorithm='fast')

    def save(self, path):
        assert self.image is not None
        self.image.save(path)

    def equal(self, other):
        diff_im_array = self.diff(other).image_array()
        return (diff_im_array == np.zeros(self.imarray.shape)).all()
