import logging

import pytest

PySide6 = pytest.importorskip("PySide6")
pytest.importorskip("pytestqt")
from PySide6.QtCore import Qt

from mc_desktop.ui.update_dialog import UpdateDialog
from mc_desktop.ui.main_window import MainWindow
from mc_desktop.commands import CMD_JOG


def test_update_dialog_toggle_notes_and_button_click(qtbot):
    dialog = UpdateDialog(
        new_version="2.0.0",
        download_url="https://example.com",
        release_notes="* Item 1\n* Item 2",
    )
    qtbot.addWidget(dialog)
    dialog.show()

    assert dialog.notes_container.isVisible() is False

    with qtbot.waitSignal(dialog.notes_toggle.toggled):
        qtbot.mouseClick(dialog.notes_toggle, Qt.LeftButton)

    assert dialog.notes_container.isVisible() is True

    with qtbot.waitSignal(dialog.later_btn.clicked):
        qtbot.mouseClick(dialog.later_btn, Qt.LeftButton)


def test_update_dialog_progress_updates_ui(qtbot):
    dialog = UpdateDialog(
        new_version="2.0.0",
        download_url="https://example.com",
        release_notes="",
    )
    qtbot.addWidget(dialog)

    dialog.progress_bar.setVisible(True)
    dialog.status_label.setVisible(True)
    dialog._on_progress(1024, 2048)

    assert dialog.progress_bar.maximum() == 2048
    assert dialog.progress_bar.value() == 1024
    assert "Downloading" in dialog.status_label.text()


def test_send_command_skips_without_node_id(qtbot, caplog, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    called = False

    def _spy(*_args, **_kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(window.serial, "transmit_queue", _spy)

    with caplog.at_level(logging.WARNING):
        window.send_command((CMD_JOG, "1"))

    assert called is False
    assert "No node selected" in caplog.text


def test_validate_node_id_accepts_known_node(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.node_manager.add_node("1")

    assert window._validate_node_id("1", context="test") == "1"
