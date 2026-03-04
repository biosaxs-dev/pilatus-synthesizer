"""Dialog for selecting / confirming a new folder to create.

Shows a list of suggested folders as radio + text-entry pairs.
The user picks one (editing the path if needed), clicks OK, and the
folder is created via ``os.makedirs``.
If the user cancels, ``applied`` remains False and the caller can fall
back to a normal file-selection dialog.

Original: lib/Synthesizer/CreateFolderDialog.py
Copyright (c) SAXS Team, KEK-PF
"""

import os
import tkinter as tk
import tkinter.simpledialog as simpledialog

from pilatus_synthesizer._keklib.tk_supplements import tk_set_icon_portable


class CreateFolderDialog(simpledialog.Dialog):
    """Modal dialog that offers a list of suggested folder paths."""

    def __init__(self, parent, title: str, suggested_folders: list):
        self.grab = 'local'
        self.suggested_folders = suggested_folders
        self.applied = False
        self.created_folder = None
        super().__init__(parent, title)

    # ------------------------------------------------------------------
    def body(self, frame):
        tk_set_icon_portable(self, 'synthesizer')

        inner = tk.Frame(frame)
        inner.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        tk.Label(
            inner,
            text='Select (and change if necessary) one of the new folders '
                 'suggested below to create.',
        ).pack(anchor=tk.W)

        entry_frame = tk.Frame(inner)
        entry_frame.pack(anchor=tk.W)

        self._selection = tk.IntVar(value=0)
        self._folder_vars = []

        for i, folder in enumerate(self.suggested_folders):
            tk.Radiobutton(
                entry_frame,
                text='',
                variable=self._selection,
                value=i,
            ).grid(row=i, column=0, sticky=tk.W)

            var = tk.StringVar(value=folder)
            self._folder_vars.append(var)
            tk.Entry(entry_frame, textvariable=var, width=80).grid(
                row=i, column=1, sticky=tk.W)

        tk.Label(
            inner,
            text='If you cancel, the file selection dialog will follow.',
        ).pack(anchor=tk.W)

    # ------------------------------------------------------------------
    def apply(self):
        i = self._selection.get()
        selected = self._folder_vars[i].get()
        if not os.path.exists(selected):
            os.makedirs(selected)
        self.created_folder = selected
        self.applied = True
