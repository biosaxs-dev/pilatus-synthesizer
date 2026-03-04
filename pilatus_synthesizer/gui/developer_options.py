"""Developer options dialog.

Exposes algorithm tuning knobs (adj_algorithm, min_ratio, adj_output,
postfix_adj, intermediate_results) to advanced users.

Original: lib/Synthesizer/Development.py (DeveloperOptionsDialog class)
Copyright (c) 2015–2020, SAXS Team, KEK-PF
"""

import tkinter as tk
import tkinter.simpledialog as simpledialog

from pilatus_synthesizer._keklib.tk_supplements import tk_set_icon_portable
from pilatus_synthesizer.config.development import (
    get_devel_info, set_devel_info,
)


class DeveloperOptionsDialog(simpledialog.Dialog):
    """Modal dialog for developer / algorithm options."""

    def __init__(self, parent, title: str):
        self.applied = False
        super().__init__(parent, title)

    # ------------------------------------------------------------------
    def body(self, frame):
        tk_set_icon_portable(self, 'synthesizer')

        inner = tk.Frame(frame)
        inner.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        row = 0

        # ── Adjust Algorithm ─────────────────────────────────────────
        tk.Label(inner, text='Adjust Algorithm:     ').grid(
            row=row, column=0, sticky=tk.E)
        self._adj_algorithm = tk.StringVar()
        for col, (label, value) in enumerate(
                [('Round', 'round'), ('Fast', 'fast'), ('Slow', 'slow')], start=1):
            tk.Radiobutton(inner, text=f'{label:<20}',
                           variable=self._adj_algorithm, value=value).grid(
                row=row, column=col, sticky=tk.W)
        row += 1

        # ── Min ratio ────────────────────────────────────────────────
        tk.Label(inner, text='Acceptable Pixel Cover Ratio:     ').grid(
            row=row, column=0, sticky=tk.E)
        self._min_ratio = tk.DoubleVar(value=get_devel_info('min_ratio'))
        self._min_ratio_entry = tk.Entry(
            inner, textvariable=self._min_ratio, width=12, justify=tk.CENTER)
        self._min_ratio_entry.grid(row=row, column=1, sticky=tk.W)
        row += 1

        def _algo_trace(*_):
            state = 'disabled' if self._adj_algorithm.get() == 'round' else 'normal'
            self._min_ratio_entry.configure(state=state)

        self._adj_algorithm.trace_add('write', _algo_trace)
        self._adj_algorithm.set(get_devel_info('adj_algorithm'))

        # ── Adjusted File Output ─────────────────────────────────────
        tk.Label(inner, text='Adjusted File Output:     ').grid(
            row=row, column=0, sticky=tk.E)
        self._adj_output = tk.StringVar()
        for col, (label, value) in enumerate(
                [('Yes', 'YES'), ('No', 'NO')], start=1):
            tk.Radiobutton(inner, text=label,
                           variable=self._adj_output, value=value).grid(
                row=row, column=col, sticky=tk.W)
        row += 1

        # ── Adjusted File Postfix ─────────────────────────────────────
        tk.Label(inner, text='Adjusted File Postfix:     ').grid(
            row=row, column=0, sticky=tk.E)
        self._postfix_adj = tk.StringVar(value=get_devel_info('postfix_adj'))
        self._postfix_adj_entry = tk.Entry(
            inner, textvariable=self._postfix_adj, width=12, justify=tk.CENTER)
        self._postfix_adj_entry.grid(row=row, column=1, sticky=tk.W)
        row += 1

        def _adj_output_trace(*_):
            state = 'disabled' if self._adj_output.get() == 'NO' else 'normal'
            self._postfix_adj_entry.configure(state=state)

        self._adj_output.trace_add('write', _adj_output_trace)
        self._adj_output.set(get_devel_info('adj_output'))

        # ── Intermediate Results Output ───────────────────────────────
        tk.Label(inner, text='Intermediate Results Output:     ').grid(
            row=row, column=0, sticky=tk.E)
        self._intermediate = tk.StringVar(
            value=get_devel_info('intermediate_results'))
        for col, (label, value) in enumerate(
                [('Yes', 'YES'), ('No', 'NO')], start=1):
            tk.Radiobutton(inner, text=label,
                           variable=self._intermediate, value=value).grid(
                row=row, column=col, sticky=tk.W)

    # ------------------------------------------------------------------
    def apply(self):
        set_devel_info('min_ratio',           self._min_ratio.get())
        set_devel_info('adj_algorithm',       self._adj_algorithm.get())
        set_devel_info('intermediate_results', self._intermediate.get())
        set_devel_info('adj_output',          self._adj_output.get())
        set_devel_info('postfix_adj',         self._postfix_adj.get())
        self.applied = True
