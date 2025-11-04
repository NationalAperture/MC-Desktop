"""MC Desktop application package."""

from .app import run_app

__all__ = ["run_app"]

try:  # pragma: no cover - optional UI dependency
    from .ui import MainWindow
except ModuleNotFoundError:
    MainWindow = None  # type: ignore[assignment]
else:
    __all__.append("MainWindow")
