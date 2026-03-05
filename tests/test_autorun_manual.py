"""
Manual interactive test for auto-run mode.

Usage:
    python tests/test_autorun_manual.py

What it does:
    1. Creates a temp input folder with the first batch of images (simulating
       images already on disk when auto-run starts).
    2. Launches the GUI in AUTOMATIC mode — auto-run starts immediately.
    3. Every DELIVER_INTERVAL seconds, copies the next batch of 3 images
       (one sample) into the temp folder, simulating new data arriving from
       the detector.
    4. Stops delivering after all samples have been copied.

Data source: C:\\Users\\takahashi\\Synthesizer\\20241112\\GISAXS
    - Naming pattern: prefix_dN_NNNNN.tif (new-style, 3 detector positions)
    - 6 files = 2 samples x 3 detector positions (d0, d1, d2)
    - Prefixes: SAXS_bAz_P_change, SAXS_Murata_N_fix
    - Log:  measurement_GISAXS.log
    - Mask: AgBh_20250312.mask
"""

import shutil
import threading
import time
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
SRC  = Path(r"C:\Users\takahashi\Synthesizer\20241112\GISAXS")
TMP  = Path(r"C:\Users\takahashi\Synthesizer\20241112\GISAXS_autorun_test")
LOG  = SRC / "measurement_GISAXS.log"
MASK = SRC / "AgBh_20250312.mask"

# ── Delivery parameters ────────────────────────────────────────────────
FILES_PER_SAMPLE  = 3   # number of detector positions per sample
DELIVER_INTERVAL  = 30  # seconds between sample deliveries


def _deliver_remaining(files: list[Path], interval: int) -> None:
    """Background thread: copy files in batches spaced by *interval* seconds."""
    batches = [files[i:i + FILES_PER_SAMPLE]
               for i in range(0, len(files), FILES_PER_SAMPLE)]
    for batch in batches:
        time.sleep(interval)
        for f in batch:
            shutil.copy2(f, TMP / f.name)
        print(f"[autorun-test] Delivered: {[f.name for f in batch]}")
    print("[autorun-test] All files delivered.")


def main() -> None:
    # ── 1. Prepare temp folder ─────────────────────────────────────────
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)

    # Copy log and mask so the GUI can find them automatically
    shutil.copy2(LOG,  TMP / LOG.name)
    shutil.copy2(MASK, TMP / MASK.name)

    # Create output folder (required by entry validation)
    (TMP / "Synthesized").mkdir(exist_ok=True)

    # ── 2. Deliver first batch immediately ─────────────────────────────
    # Deliver _dN_-style multi-detector files (not the sequential single-detector
    # time series).  Two complete samples (d0/d1/d2) in arrival order.
    all_files = (
        sorted(SRC.glob("SAXS_bAz_P_change_d[012]_*.tif")) +
        sorted(SRC.glob("SAXS_Murata_N_fix_d[012]_*.tif"))
    )
    if not all_files:
        raise FileNotFoundError(f"No _dN_ multi-detector .tif files found in {SRC}")

    first_batch = all_files[:FILES_PER_SAMPLE]
    for f in first_batch:
        shutil.copy2(f, TMP / f.name)
    print(f"[autorun-test] Initial batch: {[f.name for f in first_batch]}")

    # ── 3. Start background delivery for remaining samples ─────────────
    remaining = all_files[FILES_PER_SAMPLE:]
    t = threading.Thread(
        target=_deliver_remaining,
        args=(remaining, DELIVER_INTERVAL),
        daemon=True,
    )
    t.start()

    # ── 4. Configure settings and launch GUI ───────────────────────────
    from pilatus_synthesizer.config.settings import set_setting, save_settings
    from pilatus_synthesizer.config.development import set_devel_info

    set_setting('in_folder',     str(TMP))
    set_setting('log_file',      str(TMP / LOG.name))
    set_setting('mask_file',     str(TMP / MASK.name))
    set_setting('syn_folder',    str(TMP / "Synthesized"))
    set_setting('op_option',     'AUTOMATIC')
    set_setting('watch_interval', DELIVER_INTERVAL)
    set_devel_info('adj_output', 'NO')
    save_settings()

    # Verify settings are visible before GUI starts
    from pilatus_synthesizer.config.settings import get_setting
    print(f"[autorun-test] in_folder  = {get_setting('in_folder')}")
    print(f"[autorun-test] log_file   = {get_setting('log_file')}")
    print(f"[autorun-test] mask_file  = {get_setting('mask_file')}")
    print(f"[autorun-test] syn_folder = {get_setting('syn_folder')}")
    print(f"[autorun-test] op_option  = {get_setting('op_option')}")

    from pilatus_synthesizer.app import gui_main
    gui_main()


if __name__ == '__main__':
    main()
