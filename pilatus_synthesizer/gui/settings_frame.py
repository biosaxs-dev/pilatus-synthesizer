"""Entry frame for folder / file settings.

Contains labeled Entry widgets for:
  - Measured Image Folder (in_folder)
  - Measurement Log File  (log_file)
  - SAngler Mask File     (mask_file)
  - Adjusted Image Folder (adj_folder) — only if adj_output=='YES'
  - Synthesized Image Folder (syn_folder)
  - Operation Mode radio buttons (MANUAL / AUTOMATIC) + watch-interval
    spinbox + Auto-Run Start button

Drag-and-drop is supported via TkDND when tkdnd2.8 is available.

Original: lib/Synthesizer/GuiSettingInfo.py
Copyright (c) 2016–2021, SAXS Team, KEK-PF
"""

import os
import re
import tkinter as tk

import pilatus_synthesizer._keklib.our_messagebox as MessageBox
from pilatus_synthesizer._keklib.our_tkinter import FileDialog, TkDND, ToolTip
from pilatus_synthesizer._keklib.tk_supplements import SlimButton
from pilatus_synthesizer._keklib.changeable_logger import Logger as ChangeableLogger

import pilatus_synthesizer.core.pilatus_counter as pc_module
from pilatus_synthesizer.core.pilatus_utils import get_in_folder_info
from pilatus_synthesizer._keklib.basic_utils import exe_name

from pilatus_synthesizer.config.preferences import get_preference
from pilatus_synthesizer.config.development import get_devel_info
from pilatus_synthesizer.config.settings import (
    clear_settings, get_setting, set_setting, set_mask, get_mask,
)

from pilatus_synthesizer.gui.create_folder_dialog import CreateFolderDialog

DEFAULT_WATCH_INTERVAL = 180


def _is_empty(val) -> bool:
    return val is None or val == '' or (isinstance(val, str) and val[0] == '<') or val == 'None'


class EntryFrame(tk.Frame):
    """Grid of labelled path entries with DnD, focus helpers, and validation."""

    def __init__(self, master, controller):
        super().__init__(master)

        self._during_init   = True
        self.controller     = controller
        self._entries       = []   # [(type_str, entry_widget, on_entry_callable)]
        self.app_logger     = None
        self.pilatus_counter = None
        self.auto_set_asked = False
        self.auto_set_done  = False
        self.adj_output     = get_devel_info('adj_output')
        self.data_entry_ready   = False
        self._in_construction   = True
        self.logfile_path       = ''
        self._error_notified    = {}

        self.changed_after_refresh = False
        self.changed_ever          = False

        # ── previous-value trackers initialised in after_construction_proc ──
        self.previous_in_folder  = None
        self.previous_log_file   = None
        self.previous_mask_file  = None
        self.previous_adj_folder = None
        self.previous_syn_folder = None

        row = -1

        # in_folder -------------------------------------------------------
        row += 1
        tk.Label(self, text='Measured Image Folder: ').grid(
            row=row, column=0, sticky=tk.E)
        self.in_folder = tk.StringVar(value=get_setting('in_folder') or '')
        self.in_folder_entry = tk.Entry(
            self, textvariable=self.in_folder, width=80)
        self._entries.append(('dir', self.in_folder_entry, self.on_entry_in_folder))
        self.in_folder_entry.grid(row=row, column=1)
        b = tk.Button(self, text='...', command=self._select_in_folder)
        b.grid(row=row, column=2, sticky=tk.W)
        ToolTip(b, 'Select an appropriate folder with this button.')
        tk.Label(self, text=' must be entered manually').grid(
            row=row, column=3, sticky=tk.W)

        # log_file --------------------------------------------------------
        row += 1
        tk.Label(self, text='Measurement Log File: ').grid(
            row=row, column=0, sticky=tk.E)
        self.log_file = tk.StringVar(value=get_setting('log_file') or '')
        self.log_file_entry = tk.Entry(
            self, textvariable=self.log_file, width=80)
        self._entries.append(('file', self.log_file_entry, self.on_entry_log_file))
        self.log_file_entry.grid(row=row, column=1)
        b = tk.Button(self, text='...', command=self._select_log_file)
        b.grid(row=row, column=2, sticky=tk.W)
        ToolTip(b, 'Select an appropriate file with this button.')
        tk.Label(self, text=' automatically set if exists in the above folder').grid(
            row=row, column=3, sticky=tk.W)

        # mask_file -------------------------------------------------------
        row += 1
        tk.Label(self, text='SAngler Mask File: ').grid(
            row=row, column=0, sticky=tk.E)
        self.mask_file = tk.StringVar(value=get_setting('mask_file') or '')
        self.mask_file_entry = tk.Entry(
            self, textvariable=self.mask_file, width=80)
        self._entries.append(('file', self.mask_file_entry, self.on_entry_mask_file))
        self.mask_file_entry.grid(row=row, column=1)
        b = tk.Button(self, text='...', command=self._select_mask_file)
        b.grid(row=row, column=2, sticky=tk.W)
        ToolTip(b, 'Select an appropriate file with this button.')
        tk.Label(self, text=' automatically set if exists in the above folder').grid(
            row=row, column=3, sticky=tk.W)

        # adj_folder (conditional) ----------------------------------------
        if self.adj_output == 'YES':
            row += 1
            tk.Label(self, text='Adjusted Image Folder: ').grid(
                row=row, column=0, sticky=tk.E)
            self.adj_folder = tk.StringVar(value=get_setting('adj_folder') or '')
            self.adj_folder_entry = tk.Entry(
                self, textvariable=self.adj_folder, width=80)
            self._entries.append(('dir', self.adj_folder_entry, self.on_entry_adj_folder))
            self.adj_folder_entry.grid(row=row, column=1)
            b = tk.Button(self, text='...', command=self._select_adj_folder)
            b.grid(row=row, column=2, sticky=tk.W)
            ToolTip(b, 'Select an appropriate folder with this button.')
            tk.Label(self, text=' must be entered manually').grid(
                row=row, column=3, sticky=tk.W)

        # syn_folder -------------------------------------------------------
        row += 1
        tk.Label(self, text='Synthesized Image Folder: ').grid(
            row=row, column=0, sticky=tk.E)
        self.syn_folder = tk.StringVar(value=get_setting('syn_folder') or '')
        self.syn_folder_entry = tk.Entry(
            self, textvariable=self.syn_folder, width=80)
        self._entries.append(('dir', self.syn_folder_entry, self.on_entry_syn_folder))
        self.syn_folder_entry.grid(row=row, column=1)
        b = tk.Button(self, text='...', command=self._select_syn_folder)
        b.grid(row=row, column=2, sticky=tk.W)
        ToolTip(b, 'Select an appropriate folder with this button.')
        tk.Label(self, text=' must be entered manually').grid(
            row=row, column=3, sticky=tk.W)

        # Operation Mode --------------------------------------------------
        row += 1
        tk.Label(self, text='Operation Mode: ').grid(
            row=row, column=0, sticky=tk.E)
        op_frame = tk.Frame(self)
        op_frame.grid(row=row, column=1, sticky=tk.W)

        self.op_option = tk.StringVar()
        self._op_option_buttons = []
        col = 0
        for label, value in [('Manual   ', 'MANUAL'), ('Automatic', 'AUTOMATIC')]:
            rb = tk.Radiobutton(op_frame, text=label + '    ',
                                variable=self.op_option, value=value)
            self._op_option_buttons.append(rb)
            rb.grid(row=0, column=col, sticky=tk.W)
            col += 1

        self._watch_interval_label = tk.Label(op_frame, text='Watch Interval ')
        self._watch_interval_label.grid(row=0, column=col, sticky=tk.W)
        col += 1

        self.watch_interval = tk.StringVar(
            value=str(get_setting('watch_interval') or DEFAULT_WATCH_INTERVAL))
        self.watch_interval_box = tk.Spinbox(
            op_frame, textvariable=self.watch_interval,
            from_=10, to=600, increment=10, width=4, justify=tk.CENTER)
        self.watch_interval_box.grid(row=0, column=col, sticky=tk.W)
        col += 1

        tk.Label(op_frame, text='s  ').grid(row=0, column=col, sticky=tk.W)
        col += 1

        self.autorun_button = SlimButton(
            op_frame, text='Auto-Run Start',
            command=self.controller.auto_start)
        self.autorun_button.grid(row=0, column=col, sticky=tk.W)
        ToolTip(self.autorun_button,
                "Select 'Automatic' and press this button to start automatic operation.")

        # ── initial state ────────────────────────────────────────────────
        # populate placeholder text / trigger syn_folder callback
        if not _is_empty(self.syn_folder.get()):
            self.on_entry_syn_folder()

        self._add_focus_binds()
        self._add_dnd_binds()
        self._during_init = False

    # ------------------------------------------------------------------
    # after_construction_proc — called by Controller after mainloop starts
    # ------------------------------------------------------------------

    def after_construction_proc(self):
        """Run entry validation and set up change-tracking traces.

        Must be called once immediately after __init__ because some
        operations require the Tk event loop to be running.
        """
        check_result = self.check_entries()

        self.previous_in_folder  = None
        self.previous_log_file   = None
        self.previous_mask_file  = None
        self.previous_adj_folder = None

        if check_result:
            self.on_entry_in_folder(check_only=True)
            self.on_entry_log_file()
            self.on_entry_mask_file()
            if self.adj_output == 'YES':
                self.on_entry_adj_folder()
            self.on_entry_syn_folder()
            self.controller.refresh_button_suggestion.stop()

        self.previous_in_folder  = self.in_folder.get()
        self.previous_log_file   = self.log_file.get()
        self.previous_mask_file  = self.mask_file.get()
        if self.adj_output == 'YES':
            self.previous_adj_folder = self.adj_folder.get()
        self.previous_syn_folder = self.syn_folder.get()

        self.changed_after_refresh = False
        self.changed_ever          = False

        def _entry_tracer(*_):
            self.changed_after_refresh = True
            self.changed_ever          = True
            if not self._in_construction:
                self.after(0, self.check_entries)

        self.in_folder.trace_add('write', _entry_tracer)
        self.log_file.trace_add('write', _entry_tracer)
        self.mask_file.trace_add('write', _entry_tracer)
        if self.adj_output == 'YES':
            self.adj_folder.trace_add('write', _entry_tracer)
        self.syn_folder.trace_add('write', _entry_tracer)

        def _op_tracer(*_):
            val = self.op_option.get()
            set_setting('op_option', val)
            if val == 'MANUAL':
                self._auto_run_widgets_disable()
                self.controller.auto_disable(force=True)
            else:
                if self.check_entries():
                    self._auto_run_widgets_enable()
                    self.controller.auto_enable()
                else:
                    if not self._in_construction:
                        MessageBox.showinfo(
                            'Not Allowed',
                            "You can't select 'Automatic' until all "
                            'required entries are filled.')
                        self.op_option.set('MANUAL')

        self.op_option.trace_add('write', _op_tracer)
        self.op_option.set(get_setting('op_option') or 'MANUAL')
        self._in_construction = False

    # ------------------------------------------------------------------
    def __del__(self):
        self.app_logger = None

    # ------------------------------------------------------------------
    # Public interface used by Controller
    # ------------------------------------------------------------------

    def clear(self):
        self._clear_entries()
        self.check_entries()
        for attr, key in [
            ('previous_in_folder',  'in_folder'),
            ('previous_log_file',   'log_file'),
            ('previous_mask_file',  'mask_file'),
            ('previous_syn_folder', 'syn_folder'),
        ]:
            setattr(self, attr, '')
            set_setting(key, '')
        if self.adj_output == 'YES':
            self.previous_adj_folder = ''
            set_setting('adj_folder', '')

    def enable(self):
        for _, entry, _ in self._entries:
            entry.configure(state='normal')
        for b in self._op_option_buttons:
            b.configure(state='normal')
        if self.op_option.get() == 'MANUAL':
            self.controller.refresh_button_enable()
            self.controller.run_button_enable()
        else:
            self._auto_run_widgets_enable()

    def disable(self):
        for _, entry, _ in self._entries:
            entry.configure(state='disabled')
        for b in self._op_option_buttons:
            b.configure(state='disabled')
        if self.op_option.get() == 'MANUAL':
            self.controller.refresh_button_disable()
            self.controller.run_button_disable()
        else:
            self._auto_run_widgets_disable()

    def change_reset(self):
        self.changed_after_refresh = False

    def has_been_changed_after_refresh(self) -> bool:
        return self.changed_after_refresh

    def has_been_changed_ever(self) -> bool:
        return self.changed_ever

    # ------------------------------------------------------------------
    # check_entries
    # ------------------------------------------------------------------

    def check_entries(self, index: int = -999) -> bool:  # noqa: C901
        msg = ''
        ret = True
        if index == -999:
            self._error_entries = []

        entries_to_check = [self._entries[index]] if index >= -1 else self._entries
        error_index = None
        i_ = -1

        for obj_type, entry, _ in entries_to_check:
            i_ += 1
            path = entry.get()
            entry_ok = True

            if path and os.path.exists(path):
                if obj_type == 'dir' and not os.path.isdir(path):
                    if not msg:
                        error_index = i_
                        msg = f'{path} is not a folder.'
                    entry.configure(fg='red')
                    ret = False
                    entry_ok = False
                elif obj_type == 'file' and not os.path.isfile(path):
                    if not msg:
                        error_index = i_
                        msg = f'{path} is not a file.'
                    entry.configure(fg='red')
                    ret = False
                    entry_ok = False
                else:
                    entry.configure(fg='black')
            else:
                if not _is_empty(path):
                    if not msg:
                        error_index = i_
                        msg = f'{path} does not exist.'
                entry.configure(fg='red')
                ret = False
                entry_ok = False

            if index == -999 and not entry_ok:
                self._error_entries.append(entry)

        if msg:
            key = (error_index, msg)
            if index == -999:
                if error_index == len(entries_to_check) - 1:
                    error_index = -1
                self._error_notified[key] = True
                if MessageBox.askyesno(
                    'Entry Error & Clear Info Question',
                    msg
                    + '\nLooks like the setting environment has been changed.\n'
                    'Do you want to clear the previous setting info?',
                ):
                    clear_settings()
                    self._clear_entries()
                    self.check_entries()
            else:
                if not self._error_notified.get(key):
                    MessageBox.showerror('Entry Error', msg)
                self._error_notified[key] = True

        if ret and index == -999:
            if get_mask() is None:
                self.on_entry_mask_file(set_force=True)
            self.data_entry_ready = True
            if self.op_option.get() == 'MANUAL':
                if self.controller.op_is_manual:
                    self.controller.auto_disable()
            else:
                if not self.controller.op_is_manual:
                    self.controller.auto_enable()

            # enable Refresh button when all entries are filled
            if self.op_option.get() == 'MANUAL':
                if all(not _is_empty(e.get()) for _, e, _ in self._entries):
                    self.controller.refresh_button_enable()
                    if self.changed_after_refresh:
                        self.controller.refresh_button_suggestion.start()
        elif not ret and index == -999:
            self.data_entry_ready = False
            if self.controller.op_is_manual and not self._during_init:
                self.controller.auto_disable()
                self.controller.manual_buttons_disable()
                self.controller.refresh_button_suggestion.stop()

        return ret

    # ------------------------------------------------------------------
    # on_entry handlers
    # ------------------------------------------------------------------

    def on_entry_in_folder(self, event=None, check_only: bool = False):
        self.auto_set_asked = False
        self.auto_set_done  = False
        in_folder = self.in_folder.get()

        if not self.check_entries(0):
            self.previous_in_folder = in_folder
            return
        if check_only:
            return
        if self.previous_in_folder and in_folder == self.previous_in_folder:
            return
        self.previous_in_folder = in_folder
        set_setting('in_folder', in_folder)

        log_file, mask_file = get_in_folder_info(in_folder)
        do_auto_fill = True
        if log_file or mask_file:
            action = 'Insert' if _is_empty(self.log_file.get()) else 'Replace'
            self.auto_set_asked = True
            if not MessageBox.askyesno(
                'Question',
                f'Log and/or mask files exist in the folder. '
                f'{action} the corresponding entries?'
            ):
                do_auto_fill = False

        if do_auto_fill:
            if log_file:
                self.log_file.set(f'{in_folder}/{log_file}')
                self.auto_set_done = True
                self.on_entry_log_file()
            if mask_file:
                self.mask_file.set(f'{in_folder}/{mask_file}')
                self.auto_set_done = True
                self.on_entry_mask_file()

        if self.controller.image_info_table is not None:
            self.controller.image_info_table.current_data_end = 0

    def on_entry_log_file(self):
        f = self.log_file.get()
        if not self.check_entries(1):
            self.previous_log_file = f
            return
        if self.previous_log_file and f == self.previous_log_file:
            return
        self.previous_log_file = f
        self.pilatus_counter = pc_module.Counter(self.in_folder.get())
        set_setting('log_file', f)

    def on_entry_mask_file(self, set_force: bool = False):
        f = self.mask_file.get()
        if not self.check_entries(2):
            self.previous_mask_file = f
            return
        if not set_force and self.previous_mask_file and f == self.previous_mask_file:
            return
        self.previous_mask_file = f
        try:
            if set_mask(f):
                self.mask_file_entry.configure(fg='black')
            else:
                self.mask_file_entry.configure(fg='red')
                MessageBox.showerror(
                    'SAngler Mask File Error',
                    'Not a well-formatted SAngler mask file.')
                return False
            set_setting('mask_file', f)
        except Exception as exc:
            print(f'on_entry_mask_file: unexpected exception {exc}')
            return False
        return True

    def on_entry_adj_folder(self):
        f = self.adj_folder.get()
        idx = 3  # index in _entries when adj_output==YES
        if not self.check_entries(idx):
            self.previous_adj_folder = f
            return
        if self.previous_adj_folder and f == self.previous_adj_folder:
            return
        self.previous_adj_folder = f
        set_setting('adj_folder', f)

    def on_entry_syn_folder(self):
        f = self.syn_folder.get()
        if not self.check_entries(-1):
            self.previous_syn_folder = f
            return
        if self.previous_syn_folder and f == self.previous_syn_folder:
            return
        self.previous_syn_folder = f
        self._on_entry_syn_folder_sub()

    def _on_entry_syn_folder_sub(self):
        syn_folder = self.syn_folder.get()
        if _is_empty(syn_folder):
            return
        set_setting('syn_folder', syn_folder)
        exe = exe_name()
        self.logfile_path = f'{syn_folder}/{exe}.log'
        if self.app_logger:
            self.app_logger.changeto(self.logfile_path)
        else:
            self.app_logger = ChangeableLogger(self.logfile_path)

    # ------------------------------------------------------------------
    # Folder / file selection dialogs
    # ------------------------------------------------------------------

    def _select_in_folder(self):
        f = self._askdirectory(self.in_folder)
        if f:
            self.in_folder.set(f)
            self.on_entry_in_folder()

    def _select_log_file(self):
        f = FileDialog.askopenfilename(initialdir=get_setting('in_folder'))
        if f:
            self.log_file.set(f)
            self.on_entry_log_file()

    def _select_mask_file(self):
        f = FileDialog.askopenfilename(initialdir=get_setting('in_folder'))
        if f:
            self.mask_file.set(f)
            self.on_entry_mask_file()

    def _select_adj_folder(self):
        f = self._askdirectory(self.adj_folder, suggest_name='Adjusted')
        if f:
            self.adj_folder.set(f)
            self.on_entry_adj_folder()

    def _select_syn_folder(self):
        f = self._askdirectory(self.syn_folder, suggest_name='Synthesized')
        if f:
            self.syn_folder.set(f)
            self.on_entry_syn_folder()

    def _askdirectory(self, entry_var: tk.StringVar,
                      suggest_name: str = '') -> str:
        entered = entry_var.get()
        initial = os.path.dirname(entered).replace('/', os.sep)
        if suggest_name and _is_empty(entered):
            dialog = CreateFolderDialog(
                self, 'Folder Creation Dialog',
                self._suggested_folders(suggest_name))
            if dialog.created_folder:
                return dialog.created_folder
        return FileDialog.askdirectory(initialdir=initial)

    def _suggested_folders(self, name: str) -> list:
        folders = []
        in_folder = self.in_folder.get()
        if not _is_empty(in_folder):
            in_path = os.path.abspath(in_folder)
            folders.append(os.path.join(in_path, name))
            folders.append(in_path + '-' + name)
        cwd   = os.getcwd()
        drive = cwd.split(os.sep)[0] + os.sep
        folders.append(os.path.join(drive, name))
        return [f.replace('\\', '/') for f in folders]

    # ------------------------------------------------------------------
    # Helper: focus enter/leave placeholder logic
    # ------------------------------------------------------------------

    def _add_focus_binds(self):
        def _focusin(event):
            w = event.widget
            v = w.get()
            if v == '':
                pass                     # nothing to clear
            elif v and v[0] == '<':
                w.delete(0, tk.END)

        def _focusout(event, placeholder, proc):
            w = event.widget
            v = w.get()
            if v == '':
                w.insert(0, placeholder)
                w.configure(fg='red')
            if proc:
                proc()

        for obj_type, entry, on_entry in self._entries:
            placeholder = '<Folder>' if obj_type == 'dir' else '<File>'
            if _is_empty(entry.get()):
                entry.delete(0, tk.END)
                entry.insert(0, placeholder)
            entry.bind('<FocusIn>', _focusin)
            entry.bind('<FocusOut>',
                       lambda ev, ph=placeholder, pr=on_entry:
                           _focusout(ev, ph, pr))

    # ------------------------------------------------------------------
    # DnD
    # ------------------------------------------------------------------

    def _add_dnd_binds(self):
        try:
            self._dnd = TkDND(self)
        except Exception:
            return  # tkdnd not available

        def _drop(event, post_proc=None):
            event.widget.delete(0, tk.END)
            data = re.sub(r'[{}]', '', event.data)
            event.widget.insert(0, data)
            if post_proc:
                post_proc()

        bindings = [
            (self.in_folder_entry,  self.on_entry_in_folder),
            (self.log_file_entry,   self.on_entry_log_file),
            (self.mask_file_entry,  self.on_entry_mask_file),
        ]
        if self.adj_output == 'YES':
            bindings.append((self.adj_folder_entry, self.on_entry_adj_folder))
        bindings.append((self.syn_folder_entry, self.on_entry_syn_folder))

        for widget, proc in bindings:
            self._dnd.bindtarget(
                widget,
                lambda ev, p=proc: _drop(ev, p),
                '*',
            )
            ToolTip(widget,
                    'You can enter directly, use the file dialog button, '
                    'or drag and drop here.')

    # ------------------------------------------------------------------
    # Auto-run widget helpers
    # ------------------------------------------------------------------

    def _auto_run_widgets_disable(self):
        self._watch_interval_label.configure(state='disabled')
        self.watch_interval_box.configure(state='disabled')
        self.autorun_button.configure(state='disabled')

    def _auto_run_widgets_enable(self):
        self._watch_interval_label.configure(state='normal')
        self.watch_interval_box.configure(state='normal')
        self.autorun_button.configure(state='normal')

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _clear_entries(self):
        for obj_type, entry, _ in self._entries:
            entry.delete(0, tk.END)
            entry.insert(0, '<Folder>' if obj_type == 'dir' else '<File>')
