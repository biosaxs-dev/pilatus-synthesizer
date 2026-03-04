# AI Assistant Initialization Guide

**Purpose**: Initialize AI context for working with this repository  
**Created**: March 4, 2026  
**Magic phrase**: **"Please read COPILOT-INIT.md to initialize"**

---

## Core Documents

1. **[README.md](README.md)** — Repository purpose and usage
2. **[MIGRATION_PLAN.md](MIGRATION_PLAN.md)** — Migration plan from legacy Synthesizer 0.4.8
3. **[pyproject.toml](pyproject.toml)** — Package configuration

## Repository Context

**What**: Pilatus detector image synthesizer for SAXS beamlines at KEK-PF and SPring-8.

**Origin**: Migrated from closed-source Synthesizer 0.4.8 (2015–2025) to open-source Python package, aligned with the molass ecosystem (molass-library, molass-legacy).

**Original source**: Preserved in `legacy/synthesizer-0_4_8-x64/` for reference.

## Package Structure

```
pilatus_synthesizer/
├── app.py          — Entry point (GUI + CLI dispatch)
├── core/           — Image processing (GUI-independent)
├── gui/            — Tkinter GUI (optional)
├── cli/            — Command-line interface
├── config/         — Settings & persistence
└── _keklib/        — Internal utility subset from KekLib
```

## Conventions

- **Build system**: hatchling (same as molass-library, molass-legacy)
- **License**: GPLv3
- **Python**: >=3.12
- **File naming**: snake_case for modules, PascalCase for classes
- **Imports**: absolute package imports (`from pilatus_synthesizer.core.pilatus_image import ...`)
- **No Python 2 compat**: No `from __future__` imports

## Current Progress

- **Phase 1 (Scaffold)**: ✅ Complete — `pip install -e .` works
- **Phase 2 (Core)**: ✅ Complete — all core/ and _keklib/ modules migrated
- **Phase 3 (Config & CLI)**: Not started
- **Phase 4 (GUI)**: Not started — tksheet modernization planned
- **Phase 5 (Tests & Polish)**: Not started

### Migrated modules (Phase 2)

| New module | Original | Key changes |
|---|---|---|
| `_keklib/our_exception.py` | `OurException.py` | Removed `__future__` |
| `_keklib/exception_traceback.py` | `ExceptionTracebacker.py` | Removed unused numpy |
| `_keklib/basic_utils.py` | `BasicUtils.py` | Subset only |
| `core/sangler_mask.py` | `SAnglerMask.py` | `with open()` |
| `core/minimal_tiff.py` | `MinimalTiff.py` | `with open()`, `.copy()` on frombuffer |
| `core/image_io.py` | `OurImageIO.py` | Relative imports |
| `core/image_property.py` | `PilatusImageProperty.py` | Core only (GUI class deferred) |
| `core/pilatus_counter.py` | `PilatusCounter.py` | Absolute paths, `items()` |
| `core/pilatus_image.py` | `PilatusImage.py` | `algorithm` param replaces `get_devel_info` |
| `core/pilatus_utils.py` | `PilatusUtils.py` | Absolute paths, no `os.chdir` |
| `core/pilatus_utils_old_style.py` | `PilatusUtilsOldStyle.py` | Absolute paths |
| `core/pilatus_utils_new_style.py` | `PilatusUtilsNewStyle.py` | Relative imports |
| `core/image_synthesizer.py` | `ImageSynthesizer.py` | Pure computation, no GUI |

## Working With Legacy Code

When migrating a module from `legacy/`, follow these steps:
1. Read the original file in `legacy/synthesizer-0_4_8-x64/synthesizer-0_4_8-x64/lib/`
2. Create the new file in the appropriate subpackage
3. Convert bare imports to absolute package imports
4. Remove `from __future__` imports
5. Fix `open()` calls to use `with` statements
6. Replace `os.chdir()` with absolute path operations where possible
