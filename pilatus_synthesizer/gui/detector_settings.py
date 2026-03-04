"""Dialog for setting the detector positive-direction.

Stores the result in the application settings.

Original: lib/Synthesizer/DetectorSettings.py
Copyright (c) SAXS Team, KEK-PF
"""

import tkinter as tk
import tkinter.simpledialog as simpledialog

from pilatus_synthesizer._keklib.tk_supplements import tk_set_icon_portable
from pilatus_synthesizer.config.settings import get_setting, set_setting, save_settings


class DetectorSettings(simpledialog.Dialog):
    """Modal dialog for choosing the positive-adjustment direction."""

    def __init__(self, parent, title: str):
        self.applied = False
        simpledialog.Dialog.__init__(self, parent, title)

    def body(self, frame) -> None:
        tk_set_icon_portable(self, 'synthesizer')

        tk.Label(frame, text='Positive Adjust Direction:').grid(
            row=0, column=0, sticky=tk.W, padx=8, pady=8)

        self._direction = tk.StringVar()
        current = get_setting('positive_direction') or 'right'
        self._direction.set(current)

        for col, (label, value) in enumerate(
                [('Left  (KEK-PF style)', 'left'),
                 ('Right (SPring-8 style)', 'right')]):
            tk.Radiobutton(frame, text=label,
                           variable=self._direction, value=value).grid(
                row=0, column=col + 1, sticky=tk.W, padx=4)

    def buttonbox(self) -> None:
        box = tk.Frame(self)
        tk.Button(box, text='OK', width=10, command=self.ok,
                  default=tk.ACTIVE).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(box, text='Cancel', width=10, command=self.cancel).pack(
            side=tk.LEFT, padx=5, pady=5)
        self.bind('<Return>', self.ok)
        self.bind('<Escape>', self.cancel)
        box.pack()

    def apply(self) -> None:
        direction = self._direction.get()
        set_setting('positive_direction', direction)
        save_settings()
        self.applied = True
