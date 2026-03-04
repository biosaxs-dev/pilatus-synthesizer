"""Automatic (watch-mode) run controller.

Polls at a fixed interval and re-runs synthesis when new data appears.

Original: lib/Synthesizer/AutoRunController.py
Copyright (c) SAXS Team, KEK-PF
"""

import logging

logger = logging.getLogger(__name__)


class AutoRunController:
    """Periodically refreshes the image table and synthesizes new rows.

    Parameters
    ----------
    controller:
        The main :class:`~pilatus_synthesizer.gui.controller.Controller` window.
    interval_seconds:
        Polling interval.
    image_table:
        :class:`~pilatus_synthesizer.gui.image_table.ImageTable` instance.
    log_file_path:
        Path for logging output.
    on_stop:
        Called when auto-run stops (allows parent to re-enable UI).
    """

    def __init__(self, controller, interval_seconds: int,
                 image_table, log_file_path: str = '',
                 on_stop=None):
        self._controller = controller
        self._interval_ms = int(interval_seconds * 1000)
        self._image_table = image_table
        self._log_file_path = log_file_path
        self._on_stop = on_stop
        self._running = False
        self._after_id = None

    def start(self) -> None:
        """Begin the auto-run polling loop."""
        if self._running:
            return
        self._running = True
        logger.info('Auto-run started (interval=%ds)', self._interval_ms // 1000)
        self._poll()

    def stop(self) -> None:
        """Stop the polling loop."""
        self._running = False
        if self._after_id:
            try:
                self._controller.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        logger.info('Auto-run stopped.')
        if self._on_stop:
            self._on_stop()

    def _poll(self) -> None:
        if not self._running:
            return
        try:
            self._image_table.refresh(
                log_file_path=self._log_file_path,
                restore_view=True,
                autorun=True,
            )
            # After refresh, run synthesis on any newly-selected rows
            if self._image_table.num_selected_rows > 0:
                self._image_table.do_action(3)
        except Exception:
            logger.exception('Auto-run poll error')

        if self._running:
            self._after_id = self._controller.after(self._interval_ms, self._poll)
