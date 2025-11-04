#!/usr/bin/env python3
"""Compile Qt Designer `.ui` files into PySide6 form classes.

Usage:
    python scripts/generate_ui.py
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
from typing import Iterable, Tuple

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent

DESIGNER_DIR = PROJECT_ROOT / "mc_desktop" / "ui" / "designer"

UI_MAPPINGS: Iterable[Tuple[pathlib.Path, pathlib.Path]] = (
    (DESIGNER_DIR / "form.ui", PROJECT_ROOT / "mc_desktop" / "ui" / "forms" / "ui_form.py"),
    (DESIGNER_DIR / "connection_form.ui", PROJECT_ROOT / "mc_desktop" / "ui" / "forms" / "ui_connection_form.py"),
    (DESIGNER_DIR / "motor_stats.ui", PROJECT_ROOT / "mc_desktop" / "ui" / "forms" / "ui_motor_stats.py"),
    (DESIGNER_DIR / "record_bus.ui", PROJECT_ROOT / "mc_desktop" / "ui" / "forms" / "ui_record_bus.py"),
    (DESIGNER_DIR / "record_system.ui", PROJECT_ROOT / "mc_desktop" / "ui" / "forms" / "ui_record_system.py"),
)


def find_uic_executable() -> pathlib.Path:
    candidate = shutil.which("pyside6-uic")
    if candidate:
        return pathlib.Path(candidate)

    python_dir = pathlib.Path(sys.executable).parent
    direct_candidate = python_dir / "pyside6-uic"
    if direct_candidate.exists():
        return direct_candidate

    if sys.platform.startswith("win"):
        windows_candidate = direct_candidate.with_suffix(".exe")
        if windows_candidate.exists():
            return windows_candidate

    raise FileNotFoundError("pyside6-uic not found in PATH or alongside the active Python executable.")


def compile_ui(uic_executable: pathlib.Path, source: pathlib.Path, target: pathlib.Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    command = [str(uic_executable), str(source), "-o", str(target), "--from-imports"]
    subprocess.run(command, check=True)


def main() -> int:
    missing = [str(src) for src, _ in UI_MAPPINGS if not src.exists()]
    if missing:
        print("Missing .ui files:", ", ".join(missing), file=sys.stderr)
        return 1

    try:
        uic_executable = find_uic_executable()
    except FileNotFoundError:
        print("pyside6-uic not found. Install PySide6 and ensure it is on PATH.", file=sys.stderr)
        return 1

    try:
        for source, target in UI_MAPPINGS:
            compile_ui(uic_executable, source, target)
            print(f"Generated {target.relative_to(PROJECT_ROOT)}")
    except subprocess.CalledProcessError as exc:
        print(f"Failed to compile {exc.cmd[1]} -> {exc.cmd[3]}", file=sys.stderr)
        return exc.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
