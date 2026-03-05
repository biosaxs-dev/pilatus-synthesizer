"""Drag-and-drop wrapper for the bundled tkdnd2.8 Tcl package.

Provides a ``TkDND`` helper that registers drop targets on Tk widgets.
The bundled ``tkdnd2.8/`` directory is loaded automatically if the system
does not already have tkdnd installed.

Usage::

    dnd = TkDND(some_widget)
    dnd.bindtarget(entry_widget, my_callback, 'text/uri-list')

The callback receives a synthetic event with a ``data`` attribute containing
the dropped text.

Original: lib/KekLib/TkDndWrapper.py
Copyright (c) SAXS Team, KEK-PF
"""

import os
import tkinter

TKDND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tkdnd2.8')

# tkdnd substitution variables passed to every DnD callback
_SUBST_FORMAT = ('%A', '%a', '%b', '%D', '%d', '%m', '%T',
                 '%W', '%X', '%Y', '%x', '%y')
_SUBST_FORMAT_STR = ' '.join(_SUBST_FORMAT)


class TkDND:
    """Thin wrapper around the tkdnd2.8 Tcl package."""

    def __init__(self, widget):
        self._available = False
        self._master = widget.winfo_toplevel()
        self._tk = self._master.tk
        try:
            try:
                self._tk.call('package', 'require', 'tkdnd')
            except tkinter.TclError:
                self._tk.call('lappend', 'auto_path', TKDND_DIR)
                self._tk.call('package', 'require', 'tkdnd')
            self._available = True
        except tkinter.TclError:
            print('Warning: tkdnd not available – drag-and-drop disabled.')

    # ------------------------------------------------------------------

    def bindtarget(self, widget, callback, dndtype: str, priority: int = 50) -> None:
        """Register *widget* as a drop target for *dndtype* data.

        Parameters
        ----------
        widget:
            The Tk widget to receive drops.
        callback:
            Callable receiving a synthetic event with ``.widget`` and
            ``.data`` attributes.
        dndtype:
            MIME-like type string, e.g. ``'text/uri-list'``.
        """
        if not self._available:
            return

        cmd = self._prepare_dnd_func(widget, callback)
        self._tk.call('dnd', 'bindtarget', widget, dndtype, '<Drop>', cmd, priority)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _prepare_dnd_func(self, widget, callback):
        """Register *callback* with Tcl and return the Tcl command string."""
        funcid = self._master.register(callback, self._dnd_substitute)
        return f'{funcid} {_SUBST_FORMAT_STR}'

    def _dnd_substitute(self, *args):
        """Convert raw Tcl DnD substitution args into a synthetic Event."""
        if len(args) != len(_SUBST_FORMAT):
            return args

        def _try_int(x):
            try:
                return int(str(x))
            except ValueError:
                return x

        A, a, b, D, d, m, T, W, X, Y, x, y = args

        event = tkinter.Event()
        event.action      = A
        event.action_list = str(a).split()
        event.mouse_button = _try_int(b)
        event.data        = D
        event.descr       = d
        event.modifier    = m
        event.dndtype     = T
        event.widget      = self._master.nametowidget(W)
        event.x_root      = _try_int(X)
        event.y_root      = _try_int(Y)
        event.x           = _try_int(x)
        event.y           = _try_int(y)

        return (event,)
