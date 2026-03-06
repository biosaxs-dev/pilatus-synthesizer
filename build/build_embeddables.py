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
import tomllib
import urllib.request
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PACKAGE_NAME     = "pilatus-synthesizer"

# Read version and dependencies from pyproject.toml — single source of truth.
_REPO_ROOT_EARLY = Path(__file__).resolve().parent.parent
with open(_REPO_ROOT_EARLY / "pyproject.toml", "rb") as _f:
    _pyproject = tomllib.load(_f)
    VERSION   = _pyproject["project"]["version"]
    _ALL_DEPS = _pyproject["project"]["dependencies"]

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

# Each entry is a list of arguments appended to `pip install --no-cache-dir`.
#
# Strategy: install python-tkdnd without its sdist-only dep (ttkwidgets), then
# install pilatus-synthesizer itself without dep-resolution, then install all
# remaining declared deps from pyproject.toml (all have binary wheels).
# ttkwidgets is imported by tkinterDnD at runtime so must be installed; it is
# sdist-only, so we first install setuptools and then use --no-build-isolation.
PACKAGES_TO_INSTALL = [
    # Skip ttkwidgets dep — we install it explicitly below after setuptools.
    ["python-tkdnd", "--no-deps"],
    # Skip dep resolution for the main package; deps installed below.
    [PACKAGE_NAME, "--no-deps"],
    # ttkwidgets needs a build backend; install setuptools first, then build
    # ttkwidgets reusing it (--no-build-isolation avoids a failing isolated env).
    ["setuptools"],
    ["ttkwidgets", "--no-build-isolation"],
    # Remaining declared deps from pyproject.toml, excluding python-tkdnd
    # (already installed above).  All of these ship binary wheels.
    *([dep] for dep in _ALL_DEPS if "python-tkdnd" not in dep),
]

# ---------------------------------------------------------------------------

def banner(msg):
    print(f"\n{'='*60}\n  {msg}\n{'='*60}")


def check_version_consistency():
    """Warn if the repo version differs from the latest version on PyPI.

    The build installs pilatus-synthesizer from PyPI.  If the PyPI version
    differs from the repo version in pyproject.toml the embeddable will not
    contain the intended release.  Publish a new release before building.
    """
    import json
    import urllib.error

    pypi_url = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
    try:
        with urllib.request.urlopen(pypi_url, timeout=10) as resp:
            data = json.loads(resp.read())
        pypi_latest = data["info"]["version"]
    except urllib.error.URLError as exc:
        print(f"  WARNING: could not reach PyPI ({exc}). Skipping version check.")
        return

    if pypi_latest == VERSION:
        print(f"  OK: repo version == PyPI latest == {VERSION}")
    else:
        print(f"  WARNING: version mismatch detected!")
        print(f"    pyproject.toml (repo) : {VERSION}")
        print(f"    PyPI latest           : {pypi_latest}")
        print(f"  The embeddable will install v{pypi_latest} from PyPI, not v{VERSION}.")
        print(f"  If you intended v{VERSION}, publish it to PyPI first.")
        answer = input("  Continue anyway? [y/N] ").strip().lower()
        if answer != "y":
            sys.exit("Aborted.")


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
    return pth


def ensure_lib_in_pth(pth: Path):
    """Add 'Lib' and 'DLLs' entries to the ._pth file.

    The embeddable zip doesn't include these paths by default, but we copy
    tkinter into Lib/ and _tkinter.pyd into DLLs/, both of which need to be
    on sys.path for 'import tkinter' to work.
    """
    text = pth.read_text(encoding="utf-8")
    changed = False
    for entry in ("Lib", "DLLs"):
        if re.search(rf"^{entry}\s*$", text, flags=re.MULTILINE):
            print(f"{pth.name}: '{entry}' already in path.")
        else:
            text = re.sub(r"^(python\d+\.zip)", rf"\1\n{entry}", text, count=1, flags=re.MULTILINE)
            changed = True
            print(f"{pth.name}: added '{entry}' to path.")
    if changed:
        pth.write_text(text, encoding="utf-8")


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
    """Install packages into the embeddable runtime.

    *packages* is a list of argument lists; the first element is the package
    name/spec and any additional elements are extra pip flags.
    """
    python_exe = emb_dir / "python.exe"
    for pkg_args in packages:
        if isinstance(pkg_args, str):
            pkg_args = [pkg_args]
        run([python_exe, "-m", "pip", "install", "--no-cache-dir", *pkg_args])


def installed_version_in_emb(emb_dir: Path) -> str | None:
    """Return the version of PACKAGE_NAME installed in the embeddable, or None."""
    python_exe = emb_dir / "python.exe"
    if not python_exe.exists():
        return None
    result = subprocess.run(
        [python_exe, "-c",
         f"import importlib.metadata; print(importlib.metadata.version('{PACKAGE_NAME}'))"],
        capture_output=True, text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def copy_launcher_script(out_dir: Path):
    src = REPO_ROOT / "build" / "synthesizer.py"
    dst_dir = out_dir / "build"
    dst_dir.mkdir(exist_ok=True)
    shutil.copyfile(src, dst_dir / "synthesizer.py")
    print(f"  Copied synthesizer.py -> {dst_dir}")


def find_vcvars64() -> Path | None:
    """Locate vcvars64.bat for the latest installed Visual Studio via vswhere."""
    vswhere = Path(r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe")
    if not vswhere.exists():
        return None
    result = subprocess.run(
        [
            vswhere, "-latest", "-products", "*",
            "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
            "-property", "installationPath",
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    vcvars = Path(result.stdout.strip()) / "VC" / "Auxiliary" / "Build" / "vcvars64.bat"
    return vcvars if vcvars.exists() else None


def build_exe(out_dir: Path) -> bool:
    """Build synthesizer.exe from build/run.cpp using MSVC.

    Falls back to copying a pre-built exe from build/ if one exists.
    Returns True on success, False if MSVC was not found.
    """
    # Fast path: pre-built exe already committed to build/
    src_prebuilt = REPO_ROOT / "build" / "synthesizer.exe"
    if src_prebuilt.exists():
        shutil.copyfile(src_prebuilt, out_dir / "synthesizer.exe")
        print("  Copied pre-built synthesizer.exe")
        return True

    vcvars = find_vcvars64()
    if vcvars is None:
        print("  MSVC not found — synthesizer.exe not built.")
        print("  Install Visual Studio (C++ workload) or Build Tools for VS 2022.")
        print("  Then re-run this script, or build manually:")
        print("    cd build && cl /D WINDOWS /D UNICODE /MT /EHsc run.cpp /Fe:synthesizer.exe")
        return False

    cpp_src = REPO_ROOT / "build" / "run.cpp"
    exe_out = out_dir / "synthesizer.exe"
    cl_cmd = f'cl /D WINDOWS /D UNICODE /MT /EHsc "{cpp_src}" /Fe:"{exe_out}"'
    # `call` + single string avoids subprocess's extra quoting and cmd.exe's
    # quote-stripping behavior (which triggers when the string starts with ").
    print(f"  Using: {vcvars}")
    result = subprocess.run(
        f'cmd /c call "{vcvars}" && {cl_cmd}',
        capture_output=True, text=True,
    )
    if result.stdout:
        # Print only last few lines (cl.exe is verbose)
        lines = result.stdout.strip().splitlines()
        for line in lines[-6:]:
            print(f"    {line}")
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr)
        print("  WARNING: synthesizer.exe build failed.")
        return False
    print(f"  Built: {exe_out}")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if platform.system() != "Windows":
        sys.exit("This script is Windows-only.")

    banner(f"Building {OUT_NAME}")
    banner("Version check")
    check_version_consistency()

    DIST_ROOT.mkdir(parents=True, exist_ok=True)

    if EMB_DIR.exists():
        emb_ver = installed_version_in_emb(EMB_DIR)
        if emb_ver == VERSION:
            print(f"embeddables/ already exists with {PACKAGE_NAME}=={VERSION}, skipping download+unpack.")
        else:
            print(f"embeddables/ exists but has {PACKAGE_NAME}=={emb_ver} (want {VERSION}).")
            print(f"Deleting {EMB_DIR} for a clean rebuild ...")
            shutil.rmtree(EMB_DIR)
    if not EMB_DIR.exists():
        banner("Step 1: Download embeddable Python")
        zip_path = download_embeddable_zip(DIST_ROOT)

        banner("Step 2: Unpack")
        unzip_embeddable(zip_path, EMB_DIR)

    banner("Step 3: Enable site-packages")
    pth = enable_site_packages(EMB_DIR)

    banner("Step 4: Copy Tkinter support")
    copy_tkinter(EMB_DIR, LOCAL_PYTHON_DIR)
    ensure_lib_in_pth(pth)

    banner("Step 5: Install pip")
    install_pip(EMB_DIR)

    banner("Step 6: Pip-install packages")
    pip_install(EMB_DIR, PACKAGES_TO_INSTALL)

    banner("Step 7: Copy launcher script")
    copy_launcher_script(OUT_DIR)

    banner("Step 8: Build synthesizer.exe")
    build_exe(OUT_DIR)

    banner("Done!")
    print(f"\nOutput folder: {OUT_DIR}")
    print("To run: synthesizer.exe  (or:  embeddables\\pythonw.exe build\\synthesizer.py)")


if __name__ == "__main__":
    main()
