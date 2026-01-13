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