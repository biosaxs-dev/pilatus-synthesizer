"""
build_embeddables.py — build the pilatus-synthesizer embeddable distribution.

Run from the repo root with the system Python (not inside a venv):

    python build/build_embeddables.py

What this script does:
  1. Downloads the Windows embeddable Python zip from python.org
  2. Unpacks it into  dist/<name>/embeddables/
  3. Enables site-packages (uncommenting 'import site' in the ._pth file)
  4. Copies Tkinter/tcl support from the local Python installation
  5. Installs pip, then: pip install python-tkdnd pilatus-synthesizer
  6. Copies build/synthesizer.py into the output folder
  7. Copies a pre-built synthesizer.exe if present (optional)

Output folder layout:
    dist/synthesizer-<version>-x64/
        embeddables/          <- embedded Python runtime
        build/
            synthesizer.py    <- entry-point script
        synthesizer.exe       <- launcher (optional, pre-built from run.cpp)
"""

import os
import re
import sys
import platform
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PACKAGE_NAME     = "pilatus-synthesizer"
VERSION          = "0.5.1"          # update when bumping pyproject.toml
PYTHON_VERSION   = "3.13.3"         # must match embeddable zip on python.org
ARCH             = "amd64"          # amd64 or win32

LOCAL_PYTHON_DIR = Path(sys.executable).parent  # e.g. C:\Program Files\Python313

REPO_ROOT  = Path(__file__).resolve().parent.parent
DIST_ROOT  = REPO_ROOT / "dist"
OUT_NAME   = f"synthesizer-{VERSION.replace('.', '_')}-x64"
OUT_DIR    = DIST_ROOT / OUT_NAME
EMB_DIR    = OUT_DIR / "embeddables"
BUILD_DIR  = OUT_DIR / "build"

PYTHON_ZIP_URL = (
    f"https://www.python.org/ftp/python/{PYTHON_VERSION}/"
    f"python-{PYTHON_VERSION}-embed-{ARCH}.zip"
)

PACKAGES_TO_INSTALL = [
    "python-tkdnd",
    PACKAGE_NAME,
]

# ---------------------------------------------------------------------------

def banner(msg):
    print(f"\n{'='*60}\n  {msg}\n{'='*60}")


def download_embeddable_zip(dest: Path) -> Path:
    zip_path = DIST_ROOT / f"python-{PYTHON_VERSION}-embed-{ARCH}.zip"
    if zip_path.exists():
        print(f"Already downloaded: {zip_path.name}")
        return zip_path
    print(f"Downloading {PYTHON_ZIP_URL} ...")
    urllib.request.urlretrieve(PYTHON_ZIP_URL, zip_path)
    print("Done.")
    return zip_path


def unzip_embeddable(zip_path: Path, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zh:
        zh.extractall(dest)
    print(f"Unpacked into {dest}")


def enable_site_packages(emb_dir: Path):
    """Uncomment 'import site' in the ._pth file so pip-installed packages work."""
    pth_files = list(emb_dir.glob("python*._pth"))
    assert pth_files, f"No ._pth file found in {emb_dir}"
    pth = pth_files[0]
    text = pth.read_text(encoding="utf-8")
    new_text = re.sub(r"^#(import site)", r"\1", text, flags=re.MULTILINE)
    if new_text == text:
        print(f"{pth.name}: 'import site' already enabled.")
    else:
        pth.write_text(new_text, encoding="utf-8")
        print(f"{pth.name}: enabled 'import site'.")


def copy_tkinter(emb_dir: Path, local_python: Path):
    """Copy Tkinter, tcl/tk dlls from the local installation."""
    # Folders
    for folder in ["tcl", "Lib/tkinter", "Lib/idlelib"]:
        src = local_python / folder
        dst = emb_dir / folder
        if dst.exists():
            print(f"  {folder}: already exists, skipping.")
        else:
            print(f"  Copying {folder} ...")
            shutil.copytree(src, dst)

    # DLLs
    dll_names = ["_tkinter.pyd", "tcl86t.dll", "tk86t.dll", "zlib1.dll"]
    src_dlls = local_python / "DLLs"
    dst_dlls = emb_dir / "DLLs"
    dst_dlls.mkdir(exist_ok=True)
    for name in dll_names:
        src = src_dlls / name
        dst = dst_dlls / name
        if not src.exists():
            print(f"  {name}: not found in local DLLs, skipping.")
            continue
        if dst.exists():
            print(f"  {name}: already exists, skipping.")
        else:
            shutil.copyfile(src, dst)
            print(f"  Copied {name}")


def run(cmd, **kwargs):
    print(f"  > {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")
    return result


def install_pip(emb_dir: Path):
    python_exe = emb_dir / "python.exe"
    get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
    get_pip = DIST_ROOT / "get-pip.py"
    if not get_pip.exists():
        print("Downloading get-pip.py ...")
        urllib.request.urlretrieve(get_pip_url, get_pip)
    run([python_exe, get_pip])


def pip_install(emb_dir: Path, packages: list):
    python_exe = emb_dir / "python.exe"
    for pkg in packages:
        run([python_exe, "-m", "pip", "install", pkg])


def copy_launcher_script(out_dir: Path):
    src = REPO_ROOT / "build" / "synthesizer.py"
    dst_dir = out_dir / "build"
    dst_dir.mkdir(exist_ok=True)
    shutil.copyfile(src, dst_dir / "synthesizer.py")
    print(f"  Copied synthesizer.py -> {dst_dir}")


def copy_exe_if_present(out_dir: Path):
    """Copy a pre-built synthesizer.exe from build/ if available."""
    src = REPO_ROOT / "build" / "synthesizer.exe"
    if src.exists():
        shutil.copyfile(src, out_dir / "synthesizer.exe")
        print(f"  Copied synthesizer.exe")
    else:
        print("  synthesizer.exe not found — build from build/run.cpp with MSVC if needed.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if platform.system() != "Windows":
        sys.exit("This script is Windows-only.")

    banner(f"Building {OUT_NAME}")

    DIST_ROOT.mkdir(parents=True, exist_ok=True)

    if EMB_DIR.exists():
        print(f"embeddables/ already exists at {EMB_DIR}, skipping download+unpack.")
    else:
        banner("Step 1: Download embeddable Python")
        zip_path = download_embeddable_zip(DIST_ROOT)

        banner("Step 2: Unpack")
        unzip_embeddable(zip_path, EMB_DIR)

    banner("Step 3: Enable site-packages")
    enable_site_packages(EMB_DIR)

    banner("Step 4: Copy Tkinter support")
    copy_tkinter(EMB_DIR, LOCAL_PYTHON_DIR)

    banner("Step 5: Install pip")
    install_pip(EMB_DIR)

    banner("Step 6: Pip-install packages")
    pip_install(EMB_DIR, PACKAGES_TO_INSTALL)

    banner("Step 7: Copy launcher script")
    copy_launcher_script(OUT_DIR)

    banner("Step 8: Copy synthesizer.exe (optional)")
    copy_exe_if_present(OUT_DIR)

    banner("Done!")
    print(f"\nOutput folder: {OUT_DIR}")
    print("To run: synthesizer.exe  (or:  embeddables\\pythonw.exe build\\synthesizer.py)")


if __name__ == "__main__":
    main()
