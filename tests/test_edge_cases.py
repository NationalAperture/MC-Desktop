import logging
from types import SimpleNamespace

import pytest

from mc_desktop.communication import CommunicationManager
from mc_desktop.node_manager import NodeManager
from mc_desktop.ui.controllers import MacroRunner


class _FakeTransport:
    def __init__(self, response: str):
        self._response = response
        self.writes = []

    def write(self, payload: str) -> None:
        self.writes.append(payload)

    def read_line(self) -> str:
        return self._response


class _FakeMacroText:
    def __init__(self):
        self.lines = []

    def clear(self):
        self.lines = []

    def append(self, text: str):
        self.lines.append(text)


def test_node_manager_empty_list_defaults():
    manager = NodeManager()
    assert manager.list_nodes() == []
    assert manager.current_node_id is None
    assert manager.get_stage_values("missing") == ""


def test_check_status_handles_empty_response():
    manager = CommunicationManager(parent=object(), logger=logging.getLogger("test_comm"))
    manager.connection = SimpleNamespace(is_open=True)
    manager._transport = _FakeTransport(response="")

    assert manager.check_status() is None
    assert manager.in_motion is False


def test_macro_runner_logs_malformed_loop(caplog):
    window = SimpleNamespace(macro_text=_FakeMacroText(), set_macro_progress=lambda *_: None)
    runner = MacroRunner(window, logger=logging.getLogger("test_macro"))

    with caplog.at_level(logging.WARNING):
        bounds = runner._compute_loop_bounds(["loop 2", "1 mov 10"])
        count = runner._parse_loop_count("loop foo")

    assert bounds == {}
    assert count == 0
    assert "Loop(s) without matching 'end'" in caplog.text
    assert "Invalid loop count" in caplog.text
