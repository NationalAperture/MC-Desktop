"""Module entry point for ``python -m mc_desktop``."""

from __future__ import annotations

import sys

from mc_desktop.app import run_app

if __name__ == "__main__":  # pragma: no cover - entry point
    sys.exit(run_app())
