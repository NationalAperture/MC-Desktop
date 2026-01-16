import types

from mc_desktop.ui.controllers import MacroRunner


class FakeTextEdit:
    def __init__(self) -> None:
        self._lines: list[str] = []

    def toPlainText(self) -> str:
        return "\n".join(self._lines)

    def setPlainText(self, text: str) -> None:
        self._lines = text.splitlines()

    def clear(self) -> None:
        self._lines = []

    def append(self, value: str) -> None:
        self._lines.append(value)


class FakeLabel:
    def __init__(self) -> None:
        self.text_value = ""

    def setText(self, value: str) -> None:
        self.text_value = value


class FakeButton:
    def __init__(self, checked: bool = False) -> None:
        self._checked = checked

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, value: bool) -> None:
        self._checked = value


class FakeLineEdit:
    def __init__(self, value: str = "") -> None:
        self._value = value

    def text(self) -> str:
        return self._value

    def setText(self, value: str) -> None:
        self._value = value


class FakeSerial:
    def __init__(self) -> None:
        self.sent: list[tuple[tuple[str, ...], dict]] = []

    def transmit_queue(self, *args, **kwargs) -> None:
        self.sent.append((args, kwargs))


class FakeWindow:
    def __init__(self) -> None:
        self.serial = FakeSerial()
        self.macro_text = FakeTextEdit()
        self.sent_log: list[tuple[str, ...]] = []

        self.ui = types.SimpleNamespace(
            run_once_rb=FakeButton(checked=True),
            run_variable_rb=FakeButton(checked=False),
            run_forever_rb=FakeButton(checked=False),
            run_count=FakeLabel(),
            variable_amount_value=FakeLineEdit("1"),
        )

    def log_sent_messages(self, message: tuple[str, ...]) -> None:
        self.sent_log.append(message)

    def set_macro_pause_state(self, *_args, **_kwargs) -> None:
        return None

    def set_macro_progress(self, *_args, **_kwargs) -> None:
        return None


def complete_macro(runner: MacroRunner) -> None:
    runner.on_command_complete(types.SimpleNamespace(context="macro"), None)


def test_macro_runner_waits_for_completion():
    window = FakeWindow()
    window.macro_text.setPlainText("0 mvr 10\n0 mvr 20")
    runner = MacroRunner(window)

    runner.run_macro()

    assert [args for args, _ in window.serial.sent] == [("0", "mvr", "10")]

    complete_macro(runner)
    assert [args for args, _ in window.serial.sent] == [("0", "mvr", "10"), ("0", "mvr", "20")]


def test_macro_runner_handles_loop_iterations():
    window = FakeWindow()
    window.macro_text.setPlainText("loop 2\n0 mvr 10\nend\n0 mvr 99")
    runner = MacroRunner(window)

    runner.run_macro()
    assert [args for args, _ in window.serial.sent] == [("0", "mvr", "10")]

    complete_macro(runner)
    assert [args for args, _ in window.serial.sent] == [("0", "mvr", "10"), ("0", "mvr", "10")]

    complete_macro(runner)
    assert [args for args, _ in window.serial.sent] == [
        ("0", "mvr", "10"),
        ("0", "mvr", "10"),
        ("0", "mvr", "99"),
    ]


def test_macro_runner_wait_command_relayed_after_completion():
    window = FakeWindow()
    window.macro_text.setPlainText("wait 5\n0 mvr 1")
    runner = MacroRunner(window)

    runner.run_macro()
    assert [args for args, _ in window.serial.sent] == [("wait", "5")]

    complete_macro(runner)
    assert [args for args, _ in window.serial.sent] == [("wait", "5"), ("0", "mvr", "1")]
