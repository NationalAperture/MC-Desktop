"""Application bootstrap helpers for MC Desktop."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional, TYPE_CHECKING
from logging.handlers import RotatingFileHandler

from importlib import resources

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

LOGGER_NAME = "mc_desktop"
STYLESHEET_NAME = "Diffnes-Gold.qss"
_STYLESHEET_CACHE: Optional[str] = None


def configure_logging(log_directory: Optional[Path] = None) -> logging.Logger:
    """Configure application logging and return the configured logger."""
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    log_dir = log_directory or Path.cwd() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(log_dir / "info.log", maxBytes=10240, backupCount=3)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def _apply_stylesheet(app: "QApplication") -> None:
    """Apply the packaged Qt stylesheet if it exists."""
    global _STYLESHEET_CACHE
    if _STYLESHEET_CACHE is not None:
        app.setStyleSheet(_STYLESHEET_CACHE)
        return
    try:
        stylesheet = resources.files("mc_desktop.resources").joinpath(STYLESHEET_NAME).read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError):
        logging.getLogger(LOGGER_NAME).warning("Stylesheet %s not found in resources package", STYLESHEET_NAME)
        return

    _STYLESHEET_CACHE = stylesheet
    app.setStyleSheet(stylesheet)


def run_app() -> int:
    """Create the QApplication, show the main window, and start the event loop."""
    logger = configure_logging()
    logger.info("Application started")
    try:
        from PySide6.QtWidgets import QApplication
        from .ui import MainWindow

        app = QApplication(sys.argv)
        window = MainWindow(logger)
        window.show()
        app.processEvents()
        _apply_stylesheet(app)
        return app.exec()
    except Exception as exc:  # pragma: no cover - surface to caller/log
        logger.exception("Main crashed. Error: %s", exc)
        raise
    finally:
        logger.info("Application shutdown")
