"""Tkinter window geometry helpers.

Provides geometry string parsing, construction, and screen-boundary
adjustment without the MultiMonitor dependency of the legacy code.

Original: lib/KekLib/TkUtils.py (simplified)
Copyright (c) SAXS Team, KEK-PF
"""

import re
import tkinter


def split_geometry(geometry: str):
    """Parse a Tk geometry string ``"WxH+X+Y"`` into ``(W, H, X, Y)`` ints.

    Returns ``(None, None, None, None)`` if the string cannot be parsed.
    """
    m = re.match(r'(\d+)x(\d+)\+(-?\d+)\+(-?\d+)', geometry)
    if not m:
        return None, None, None, None
    return int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))


def join_geometry(w: int, h: int, x: int, y: int) -> str:
    """Format integers into a Tk geometry string ``"WxH+X+Y"``."""
    return f'{w}x{h}+{x}+{y}'


def adjusted_geometry(geometry: str) -> str:
    """Clamp a geometry string so the window stays within the primary screen.

    Falls back to the original string if the root window is unavailable
    or the geometry cannot be parsed.
    """
    w, h, x, y = split_geometry(geometry)
    if w is None:
        return geometry

    root = tkinter._default_root
    if root is None:
        return geometry

    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()

    x = max(0, min(x, sw - w))
    y = max(0, min(y, sh - h))

    return join_geometry(w, h, x, y)
