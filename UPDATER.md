# Auto-Update System for NAI-Mover

This guide covers how to set up GitHub Releases as your distribution mechanism and implement an in-app update checker.

## Part 1: GitHub Releases Setup

### Creating a Release

1. **Tag your release** with semantic versioning:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. **Build your executable** using PyInstaller:
   ```bash
   pyinstaller NAI-Mover.spec
   ```

3. **Create the GitHub Release**:
   - Go to your repository → Releases → "Create a new release"
   - Select your tag (e.g., `v0.1.0`)
   - Add release notes describing changes
   - Upload the built executable(s) from `dist/`
   - Name platform-specific builds clearly (e.g., `NAI-Mover-windows.exe`, `NAI-Mover-linux`)

### Automating Builds with GitHub Actions

Create `.github/workflows/release.yml`:

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install -e .
          pip install pyinstaller

      - name: Build executable
        run: pyinstaller NAI-Mover.spec

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: NAI-Mover-windows
          path: dist/NAI-Mover.exe

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install -e .
          pip install pyinstaller

      - name: Build executable
        run: pyinstaller NAI-Mover.spec

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: NAI-Mover-linux
          path: dist/NAI-Mover

  create-release:
    needs: [build-windows, build-linux]
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Download Windows artifact
        uses: actions/download-artifact@v4
        with:
          name: NAI-Mover-windows
          path: ./windows

      - name: Download Linux artifact
        uses: actions/download-artifact@v4
        with:
          name: NAI-Mover-linux
          path: ./linux

      - name: Create Release
        uses: softprops/action-gh-release@v2
        with:
          files: |
            ./windows/NAI-Mover.exe
            ./linux/NAI-Mover
          generate_release_notes: true
```

## Part 2: In-App Update Checker

### Step 1: Create the Version Module

Create `mc_desktop/version.py`:

```python
__version__ = "0.1.0"
```

Update `pyproject.toml` to use dynamic versioning or keep them in sync manually.

### Step 2: Create the Update Checker Module

Create `mc_desktop/updater.py`:

```python
"""Auto-update checker using GitHub Releases API."""

import logging
from packaging import version
from PySide6.QtCore import QObject, Signal, QThread
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QUrl
import json

from mc_desktop.version import __version__

logger = logging.getLogger(__name__)

# Update this to your repository
GITHUB_REPO = "your-username/MC-Desktop"
RELEASES_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


class UpdateChecker(QObject):
    """Checks GitHub for new releases."""

    update_available = Signal(str, str)  # new_version, download_url
    no_update = Signal()
    check_failed = Signal(str)  # error_message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self._on_response)
        self.current_version = __version__

    def check_for_updates(self):
        """Initiate an update check."""
        logger.info(f"Checking for updates (current version: {self.current_version})")

        request = QNetworkRequest(QUrl(RELEASES_API_URL))
        request.setHeader(
            QNetworkRequest.KnownHeaders.UserAgentHeader,
            f"NAI-Mover/{self.current_version}"
        )
        request.setRawHeader(b"Accept", b"application/vnd.github.v3+json")

        self.manager.get(request)

    def _on_response(self, reply: QNetworkReply):
        """Handle the API response."""
        if reply.error() != QNetworkReply.NetworkError.NoError:
            error_msg = reply.errorString()
            logger.warning(f"Update check failed: {error_msg}")
            self.check_failed.emit(error_msg)
            reply.deleteLater()
            return

        try:
            data = json.loads(reply.readAll().data().decode())
            latest_version = data.get("tag_name", "").lstrip("v")

            if not latest_version:
                self.check_failed.emit("Could not parse version from release")
                return

            # Compare versions
            if version.parse(latest_version) > version.parse(self.current_version):
                # Find the appropriate download URL for this platform
                download_url = data.get("html_url", "")

                # Optionally find platform-specific asset
                assets = data.get("assets", [])
                for asset in assets:
                    name = asset.get("name", "").lower()
                    # Adjust these conditions based on your asset naming
                    import sys
                    if sys.platform == "win32" and "windows" in name:
                        download_url = asset.get("browser_download_url", download_url)
                        break
                    elif sys.platform == "linux" and "linux" in name:
                        download_url = asset.get("browser_download_url", download_url)
                        break

                logger.info(f"Update available: {latest_version}")
                self.update_available.emit(latest_version, download_url)
            else:
                logger.info("No update available")
                self.no_update.emit()

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse update response: {e}")
            self.check_failed.emit(str(e))
        finally:
            reply.deleteLater()
```

### Step 3: Create the Update Dialog

Create `mc_desktop/ui/update_dialog.py`:

```python
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
```

### Step 4: Integrate into Main Window

Add to `mc_desktop/ui/main_window.py`:

```python
from mc_desktop.updater import UpdateChecker
from mc_desktop.ui.update_dialog import UpdateDialog
from PySide6.QtCore import QSettings

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # ... existing init code ...

        # Check for updates after window is shown
        self.update_checker = UpdateChecker(self)
        self.update_checker.update_available.connect(self._on_update_available)
        self.update_checker.check_failed.connect(self._on_update_check_failed)

        # Delay the check slightly to let the UI load first
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, self._check_for_updates)

    def _check_for_updates(self):
        """Initiate update check."""
        self.update_checker.check_for_updates()

    def _on_update_available(self, new_version: str, download_url: str):
        """Handle available update."""
        settings = QSettings("NAI", "NAI-Mover")
        skipped = settings.value("skipped_version", "")

        # Don't prompt if user skipped this version
        if skipped == new_version:
            return

        dialog = UpdateDialog(new_version, download_url, self)
        result = dialog.exec()

        # Save skipped version if user chose to skip
        if dialog.skip_checkbox.isChecked():
            settings.setValue("skipped_version", new_version)

    def _on_update_check_failed(self, error: str):
        """Handle update check failure (silent, just log)."""
        import logging
        logging.getLogger(__name__).debug(f"Update check failed: {error}")
```

### Step 5: Add Required Dependency

Add `packaging` to your `pyproject.toml` dependencies:

```toml
dependencies = [
    "pyside6>=6.10.0",
    "pyserial>=3.5",
    "packaging>=24.0",
]
```

## Part 3: Alternative - Using a Dedicated Update Library

For more advanced features (automatic downloads, delta updates, code signing verification), consider these libraries:

### Option A: pyupdater (Recommended for PyInstaller apps)

```bash
pip install pyupdater
```

PyUpdater provides:
- Automatic binary patching (delta updates)
- Code signing support
- Multiple update channels (stable, beta)
- S3/GitHub/custom server support

### Option B: esky

A simpler alternative that works well with PyInstaller frozen apps.

## Summary

1. **Version your releases** using git tags (`v0.1.0`)
2. **Automate builds** with GitHub Actions on tag push
3. **Check for updates** using the GitHub Releases API
4. **Prompt users** with a non-intrusive dialog
5. **Respect user choice** with "skip this version" option
6. **Open browser** to download page (simplest approach)

For production use, consider adding:
- Code signing for your executables
- SHA256 checksum verification
- In-app download progress with automatic replacement
- Rollback capability if update fails
