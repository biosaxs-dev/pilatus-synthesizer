"""File-changeable logger with in-memory stream capture.

Wraps Python's logging module to support runtime log file changes and
buffered stream output (for ActionWindow display).

Original: lib/KekLib/ChangeableLogger.py
Copyright (c) SAXS Team, KEK-PF
"""

import io
import logging


class Logger:
    """Logger that can change its output file at runtime."""

    def __init__(self, path: str = None):
        # Use a unique logger name to avoid cross-instance contamination
        self._logger = logging.getLogger(f'pilatus_synthesizer.{id(self):x}')
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

        # Always-on stream buffer for get_stream_buffer()
        self._stream = io.StringIO()
        fmt = logging.Formatter('%(levelname)s: %(message)s')
        sh = logging.StreamHandler(self._stream)
        sh.setFormatter(fmt)
        self._logger.addHandler(sh)

        self._file_handler = None
        if path:
            self.changeto(path)

    # ------------------------------------------------------------------
    # File handler management
    # ------------------------------------------------------------------

    def changeto(self, path: str) -> None:
        """Switch the log file to *path* (creates or appends)."""
        if self._file_handler:
            self._logger.removeHandler(self._file_handler)
            self._file_handler.close()
            self._file_handler = None
        try:
            fh = logging.FileHandler(path, encoding='utf-8')
            fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
            self._logger.addHandler(fh)
            self._file_handler = fh
        except OSError as e:
            self._logger.warning('Could not open log file %s: %s', path, e)

    def get_stream_buffer(self) -> str:
        """Return all text written to the in-memory stream so far."""
        return self._stream.getvalue()

    # ------------------------------------------------------------------
    # Logging convenience methods
    # ------------------------------------------------------------------

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self._logger.exception(msg, *args, **kwargs)

    def __del__(self):
        if self._file_handler:
            try:
                self._logger.removeHandler(self._file_handler)
                self._file_handler.close()
            except Exception:
                pass
