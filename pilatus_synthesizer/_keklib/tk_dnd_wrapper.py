"""Drag-and-drop wrapper for the bundled tkdnd2.8 Tcl package.

Provides a ``TkDND`` helper that registers drop targets on Tk widgets.
The bundled ``tkdnd2.8/`` directory is loaded automatically if the system
does not already have tkdnd installed.

Usage::

    dnd = TkDND(some_widget)
    dnd.bindtarget(entry_widget, my_callback, 'text/uri-list')

The callback receives a synthetic event with a ``data`` attribute containing
the dropped text (after stripping ``{`` / ``}`` that Windows adds around
paths with spaces).

Original: lib/KekLib/TkDndWrapper.py
Copyright (c) SAXS Team, KEK-PF
"""

import os
import tkinter

TKDND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tkdnd2.8')


class TkDND:
    """Thin wrapper around the tkdnd2.8 Tcl package."""

    def __init__(self, widget):
        self._available = False
        try:
            root = widget.winfo_toplevel()
            try:
                root.tk.call('package', 'require', 'tkdnd')
            except tkinter.TclError:
                root.tk.call('lappend', 'auto_path', TKDND_DIR)
                root.tk.call('package', 'require', 'tkdnd')
            self._available = True
        except tkinter.TclError:
            print('Warning: tkdnd not available – drag-and-drop disabled.')

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

        widget.tk.call('tkdnd::drop_target', 'register', widget._w, dndtype)

        # Build a unique Tcl command name for this widget
        cmd_name = f'_pilatus_dnd_{id(widget):x}'

        class _DropEvent:
            __slots__ = ('widget', 'data')

            def __init__(self, w, d):
                self.widget = w
                self.data = d

        def _tcl_handler(raw_data: str) -> str:
            event = _DropEvent(widget, raw_data)
            try:
                callback(event)
            except Exception as exc:
                print(f'DnD callback error: {exc}')
            return 'copy'  # inform tkdnd the drop succeeded

        # Replace any previous binding for this widget
        try:
            widget.tk.deletecommand(cmd_name)
        except Exception:
            pass
        widget.tk.createcommand(cmd_name, _tcl_handler)
        widget.tk.call('bind', widget._w, '<<Drop>>', f'{cmd_name} %D')
