import logging

import pytest

pytest.importorskip("pytest_benchmark")
pytest.importorskip("pytestqt")
PySide6 = pytest.importorskip("PySide6")

from mc_desktop.communication import CommunicationManager
from mc_desktop.ui.update_dialog import UpdateDialog


class _FakeTransport:
    def __init__(self, response: str = "0"):
        self._response = response
        self.writes = []

    def write(self, payload: str) -> None:
        self.writes.append(payload)

    def read_line(self) -> str:
        return self._response


def test_poll_latency_benchmark(benchmark):
    manager = CommunicationManager(parent=object(), logger=logging.getLogger("bench_poll"))
    manager.connection = object()
    manager._transport = _FakeTransport(response="1")

    benchmark(manager.poll)


def test_ui_progress_update_benchmark(benchmark, qapp):
    dialog = UpdateDialog(new_version="2.0.0", download_url="https://example.com", release_notes="")

    benchmark(dialog._on_progress, 1024, 4096)
