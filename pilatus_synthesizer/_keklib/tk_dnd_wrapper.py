"""Drag-and-drop wrapper using python-tkdnd (pip install python-tkdnd).

Provides a ``TkDND`` helper that registers drop targets on Tk widgets.
Requires the root Tk window to be created via ``tkinterDnD.Tk``.

Usage::

    dnd = TkDND(some_widget)
    dnd.bindtarget(entry_widget, my_callback, 'text/uri-list')

The callback receives an event with a ``data`` attribute containing
the dropped text.

Original: lib/KekLib/TkDndWrapper.py
Copyright (c) SAXS Team, KEK-PF
"""


class TkDND:
    """Thin wrapper around python-tkdnd (tkinterDnD)."""

    def __init__(self, widget):
        self._available = False
        try:
            import tkinterDnD  # noqa: F401 — ensures package is present
            self._available = True
        except ImportError:
            print('Warning: python-tkdnd not installed – drag-and-drop disabled.')

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

        widget.drop_target_register(dndtype)
        widget.dnd_bind('<<Drop>>', callback)
