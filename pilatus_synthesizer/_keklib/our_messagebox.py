"""Thread-safe message box wrappers for Tkinter.

Dispatches tkinter.messagebox calls safely from any thread by routing
through the Tk event loop when called from a background thread.

Original: lib/KekLib/OurMessageBox.py + OurCommonDialog.py
Copyright (c) SAXS Team, KEK-PF
"""

import threading
import tkinter.messagebox as _tkmb

# ------------------------------------------------------------------
# Thread-safety helper
# ------------------------------------------------------------------

def _call(fn, *args, **kwargs):
    """Call a tkinter.messagebox function, thread-safely.

    If we are already on the main thread (or tkinter's root thread),
    we call directly.  If called from a worker thread, we post the
    call to the main thread via result-sharing and an Event.
    """
    from tkinter import _default_root
    root = _default_root
    if root is None or threading.current_thread() is threading.main_thread():
        return fn(*args, **kwargs)

    # Off-thread: dispatch to main thread and wait for result
    result_holder = [None]
    done = threading.Event()

    def _run():
        result_holder[0] = fn(*args, **kwargs)
        done.set()

    root.after(0, _run)
    done.wait()
    return result_holder[0]


# ------------------------------------------------------------------
# Public API  (mirrors tkinter.messagebox surface)
# ------------------------------------------------------------------

def showinfo(title, message, **kw):
    return _call(_tkmb.showinfo, title, message, **kw)


def showwarning(title, message, **kw):
    return _call(_tkmb.showwarning, title, message, **kw)


def showerror(title, message, **kw):
    return _call(_tkmb.showerror, title, message, **kw)


def askyesno(title, message, **kw):
    return _call(_tkmb.askyesno, title, message, **kw)


def askokcancel(title, message, **kw):
    return _call(_tkmb.askokcancel, title, message, **kw)


def askquestion(title, message, **kw):
    return _call(_tkmb.askquestion, title, message, **kw)


def askyesnocancel(title, message, **kw):
    return _call(_tkmb.askyesnocancel, title, message, **kw)
