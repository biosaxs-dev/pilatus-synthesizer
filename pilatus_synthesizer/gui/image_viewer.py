"""Pilatus image viewer Toplevel window.

Shows one or more detector images side-by-side in a matplotlib canvas
with zoom/pan, data cursor, log-scale colour bar, and navigation toolbar.

Original: lib/Synthesizer/PilatusImageViewer.py
Copyright (c) SAXS Team, KEK-PF
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

from pilatus_synthesizer._keklib.our_color_maps import get_colour_map
from pilatus_synthesizer._keklib.our_matplotlib import (
    NavigationToolbar, CoordinateFormatter, DataCursor, ColorBar,
)
from pilatus_synthesizer._keklib.tk_supplements import tk_set_icon_portable
from pilatus_synthesizer._keklib.control_key_state import (
    set_shift_key_state, set_ctrl_key_state,
)
from pilatus_synthesizer.gui.zoom_pan import ZoomPan
from pilatus_synthesizer.config.preferences import get_preference

_MIN_INTENSITY = 1          # displayed minimum (log scale)
_MAX_INTENSITY = 1_000_000  # displayed maximum


class PilatusImageViewer(tk.Toplevel):
    """Tkinter Toplevel showing one or more Pilatus detector images.

    Parameters
    ----------
    action:
        1 = show originals, 2 = show adjusted.
    sample_id:
        Used as the window title.
    exec_params:
        List of ``[filename, im_array]`` or
        ``[filename, im_array, dy_pixel, dx_pixel]`` entries (one per column).
    """

    def __init__(self, action: int, sample_id: str, exec_params: list):
        tk.Toplevel.__init__(self)
        self.title(sample_id)
        tk_set_icon_portable(self, 'synthesizer')

        n_images = len(exec_params)
        if n_images == 0:
            self.destroy()
            return

        cmap_name = get_preference('color_map') or 'ALBULA'
        cmap = get_colour_map(cmap_name)

        # Build matplotlib figure
        fig, axes = plt.subplots(1, n_images, squeeze=False,
                                 figsize=(5 * n_images, 5))
        axes = axes[0]  # flatten to 1-D list

        ax_list = list(axes)
        im_list = []
        im_array_list = []
        im_shift_list = []

        for i, (ax, params) in enumerate(zip(ax_list, exec_params)):
            filename = params[0]
            im_array = params[1]
            shift = params[2:4] if len(params) >= 4 else []

            im_array_list.append(im_array)
            im_shift_list.append(shift)

            # Clip and display with log-scale norm
            disp = np.clip(im_array.astype(float), _MIN_INTENSITY, _MAX_INTENSITY)
            from matplotlib.colors import LogNorm
            im = ax.imshow(disp, cmap=cmap, norm=LogNorm(
                vmin=_MIN_INTENSITY, vmax=_MAX_INTENSITY), origin='upper')
            im_list.append(im)

            ax.set_title(filename, fontsize=8)
            ax.format_coord = CoordinateFormatter(
                im_array.shape[0], im_array.shape[1], [im_array])

            # Colour bar on last axis only
            if i == n_images - 1:
                ColorBar(im, ax)

        # Share zoom/pan across all axes
        if len(ax_list) > 1:
            for ax in ax_list[1:]:
                ax.sharex(ax_list[0])
                ax.sharey(ax_list[0])

        fig.tight_layout()

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar(canvas, self)
        toolbar.update()

        # Zoom/pan and data cursor
        self._zoom_pan = ZoomPan(fig, ax_list, cmap=cmap, im_list=im_list)

        self._data_cursor = DataCursor(ax_list, action)

        def on_key(event):
            if event.key in ('shift', 'shift+shift'):
                set_shift_key_state(True)
            elif event.key in ('ctrl', 'control'):
                set_ctrl_key_state(True)
            self._data_cursor(1, event, im_array_list, im_shift_list)

        def on_key_release(event):
            if event.key in ('shift', 'shift+shift'):
                set_shift_key_state(False)
            elif event.key in ('ctrl', 'control'):
                set_ctrl_key_state(False)

        def on_click(event):
            self._data_cursor(3, event, im_array_list, im_shift_list)

        canvas.mpl_connect('key_press_event', on_key)
        canvas.mpl_connect('key_release_event', on_key_release)
        canvas.mpl_connect('button_press_event', on_click)

        self.protocol('WM_DELETE_WINDOW', self._on_close)
        self._fig = fig

    def _on_close(self):
        plt.close(self._fig)
        self.destroy()
