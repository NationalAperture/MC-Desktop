"""Update notification dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QCheckBox
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl


class UpdateDialog(QDialog):
    """Dialog prompting user to update the application."""

    def __init__(self, new_version: str, download_url: str, parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.setWindowTitle("Update Available")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Message
        message = QLabel(
            f"A new version of NAI-Mover is available!\n\n"
            f"New version: {new_version}\n"
            f"Your version: {self._get_current_version()}\n\n"
            f"Would you like to download the update?"
        )
        message.setWordWrap(True)
        layout.addWidget(message)

        # Skip this version checkbox
        self.skip_checkbox = QCheckBox("Skip this version")
        layout.addWidget(self.skip_checkbox)

        # Buttons
        button_layout = QHBoxLayout()

        self.download_btn = QPushButton("Download Update")
        self.download_btn.clicked.connect(self._open_download)

        self.later_btn = QPushButton("Remind Me Later")
        self.later_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.later_btn)
        button_layout.addWidget(self.download_btn)

        layout.addLayout(button_layout)

    def _get_current_version(self) -> str:
        from mc_desktop.version import __version__
        return __version__

    def _open_download(self):
        """Open the download URL in the default browser."""
        QDesktopServices.openUrl(QUrl(self.download_url))
        self.accept()

    def get_skipped_version(self) -> str | None:
        """Return version to skip if checkbox was checked."""
        if self.skip_checkbox.isChecked():
            return self.windowTitle()  # Or parse from dialog
        return None