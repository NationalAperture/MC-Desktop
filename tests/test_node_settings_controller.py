import logging
from types import SimpleNamespace

from mc_desktop.node_manager import NodeManager
from mc_desktop.ui.controllers import NodeSettingsController


class _FakeLabel:
    def __init__(self):
        self.text_value = ""
        self.stylesheet = ""

    def setText(self, text: str) -> None:
        self.text_value = text

    def setStyleSheet(self, style: str) -> None:
        self.stylesheet = style


class _FakeLineEdit:
    def __init__(self, value: str = ""):
        self._value = value
        self.stylesheet = ""

    def text(self) -> str:
        return self._value

    def setText(self, value: str) -> None:
        self._value = value

    def setStyleSheet(self, style: str) -> None:
        self.stylesheet = style


class _FakeCombo:
    def __init__(self, items):
        self._items = list(items)
        self._index = 0

    def count(self) -> int:
        return len(self._items)

    def itemText(self, index: int) -> str:
        return self._items[index]

    def setCurrentIndex(self, index: int) -> None:
        self._index = index

    def currentIndex(self) -> int:
        return self._index


class _FakeComboBox:
    def __init__(self, items, index: int = 0):
        self._items = list(items)
        self._index = index

    def currentText(self) -> str:
        return self._items[self._index]

    def currentIndex(self) -> int:
        return self._index


class _FakeMotorStat:
    def __init__(self):
        self.jog_calls = 0

    def set_jog(self):
        self.jog_calls += 1


class _FakeWindow:
    def __init__(self):
        self.node_manager = NodeManager()
        self.node_manager.add_node("1")
        self.node_manager.current_node_id = "1"
        self.callbacks = []
        self.sent_commands = []
        self.comboBox = _FakeComboBox(["1"])
        self.motor_stats = [_FakeMotorStat()]

        self.ui = SimpleNamespace(
            stage_type_combo=_FakeCombo(["Linear", "Rotary"]),
            travel_unit_combo=_FakeCombo(["encoder_counts", "mm"]),
            gh_value_label=_FakeLabel(),
            tpi_value_label=_FakeLabel(),
            cpr_value_label=_FakeLabel(),
            kp_value_label=_FakeLabel(),
            ki_value_label=_FakeLabel(),
            kd_value_label=_FakeLabel(),
            int_lmt_value_label=_FakeLabel(),
            sample_rate_value_label=_FakeLabel(),
            accel_value_label=_FakeLabel(),
            vel_value_label=_FakeLabel(),
            decel_value_label=_FakeLabel(),
            err_value_label=_FakeLabel(),
            jog_label=_FakeLabel(),
            hs_jog_label=_FakeLabel(),
            lower_limit_value=_FakeLabel(),
            upper_limit_value=_FakeLabel(),
            pos_tolerance_value=_FakeLabel(),
            GH_input=_FakeLineEdit("10"),
            TPI_input=_FakeLineEdit("20"),
            CPR_input=_FakeLineEdit("30"),
            kp_input=_FakeLineEdit("1.5"),
            ki_input=_FakeLineEdit("2.5"),
            kd_input=_FakeLineEdit("3.5"),
            int_lmt_input=_FakeLineEdit("4"),
            sample_rate_input=_FakeLineEdit("5"),
            accel_input=_FakeLineEdit("6"),
            vel_input=_FakeLineEdit("7"),
            decel_input=_FakeLineEdit("8"),
            err_input=_FakeLineEdit("9"),
            jog_input=_FakeLineEdit("11"),
            hs_jog_input=_FakeLineEdit("12"),
            lower_limit_input=_FakeLineEdit("13"),
            upper_limit_input=_FakeLineEdit("14"),
            pos_tolerance_input=_FakeLineEdit("15"),
        )

    def send_command(self, cmd, **_):
        self.sent_commands.append(cmd)


def test_update_values_populates_ui_and_nodes():
    window = _FakeWindow()
    controller = NodeSettingsController(window, logger=logging.getLogger("test_settings"))

    controller.update_stage_values("Linear,encoder_counts,10,20,30")
    controller.update_pid_values("1,2,3,4,5")
    controller.update_motion_values("6,7,8,9")
    controller.update_advanced_values("100,200")

    stage = window.node_manager.get_stage("1")
    assert stage["GH"] == "10"
    assert stage["TPI"] == "20"
    assert stage["CPR"] == "30"
    assert window.ui.gh_value_label.text_value == "GH: 10"
    assert window.ui.tpi_value_label.text_value == "TPI: 20"
    assert window.ui.cpr_value_label.text_value == "CPR: 30"

    pid = window.node_manager.get_pid("1")
    assert pid["KP"] == "1"
    assert pid["KI"] == "2"
    assert pid["KD"] == "3"
    assert window.ui.kp_value_label.text_value == "KP: 1"
    assert window.ui.ki_value_label.text_value == "KI: 2"
    assert window.ui.kd_value_label.text_value == "KD: 3"

    motion = window.node_manager.get_motion("1")
    assert motion["Accel"] == "6"
    assert motion["Velo"] == "7"
    assert motion["Decel"] == "8"
    assert motion["Error"] == "9"
    assert window.ui.accel_value_label.text_value == "Acceleration: 6"

    advanced = window.node_manager.get_advanced("1")
    assert advanced["Lower"] == "100"
    assert advanced["Upper"] == "200"
    assert window.ui.lower_limit_value.text_value == "Lower Limit: 100"
    assert window.ui.upper_limit_value.text_value == "Upper Limit: 200"


def test_setters_send_commands_and_validate_inputs():
    window = _FakeWindow()
    controller = NodeSettingsController(window, logger=logging.getLogger("test_settings"))

    controller.set_kp()
    controller.set_motion_accel()
    controller.set_lower_limit()
    controller.set_jog()
    controller.set_hs_jog()

    assert ("kp 1.5",) in window.sent_commands
    assert ("acc 6",) in window.sent_commands
    assert ("sll 13",) in window.sent_commands
    assert window.ui.kp_value_label.text_value == "KP: 1.5"
    assert window.ui.accel_value_label.text_value == "Acceleration: 6"
    assert window.ui.lower_limit_value.text_value == "Lower Limit: 13"
    assert window.motor_stats[0].jog_calls == 2

    window.ui.vel_input.setText("not-an-int")
    controller.set_motion_vel()
    assert window.ui.vel_input.stylesheet
