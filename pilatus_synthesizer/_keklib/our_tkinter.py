"""Tkinter module aliases, Dialog base class, ToolTip, and TkDND re-export.

This module is the central Tk import point for the GUI layer, matching the
import pattern of the legacy ``OurTkinter`` module::

    from pilatus_synthesizer._keklib.our_tkinter import Tk, FileDialog, Dialog, ToolTip, TkDND

``Tk`` is the tkinter package itself (used as ``Tk.Frame``, ``Tk.Label`` etc.).

Original: lib/KekLib/OurTkinter.py
Copyright (c) SAXS Team, KEK-PF
"""

import tkinter as Tk
import tkinter.filedialog as FileDialog
import tkinter.simpledialog as _simpledialog

from pilatus_synthesizer._keklib.tk_dnd_wrapper import TkDND

# Re-export Dialog from tkinter.simpledialog so subclasses work identically
# to the legacy OurTkinter.Dialog (body/buttonbox/apply/validate pattern).
Dialog = _simpledialog.Dialog


# ------------------------------------------------------------------
# ToolTip
# ------------------------------------------------------------------

class ToolTip:
    """Simple hover tooltip for any Tk widget."""

    _PAD_X = 8
    _PAD_Y = 4
    _DELAY_MS = 600

    def __init__(self, widget, text: str):
        self._widget = widget
        self._text = text
        self._tip_window = None
        self._after_id = None
        widget.bind('<Enter>', self._on_enter)
        widget.bind('<Leave>', self._on_leave)
        widget.bind('<ButtonPress>', self._on_leave)

    def _on_enter(self, event=None) -> None:
        self._after_id = self._widget.after(self._DELAY_MS, self._show)

    def _on_leave(self, event=None) -> None:
        if self._after_id:
            self._widget.after_cancel(self._after_id)
            self._after_id = None
        self._hide()

    def _show(self) -> None:
        if self._tip_window or not self._text:
            return
        x = self._widget.winfo_rootx() + self._widget.winfo_width() // 2
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4

        self._tip_window = tw = Tk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f'+{x}+{y}')
        label = Tk.Label(
            tw, text=self._text, justify=Tk.LEFT,
            background='#ffffe0', relief=Tk.SOLID, borderwidth=1,
            font=('TkDefaultFont', 9),
            padx=self._PAD_X, pady=self._PAD_Y,
        )
        label.pack()

    def _hide(self) -> None:
        tw, self._tip_window = self._tip_window, None
        if tw:
            tw.destroy()
