# Pilatus Synthesizer

Pilatus Synthesizer combines multiple Pilatus X-ray detector images taken at different detector positions into a single synthesized image. Used at KEK Photon Factory and SPring-8 beamlines for SAXS experiments.

## Features

- **Sub-pixel alignment**: Bilinear interpolation for accurate image registration
- **Mask handling**: SAngler mask file support for excluding bad pixels
- **Intensity normalization**: Beam monitor counter-based intensity correction
- **Multiple synthesis methods**: Cover (gap-filling) and average modes
- **GUI and CLI**: Interactive Tkinter interface or batch command-line processing
- **Auto-run**: Folder polling for automated synthesis during measurements
- **Facility support**: Photon Factory (left direction) and SPring-8 (right direction)

## Tested Platforms

- Python 3.13 on Windows 11
- Python 3.12 on Windows 11

## Installation

```
pip install -U pilatus-synthesizer
```

## Usage

### GUI mode (default)

```
pilatus-synthesizer
```

### Command-line mode

```
pilatus-synthesizer -c -i INPUT_FOLDER [-o OUTPUT_FOLDER]
```

### Options

| Flag | Description |
|------|-------------|
| `-c` | Run in command mode (no GUI) |
| `-i FOLDER` | Input image folder (required for command mode) |
| `-o FOLDER` | Output folder (default: `INPUT/Synthesized`) |
| `-n` | Auto-number output folders if default exists |
| `-j FOLDER` | Adjusted image folder |
| `-m` | Write intermediate results |
| `-v` | Show version info |

## Documentation

- **User's Guide**: [doc/UsersGuide-0_4_8.pdf](doc/UsersGuide-0_4_8.pdf)
- **Migration Plan**: [MIGRATION_PLAN.md](MIGRATION_PLAN.md)

## Related Projects

- [molass-library](https://github.com/biosaxs-dev/molass-library) — SEC-SAXS analysis library
- [molass-legacy](https://github.com/biosaxs-dev/molass-legacy) — Legacy MOLASS application

## License

[GNU General Public License v3.0](LICENSE)

## Copyright

Copyright (c) 2015-2026, SAXS Team, KEK-PF

## Acknowledgements

The migration of this project from the legacy codebase to the current Python package structure was performed with the assistance of [GitHub Copilot](https://github.com/features/copilot) (Claude Sonnet 4.6), 2026.
