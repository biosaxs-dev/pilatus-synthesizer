"""Tkinter supplement widgets and helpers.

Provides:
  - tk_set_icon_portable(window, name)   — portable icon setter
  - BlinkingFrame                         — attention-drawing animated frame
  - SlimButton                            — compact, low-profile button

Original: lib/KekLib/TkSupplements.py
Copyright (c) SAXS Team, KEK-PF
"""

import os
import tkinter as tk

# Resource directory: pilatus_synthesizer/resource/
_RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'resource',
)


# ------------------------------------------------------------------
# Icon helper
# ------------------------------------------------------------------

def tk_set_icon_portable(window, name: str) -> None:
    """Set the window icon from the package resource directory.

    Tries *name*.ico first (Windows), then *name*.png.  Silently
    skips if neither file exists or setting fails.
    """
    ico = os.path.join(_RESOURCE_DIR, name + '.ico')
    png = os.path.join(_RESOURCE_DIR, name + '.png')
    try:
        if os.name == 'nt' and os.path.exists(ico):
            window.wm_iconbitmap(ico)
        elif os.path.exists(png):
            img = tk.PhotoImage(file=png)
            window.wm_iconphoto(True, img)
            # Keep reference so it isn't GC'd
            window._icon_photo = img
    except Exception:
        pass


# ------------------------------------------------------------------
# BlinkingFrame
# ------------------------------------------------------------------

_BLINK_INTERVAL_MS = 600


class BlinkingFrame(tk.Frame):
    """A transparent container whose children blink to attract attention.

    Children are described as pairs of (widget, pack_kwargs) so that the
    frame can pack and unpack them rhythmically.

    Parameters
    ----------
    master:
        Parent widget.
    object_spec_array:
        List of ``[widget, pack_kwargs_dict]`` pairs that will blink together.
    start_proc:
        Called once when blinking starts.
    stop_proc:
        Called once when blinking stops.
    """

    def __init__(self, master, object_spec_array,
                 start_proc=None, stop_proc=None, debug=False):
        tk.Frame.__init__(self, master)
        self._specs = object_spec_array
        self._start_proc = start_proc
        self._stop_proc = stop_proc
        self._blinking = False
        self._visible = False
        self._after_id = None
        self._show()  # show children immediately at construction

    # ------------------------------------------------------------------
    # Public control
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Begin blinking the contained widgets."""
        if self._blinking:
            return
        self._blinking = True
        if self._start_proc:
            self._start_proc()
        self._blink()

    def stop(self) -> None:
        """Stop blinking and leave widgets visible."""
        if not self._blinking:
            return
        self._blinking = False
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        self._show()
        if self._stop_proc:
            self._stop_proc()

    def is_blinking(self) -> bool:
        return self._blinking

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _show(self) -> None:
        for widget, pack_kw in self._specs:
            widget.pack(**pack_kw)
        self._visible = True

    def _hide(self) -> None:
        for widget, _ in self._specs:
            widget.pack_forget()
        self._visible = False

    def _blink(self) -> None:
        if not self._blinking:
            return
        if self._visible:
            self._hide()
        else:
            self._show()
        self._after_id = self.after(_BLINK_INTERVAL_MS, self._blink)


# ------------------------------------------------------------------
# SlimButton
# ------------------------------------------------------------------

class SlimButton(tk.Button):
    """A compact button suitable for toolbar use."""

    def __init__(self, master, **kwargs):
        kwargs.setdefault('relief', tk.RAISED)
        kwargs.setdefault('padx', 4)
        kwargs.setdefault('pady', 1)
        kwargs.setdefault('bd', 2)
        tk.Button.__init__(self, master, **kwargs)
