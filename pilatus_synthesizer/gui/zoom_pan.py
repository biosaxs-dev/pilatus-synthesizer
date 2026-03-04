"""Scroll-zoom and drag-pan for the Pilatus image matplotlib axes.

Binds:
  - Mouse-wheel (or trackpad scroll) → zoom in/out centred on the cursor,
    adjusted by Ctrl key for finer/coarser steps.
  - Middle-button drag (or Ctrl+left-drag) → pan.

Original: lib/Synthesizer/ZoomPan.py
Copyright (c) SAXS Team, KEK-PF
"""

import numpy as np
from pilatus_synthesizer._keklib.control_key_state import (
    get_ctrl_key_state, set_shift_key_state, set_ctrl_key_state,
)
from pilatus_synthesizer._keklib.our_color_maps import CmapAlbulaLikeDynamic


class ZoomPan:
    """Attach scroll-zoom and drag-pan behaviour to one or more matplotlib axes.

    Parameters
    ----------
    fig:
        The matplotlib Figure.
    ax_list:
        List of ``Axes`` that share the same zoom/pan state.
    cmap:
        Initial colourmap (must expose an ``adjusted_cmap(delta)`` method
        for brightness adjustment via Ctrl+wheel).
    im_list:
        Optional list of ``AxesImage`` objects; when provided, Ctrl+wheel
        adjusts the colourmap brightness instead of zooming.
    """

    _ZOOM_FACTOR = 1.3
    _CTRL_ZOOM_FACTOR = 1.05
    _CMAP_DELTA = 0.02

    def __init__(self, fig, ax_list: list, cmap=None, im_list=None):
        self._fig = fig
        self._ax_list = ax_list
        self._cmap = cmap
        self._im_list = im_list or []

        self._press_data = None  # (x0, y0, xlim, ylim) on pan start

        canvas = fig.canvas
        canvas.mpl_connect('scroll_event', self._on_scroll)
        canvas.mpl_connect('button_press_event', self._on_press)
        canvas.mpl_connect('button_release_event', self._on_release)
        canvas.mpl_connect('motion_notify_event', self._on_motion)
        canvas.mpl_connect('key_press_event', self._on_key_press)
        canvas.mpl_connect('key_release_event', self._on_key_release)

    # ------------------------------------------------------------------
    # Key state tracking
    # ------------------------------------------------------------------

    def _on_key_press(self, event) -> None:
        if event.key in ('shift', 'shift+shift'):
            set_shift_key_state(True)
        elif event.key in ('ctrl', 'control'):
            set_ctrl_key_state(True)

    def _on_key_release(self, event) -> None:
        if event.key in ('shift', 'shift+shift'):
            set_shift_key_state(False)
        elif event.key in ('ctrl', 'control'):
            set_ctrl_key_state(False)

    # ------------------------------------------------------------------
    # Scroll (zoom or brightness)
    # ------------------------------------------------------------------

    def _on_scroll(self, event) -> None:
        if event.inaxes not in self._ax_list:
            return

        if get_ctrl_key_state() and self._im_list and isinstance(self._cmap, CmapAlbulaLikeDynamic):
            # Ctrl+scroll → adjust colourmap brightness
            delta = self._CMAP_DELTA if event.button == 'up' else -self._CMAP_DELTA
            self._cmap = self._cmap.adjusted_cmap(delta)
            for im in self._im_list:
                im.set_cmap(self._cmap)
            self._fig.canvas.draw_idle()
            return

        # Normal scroll → zoom about cursor position
        factor = self._CTRL_ZOOM_FACTOR if get_ctrl_key_state() else self._ZOOM_FACTOR
        zoom_in = event.button == 'up'
        scale = 1.0 / factor if zoom_in else factor

        xdata, ydata = event.xdata, event.ydata
        if xdata is None or ydata is None:
            return

        for ax in self._ax_list:
            xl, xr = ax.get_xlim()
            yb, yt = ax.get_ylim()
            ax.set_xlim([xdata + (xl - xdata) * scale,
                         xdata + (xr - xdata) * scale])
            ax.set_ylim([ydata + (yb - ydata) * scale,
                         ydata + (yt - ydata) * scale])

        self._fig.canvas.draw_idle()

    # ------------------------------------------------------------------
    # Pan (middle-button or ctrl+left)
    # ------------------------------------------------------------------

    def _on_press(self, event) -> None:
        if event.inaxes not in self._ax_list:
            return
        if event.button == 2 or (event.button == 1 and get_ctrl_key_state()):
            ax = self._ax_list[0]
            self._press_data = (event.xdata, event.ydata,
                                ax.get_xlim(), ax.get_ylim())

    def _on_release(self, event) -> None:
        self._press_data = None

    def _on_motion(self, event) -> None:
        if self._press_data is None or event.inaxes not in self._ax_list:
            return
        x0, y0, xlim, ylim = self._press_data
        if event.xdata is None or event.ydata is None:
            return
        dx = event.xdata - x0
        dy = event.ydata - y0
        for ax in self._ax_list:
            xl, xr = ax.get_xlim()
            yb, yt = ax.get_ylim()
            ax.set_xlim(xl - dx, xr - dx)
            ax.set_ylim(yb - dy, yt - dy)
        self._fig.canvas.draw_idle()
