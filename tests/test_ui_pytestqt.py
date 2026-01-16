import pytest

PySide6 = pytest.importorskip("PySide6")
pytest.importorskip("pytestqt")
from PySide6.QtCore import Qt

from mc_desktop.ui.update_dialog import UpdateDialog


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
