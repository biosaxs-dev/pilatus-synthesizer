"""logging.Handler that routes log records to a ThreadsConnector queue.

Original: lib/KekLib/ExecutionWindow/bin/LoggerToWindow.py
Copyright (c) SAXS Team, KEK-PF
"""

import logging


class LoggerToWindow(logging.Handler):
    """Forwards log records as text to a :class:`ThreadsConnector`.

    Attach this handler to any Python logger whose output should appear in
    the :class:`ActionWindow` log panel.
    """

    def __init__(self, connector):
        logging.Handler.__init__(self)
        self._connector = connector
        self.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self._connector.put_log(msg)
        except Exception:
            self.handleError(record)
