"""Canvas-based progress bar widget.

Original: lib/KekLib/ExecutionWindow/bin/ProgressBarView.py
Copyright (c) SAXS Team, KEK-PF
"""

import tkinter as tk


class ProgressBarView(tk.Canvas):
    """Horizontal progress bar drawn on a Canvas.

    Parameters
    ----------
    master:
        Parent widget.
    max_value:
        The value that corresponds to a full bar.
    width, height:
        Canvas dimensions in pixels.
    bar_color:
        Fill colour for the progress bar.
    """

    def __init__(self, master, max_value: int = 100,
                 width: int = 300, height: int = 16,
                 bar_color: str = 'steel blue', **kwargs):
        kwargs.setdefault('bg', '#e0e0e0')
        kwargs.setdefault('bd', 1)
        kwargs.setdefault('relief', tk.SUNKEN)
        tk.Canvas.__init__(self, master, width=width, height=height, **kwargs)
        self._max = max_value
        self._width = width
        self._height = height
        self._bar_color = bar_color
        self._bar = self.create_rectangle(0, 0, 0, height, fill=bar_color, outline='')
        self._value = 0

    def set_value(self, value: int) -> None:
        """Update the displayed progress to *value* (clipped to [0, max])."""
        self._value = max(0, min(value, self._max))
        filled_w = int(self._width * self._value / self._max) if self._max else 0
        self.coords(self._bar, 0, 0, filled_w, self._height)
        self.update_idletasks()

    def reset(self) -> None:
        self.set_value(0)
