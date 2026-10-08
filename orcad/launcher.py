"""
orcad/launcher.py  --  Launch OrCAD Capture and source a Tcl script.

Update LAUNCH_MODE after Day 0 verification.

CLI:
    python -m orcad.launcher out/design.tcl
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# -----------------------------------------------------------------------
# CONFIGURE AFTER DAY 0 VERIFICATION
# -----------------------------------------------------------------------
LAUNCH_MODE = "manual"          # "cli" | "pywinauto" | "manual"
ORCAD_EXE   = r"C:\Cadence\SPB_17.4\tools\bin\capture.exe"   # adjust path
# -----------------------------------------------------------------------


class LaunchError(RuntimeError):
    pass


def launch_cli(tcl_path: str) -> int:
    """
    Run Capture with -batch flag.
    VERIFY: confirm Capture accepts -batch and -script flags.
    """
    cmd = [ORCAD_EXE, "-batch", "-script", str(tcl_path)]
    print(f"[launcher] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise LaunchError(f"Capture exited with code {result.returncode}")
    return result.returncode


def launch_pywinauto(tcl_path: str) -> None:
    """
    Use pywinauto to drive Capture GUI.
    VERIFY: window title and control IDs from Day 0 journaling.
    """
    try:
        import pywinauto
    except ImportError:
        raise LaunchError("pywinauto not installed. Run: pip install pywinauto")

    raise NotImplementedError(
        "pywinauto mode not yet verified. "
        "Journal the window title from Capture, then update this function."
    )


def launch_manual(tcl_path: str) -> None:
    """Print instructions for manual execution."""
    tcl_abs = str(Path(tcl_path).resolve()).replace('\\', '/')
    print("[launcher] MANUAL MODE")
    print("  1. Open OrCAD Capture")
    print("  2. Create a new design or open an existing project")
    print("  3. In the Capture command window, run:")
    print(f"       source {tcl_abs}")
    print("  4. The design will be placed automatically.")


def launch(tcl_path: str) -> None:
    if LAUNCH_MODE == "cli":
        launch_cli(tcl_path)
    elif LAUNCH_MODE == "pywinauto":
        launch_pywinauto(tcl_path)
    elif LAUNCH_MODE == "manual":
        launch_manual(tcl_path)
    else:
        raise LaunchError(f"Unknown LAUNCH_MODE: {LAUNCH_MODE}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Launch OrCAD Capture and source a generated Tcl script."
    )
    parser.add_argument("tcl", help="Path to the .tcl script")
    args = parser.parse_args()

    if not Path(args.tcl).exists():
        print(f"ERROR: Tcl script not found: {args.tcl}", file=sys.stderr)
        sys.exit(1)

    launch(args.tcl)


if __name__ == "__main__":
    main()
