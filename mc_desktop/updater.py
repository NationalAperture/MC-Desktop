"""Auto-update checker using GitHub Releases API."""

import logging
import os
import sys
import stat
import tempfile
import subprocess
from pathlib import Path
from packaging import version
from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QUrl
import json

from mc_desktop.version import __version__

logger = logging.getLogger(__name__)

# Update this to your repository
GITHUB_REPO = "NationalAperture/MC-Desktop"
RELEASES_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def get_executable_path() -> Path:
    """Get the path to the current executable."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return Path(sys.executable)
    else:
        # Running as script (for development)
        return Path(__file__).parent.parent / "dist" / "NAI-Mover"


class UpdateChecker(QObject):
    """Checks GitHub for new releases."""

    update_available = Signal(str, str, str)  # new_version, download_url, release_notes
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
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)

        if reply.error() != QNetworkReply.NetworkError.NoError:
            # 404 means no releases exist yet - this is not an error
            if status_code == 404:
                logger.info("No releases found on GitHub (this is normal for new repositories)")
                self.no_update.emit()
                reply.deleteLater()
                return

            error_msg = f"{reply.errorString()} (HTTP {status_code})"
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
                html_url = data.get("html_url", "")
                download_url = None

                # Find platform-specific asset
                assets = data.get("assets", [])
                for asset in assets:
                    name = asset.get("name", "").lower()
                    asset_url = asset.get("browser_download_url", "")

                    if sys.platform == "win32":
                        # Match: NAI-Mover-windows.exe, NAI-Mover.exe, or anything with .exe
                        if name.endswith(".exe"):
                            download_url = asset_url
                            if "windows" in name:
                                break  # Prefer explicitly named windows build
                    elif sys.platform == "linux":
                        # Match: NAI-Mover-linux, NAI-Mover, or anything without .exe
                        if not name.endswith(".exe") and "NAI-Mover" in asset.get("name", ""):
                            download_url = asset_url
                            if "linux" in name:
                                break  # Prefer explicitly named linux build

                if not download_url:
                    logger.warning(f"No matching asset found for platform {sys.platform}, using release page")
                    download_url = html_url

                release_notes = data.get("body", "")
                logger.info(f"Update available: {latest_version}, download: {download_url}")
                self.update_available.emit(latest_version, download_url, release_notes)
            else:
                logger.info("No update available")
                self.no_update.emit()

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse update response: {e}")
            self.check_failed.emit(str(e))
        finally:
            reply.deleteLater()


class UpdateDownloader(QObject):
    """Downloads and installs updates from GitHub releases."""

    progress = Signal(int, int)  # bytes_received, bytes_total
    download_complete = Signal(str)  # path to downloaded file
    download_failed = Signal(str)  # error message
    install_complete = Signal()
    install_failed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = QNetworkAccessManager(self)
        self.reply = None
        self.download_path = None

    def download(self, url: str):
        """Start downloading the update."""
        logger.info(f"Starting download from: {url}")

        # Create temp file for download
        self.download_path = Path(tempfile.gettempdir()) / "NAI-Mover-update"
        if sys.platform == "win32":
            self.download_path = self.download_path.with_suffix(".exe")

        request = QNetworkRequest(QUrl(url))
        request.setHeader(
            QNetworkRequest.KnownHeaders.UserAgentHeader,
            f"NAI-Mover/{__version__}"
        )
        # Follow redirects (GitHub uses redirects for release assets)
        request.setAttribute(
            QNetworkRequest.Attribute.RedirectPolicyAttribute,
            QNetworkRequest.RedirectPolicy.NoLessSafeRedirectPolicy
        )

        self.reply = self.manager.get(request)
        self.reply.downloadProgress.connect(self._on_progress)
        self.reply.finished.connect(self._on_finished)

    def _on_progress(self, bytes_received: int, bytes_total: int):
        """Handle download progress updates."""
        self.progress.emit(bytes_received, bytes_total)

    def _on_finished(self):
        """Handle download completion."""
        if self.reply.error() != QNetworkReply.NetworkError.NoError:
            error_msg = self.reply.errorString()
            logger.error(f"Download failed: {error_msg}")
            self.download_failed.emit(error_msg)
            self.reply.deleteLater()
            return

        # Write the downloaded data to file
        try:
            data = self.reply.readAll().data()
            with open(self.download_path, 'wb') as f:
                f.write(data)

            logger.info(f"Download complete: {self.download_path}")
            self.download_complete.emit(str(self.download_path))

        except IOError as e:
            logger.error(f"Failed to save download: {e}")
            self.download_failed.emit(str(e))
        finally:
            self.reply.deleteLater()

    def install(self):
        """Install the downloaded update by replacing the current executable."""
        if not self.download_path or not self.download_path.exists():
            self.install_failed.emit("No download available to install")
            return

        current_exe = get_executable_path()
        logger.info(f"Installing update: {self.download_path} -> {current_exe}")

        try:
            if sys.platform == "win32":
                # Windows: Can't replace running executable, use a batch script
                self._install_windows(current_exe)
            else:
                # Linux/macOS: Can replace executable directly
                self._install_unix(current_exe)

        except Exception as e:
            logger.error(f"Installation failed: {e}")
            self.install_failed.emit(str(e))

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
            current_exe.chmod(current_exe.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

            # Remove backup
            if backup_path.exists():
                backup_path.unlink()

            logger.info("Update installed successfully")
            self.install_complete.emit()

            # Restart the application
            self._restart_app(current_exe)

        except Exception as e:
            # Restore backup on failure
            if backup_path.exists():
                backup_path.rename(current_exe)
            raise

    def _install_windows(self, current_exe: Path):
        """Install on Windows using a batch script that runs after app exits."""
        batch_path = Path(tempfile.gettempdir()) / "nai_mover_update.bat"

        batch_content = f'''@echo off
echo Waiting for application to close...
timeout /t 2 /nobreak >nul
echo Installing update...
move /y "{self.download_path}" "{current_exe}"
if errorlevel 1 (
    echo Update failed!
    pause
    exit /b 1
)
echo Update complete, restarting...
start "" "{current_exe}"
del "%~f0"
'''
        with open(batch_path, 'w') as f:
            f.write(batch_content)

        # Start the batch script and exit
        subprocess.Popen(
            ['cmd', '/c', str(batch_path)],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

        logger.info("Update batch script started, exiting application")
        self.install_complete.emit()

        # Exit the application so the batch script can replace it
        from PySide6.QtWidgets import QApplication
        QApplication.quit()

    def _restart_app(self, exe_path: Path):
        """Restart the application after update."""
        logger.info(f"Restarting application: {exe_path}")

        # Start new instance
        subprocess.Popen([str(exe_path)])

        # Exit current instance
        from PySide6.QtWidgets import QApplication
        QApplication.quit()