import logging
from types import SimpleNamespace

from mc_desktop.node_manager import NodeManager
from mc_desktop.ui.controllers import CommandDispatcher, MacroRunner, NodeSettingsController


def test_macro_runner_parse_macro_text_filters_empty_lines():
    text = "\nmove 1\n   \nwait 5\n"
    steps = MacroRunner.parse_macro_text(text)
    assert steps == ["move 1", "wait 5"]


def test_command_dispatcher_executes_registered_command(monkeypatch):
    captured = []

    dispatcher = CommandDispatcher(
        parent=object(),
        send_command=captured.append,
        prompter=lambda parent, title, prompt: ("10", True),
        logger=logging.getLogger("test_dispatcher"),
    )

    assert dispatcher.execute("move_absolute") is True
    assert captured == [("mva", "10")]


def test_command_dispatcher_handles_unknown_key(caplog):
    dispatcher = CommandDispatcher(parent=object(), send_command=lambda _: None)
    with caplog.at_level(logging.ERROR):
        assert dispatcher.execute("unknown") is False
    assert "Unknown command key" in caplog.text


def test_node_settings_snapshot_helpers_use_node_manager():
    window = SimpleNamespace(node_manager=NodeManager())
    window.node_manager.add_node("1")
    controller = NodeSettingsController(window)

    assert controller.snapshot_stage("1") == "1,1,N/A,N/A,N/A"
    assert controller.snapshot_pid("1") == "N/A,N/A,N/A,N/A,N/A"
    assert controller.snapshot_motion("1") == "N/A,N/A,N/A,N/A"
    assert controller.snapshot_advanced("1") == "N/A,N/A,N/A"
