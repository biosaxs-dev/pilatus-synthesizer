# Building the Embeddable Distribution

This folder contains the scripts needed to produce a self-contained Windows
distribution of `pilatus-synthesizer`, similar to the legacy
`synthesizer-0_4_8-x64` layout.

## Output layout

```
dist/synthesizer-0_5_1-x64/
    embeddables/              ← embedded Python runtime + all packages
    build/
        synthesizer.py        ← entry-point script
    synthesizer.exe           ← C++ launcher (optional, see below)
```

The user double-clicks `synthesizer.exe`, which launches
`embeddables\pythonw.exe build\synthesizer.py` — no system Python required.

---

## Step 1 — Build the Python distribution folder

Run from the **repository root** with the system Python (not inside a venv):

```powershell
python build/build_embeddables.py
```

This will:

1. Download `python-3.13.3-embed-amd64.zip` from python.org into `dist/`
2. Unpack it into `dist/synthesizer-0_5_1-x64/embeddables/`
3. Enable site-packages (uncomment `import site` in the `._pth` file)
4. Copy Tkinter / tcl support from the local Python installation
5. Download and install `pip` into the embeddable runtime
6. `pip install python-tkdnd pilatus-synthesizer` into the embeddable runtime
7. Copy `build/synthesizer.py` into the output folder

> **Note:** The Python version and package version are configured at the top of
> `build_embeddables.py`. Update `VERSION` and `PYTHON_VERSION` before building
> a new release.

---

## Step 2 — Build the C++ launcher (optional)

The launcher `synthesizer.exe` is a small Windows GUI program (no console
window) that locates `embeddables\pythonw.exe` and runs `build\synthesizer.py`.

### Prerequisites

- Visual Studio with C++ workload, **or** the standalone
  [Build Tools for Visual Studio](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)

### Build

Open a **Developer Command Prompt for VS** (or run `vcvars64.bat`) and execute:

```cmd
cd C:\Users\takahashi\GitHub\pilatus-synthesizer\build
cl /D WINDOWS /D UNICODE /MT /EHsc run.cpp /Fe:synthesizer.exe
```

The `/MT` flag statically links the CRT so the exe runs without redistributable
DLLs on end-user machines.

### Set an icon (optional)

Using [rcedit](https://github.com/electron/rcedit):

```cmd
rcedit-x64.exe synthesizer.exe --set-icon path\to\synthesizer.ico
```

### Deploy

Copy `synthesizer.exe` into the distribution root:

```
dist/synthesizer-0_5_1-x64/synthesizer.exe
```

Alternatively, place it in `build/synthesizer.exe` **before** running
`build_embeddables.py` — the build script copies it automatically.

---

## Files in this folder

| File | Description |
|---|---|
| `build_embeddables.py` | Main build script — creates the full distribution folder |
| `synthesizer.py` | Entry-point script executed by the embedded Python |
| `run.cpp` | C++ source for the launcher exe |
| `README.md` | This file |
