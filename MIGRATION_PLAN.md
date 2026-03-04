# Synthesizer Migration Plan
**Created**: March 4, 2026  
**Status**: Draft — for discussion  
**Source**: `synthesizer-0_4_8-x64` (Synthesizer 0.4.8, 2025-11-20)  
**Target**: Open-source Python package aligned with the molass ecosystem

---

## 1. Overview

### What is Synthesizer?

A desktop application for combining multiple Pilatus X-ray detector images taken at different detector positions into a single synthesized image. Used at KEK Photon Factory and SPring-8 beamlines for SAXS experiments.

### Why Migrate?

- **Open-source**: Make the tool available to the broader SAXS community
- **Ecosystem alignment**: Follow the same conventions as molass-library / molass-legacy
- **Modern packaging**: Replace `sys.path.append` + PyInstaller with proper `pip install`
- **Maintainability**: Clean up Python 2 relics, use proper package imports

### Scope

This plan covers migration of the **Synthesizer application** (32 `.py` files in `lib/Synthesizer/`) and the **KekLib subset** it depends on (~28 modules from `lib/KekLib/`). Build scripts (`lib/Build/`) are out of scope — replaced by `pyproject.toml`.

---

## 2. Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Package name (PyPI)** | `pilatus-synthesizer` | Descriptive, avoids collision with generic "synthesizer" |
| **Import name (Python)** | `pilatus_synthesizer` | PEP 8 convention, matches PyPI name |
| **Build system** | hatchling | Same as molass-library and molass-legacy |
| **License** | GPLv3 | Same as molass ecosystem |
| **Python version** | `>=3.12,<3.14` | Same as molass-library |
| **KekLib strategy** | Internal subset (Option A) | Self-contained; avoids imposing molass-legacy as a dependency. Can be shared later if needed |
| **Repository** | `biosaxs-dev/pilatus-synthesizer` | Under the biosaxs-dev organization |
| **Source location** | `C:\Users\takahashi\GitHub\synthesizer-migration\` | Repurpose existing folder as the repository root |

---

## 3. Architecture: Before and After

### Before (0.4.8)

```
synthesizer-0_4_8-x64/
├── synthesizer.exe              ← PyInstaller frozen bundle
├── lib/
│   ├── Synthesizer/             ← App code (32 files, PascalCase)
│   │   ├── ImageSynthesizer.py  ← Core engine
│   │   ├── PilatusImage.py      ← Image model + adjustment
│   │   ├── PilatusUtils*.py     ← Data discovery
│   │   ├── GuiController.py     ← Tkinter GUI
│   │   ├── CommandController.py ← CLI mode
│   │   └── ...
│   ├── KekLib/                  ← Shared utility library (~120 modules)
│   └── Build/                   ← PyInstaller build scripts
├── test/                        ← Test suite
└── doc/                         ← User's guide PDF
```

**Import mechanism**: `sys.path.append()` in `__init__.py` — all modules are flat, import by bare name.

### After (1.0.0)

```
pilatus-synthesizer/             ← Repository root
├── pyproject.toml
├── README.md
├── LICENSE
├── COPILOT-INIT.md
├── pilatus_synthesizer/         ← Main package
│   ├── __init__.py              ← Version, public API
│   ├── app.py                   ← Entry point (GUI + CLI dispatch)
│   ├── core/                    ← Image processing (GUI-independent)
│   │   ├── __init__.py
│   │   ├── pilatus_image.py     ← Image model + adjustment algorithms
│   │   ├── image_synthesizer.py ← Synthesis engine
│   │   ├── pilatus_utils.py     ← Data discovery (old + new style merged)
│   │   ├── pilatus_counter.py   ← Beam monitor counter parsing
│   │   ├── sangler_mask.py      ← SAngler mask file parser
│   │   ├── image_io.py          ← TIFF/CBF image I/O
│   │   ├── minimal_tiff.py      ← Pure-Python TIFF reader
│   │   └── image_property.py    ← TIFF header extraction
│   ├── gui/                     ← Tkinter GUI (optional at runtime)
│   │   ├── __init__.py
│   │   ├── controller.py        ← Main window (was GuiController.py)
│   │   ├── settings_frame.py    ← Entry frame (was GuiSettingInfo.py)
│   │   ├── preferences.py       ← User preferences dialog
│   │   ├── detector_settings.py ← Detector config dialog
│   │   ├── image_viewer.py      ← Image display (was PilatusImageViewer.py)
│   │   ├── image_table.py       ← Sample table (was PilatusImageInfoTable*.py)
│   │   ├── zoom_pan.py          ← Matplotlib zoom/pan handler
│   │   └── auto_run.py          ← Auto-synthesis controller
│   ├── cli/                     ← Command-line interface
│   │   ├── __init__.py
│   │   └── command.py           ← CLI controller (was CommandController.py)
│   ├── config/                  ← Settings & persistence
│   │   ├── __init__.py
│   │   ├── settings.py          ← Application settings (was SynthesizerSettings.py)
│   │   ├── preferences.py       ← User preferences (was Preferences.py)
│   │   ├── development.py       ← Developer options
│   │   └── version.py           ← Version info (was AppVersion.py)
│   └── _keklib/                 ← Internal KekLib subset (28 modules)
│       ├── __init__.py
│       ├── our_tkinter.py
│       ├── our_messagebox.py
│       ├── persistent_info.py
│       ├── tk_supplements.py
│       ├── ...
│       └── execution_window/
│           ├── __init__.py
│           ├── action_window.py
│           ├── threads_connector.py
│           └── ...
├── tests/                       ← Migrated test suite
│   ├── conftest.py
│   ├── test_pilatus_image.py
│   ├── test_image_synthesizer.py
│   ├── test_pilatus_utils.py
│   └── ...
├── doc/
│   └── UsersGuide-0_4_8.pdf    ← Preserved
└── legacy/                      ← Original snapshot (read-only reference)
    └── synthesizer-0_4_8-x64/
```

---

## 4. Migration Phases

### Phase 1: Scaffold (no code changes yet)

**Goal**: Create the new package skeleton with working `pyproject.toml`.

1. Create directory structure under `C:\Users\takahashi\GitHub\synthesizer-migration\`
2. Create `pyproject.toml` (hatchling, dependencies, entry points)
3. Create `README.md`, `LICENSE` (GPLv3), `COPILOT-INIT.md`
4. Create `pilatus_synthesizer/__init__.py` with version
5. Move `synthesizer-0_4_8-x64/` into `legacy/` as reference snapshot

**Deliverable**: `pip install -e .` succeeds (empty package).

### Phase 2: Core Migration (image processing, no GUI)

**Goal**: Migrate the computation-only modules that can work without Tkinter.

Files to migrate:

| Original | Target | Notes |
|----------|--------|-------|
| `PilatusImage.py` | `core/pilatus_image.py` | Remove `from __future__`, fix imports |
| `SAnglerMask.py` | `core/sangler_mask.py` | Fix file handle (use `with open`) |
| `OurImageIO.py` | `core/image_io.py` | Keep fabio + MinimalTiff support |
| `MinimalTiff.py` | `core/minimal_tiff.py` | Pure Python, minimal changes |
| `PilatusImageProperty.py` | `core/image_property.py` | — |
| `PilatusCounter.py` | `core/pilatus_counter.py` | — |
| `PilatusUtils.py` | `core/pilatus_utils.py` | Merge old+new style |
| `PilatusUtilsOldStyle.py` | `core/pilatus_utils.py` | Merge into one module |
| `PilatusUtilsNewStyle.py` | `core/pilatus_utils.py` | Merge into one module |
| `ImageSynthesizer.py` | `core/image_synthesizer.py` | Separate GUI calls from core logic |

KekLib modules needed for Phase 2 (non-GUI subset):

| Original | Target |
|----------|--------|
| `OurImageIO.py` | Absorbed into `core/image_io.py` |
| `MinimalTiff.py` | Absorbed into `core/minimal_tiff.py` |
| `OurException.py` | `_keklib/our_exception.py` |
| `BasicUtils.py` | `_keklib/basic_utils.py` |
| `ExceptionTracebacker.py` | `_keklib/exception_traceback.py` |
| `OurMock.py` | Can use `unittest.mock` directly |
| `PersistentInfo.py` | `config/persistent_info.py` (or `_keklib/`) |

**Deliverable**: `from pilatus_synthesizer.core import PilatusImage, ImageSynthesizer` works. Tests for adjustment algorithms pass.

### Phase 3: Config & CLI Migration

**Goal**: Migrate settings/preferences and command-line mode.

| Original | Target |
|----------|--------|
| `SynthesizerSettings.py` | `config/settings.py` |
| `Preferences.py` | `config/preferences.py` |
| `Development.py` | `config/development.py` |
| `AppVersion.py` | `config/version.py` |
| `CommandController.py` | `cli/command.py` |
| `SynthesizerCommandLineOptions.py` | `cli/command.py` (use `argparse` instead of `optparse`) |

**Deliverable**: `pilatus-synthesizer -c -i FOLDER` works from command line.

### Phase 4: GUI Migration

**Goal**: Migrate the Tkinter GUI and remaining KekLib modules.

| Original | Target |
|----------|--------|
| `GuiController.py` | `gui/controller.py` |
| `GuiSettingInfo.py` | `gui/settings_frame.py` |
| `GuiPreferences.py` | `gui/preferences.py` |
| `DetectorSettings.py` | `gui/detector_settings.py` |
| `PilatusImageViewer.py` | `gui/image_viewer.py` |
| `PilatusImageInfoTable.py` | `gui/image_table.py` |
| `PilatusImageInfoTable.py` | `gui/image_table.py` — **rewrite with tksheet** |
| `PilatusImageInfoTable2.py` | Dropped (pandastable path eliminated) |
| `CuntomizedPandasTable.py` | Dropped (replaced by tksheet) |
| `AutoRunController.py` | `gui/auto_run.py` |
| `ZoomPan.py` | `gui/zoom_pan.py` |
| `CreateFolderDialog.py` | `gui/controller.py` (inline) |
| `TestDataGenerator.py` | `tests/` or `tools/` |

KekLib GUI modules needed:

| Module | Notes |
|--------|-------|
| `OurTkinter.py` | Wrapper around tkinter — most complex KekLib module |
| `OurMessageBox.py` | MessageBox wrapper |
| `TkSupplements.py` | BlinkingFrame, SlimButton, etc. |
| `TkUtils.py` | Geometry helpers |
| ~~`TkTableWrapper.py`~~ | **Dropped** — replaced by `tksheet` (pure Python, actively maintained, same as molass-legacy) |
| `OurColorMaps.py` | ALBULA-like colormaps |
| `OurMatplotlib.py` | Matplotlib integration |
| `ControlKeyState.py` | Keyboard modifier detection |
| `ChangeableLogger.py` | Logging utilities |
| `ExecutionWindow/` | Action window, threads connector, progress bars |

**Deliverable**: `pilatus-synthesizer` launches the GUI.

### Phase 5: Tests & Polish

**Goal**: Migrate tests, add CI, clean up.

1. Migrate test files from `test/` → `tests/`
2. Convert from `nose` to `pytest`
3. Add `conftest.py` with test data fixtures
4. Verify coverage
5. Add GitHub Actions CI
6. Update documentation

**Deliverable**: `pytest` passes, CI green.

---

## 5. Import Modernization Strategy

### Problem

The original code uses `sys.path.append()` so all modules are importable by bare name:

```python
# Old style (Synthesizer/ImageSynthesizer.py)
from PilatusImage import PilatusImage
from SAnglerMask  import SAnglerMask
from Preferences  import get_preference
```

### Solution

Use proper relative/absolute imports:

```python
# New style (pilatus_synthesizer/core/image_synthesizer.py)
from pilatus_synthesizer.core.pilatus_image import PilatusImage
from pilatus_synthesizer.core.sangler_mask import SAnglerMask
from pilatus_synthesizer.config.preferences import get_preference
```

### Approach

Rather than creating a compatibility shim, do a **direct rewrite** of all imports module by module. This is mechanical and reduces ongoing confusion. The total is ~32 source files + ~28 KekLib files — manageable.

### `_keklib/` Internal Imports

Within `_keklib/`, modules import each other. These become relative imports:

```python
# Old (KekLib/TkSupplements.py)
from BasicUtils import clear_dirs_with_retry

# New (pilatus_synthesizer/_keklib/tk_supplements.py)
from .basic_utils import clear_dirs_with_retry
```

---

## 6. Python 2 Cleanup

Remove from all files:

```python
# Remove these:
from __future__ import division, print_function, unicode_literals
```

The `//` vs `/` division behavior is standard in Python 3. The code already uses `//` correctly for integer division in `PilatusImage.py`.

---

## 7. Dependencies

### `pyproject.toml` dependencies

```toml
[project]
dependencies = [
  "numpy",
  "pandas",
  "pillow",          # PIL for TIFF
  "matplotlib",
  "fabio",           # CBF image support
  "tksheet",         # Modern spreadsheet widget for Tkinter (replaces TkTableWrapper + pandastable)
]

[project.optional-dependencies]
gui = [
  "python-tkdnd",   # Drag-and-drop (if needed)
]
testing = [
  "pytest",
  "pytest-cov",
]
```

### Notes

- **fabio**: Required for CBF format support (used in `OurImageIO.py`). This is a well-maintained package from the ESRF.
- **pillow**: For TIFF image handling (fallback / metadata). The custom `MinimalTiff` handles the core reading.
- **tkinter**: Ships with Python, not a pip dependency.
- **pywin32**: NOT needed — the Synthesizer doesn't use Excel features.

---

## 8. Entry Points

```toml
[project.scripts]
pilatus-synthesizer = "pilatus_synthesizer.app:main"

[project.gui-scripts]
pilatus-synthesizer-gui = "pilatus_synthesizer.app:gui_main"
```

This replaces the old `synthesizer.exe` (PyInstaller) with standard pip-installed console scripts.

---

## 9. File Naming Convention

| Original (PascalCase) | New (snake_case) | Reason |
|------------------------|-------------------|--------|
| `ImageSynthesizer.py` | `image_synthesizer.py` | PEP 8 |
| `PilatusImage.py` | `pilatus_image.py` | PEP 8 |
| `OurTkinter.py` | `our_tkinter.py` | PEP 8 |

**Class names stay PascalCase** — only file/module names change. This is standard Python convention.

---

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Circular imports in KekLib** | Crashes on import | Already identified: TkUtils↔DebugPlot, ThreadsConnector↔ActionWindow. Break cycles with lazy imports or restructuring |
| **`PersistentInfo` uses pickle** | Security concern for open-source | Replace with JSON/TOML for settings persistence (Phase 3). Mark as known issue with deprecation warning initially |
| **`fabio` heavy dependency** | Large install size | Make CBF support optional; TIFF-only works with MinimalTiff alone |
| **GUI-only testing** | Some tests require display | Use `pytest` marks to separate GUI tests; mock Tk where possible |
| **`os.chdir()` in PilatusUtils** | Not thread-safe, changes global state | Refactor to use absolute paths instead (Phase 2) |

---

## 11. Version Strategy

| Version | Milestone |
|---------|-----------|
| **0.5.0** | Phase 2 complete — core image processing works as a library |
| **0.6.0** | Phase 3 complete — CLI works |
| **0.8.0** | Phase 4 complete — GUI works |
| **1.0.0** | Phase 5 complete — tests, CI, documentation |

Start at 0.5.0 (not 0.4.9) to signal this is a new codebase, not a patch on the old one.

---

## 12. What NOT to Migrate

| Item | Reason |
|------|--------|
| `lib/Build/` (7 files) | PyInstaller build scripts — replaced by `pyproject.toml` |
| `synthesizer.exe` | Frozen binary — replaced by `pip install` |
| `embeddables/` | Embedded Python — not needed with `pip install` |
| `KekLib` modules not used by Synthesizer (~90 files) | Dead code for this project |
| `CupyUtils/` | GPU wrappers — not used by Synthesizer |
| `tkdnd2.8/`, `tktable-2.11.kek/` | Native Tcl extensions — `tktable` replaced by `tksheet`; `tkdnd` replaced by `python-tkdnd` if needed |

---

## 13. Relationship to molass-legacy KekLib

The Synthesizer's KekLib (v1.1.4) and molass-legacy's KekLib are **divergent forks** from the same origin. Comparison of the 28 required modules shows:

- **Identical**: `OurImageIO.py`, `MinimalTiff.py`, `SAnglerMask.py`, `OurException.py`, and most others
- **Diverged**: Some modules have additional features in molass-legacy (e.g., `OurTkinter.py` has more widget helpers)

**Decision**: Copy from Synthesizer's KekLib (the exact version known to work) into `_keklib/`. Do NOT import from molass-legacy — that would create an unnecessary coupling.

**Future possibility**: If both projects share significant KekLib code, extract a `keklib` package later. This is not needed now.

---

## 14. Open Questions

1. **Should the `_keklib/` prefix stay private (`_`)?** This signals that external code should not depend on it. The underscore convention means "internal implementation detail." Recommend: yes, keep private.

2. ~~**Merge `PilatusImageInfoTable.py` and `PilatusImageInfoTable2.py`?**~~ **Resolved**: Rewrite as a single `gui/image_table.py` using `tksheet`. This eliminates both `TkTableWrapper` (native Tcl extension, hard to distribute) and `pandastable` (heavy, unmaintained Python 2 code). `tksheet` is pure Python, actively maintained, and already adopted by molass-legacy.

3. **Should `PersistentInfo` pickle files remain backward-compatible?** Users may have existing `settings.dump` and `preferences.dump` files from 0.4.8. Recommend: support reading old pickle files but write new format (JSON/TOML).

4. **Test data**: The test suite needs sample Pilatus images. Are the images in `test/images-desktop/` and `test/images-notebook/` redistributable? If not, need to create synthetic test data.

---

## Next Steps

After agreeing on this plan:

1. **Phase 1** — Create scaffold, verify `pip install -e .` works
2. **Phase 2** — Migrate core (the most valuable step — makes the algorithms available as a library)
3. Iterate through Phases 3–5

The plan is designed so that **each phase produces a working, testable deliverable**. We can pause after any phase and have something useful.
