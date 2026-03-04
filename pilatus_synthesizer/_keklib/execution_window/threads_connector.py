"""Thread ↔ GUI message bus for the execution window.

The connector decouples the calculation thread from tkinter by routing
messages through a ``queue.Queue``.  The ActionWindow polls this queue
via ``after()`` on the main thread.

Message types:
  - ``('log',  str)``       — append a line to the log panel
  - ``('progress', int)``   — update the progress bar (absolute value)
  - ``('done', bool)``      — calculation finished; True = success
  - ``('cancelled', None)`` — cancellation was acknowledged

Original: lib/KekLib/ExecutionWindow/bin/ThreadsConnector.py
Copyright (c) SAXS Team, KEK-PF
"""

import queue
import threading
from typing import Callable, Any


class ThreadsConnector:
    """Queue-based connector between a worker thread and the Tk main loop."""

    def __init__(self):
        self._queue: queue.Queue = queue.Queue()
        self._cancel_event = threading.Event()

    # ------------------------------------------------------------------
    # Worker-thread API
    # ------------------------------------------------------------------

    def put_log(self, message: str) -> None:
        self._queue.put(('log', message))

    def put_progress(self, value: int) -> None:
        self._queue.put(('progress', value))

    def put_done(self, success: bool = True) -> None:
        self._queue.put(('done', success))

    def put_cancelled(self) -> None:
        self._queue.put(('cancelled', None))

    def is_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    # ------------------------------------------------------------------
    # Main-thread API
    # ------------------------------------------------------------------

    def request_cancel(self) -> None:
        self._cancel_event.set()

    def get_nowait(self):
        """Non-blocking dequeue; raises ``queue.Empty`` if nothing pending."""
        return self._queue.get_nowait()

    # ------------------------------------------------------------------
    # Thread launcher
    # ------------------------------------------------------------------

    def run_in_thread(self, func: Callable, *args, **kwargs) -> threading.Thread:
        """Run *func* in a daemon thread, posting ``done`` when it returns."""

        def _target():
            try:
                func(*args, **kwargs)
                self.put_done(True)
            except Exception as exc:
                self.put_log(f'ERROR: {exc}')
                self.put_done(False)

        t = threading.Thread(target=_target, daemon=True)
        t.start()
        return t
