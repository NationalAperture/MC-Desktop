import json
import logging

import pytest

from mc_desktop.updater import UpdateChecker, UpdateDownloader

PySide6 = pytest.importorskip("PySide6")
from PySide6.QtCore import QByteArray
from PySide6.QtNetwork import QNetworkReply, QNetworkRequest


class _FakeReply:
    def __init__(self, payload: bytes, *, error=QNetworkReply.NetworkError.NoError, status_code=200, error_string=""):
        self._payload = payload
        self._error = error
        self._status_code = status_code
        self._error_string = error_string
        self.deleted = False

    def attribute(self, attr):
        if attr == QNetworkRequest.Attribute.HttpStatusCodeAttribute:
            return self._status_code
        return None

    def error(self):
        return self._error

    def errorString(self):
        return self._error_string

    def readAll(self):
        return QByteArray(self._payload)

    def deleteLater(self):
        self.deleted = True


def test_update_checker_emits_update_available(qtbot):
    checker = UpdateChecker()
    captured = {}

    def _capture(version, url, notes, size):
        captured["version"] = version
        captured["url"] = url
        captured["notes"] = notes
        captured["size"] = size

    checker.update_available.connect(_capture)

    response = {
        "tag_name": "v999.0.0",
        "html_url": "https://example.com/release",
        "assets": [{"name": "NAI-Mover-linux", "browser_download_url": "https://example.com/app", "size": 12}],
        "body": "Release notes",
    }
    reply = _FakeReply(json.dumps(response).encode())

    checker._on_response(reply)

    assert captured["version"] == "999.0.0"
    assert captured["url"]
    assert captured["notes"] == "Release notes"
    assert reply.deleted is True


def test_update_checker_handles_invalid_payload(qtbot):
    checker = UpdateChecker()
    errors = []
    checker.check_failed.connect(errors.append)

    reply = _FakeReply(b"not-json")
    checker._on_response(reply)

    assert errors


def test_update_downloader_writes_download(tmp_path, qtbot, caplog):
    downloader = UpdateDownloader()
    downloader.download_path = tmp_path / "update.bin"
    downloader.reply = _FakeReply(b"payload")

    with caplog.at_level(logging.INFO):
        downloader._on_finished()

    assert downloader.download_path.read_bytes() == b"payload"


def test_update_downloader_emits_failure(tmp_path, qtbot):
    downloader = UpdateDownloader()
    downloader.download_path = tmp_path / "update.bin"
    downloader.reply = _FakeReply(
        b"",
        error=QNetworkReply.NetworkError.ContentNotFoundError,
        status_code=404,
        error_string="Not found",
    )
    errors = []
    downloader.download_failed.connect(errors.append)

    downloader._on_finished()

    assert errors
