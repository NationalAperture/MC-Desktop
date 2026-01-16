"""Update notification dialog."""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QCheckBox,
    QProgressBar,
    QMessageBox,
    QTextBrowser,
    QToolButton,
    QWidget,
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

from mc_desktop.updater import UpdateDownloader


class UpdateDialog(QDialog):
    """Dialog prompting user to update the application."""

    def __init__(
        self,
        new_version: str,
        download_url: str,
        release_notes: str = "",
        download_size: object = None,
        parent=None,
    ):
        super().__init__(parent)
        self.download_url = download_url
        self.new_version = new_version
        self.setWindowTitle("Update Available")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setMinimumHeight(350)

        # Downloader
        self.downloader = UpdateDownloader(self)
        self.downloader.progress.connect(self._on_progress)
        self.downloader.download_complete.connect(self._on_download_complete)
        self.downloader.download_failed.connect(self._on_download_failed)
        self.downloader.install_complete.connect(self._on_install_complete)
        self.downloader.install_failed.connect(self._on_install_failed)

        layout = QVBoxLayout(self)

        # Message
        self.message = QLabel(
            f"A new version of NAI-Mover is available!\n\n"
            f"New version: {new_version}\n"
            f"Your version: {self._get_current_version()}"
        )
        self.message.setWordWrap(True)
        layout.addWidget(self.message)

        # Download size
        self.size_label = QLabel()
        self._set_download_size(download_size)
        layout.addWidget(self.size_label)

        # Release notes (collapsible)
        if release_notes:
            self.notes_toggle = QToolButton()
            self.notes_toggle.setText("What's New")
            self.notes_toggle.setCheckable(True)
            self.notes_toggle.setChecked(False)
            self.notes_toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            self.notes_toggle.setArrowType(Qt.ArrowType.RightArrow)
            layout.addWidget(self.notes_toggle)

            self.notes_container = QWidget()
            notes_layout = QVBoxLayout(self.notes_container)
            notes_layout.setContentsMargins(0, 0, 0, 0)

            self.release_notes = QTextBrowser()
            self.release_notes.setMarkdown(release_notes)
            self.release_notes.setOpenExternalLinks(True)
            self.release_notes.setMaximumHeight(150)
            notes_layout.addWidget(self.release_notes)

            self.notes_container.setVisible(False)
            layout.addWidget(self.notes_container)
            self.notes_toggle.toggled.connect(self._toggle_release_notes)

        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label (hidden initially)
        self.status_label = QLabel()
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        # Skip this version checkbox
        self.skip_checkbox = QCheckBox("Skip this version")
        layout.addWidget(self.skip_checkbox)

        # Buttons
        button_layout = QHBoxLayout()

        self.later_btn = QPushButton("Remind Me Later")
        self.later_btn.clicked.connect(self.reject)

        self.download_btn = QPushButton("Download && Install")
        self.download_btn.clicked.connect(self._start_download)

        self.open_browser_btn = QPushButton("Open in Browser")
        self.open_browser_btn.clicked.connect(self._open_download)

        button_layout.addWidget(self.later_btn)
        button_layout.addWidget(self.open_browser_btn)
        button_layout.addWidget(self.download_btn)

        layout.addLayout(button_layout)

    def _get_current_version(self) -> str:
        from mc_desktop.version import __version__
        return __version__

    def _set_download_size(self, download_size: object) -> None:
        if download_size is None:
            self.size_label.setText("Download size: Unknown")
            return
        try:
            size = int(download_size)
        except (TypeError, ValueError):
            self.size_label.setText("Download size: Unknown")
            return
        size_mb = size / (1024 * 1024)
        self.size_label.setText(f"Download size: {size_mb:.1f} MB")

    def _toggle_release_notes(self, expanded: bool) -> None:
        self.notes_container.setVisible(expanded)
        self.notes_toggle.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )

    def _open_download(self):
        """Open the download URL in the default browser."""
        QDesktopServices.openUrl(QUrl(self.download_url))
        self.accept()

    def _start_download(self):
        """Start downloading the update."""
        self.download_btn.setEnabled(False)
        self.open_browser_btn.setEnabled(False)
        self.later_btn.setEnabled(False)
        self.skip_checkbox.setEnabled(False)

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate until we know the size
        self.status_label.setVisible(True)
        self.status_label.setText("Starting download...")

        self.downloader.download(self.download_url)

    def _on_progress(self, bytes_received: int, bytes_total: int):
        """Update progress bar."""
        if bytes_total > 0:
            self.progress_bar.setRange(0, bytes_total)
            self.progress_bar.setValue(bytes_received)

            # Show progress in MB
            received_mb = bytes_received / (1024 * 1024)
            total_mb = bytes_total / (1024 * 1024)
            self.status_label.setText(f"Downloading: {received_mb:.1f} / {total_mb:.1f} MB")
        else:
            self.status_label.setText(f"Downloading: {bytes_received / 1024:.0f} KB")

    def _on_download_complete(self, path: str):
        """Handle download completion."""
        self.status_label.setText("Download complete. Installing...")
        self.progress_bar.setRange(0, 0)  # Indeterminate for install

        # Start installation
        self.downloader.install()

    def _on_download_failed(self, error: str):
        """Handle download failure."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Download failed: {error}")

        QMessageBox.warning(
            self,
            "Download Failed",
            f"Failed to download update:\n{error}\n\nYou can try downloading manually from the browser."
        )

        self._reset_buttons()

    def _on_install_complete(self):
        """Handle installation completion."""
        self.status_label.setText("Update installed! Restarting...")
        # App will restart automatically

    def _on_install_failed(self, error: str):
        """Handle installation failure."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Installation failed: {error}")

        QMessageBox.warning(
            self,
            "Installation Failed",
            f"Failed to install update:\n{error}\n\nYou can try downloading manually from the browser."
        )

        self._reset_buttons()

    def _reset_buttons(self):
        """Re-enable buttons after failure."""
        self.download_btn.setEnabled(True)
        self.open_browser_btn.setEnabled(True)
        self.later_btn.setEnabled(True)
        self.skip_checkbox.setEnabled(True)

    def get_skipped_version(self) -> str | None:
        """Return version to skip if checkbox was checked."""
        if self.skip_checkbox.isChecked():
            return self.new_version
        return None
