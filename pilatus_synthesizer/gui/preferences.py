"""Preferences dialog.

Shows/edits the user-facing Synthesizer preferences:
synthesis method, counter, colour map, save policy, syn policy, and
synthesis flags.

Original: lib/Synthesizer/GuiPreferences.py
Copyright (c) SAXS Team, KEK-PF
"""

import tkinter as tk
import tkinter.simpledialog as simpledialog

from pilatus_synthesizer._keklib.tk_supplements import tk_set_icon_portable
from pilatus_synthesizer._keklib.our_color_maps import COLOUR_MAP_NAMES
from pilatus_synthesizer.config.preferences import get_preference, set_preference
from pilatus_synthesizer.config.development import get_devel_info, set_devel_info


class PreferencesDialog(simpledialog.Dialog):
    """Modal dialog for editing the usual (non-developer) preferences.

    Parameters
    ----------
    parent:
        Tk parent window.
    title:
        Window title.
    pilatus_counter:
        :class:`~pilatus_synthesizer.core.pilatus_counter.Counter` instance
        used to populate the detection-counter dropdown.  Pass ``None`` to
        show only "None".
    action:
        Optional action code (1=show, 2=adjusted, 3=synthesize).  When set,
        only preferences relevant to that action are shown (used by the
        "temporary preferences" menu in the image table).
    """

    def __init__(self, parent, title: str, pilatus_counter=None, action=None):
        self.applied = False
        self.adj_output_changed = False
        self.couter_id_changed = False
        self._pilatus_counter = pilatus_counter
        self._action = action
        simpledialog.Dialog.__init__(self, parent, title)

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------

    def body(self, frame) -> None:
        tk_set_icon_portable(self, 'synthesizer')

        row = 0

        # --- Synthesis method (cover / average) -------------------------
        if self._action in (None, 3):
            tk.Label(frame, text='Synthesis Method:').grid(
                row=row, column=0, sticky=tk.E, padx=8, pady=4)
            self._syn_method = tk.StringVar(value=get_preference('syn_method'))
            f = tk.Frame(frame)
            f.grid(row=row, column=1, sticky=tk.W)
            for label, value in [('Cover', 'cover'), ('Average', 'average')]:
                tk.Radiobutton(f, text=label,
                               variable=self._syn_method, value=value).pack(
                    side=tk.LEFT)
            row += 1

        # --- Detection counter ------------------------------------------
        if self._action in (None, 3):
            tk.Label(frame, text='Detection Counter:').grid(
                row=row, column=0, sticky=tk.E, padx=8, pady=4)
            counter_ids = ['None']
            if self._pilatus_counter:
                try:
                    counter_ids += list(self._pilatus_counter.get_counter_ids())
                except Exception:
                    pass
            self._counter = tk.StringVar(value=get_preference('detection_counter'))
            tk.OptionMenu(frame, self._counter, *counter_ids).grid(
                row=row, column=1, sticky=tk.W)
            row += 1

        # --- Colour map -------------------------------------------------
        if self._action in (None, 1, 2):
            tk.Label(frame, text='Colour Map:').grid(
                row=row, column=0, sticky=tk.E, padx=8, pady=4)
            self._color_map = tk.StringVar(value=get_preference('color_map'))
            tk.OptionMenu(frame, self._color_map, *COLOUR_MAP_NAMES).grid(
                row=row, column=1, sticky=tk.W)
            row += 1

        # --- Save policy ------------------------------------------------
        if self._action is None:
            tk.Label(frame, text='Save Policy:').grid(
                row=row, column=0, sticky=tk.E, padx=8, pady=4)
            self._save_policy = tk.StringVar(value=get_preference('save_policy'))
            tk.OptionMenu(frame, self._save_policy,
                          'Ask', 'Yes', 'No').grid(
                row=row, column=1, sticky=tk.W)
            row += 1

        # --- Syn policy -------------------------------------------------
        if self._action in (None, 3):
            tk.Label(frame, text='Synthesize:').grid(
                row=row, column=0, sticky=tk.E, padx=8, pady=4)
            self._syn_policy = tk.StringVar(value=get_preference('syn_policy'))
            tk.OptionMenu(frame, self._syn_policy,
                          'all', 'missing').grid(
                row=row, column=1, sticky=tk.W)
            row += 1

        # --- Synthesis flags (3 checkboxes) -----------------------------
        if self._action in (None, 3):
            tk.Label(frame, text='Synthesis Flags:').grid(
                row=row, column=0, sticky=tk.E, padx=8, pady=4)
            flags = get_preference('syn_flags')
            self._syn_flags = []
            f = tk.Frame(frame)
            f.grid(row=row, column=1, sticky=tk.W)
            for i, label in enumerate(['Flag 1', 'Flag 2', 'Flag 3']):
                var = tk.IntVar(value=flags[i] if i < len(flags) else 1)
                self._syn_flags.append(var)
                tk.Checkbutton(f, text=label, variable=var).pack(side=tk.LEFT)
            row += 1

        # --- Adj output (developer-facing but visible here) -------------
        if self._action is None:
            tk.Label(frame, text='Adj Output:').grid(
                row=row, column=0, sticky=tk.E, padx=8, pady=4)
            adj_options = ['NO', 'YES']
            self._adj_output = tk.StringVar(value=get_devel_info('adj_output'))
            tk.OptionMenu(frame, self._adj_output, *adj_options).grid(
                row=row, column=1, sticky=tk.W)
            row += 1

    # ------------------------------------------------------------------
    # Apply
    # ------------------------------------------------------------------

    def apply(self) -> None:
        self.applied = True

        if hasattr(self, '_syn_method'):
            set_preference('syn_method', self._syn_method.get())

        if hasattr(self, '_counter'):
            old = get_preference('detection_counter')
            new = self._counter.get()
            set_preference('detection_counter', new)
            self.couter_id_changed = (old != new)

        if hasattr(self, '_color_map'):
            set_preference('color_map', self._color_map.get())

        if hasattr(self, '_save_policy'):
            set_preference('save_policy', self._save_policy.get())

        if hasattr(self, '_syn_policy'):
            set_preference('syn_policy', self._syn_policy.get())

        if hasattr(self, '_syn_flags'):
            set_preference('syn_flags', [v.get() for v in self._syn_flags])

        if hasattr(self, '_adj_output'):
            old = get_devel_info('adj_output')
            new = self._adj_output.get()
            set_devel_info('adj_output', new)
            self.adj_output_changed = (old != new)
