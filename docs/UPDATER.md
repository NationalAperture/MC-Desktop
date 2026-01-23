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

      - name: Rename artifacts with platform suffix
        run: |
          mv ./windows/NAI-Mover.exe ./windows/NAI-Mover-windows.exe
          mv ./linux/NAI-Mover ./linux/NAI-Mover-linux

      - name: Create Release
        uses: softprops/action-gh-release@v2
        with:
          files: |
            ./windows/NAI-Mover-windows.exe
            ./linux/NAI-Mover-linux
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

---

## Part 4: Auto-Restart After Update

The current implementation in `mc_desktop/updater.py` includes download, install, and restart functionality. This section documents known issues and solutions for reliable auto-restart behavior.

### Current Implementation Overview

The `UpdateDownloader` class handles:
1. Downloading the new executable to a temp directory
2. Replacing the current executable
3. Restarting the application

**Windows** (`_install_windows`): Uses a batch script that waits for the app to close, replaces the executable, and restarts.

**Linux** (`_install_unix`): Directly replaces the executable and spawns a new process.

### Known Issues and Root Causes

#### Issue 1: Linux - Child Process Termination

**Problem**: On Linux, the restart uses `subprocess.Popen([str(exe_path)])` followed by `QApplication.quit()`. The new process is spawned as a **child** of the current process. When the parent process terminates, the child may:
- Receive SIGHUP signal and terminate
- Become orphaned with unexpected behavior
- Have its stdout/stderr closed unexpectedly

**Root Cause**: `subprocess.Popen()` by default creates a child process that inherits the parent's process group.

**Solution**: Detach the new process from the parent using `start_new_session=True`:

```python
def _restart_app(self, exe_path: Path):
    """Restart the application after update (Linux/macOS)."""
    logger.info(f"Restarting application: {exe_path}")

    # Detach completely from parent process
    subprocess.Popen(
        [str(exe_path)],
        start_new_session=True,  # Creates new process group
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Exit current instance
    from PySide6.QtWidgets import QApplication
    QApplication.quit()
```

**Alternative - Using os.execv()**: For in-place process replacement (same PID):

```python
import os

def _restart_app_exec(self, exe_path: Path):
    """Replace current process with new executable."""
    os.execv(str(exe_path), [str(exe_path)])
    # Note: Code after execv never runs - process is replaced
```

This approach is cleaner but doesn't work on Windows for frozen executables.

#### Issue 2: Windows - Visible Console Window

**Problem**: The batch script uses `CREATE_NEW_CONSOLE` which opens a visible command prompt window during the update.

**Root Cause**: `subprocess.CREATE_NEW_CONSOLE` is used to ensure the batch script runs independently but it creates a visible window.

**Solution**: Use `DETACHED_PROCESS` and `CREATE_NO_WINDOW` flags:

```python
def _install_windows(self, current_exe: Path):
    """Install on Windows using a batch script that runs after app exits."""
    batch_path = Path(tempfile.gettempdir()) / "nai_mover_update.bat"

    batch_content = f'''@echo off
timeout /t 3 /nobreak >nul
move /y "{self.download_path}" "{current_exe}"
if errorlevel 1 exit /b 1
start "" "{current_exe}"
del "%~f0"
'''
    with open(batch_path, 'w') as f:
        f.write(batch_content)

    # Run hidden - no console window
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE

    subprocess.Popen(
        ['cmd', '/c', str(batch_path)],
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
        startupinfo=startupinfo,
    )

    logger.info("Update batch script started, exiting application")
    self.install_complete.emit()

    from PySide6.QtWidgets import QApplication
    QApplication.quit()
```

#### Issue 3: Windows - Insufficient Timeout

**Problem**: The 2-second `timeout /t 2` may not be enough for the application to fully exit on slower systems or when Qt cleanup takes longer.

**Solution**: Increase timeout and add process wait logic:

```batch
@echo off
set EXE_PATH=%1
set NEW_PATH=%2

:wait_loop
tasklist /fi "imagename eq NAI-Mover.exe" 2>nul | find /i "NAI-Mover.exe" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait_loop
)

timeout /t 1 /nobreak >nul
move /y "%NEW_PATH%" "%EXE_PATH%"
if errorlevel 1 exit /b 1
start "" "%EXE_PATH%"
del "%~f0"
```

#### Issue 4: Qt Event Loop Not Fully Processed

**Problem**: Calling `QApplication.quit()` immediately after `subprocess.Popen()` may not give Qt time to process pending events.

**Solution**: Use `QTimer.singleShot()` to delay the quit:

```python
def _restart_app(self, exe_path: Path):
    """Restart the application after update."""
    logger.info(f"Restarting application: {exe_path}")

    # Start new instance (detached)
    subprocess.Popen(
        [str(exe_path)],
        start_new_session=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Delay quit to allow Qt event processing
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    QTimer.singleShot(100, QApplication.quit)
```

### Recommended Implementation

Here's a complete, robust implementation addressing all issues:

```python
import os
import sys
import stat
import tempfile
import subprocess
from pathlib import Path

class UpdateDownloader(QObject):
    # ... existing signals and __init__ ...

    def _install_unix(self, current_exe: Path):
        """Install on Linux/macOS by replacing the executable."""
        backup_path = current_exe.with_suffix(".backup")

        # Backup current executable
        if current_exe.exists():
            current_exe.rename(backup_path)

        try:
            # Move new executable into place
            self.download_path.rename(current_exe)

            # Make it executable
            current_exe.chmod(
                current_exe.stat().st_mode |
                stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            )

            # Remove backup
            if backup_path.exists():
                backup_path.unlink()

            logger.info("Update installed successfully")
            self.install_complete.emit()

            # Restart with proper detachment
            self._restart_app_detached(current_exe)

        except Exception as e:
            # Restore backup on failure
            if backup_path.exists():
                backup_path.rename(current_exe)
            raise

    def _restart_app_detached(self, exe_path: Path):
        """Restart application fully detached from parent process."""
        logger.info(f"Restarting application: {exe_path}")

        # Spawn completely independent process
        subprocess.Popen(
            [str(exe_path)],
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )

        # Give Qt time to process before quitting
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication
        QTimer.singleShot(100, QApplication.quit)

    def _install_windows(self, current_exe: Path):
        """Install on Windows using a hidden batch script."""
        batch_path = Path(tempfile.gettempdir()) / "nai_mover_update.bat"

        # Batch script waits for app to close, then replaces and restarts
        batch_content = f'''@echo off
:wait_loop
tasklist /fi "imagename eq {current_exe.name}" 2>nul | find /i "{current_exe.name}" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait_loop
)
timeout /t 1 /nobreak >nul
move /y "{self.download_path}" "{current_exe}"
if errorlevel 1 exit /b 1
start "" "{current_exe}"
del "%~f0"
'''
        with open(batch_path, 'w') as f:
            f.write(batch_content)

        # Run batch script hidden
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        subprocess.Popen(
            ['cmd', '/c', str(batch_path)],
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
            startupinfo=startupinfo,
            close_fds=True,
        )

        logger.info("Update batch script started, exiting application")
        self.install_complete.emit()

        # Quit after brief delay
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication
        QTimer.singleShot(100, QApplication.quit)
```

### Testing Auto-Restart

To test the restart functionality during development:

1. **Create a test script** that simulates the restart:
   ```python
   # test_restart.py
   import subprocess
   import sys

   print("Starting new process...")
   subprocess.Popen(
       [sys.executable, "-c", "import time; print('New process started'); time.sleep(5)"],
       start_new_session=True,
       stdin=subprocess.DEVNULL,
       stdout=None,  # Keep stdout for testing
       stderr=subprocess.DEVNULL,
   )
   print("Parent exiting...")
   sys.exit(0)
   ```

2. **Test Windows batch script** manually:
   - Create the batch file
   - Run it from command prompt
   - Verify it waits, replaces, and restarts correctly

3. **Log file verification**: Check `logs/info.log` for:
   - "Update installed successfully"
   - "Restarting application: /path/to/exe"
   - Any error messages

### Troubleshooting

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| App closes but doesn't restart (Linux) | Child process killed with parent | Use `start_new_session=True` |
| App closes but doesn't restart (Windows) | Batch script fails silently | Check temp folder for batch file, run manually |
| Console window flashes (Windows) | Using `CREATE_NEW_CONSOLE` | Use `CREATE_NO_WINDOW` and `STARTUPINFO` |
| New app starts before old closes | Race condition | Increase timeout or use process wait loop |
| Update fails with permission error | File locked or permissions | Run as admin (Windows) or check file ownership (Linux) |

### Platform-Specific Notes

**Linux**:
- AppImage: May need special handling - the AppImage runtime extracts to temp before running
- Snap/Flatpak: Updates are managed by the package manager, not the app

**Windows**:
- UAC: If installed in Program Files, may need elevation for replacement
- Antivirus: Some AV software may block self-modifying executables

**macOS**:
- App bundles: Replace the entire `.app` bundle, not just the binary
- Code signing: Replacing binary invalidates signature; must re-sign or use unsigned
