# Project Status — Pilatus Synthesizer Migration

**Last Updated**: 2026-03-05  
**Current Phase**: Phase 5 complete → Phase 6 (Embeddable Distribution) in progress

---

## Current State

**Migration Status**: ✅ Phase 5 complete  
**Current Work**: Embeddable distribution build  
**Active Issues**: None

---

## Recent Work (2026-03-05 Session)

### DnD Migration ✅

- Deleted bundled `_keklib/tkdnd2.8/` directory (Tcl binary package)
- Rewrote `_keklib/tk_dnd_wrapper.py` to use `python-tkdnd` (`pip install python-tkdnd`)
- `TkDND.bindtarget()` now uses `widget.register_drop_target("*")` + `widget.bind("<<Drop>>")`  
  (pattern from molass-legacy `TkCustomWidgets.py`)
- Updated `app.py`: `from tkinterDnD import Tk` / `root = Tk()`
- Added `python-tkdnd` to `pyproject.toml` dependencies
- Published as **v0.5.1** on PyPI

### Execution Log Window ✅

- Replaced `scrolledtext.ScrolledText(wrap=WORD)` with `tk.Text(wrap=NONE)` + x/y scrollbars
- Window width now matches the main window (geometry set immediately after `Toplevel.__init__()`)

### Embeddable Distribution 🔄 (pending test)

Created `build/` folder (now version-controlled):

| File | Purpose |
|---|---|
| `build/build_embeddables.py` | Downloads Python embeddable zip, installs pip + packages, assembles output folder |
| `build/synthesizer.py` | Entry-point: `from pilatus_synthesizer.app import gui_main; gui_main()` |
| `build/run.cpp` | C++ launcher source — runs `embeddables\pythonw.exe build\synthesizer.py` |
| `build/README.md` | Build instructions |
| `build/.gitignore` | Excludes compiled `synthesizer.exe` and MSVC artifacts |

Output: `dist/synthesizer-0_5_1-x64/` (same layout as legacy `synthesizer-0_4_8-x64`)

---

## Previous Work (2026-03-04 Session)

### Bugs Fixed ✅

1. **Row selection on double-click** — Fixed `get_selected_rows()` to use `get_cells_as_rows=True` for cell-mode selection
2. **Matplotlib 3.9 compatibility** — Replaced deprecated `Grouper.join()` with `ax.sharex()`/`ax.sharey()`
3. **Synthesis always skipped** — Fixed off-by-one bug: `len(exec_rec_array) == num_changes` (was `num_changes + 1`)
4. **ValueError with numpy array** — Fixed `base_rec[0]` handling when it becomes ndarray on iteration 2+
5. **Wrong test data used** — User confirmed synthesis now works correctly with proper test data
6. **Initial row selection** — Fixed `_select_added_rows()` to use `add_row_selection()` for multiple row selection

### Features Added ✅

- **Select all rows**: Added Ctrl+A keyboard shortcut
- **Select all rows**: Added right-click menu "Select All Rows" option
- Initial table display now selects all newly-added rows (matching legacy behavior)

### Pending Issues ⚠️

- **Double-click behavior**: Currently only shows viewer; should also select the row
- **Single-click selection**: May not be working as expected (needs verification)
- **Header click selection**: "No" column header click doesn't select all rows (workarounds added)

---

## File Changes This Session

### Modified Files

1. `pilatus_synthesizer/gui/image_table.py`
   - Added `get_cells_as_rows=True` for row selection
   - Added `_on_double_click()` handler
   - Added `_select_all_rows()` for Ctrl+A and menu
   - Fixed `_select_added_rows()` to select multiple rows correctly
   - Added column header click handler (not working yet)
   - Added Ctrl+A bindings

2. `pilatus_synthesizer/gui/image_synthesizer.py`
   - Fixed `num_changes` off-by-one bug
   - Fixed `base_rec[0]` numpy array handling
   - (Temporary debug logs added and removed)

3. `pilatus_synthesizer/gui/image_viewer.py`
   - Fixed matplotlib 3.9 axis sharing API

4. `pilatus_synthesizer/config/settings.py`
   - Changed `positive_direction` default from `None` → `'right'`

5. `pilatus_synthesizer/core/image_synthesizer.py`
   - (Temporary debug logs added and removed)

---

## Known Working Features

- ✅ All core synthesis logic (verified with correct test data)
- ✅ Row selection via click/drag
- ✅ Select all via Ctrl+A
- ✅ Select all via right-click menu
- ✅ Double-click opens image viewer
- ✅ Right-click context menu
- ✅ Initial display selects all new rows

---

## Next Steps

1. **Fix double-click row selection** — Make double-click both select the row AND open viewer
2. **Verify single-click selection** — Ensure single-click selects rows as in legacy
3. **Fix header click** (optional) — Make "No" column header click select all rows
4. Continue GUI feature parity testing

---

## Migration Phase Summary

### Phase 1: Package Skeleton ✅
- Modern Python package structure
- pyproject.toml with dependencies
- Entry points configured

### Phase 2: Core & KekLib ✅
- All core synthesis modules migrated
- KekLib utilities migrated
- Image I/O, TIFF handling, masking

### Phase 3: Config & CLI ✅
- Settings, preferences, development options
- Command-line interface
- Persistent configuration

### Phase 4: GUI Modules ✅
- All Tkinter GUI components migrated
- tksheet replacing TkTable
- All dialogs and windows

### Phase 5: Tests & Polish ✅
- conftest.py with data gating
- Unit tests (basic_utils, preferences, settings)
- Integration tests (7 data-dependent files)
- CI workflow (pytest with data gating)
- pyproject.toml pytest and ruff config
- All 9 GUI bugs fixed
- Auto-run mode (confirmation + ActionWindow suppressed)
- PyPI release via Trusted Publisher GitHub Actions workflow
- DnD migrated from bundled tkdnd2.8 → python-tkdnd
- Execution log window width fix

### Phase 6: Embeddable Distribution 🔄 (pending test)
- `build/` folder created and version-controlled
- Build script, launcher script, C++ launcher source, README
- Test pending: run `python build/build_embeddables.py`

---

## Technical Notes

### Key Fixes This Session

- **tksheet row selection**: `get_cells_as_rows=True` required when using `single_select` mode
- **matplotlib 3.9**: `ax.sharex(ax0)` replaces `get_shared_x_axes().join(ax0, ax)`
- **Synthesis guard**: `num_changes` from data_array IS `len(exec_rec_array)` (not len-1)
- **numpy array truth**: Can't use `array or ''` — must check `isinstance(val, str)`
- **Multiple row selection**: Use `select_row(0)` then `add_row_selection(i)` for remaining rows

### tksheet Notes

- With `single_select` binding, selections are cell-based → need `get_cells_as_rows=True`
- Column header binding via `self._sheet.CH.bind()` doesn't fire reliably
- `add_row_selection()` must be used with `redraw=False` + `refresh()` for performance
- Ctrl+A and menu-based selection work as alternatives to header click

---

## Repository Structure

```
pilatus-synthesizer/
├── COPILOT-INIT.md          # Static: How to work here
├── PROJECT_STATUS.md        # Dynamic: Current state (this file)
├── MIGRATION_PLAN.md        # Migration roadmap
├── pyproject.toml           # Package config, dependencies
├── .github/workflows/       # CI: pytest + PyPI Trusted Publisher
├── build/                   # Embeddable distribution build scripts
│   ├── README.md            # Build instructions
│   ├── build_embeddables.py # Main build script
│   ├── synthesizer.py       # Entry-point script
│   └── run.cpp              # C++ launcher source
├── pilatus_synthesizer/     # Main package
│   ├── __init__.py
│   ├── app.py              # Entry point
│   ├── _keklib/            # Internal utilities
│   ├── cli/                # Command-line interface
│   ├── config/             # Settings, preferences
│   ├── core/               # Image synthesis logic
│   └── gui/                # Tkinter GUI (tksheet-based)
├── tests/                   # pytest test suite
└── legacy/                  # Original implementation (reference)
```

---

**End of status snapshot 2026-03-04**
