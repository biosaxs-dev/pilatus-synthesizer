"""Image data information table.

Displays the 9-column data table (No, Original Image, Shifted Image 1,
Relative Position 1, Intensity Ratio 1, Shifted Image 2, Relative
Position 2, Intensity Ratio 2, Synthesized Image) using the *tksheet*
widget (replaces the legacy TkTable widget).

Public interface (used by controller/settings_frame):
    __init__(parent, synthesizer, suggestion, geometry_getter=None)
    refresh(restore_view, pilatus_counter, bottom_view, log_file_path,
            logger, autorun) → bool
    do_action(action, change=False)
    num_selected_rows   [property / attribute]
    current_data_end    [int attribute]
    get_resize_height() → int

Original: lib/Synthesizer/PilatusImageInfoTable.py
Copyright (c) 2020, 2024 SAXS Team, KEK-PF
"""

import logging
import traceback

import tkinter as tk
import tksheet

import pilatus_synthesizer._keklib.our_messagebox as MessageBox
from pilatus_synthesizer._keklib.our_tkinter import ToolTip
from pilatus_synthesizer._keklib.changeable_logger import Logger as ChangeableLogger

from pilatus_synthesizer.core.pilatus_utils import get_data_info
from pilatus_synthesizer.config.preferences import (
    get_preference,
    temporary_preferences_begin,
    temporary_preferences_end,
    get_usual_preference,
)
from pilatus_synthesizer.config.settings import get_setting

log = logging.getLogger(__name__)

# ── column indices ─────────────────────────────────────────────────────
_COL_NO     = 0
_COL_ORIG   = 1
_COL_SHF1   = 2
_COL_POS1   = 3
_COL_RAT1   = 4
_COL_SHF2   = 5
_COL_POS2   = 6
_COL_RAT2   = 7
_COL_SYN    = 8

# Maps display column → settings key for the folder containing the file
# (used by show_properties)
_TIF_DIR_MAP = {
    _COL_ORIG: 'in_folder',
    _COL_SHF1: 'in_folder',
    _COL_SHF2: 'in_folder',
    _COL_SYN:  'syn_folder',
}

_COL_WIDTHS = [30, 150, 150, 70, 80, 150, 70, 80, 150]  # total ≈ 930px
_NUM_COLS   = 9


class ImageTable:
    """tksheet-based image information table."""

    def __init__(self, parent: tk.Widget, synthesizer, suggestion,
                 geometry_getter=None):
        self.parent          = parent
        self.synthesizer     = synthesizer
        self.suggestion      = suggestion
        self.geometry_getter = geometry_getter

        self.num_selected_rows   = 0
        self.current_data_end    = 0
        self.data_array          = []
        self.pilatus_counter     = None
        self.temporary_i_ratio_array = None

        self._sheet: tksheet.Sheet | None = None
        self._frame: tk.Frame | None = None
        self._in_cell_select = False

        self.refresh()

    # ------------------------------------------------------------------
    # Public: refresh
    # ------------------------------------------------------------------

    def refresh(self, restore_view=False, pilatus_counter=None,
                bottom_view=False, log_file_path=None, logger=None,
                autorun=False) -> bool:

        if not restore_view:
            self.temporary_i_ratio_array = None

        self.num_selected_rows = 0

        in_folder  = get_setting('in_folder')
        adj_folder = get_setting('adj_folder')
        syn_folder = get_setting('syn_folder')
        counter_id = get_preference('detection_counter')

        temp_logger = ChangeableLogger()
        try:
            _, _, data_array, pilatus_counter = get_data_info(
                in_folder, adj_folder, syn_folder, pilatus_counter,
                counter_id,
                log_file_path=log_file_path,
                logger=temp_logger,
            )
        except Exception:
            log.exception('Unexpected error during get_data_info')
            MessageBox.showerror('Unexpected Error', traceback.format_exc())
            return False

        buf = temp_logger.get_stream_buffer()
        if 'ERROR' in buf:
            show_msg = True
            if autorun:
                try:
                    from pilatus_synthesizer._keklib.error_log_check import all_known_errors
                    show_msg = not all_known_errors(buf)
                except ImportError:
                    pass
            if show_msg:
                MessageBox.showerror(
                    'Refresh Error',
                    'Following errors have been detected during refresh.\n'
                    'Please check them before continuing.\n'
                    '(You can copy this info with <Ctrl+c> to the clipboard\n'
                    'in case needed)\n\n'
                    + buf.replace(',root', ''))

        self.data_array      = data_array
        self.pilatus_counter = pilatus_counter

        if self.current_data_end > len(data_array):
            self.current_data_end = 0

        # ── build display rows ─────────────────────────────────────────
        header = [
            'No',
            'Original Image',
            'Shifted Image 1',
            'Relative Position 1',
            f'Intensity Ratio 1 {counter_id}',
            'Shifted Image 2',
            'Relative Position 2',
            f'Intensity Ratio 2 {counter_id}',
            'Synthesized Image',
        ]

        rows = []
        for row_idx, row_rec in enumerate(data_array):
            row_num  = row_idx + 1
            sub_recs = row_rec[1]
            row_data = [''] * _NUM_COLS
            row_data[_COL_NO] = row_num

            # base image (first sub_rec)
            if sub_recs:
                row_data[_COL_ORIG] = sub_recs[0][0] or ''

            # shifted images (sub_recs[1] and optionally [2])
            SHF_COLS = [(_COL_SHF1, _COL_POS1, _COL_RAT1),
                        (_COL_SHF2, _COL_POS2, _COL_RAT2)]
            for i_, (c_shf, c_pos, c_rat) in enumerate(SHF_COLS, start=1):
                if i_ >= len(sub_recs):
                    break
                sr = sub_recs[i_]
                row_data[c_shf] = sr[0] or ''
                row_data[c_pos] = '%s,%s' % tuple(sr[1]) if sr[1] else ''
                if sr[2]:
                    row_data[c_rat] = '%.5f' % sr[2]

            # synthesized image (last sub_rec[4], column 8)
            if len(sub_recs) >= 2:
                last_sr = sub_recs[-1]
                row_data[_COL_SYN] = last_sr[4] or ''

            rows.append(row_data)

        # ── (re)create the sheet widget ────────────────────────────────
        need_resize = (self._sheet is None and len(data_array) > 0)
        if self._frame is not None:
            self._frame.destroy()

        self._frame = tk.Frame(self.parent)
        self._frame.pack(expand=True, fill=tk.BOTH)

        self._sheet = tksheet.Sheet(
            self._frame,
            headers=header,
            data=rows,
            height=400,
            show_row_index=False,
            theme='light green',
        )
        self._sheet.pack(expand=True, fill=tk.BOTH)

        # column widths and alignment
        _CENTER_COLS = {_COL_NO, _COL_POS1, _COL_RAT1, _COL_POS2, _COL_RAT2}
        for c, w in enumerate(_COL_WIDTHS):
            self._sheet.column_width(column=c, width=w)
            align = 'center' if c in _CENTER_COLS else 'w'
            self._sheet.align_columns(columns=[c], align=align)

        # enable built-in horizontal scroll
        self._sheet.enable_bindings(
            'single_select', 'row_select', 'column_width_resize',
            'arrowkeys', 'right_click_popup_menu', 'rc_select',
            'copy',
        )

        # select newly-added rows
        self._select_added_rows()

        if bottom_view and rows:
            self._sheet.see(row=len(rows) - 1, column=0)

        # right-click context menu
        self._sheet.popup_menu_add_command(
            'Show Original Images',   lambda: self.do_action(1))
        self._sheet.popup_menu_add_command(
            'Show Adjusted Images',   lambda: self.do_action(2))
        self._sheet.popup_menu_add_command(
            'Make Synthesized Images', lambda: self.do_action(3))
        self._sheet.popup_menu_add_command(
            'Execute with Temporary Preference Changes (Show Original)',
            lambda: self.do_action(1, change=True))
        self._sheet.popup_menu_add_command(
            'Execute with Temporary Preference Changes (Show Adjusted)',
            lambda: self.do_action(2, change=True))
        self._sheet.popup_menu_add_command(
            'Execute with Temporary Preference Changes (Make Synthesized)',
            lambda: self.do_action(3, change=True))
        self._sheet.popup_menu_add_command(
            'Tiff File Description', self._show_properties)
        self._sheet.popup_menu_add_command(
            'Select All Rows', self._select_all_rows)

        # double-click → select row and show images
        self._sheet.bind('<Double-Button-1>', self._on_double_click)

        # Ctrl+A to select all rows
        self._sheet.bind('<Control-a>', lambda _e: self._select_all_rows())
        self._sheet.bind('<Control-A>', lambda _e: self._select_all_rows())

        # Try binding to column header for "No" column click
        try:
            log.debug('Setting up header click binding')
            self._sheet.CH.bind('<Button-1>', self._on_header_click, add='+')
        except Exception as e:
            log.warning(f'Could not bind to column header: {e}')

        # track selection
        self._sheet.extra_bindings(
            [('cell_select',     self._on_cell_select),
             ('row_select',      self._on_select),
             ('deselect',        self._on_select)])

        ToolTip(self._sheet,
                '<Double-click> a row to show images. '
                'Right-click to show the action menu. '
                'Ctrl+A or right-click "Select All Rows" to select all rows.')

        return need_resize

    # ------------------------------------------------------------------
    # Public: do_action
    # ------------------------------------------------------------------

    def do_action(self, action: int, change: bool = False, confirm: bool = True) -> None:
        if self.suggestion and self.suggestion.is_blinking():
            MessageBox.showwarning(
                'Not Allowed',
                "You can't do any action until you refresh the image data "
                'information table.')
            return

        selected_indices = self._get_selected_indices()
        exec_array = [self.data_array[i] for i in selected_indices]

        if not exec_array:
            MessageBox.showinfo(
                'No Rows Selected',
                'No rows are selected. Select row(s) and retry.')
            return

        if change:
            temporary_preferences_begin()
            from pilatus_synthesizer.gui.preferences import PreferencesDialog
            dialog = PreferencesDialog(
                self.parent, 'Temporary Preferences',
                self.pilatus_counter, action=action)
            if not dialog.applied:
                temporary_preferences_end()
                return

        self.synthesizer.execute(action, exec_array, confirm=confirm)

        if change:
            temporary_preferences_end()

        if action == 3:
            self._update_current(selected_indices)
            self.refresh(restore_view=True)

    # ------------------------------------------------------------------
    # Public: get_resize_height
    # ------------------------------------------------------------------

    def get_resize_height(self) -> int:
        num_rows = min(20, len(self.data_array))
        row_height = 25  # approximate default tksheet row height (pixels)
        return num_rows * row_height

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _on_cell_select(self, event=None):
        """Promote single-cell click to full row selection (legacy behavior)."""
        if self._in_cell_select:
            return
        cur = self._sheet.get_currently_selected()
        if cur and isinstance(cur[0], int):
            row = cur[0]
            if 0 <= row < len(self.data_array):
                self._in_cell_select = True
                try:
                    self._sheet.select_row(row)
                finally:
                    self._in_cell_select = False
                self.num_selected_rows = 1
                return
        # fallback: count whatever is selected
        self._on_select(event)

    def _on_select(self, event=None):
        selected = self._sheet.get_selected_rows(
            get_cells_as_rows=True, return_tuple=True)
        self.num_selected_rows = len(selected)

    def _on_double_click(self, event=None):
        """Select the clicked row and show images."""
        cur = self._sheet.get_currently_selected()
        if cur and isinstance(cur[0], int):
            row = cur[0]
            if 0 <= row < len(self.data_array):
                self._in_cell_select = True
                try:
                    self._sheet.select_row(row)
                finally:
                    self._in_cell_select = False
                self.num_selected_rows = 1
        self._sheet.after(1, lambda: self.do_action(1))

    def _on_header_click(self, event=None):
        # Check if click is on the "No" column header (column 0)
        if not event:
            return
        
        # Manually compute column from x coordinate
        x = event.x
        cumulative_width = 0
        for col_idx in range(len(_COL_WIDTHS)):
            col_width = self._sheet.column_width(col_idx)
            if cumulative_width <= x < cumulative_width + col_width:
                if col_idx == 0:
                    log.debug('Header column 0 clicked, selecting all rows')
                    self._sheet.after(1, self._select_all_rows)
                    return 'break'
                break
            cumulative_width += col_width

    def _select_all_rows(self):
        log.debug(f'Selecting all {len(self.data_array)} rows')
        if not self.data_array:
            return
        self._sheet.deselect('all')
        # Select all rows at once using a range
        self._sheet.select_row(0)  # Start with first row
        for row_idx in range(1, len(self.data_array)):
            self._sheet.add_row_selection(row_idx, redraw=False)
        self._sheet.refresh()
        self.num_selected_rows = len(self.data_array)
        log.debug(f'Selection complete, num_selected_rows={self.num_selected_rows}')

    def _get_selected_indices(self) -> list:
        return sorted(self._sheet.get_selected_rows(
            get_cells_as_rows=True, return_tuple=True))

    def _get_not_yet_done_indices(self) -> list:
        indices = []
        for k, row in enumerate(self.data_array):
            recs = row[1]
            syn_file = recs[-1][4] if recs else None
            if syn_file is None:
                indices.append(k)
        return indices

    def _select_added_rows(self) -> None:
        if not self.data_array:
            return
        n = len(self.data_array)
        if self.current_data_end < n:
            # Select rows from current_data_end to n-1
            first_idx = self.current_data_end
            self._sheet.select_row(first_idx)  # Select first new row
            for i in range(first_idx + 1, n):
                self._sheet.add_row_selection(i, redraw=False)
            self._sheet.refresh()
            self.num_selected_rows = n - self.current_data_end

    def _update_current(self, selected_indices: list) -> None:
        if selected_indices:
            end = selected_indices[-1] + 1
            if end > self.current_data_end:
                self.current_data_end = end

    def _show_properties(self) -> None:
        selected = self._get_selected_indices()
        if not selected:
            MessageBox.showinfo(
                'No Row Selected',
                'No row is selected. Select a row and retry.')
            return

        row_idx    = selected[0]
        # find out which cell column is active (use first selected cell)
        sel_cells  = self._sheet.get_selected_cells()
        col = sel_cells[0][1] if sel_cells else _COL_ORIG

        if col in _TIF_DIR_MAP:
            dirkey  = _TIF_DIR_MAP[col]
            dirpath = get_setting(dirkey)
            # column index in display → data_array sub_rec field
            row_data = self._sheet.get_row_data(row_idx)
            filename = row_data[col]
            if filename:
                path  = f'{dirpath}/{filename}'
                title = f'{filename} Description'
                from pilatus_synthesizer.gui.image_property import ImagePropertyWindow
                ImagePropertyWindow(self.parent, title, path)
                return

        MessageBox.showinfo(
            'Select Tiff File Notice',
            'Select a tiff file cell and retry.')
