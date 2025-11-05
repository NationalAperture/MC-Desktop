"""UI components for the MC Desktop application."""

__all__ = []

try:  # pragma: no cover - PySide6 may not be installed when running tests
    from .main_window import MainWindow
except ModuleNotFoundError:
    MainWindow = None  # type: ignore[assignment]
else:
    __all__.append("MainWindow")
