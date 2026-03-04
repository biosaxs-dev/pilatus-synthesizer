"""Matplotlib extensions for the image viewer.

Provides:
  - CoordinateFormatter  — status-bar pixel coordinate / intensity formatter
  - DataCursor           — Shift+click annotation cursor
  - ColorBar             — log-scale decorating colour bar

Original: lib/KekLib/OurMatplotlib.py
Copyright (c) SAXS Team, KEK-PF
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar

from pilatus_synthesizer._keklib.control_key_state import get_shift_key_state


# ------------------------------------------------------------------
# CoordinateFormatter
# ------------------------------------------------------------------

class CoordinateFormatter:
    """Callable that formats cursor position and pixel intensity for the
    matplotlib status bar.

    Parameters
    ----------
    numrows, numcols:
        Image array dimensions.
    im_array_list:
        List of 2-D arrays whose values are reported at the cursor position.
    value_shift:
        Subtracted from each intensity before display (for offset data).
    """

    def __init__(self, numrows: int, numcols: int, im_array_list: list,
                 value_shift: int = 0):
        self.numrows = numrows
        self.numcols = numcols
        self.im_array_list = im_array_list
        self.value_shift = value_shift
        self.ic = None
        self.ir = None

    def __call__(self, x, y) -> str:
        self.ic = int(x + 0.5)
        self.ir = int(y + 0.5)
        if (0 <= self.ic < self.numcols) and (0 <= self.ir < self.numrows):
            intensities = [
                '%d' % (arr[self.ir, self.ic] - self.value_shift)
                for arr in self.im_array_list
            ]
            return 'x=%d, y=%d, intensity=[ %s ]' % (
                self.ic, self.ir, ', '.join(intensities))
        return 'x=%d, y=%d' % (self.ic, self.ir)


# ------------------------------------------------------------------
# DataCursor
# ------------------------------------------------------------------

class DataCursor:
    """Shift+click annotation cursor for detector images.

    Click with shift held to pin an annotation; arrow keys nudge it one pixel;
    Escape removes it.
    """

    text_template = 'x: %d\ny: %d\ni: %d'
    xoffset, yoffset = -20, 20

    def __init__(self, ax_list: list, action: int, value_shift: int = 0):
        self.ax_list = ax_list
        self.action = action
        self.value_shift = value_shift
        self.x = None
        self.y = None
        annotation_color = 'cyan' if action == 1 else 'yellow'
        self.annotations = []
        for ax in ax_list:
            ann = ax.annotate(
                self.text_template,
                xy=(0, 0), xytext=(self.xoffset, self.yoffset),
                textcoords='offset points', ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc=annotation_color, alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'),
            )
            ann.set_visible(False)
            self.annotations.append(ann)

    def __call__(self, event_type: int, event,
                 im_array_list: list = (), im_shift_list: list = ()) -> None:
        """Handle key-press (event_type=1) or button-press (event_type=3)."""
        if event_type == 1:
            if event.key == 'escape':
                for ann in self.annotations:
                    ann.set_visible(False)
                event.canvas.draw()
                return
            if self.x is None:
                return
            if event.key == 'up':
                self.y -= 1
            elif event.key == 'down':
                self.y += 1
            elif event.key == 'right':
                self.x += 1
            elif event.key == 'left':
                self.x -= 1
            else:
                return
        else:  # button_press
            if not get_shift_key_state():
                return
            self.x, self.y = event.xdata, event.ydata

        y_limit, x_limit = im_array_list[0].shape

        def _compute_x_offset(ax, x):
            xmin, xmax = ax.get_xlim()
            span = xmax - xmin if xmax != xmin else 1
            return 50 if (x - xmin) * x_limit / span < 200 else -20

        for i, (ann, ax) in enumerate(zip(self.annotations, self.ax_list)):
            if self.action == 1 and i < len(im_shift_list):
                shift = im_shift_list[i]
                if len(shift) == 2:
                    x_, y_ = int(self.x + shift[1]), int(self.y + shift[0])
                else:
                    x_, y_ = int(self.x), int(self.y)
            else:
                x_, y_ = int(self.x), int(self.y)

            if 0 <= x_ < x_limit and 0 <= y_ < y_limit:
                intensity = im_array_list[i][y_, x_] - self.value_shift
                ann.xy = (x_, y_)
                ann.set_text(self.text_template % (x_, y_, intensity))
                ann.set_visible(True)
                ann.set_position((_compute_x_offset(ax, x_), 20))
            else:
                ann.set_visible(False)

        event.canvas.draw()


# ------------------------------------------------------------------
# ColorBar
# ------------------------------------------------------------------

class ColorBar:
    """Logarithmic colour bar attached to a matplotlib axes."""

    def __init__(self, im, ax):
        ticks = np.logspace(1.0, 6.0, num=6)
        labels = [r'$10^{%d}$' % t for t in range(1, 7)]

        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='4%', pad=0.05)
        self.cb = plt.colorbar(im, cax, ticks=ticks)
        self.cb.set_ticklabels(labels)
