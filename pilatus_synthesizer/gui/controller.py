"""Main application controller window.

Toplevel that contains:
  - Menu bar  (Settings → Detector | Preferences | Developer Options | Exit)
  - "Clear" button + EntryFrame (folder / file entries)
  - "Refresh" button (with BlinkingFrame), "Run" button
  - ImageTable (9-column image information table)

Original: lib/Synthesizer/GuiController.py
Copyright (c) 2016–2020, SAXS Team, KEK-PF
"""

import tkinter as tk

import pilatus_synthesizer._keklib.our_messagebox as MessageBox
from pilatus_synthesizer._keklib.our_tkinter import ToolTip
from pilatus_synthesizer._keklib.tk_supplements import (
    BlinkingFrame, SlimButton, tk_set_icon_portable,
)
from pilatus_synthesizer._keklib.tk_utils import adjusted_geometry, split_geometry

from pilatus_synthesizer.config.preferences import get_preference
from pilatus_synthesizer.config.settings import save_settings, get_setting, set_setting
from pilatus_synthesizer import version_string

from pilatus_synthesizer.gui.image_synthesizer import ImageSynthesizer
from pilatus_synthesizer.gui.settings_frame import EntryFrame
from pilatus_synthesizer.gui.image_table import ImageTable
from pilatus_synthesizer.gui.auto_run import AutoRunController

_LABEL_BG = 'gray25'
_LABEL_FG = 'white'
_MAX_HEIGHT = 600


class Controller(tk.Toplevel):
    """Main application window."""

    def __init__(self, root, opts=None):
        root.wm_title(version_string())

        super().__init__(root)
        self.withdraw()

        self.root               = root
        self.op_is_feasible     = False
        self.op_is_manual       = True
        self.image_info_table   = None
        self.geometry_resized   = False

        tk_set_icon_portable(self, 'synthesizer')

        # ── Menu bar ─────────────────────────────────────────────────
        menubar = tk.Menu(self)
        self.configure(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label='Settings', menu=settings_menu)
        settings_menu.add_command(label='Detector',
                                   command=self.detector_settings)
        settings_menu.add_command(label='Preferences',
                                   command=self.preferences)
        settings_menu.add_command(label='Developer Options',
                                   command=self.developer_options)
        settings_menu.add_command(label='Exit', command=self.quit)

        # ── Main inner frame ──────────────────────────────────────────
        inner = tk.Frame(self)
        inner.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ── Setting information section ───────────────────────────────
        si_label_frame = tk.Frame(inner)
        si_label_frame.pack(side=tk.TOP, anchor=tk.W)

        tk.Label(si_label_frame,
                 text=' Setting Information Entries ',
                 relief=tk.FLAT, fg=_LABEL_FG, bg=_LABEL_BG).pack(
            side=tk.LEFT, anchor=tk.W)

        self._clear_button = SlimButton(
            si_label_frame, text='Clear', command=self._setting_clear)
        self._clear_button.pack(side=tk.LEFT, anchor=tk.W, padx=10)
        tk.Label(si_label_frame,
                 text='press to clear the following entries').pack(
            side=tk.LEFT, anchor=tk.W)
        ToolTip(self._clear_button,
                'Press this button to clear the setting information.')

        self._entry_frame_frame = tk.Frame(inner)
        self._entry_frame_frame.pack()
        self.entry_frame = EntryFrame(self._entry_frame_frame, self)
        self.entry_frame.pack(side=tk.TOP, padx=10, pady=10)

        # ── Image data information section ────────────────────────────
        img_label_frame = tk.Frame(inner)
        img_label_frame.pack(side=tk.TOP, anchor=tk.W)

        tk.Label(img_label_frame,
                 text=' Image Data Information Table ',
                 relief=tk.FLAT, fg=_LABEL_FG, bg=_LABEL_BG).pack(
            side=tk.LEFT, anchor=tk.W)

        self.refresh_button = SlimButton(
            img_label_frame, text='Refresh', command=self.refresh)
        self.refresh_button_guide = tk.Label(img_label_frame, text='')
        ToolTip(self.refresh_button,
                'Press this button to refresh the measured data information '
                'listed below.')

        blinking_spec = [
            [self.refresh_button,
             {'side': tk.LEFT, 'anchor': tk.W, 'padx': 10}],
            [self.refresh_button_guide,
             {'side': tk.LEFT, 'anchor': tk.W}],
        ]
        self.refresh_button_suggestion = BlinkingFrame(
            img_label_frame, blinking_spec,
            start_proc=self.run_button_disable,
            stop_proc=self.run_button_enable,
        )
        self.refresh_button_suggestion.pack(side=tk.LEFT, anchor=tk.W, padx=10)

        self.run_button = SlimButton(
            img_label_frame, text='Run',
            command=self.run, state='disabled')
        self.run_button.pack(side=tk.LEFT, padx=10)
        self.run_button_guide = tk.Label(img_label_frame, text='')
        self.run_button_guide.pack(side=tk.LEFT)
        ToolTip(self.run_button,
                'Press this button to make synthesized images for the '
                'selected samples.')

        # ── Table frame ───────────────────────────────────────────────
        table_frame = tk.Frame(inner)
        table_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10,
                         anchor=tk.N)

        self._synthesizer = ImageSynthesizer(table_frame)
        self.image_info_table = ImageTable(
            table_frame, self._synthesizer,
            self.refresh_button_suggestion,
        )

        if self.image_info_table.num_selected_rows > 0:
            self.run_button_enable()

        # triggers change traces and op_option init
        self.entry_frame.after_construction_proc()

        # ── Show window ───────────────────────────────────────────────
        self.update()
        self.deiconify()
        self.geometry(adjusted_geometry(self.geometry()))

        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.after(100, self.check_detector_settings)

    def __del__(self):
        try:
            self.entry_frame.__del__()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Detector settings check
    # ------------------------------------------------------------------

    def check_detector_settings(self) -> bool:
        direction = get_setting('positive_direction')
        if direction is None or direction in ('', 'None'):
            MessageBox.showwarning(
                'Detector Settings Required',
                "Later versions of Synthesizer require 'Positive Adjust "
                "Direction' for proper operation.\n\n"
                "Please set it via Settings → Detector.")
            return False
        return True

    # ------------------------------------------------------------------
    # Button-state helpers (also called by EntryFrame)
    # ------------------------------------------------------------------

    def refresh_button_disable(self):
        self.refresh_button.configure(state='disabled')
        self.refresh_button_guide.configure(text='')

    def refresh_button_enable(self):
        self.refresh_button.configure(state='normal')
        self.refresh_button_guide.configure(
            text='← be sure to press after you have changed above entries')

    def run_button_disable(self):
        self.run_button.configure(state='disabled')
        self.run_button_guide.configure(text='')

    def run_button_enable(self):
        self.run_button.configure(state='normal')
        self.run_button_guide.configure(
            text='← press to make synthesized images')

    def manual_buttons_disable(self):
        self.refresh_button_disable()
        self.run_button_disable()

    # ------------------------------------------------------------------
    # Main actions
    # ------------------------------------------------------------------

    def refresh(self, autorun: bool = False):
        if self.entry_frame.check_entries():
            need_resize = self.image_info_table.refresh(
                log_file_path=self.entry_frame.log_file.get(),
                restore_view=not self.entry_frame.has_been_changed_after_refresh(),
                logger=self._get_logger(),
                autorun=autorun,
            )
            if need_resize and not self.geometry_resized:
                curr = self.geometry()
                w, h, x, y = split_geometry(curr)
                new_h = min(h + self.image_info_table.get_resize_height(),
                            _MAX_HEIGHT)
                self.geometry(f'{w}x{new_h}+{x}+{y}')
                self.geometry_resized = (new_h == _MAX_HEIGHT)

            self.refresh_button_suggestion.stop()
            self.entry_frame.change_reset()
        else:
            MessageBox.showerror('Required Entries',
                                 'Please fill in required entries.')

    def run(self):
        if not self.check_detector_settings():
            return
        self.image_info_table.do_action(3)

    def auto_start(self):
        if not self.check_detector_settings():
            return
        if not MessageBox.askokcancel(
                'Confirmation',
                'Do you want to start automatic control?'):
            return
        interval = int(self.entry_frame.watch_interval.get())
        set_setting('watch_interval', interval)
        self._grab_set_alternative()
        self._ar_controller = AutoRunController(
            self, interval,
            self.image_info_table,
            log_file_path=self.entry_frame.log_file.get(),
            on_stop=self._grab_release_alternative,
        )
        self._ar_controller.start()

    def auto_disable(self, force: bool = False):
        if force or not self.op_is_manual:
            self.op_is_manual = True
            self.refresh_button_enable()
            self.run_button_enable()

    def auto_enable(self, force: bool = False):
        if force or self.op_is_manual:
            self.op_is_manual = False
            self.refresh()
            self.refresh_button_disable()
            self.run_button_disable()

    def quit(self):
        if not MessageBox.askyesno('Quit', 'Do you want to quit?'):
            return
        if self.entry_frame.has_been_changed_ever():
            policy = get_preference('save_policy')
            do_save = (
                policy == 'Yes' or
                (policy == 'Ask' and
                 MessageBox.askyesno(
                     'Entry Data Handling Question',
                     'Do you want to save the folder/file entries?'))
            )
            if do_save:
                save_settings()
        self.root.quit()
        self.destroy()

    # ------------------------------------------------------------------
    # Menu handlers
    # ------------------------------------------------------------------

    def detector_settings(self):
        from pilatus_synthesizer.gui.detector_settings import DetectorSettings
        DetectorSettings(self.root, 'Detector Settings')

    def preferences(self):
        if (self.refresh_button_suggestion and
                self.refresh_button_suggestion.is_blinking()):
            MessageBox.showwarning(
                'Not Allowed',
                "You can't change preferences until you refresh the "
                'image data information table.')
            return
        from pilatus_synthesizer.gui.preferences import PreferencesDialog
        dialog = PreferencesDialog(
            self.root, 'Usual Preferences',
            self.entry_frame.pilatus_counter)

        if dialog.adj_output_changed:
            self.entry_frame.__del__()
            self.entry_frame.destroy()
            self.entry_frame = EntryFrame(self._entry_frame_frame, self)
            self.entry_frame.pack(side=tk.TOP, padx=10, pady=10)
            self.entry_frame.after_construction_proc()

        if dialog.couter_id_changed:
            self.image_info_table.refresh(
                log_file_path=self.entry_frame.log_file.get(),
                restore_view=True,
                pilatus_counter=self.entry_frame.pilatus_counter,
                logger=self._get_logger(),
            )

    def developer_options(self):
        from pilatus_synthesizer.gui.developer_options import DeveloperOptionsDialog
        DeveloperOptionsDialog(self.root, 'Developer Options')

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _setting_clear(self):
        if MessageBox.askyesno(
                'Confirmation',
                'Do you want to clear the following entries?'):
            self.entry_frame.clear()

    def _get_logger(self):
        return self.entry_frame.app_logger

    def _grab_set_alternative(self):
        self.entry_frame.disable()

    def _grab_release_alternative(self):
        self.entry_frame.enable()
