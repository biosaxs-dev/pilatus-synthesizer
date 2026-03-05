"""Modal execution window with scrolled log, progress bar, and Cancel/OK.

Opens a Toplevel when a long-running calculation starts.  The window polls
the :class:`ThreadsConnector` queue via ``after()`` and updates the log and
progress bar.  When the calculation is done the Cancel button becomes OK.

Original: lib/KekLib/ExecutionWindow/bin/ActionWindow.py
Copyright (c) SAXS Team, KEK-PF
"""

import queue
import tkinter as tk

from pilatus_synthesizer._keklib.execution_window.progress_bar_view import ProgressBarView
from pilatus_synthesizer._keklib.execution_window.threads_connector import ThreadsConnector
from pilatus_synthesizer._keklib.tk_supplements import tk_set_icon_portable

_POLL_INTERVAL_MS = 80


class ActionWindow(tk.Toplevel):
    """Progress / log window for background calculations.

    Parameters
    ----------
    parent:
        The parent Tk window.
    title:
        Window title.
    connector:
        The :class:`ThreadsConnector` shared with the worker thread.
    max_progress:
        Total number of steps (sets the progress-bar scale).
    on_ok:
        Callback invoked when the user presses OK after completion.
    on_cancel:
        Callback invoked if the user cancels before completion.
    """

    def __init__(self, parent, title: str,
                 connector: ThreadsConnector,
                 max_progress: int = 100,
                 on_ok=None, on_cancel=None):
        tk.Toplevel.__init__(self, parent)

        # Set geometry before any widgets are packed so the WM honours it.
        top = parent.winfo_toplevel()
        top.update_idletasks()
        pw = top.winfo_width()
        px = top.winfo_rootx()
        py = top.winfo_rooty()
        self.geometry(f'{pw}x500+{px}+{py + 40}')

        self.title(title)
        self.resizable(True, True)
        tk_set_icon_portable(self, 'synthesizer')

        self._connector = connector
        self._on_ok = on_ok
        self._on_cancel = on_cancel
        self._done = False

        # --- log area -------------------------------------------------------
        log_frame = tk.Frame(self)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 4))

        yscroll = tk.Scrollbar(log_frame, orient=tk.VERTICAL)
        xscroll = tk.Scrollbar(log_frame, orient=tk.HORIZONTAL)
        self._log = tk.Text(
            log_frame, height=16, width=100, state='disabled',
            font=('Courier', 9), wrap=tk.NONE,
            yscrollcommand=yscroll.set,
            xscrollcommand=xscroll.set,
        )
        yscroll.config(command=self._log.yview)
        xscroll.config(command=self._log.xview)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._log.pack(fill=tk.BOTH, expand=True)

        # --- progress bar ---------------------------------------------------
        pb_frame = tk.Frame(self)
        pb_frame.pack(fill=tk.X, padx=8, pady=4)

        self._progress = ProgressBarView(pb_frame, max_value=max_progress,
                                         width=460, height=16)
        self._progress.pack(fill=tk.X)

        # --- button area ----------------------------------------------------
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=8, pady=(4, 8))

        self._btn = tk.Button(btn_frame, text='Cancel', width=10,
                              command=self._on_button)
        self._btn.pack()

        self.protocol('WM_DELETE_WINDOW', self._on_button)
        self.transient(parent)
        self.grab_set()

        self._poll()

    # ------------------------------------------------------------------
    # Polling
    # ------------------------------------------------------------------

    def _poll(self) -> None:
        try:
            while True:
                msg_type, payload = self._connector.get_nowait()
                if msg_type == 'log':
                    self._append_log(payload)
                elif msg_type == 'progress':
                    self._progress.set_value(payload)
                elif msg_type == 'done':
                    self._on_done(success=payload)
                    return
                elif msg_type == 'cancelled':
                    self._on_cancelled()
                    return
        except queue.Empty:
            pass

        if not self._done:
            self.after(_POLL_INTERVAL_MS, self._poll)

    # ------------------------------------------------------------------
    # Internal state transitions
    # ------------------------------------------------------------------

    def _append_log(self, text: str) -> None:
        self._log.configure(state='normal')
        self._log.insert(tk.END, text + '\n')
        self._log.see(tk.END)
        self._log.configure(state='disabled')

    def _on_done(self, success: bool) -> None:
        self._done = True
        self._progress.set_value(self._progress._max)
        self._btn.configure(text='OK')

    def _on_cancelled(self) -> None:
        self._done = True
        self._btn.configure(text='OK')

    def _on_button(self) -> None:
        if self._done:
            if self._on_ok:
                self._on_ok()
            self.grab_release()
            self.destroy()
        else:
            self._connector.request_cancel()
            self._btn.configure(state='disabled', text='Cancelling…')
            if self._on_cancel:
                self._on_cancel()
