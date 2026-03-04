"""TIFF property display window.

Shows the IMAGEDESCRIPTION metadata from a Pilatus TIFF in a scrollable
text window.

Original: lib/Synthesizer/PilatusImageProperty.py (GUI part)
Copyright (c) SAXS Team, KEK-PF
"""

import tkinter as tk

from pilatus_synthesizer._keklib.tk_supplements import tk_set_icon_portable
from pilatus_synthesizer.core.image_property import get_properties


class ImagePropertyWindow(tk.Toplevel):
    """Non-modal window that displays a TIFF image's property text."""

    def __init__(self, parent, title: str, path: str):
        tk.Toplevel.__init__(self, parent)
        self.title(title)
        tk_set_icon_portable(self, 'synthesizer')

        text_widget = tk.Text(self, setgrid=True, height=20, width=80)
        text_widget.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        try:
            text = get_properties(path)
        except Exception as exc:
            text = f'Could not read properties: {exc}'

        text_widget.insert('1.0', text)
        text_widget.configure(state='disabled')
