from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Optional, Sequence, Tuple

try:  # pragma: no cover - allow tests without PySide6
    from PySide6.QtWidgets import QFileDialog, QInputDialog
except ModuleNotFoundError:  # pragma: no cover
    QFileDialog = None  # type: ignore[assignment]
    QInputDialog = None  # type: ignore[assignment]


@dataclass(frozen=True)
class PromptConfig:
    command: str
    title: str
    prompt: str


class CommandDispatcher:
    """Declarative registry for prompt-based motion commands."""

    _PROMPTS: Dict[str, PromptConfig] = {
        "set_home": PromptConfig("hom", "Set Home Position", "Enter Home Position"),
        "move_absolute": PromptConfig("mva", "Move Absolute", "Where would you like to move?"),
        "load_absolute": PromptConfig("lpa", "Load Absolute", "Where would you like to load?"),
        "move_relative": PromptConfig("mvr", "Move Relative", "Where would you like to move?"),
        "load_relative": PromptConfig("lpr", "Load Relative", "Where would you like to load?"),
    }

    def __init__(
        self,
        parent,
        send_command: Callable[[Tuple[str, ...]], None],
        prompter: Optional[Callable[[object, str, str], Tuple[str, bool]]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._parent = parent
        self._send_command = send_command
        if prompter is not None:
            self._prompt = prompter
        elif QInputDialog is not None:
            self._prompt = QInputDialog.getText
        else:  # pragma: no cover - should not happen in production
            raise RuntimeError("PySide6 is required to prompt for commands.")
        self._logger = logger or logging.getLogger(__name__)

    def execute(self, key: str) -> bool:
        config = self._PROMPTS.get(key)
        if not config:
            self._logger.error("Unknown command key requested: %s", key)
            return False

        value, ok = self._prompt(self._parent, config.title, config.prompt)
        if not ok or not value:
            return False

        self._send_command((config.command, value))
        return True


@dataclass
class LoopFrame:
    start_index: int
    end_index: int
    remaining: int


class MacroRunner:
    """Encapsulates macro state management and execution helpers."""

    def __init__(self, window, logger: Optional[logging.Logger] = None) -> None:
        self.window = window
        self.logger = logger or logging.getLogger(__name__)
        self.macro_list: Optional[Sequence[str]] = None
        self.macro_list_copy: Optional[Sequence[str]] = None
        self.number_of_runs: int = 1
        self._raw_steps: list[str] = []
        self._loop_bounds: Dict[int, int] = {}
        self._loop_stack: list[LoopFrame] = []
        self._current_index: int = 0
        self._awaiting_completion: bool = False
        self._runs_completed: int = 0
        self._total_runs_requested: Optional[int] = None
        self._active: bool = False

    @staticmethod
    def parse_macro_text(text: str) -> Sequence[str]:
        return [line.strip() for line in text.splitlines() if line.strip()]

    def load_macro(self) -> None:
        if QFileDialog is None:  # pragma: no cover - GUI-only
            raise RuntimeError("PySide6 is required to display file dialogs.")

        file_path, _ = QFileDialog.getOpenFileName(self.window, "Open File", "macros/", "Text Files (*.txt)")
        content = self.window.macro_text.toPlainText()
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as fh:
                    content += fh.read()
            except OSError as exc:
                self.logger.error("Failed to load macro file %s: %s", file_path, exc)
        self.window.macro_text.setPlainText(content)

    def save_macro(self) -> None:
        txt = self.window.macro_text.toPlainText()
        file_path, _ = QFileDialog.getSaveFileName(
            self.window, "Save Macro", "/macros/", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            with open(f"{file_path}.txt", "w", encoding="utf-8") as file:
                file.write(txt)

    def get_macro_text(self) -> Optional[Sequence[str]]:
        steps = self.parse_macro_text(self.window.macro_text.toPlainText())
        return steps if steps else None

    def step_through_macro(self) -> None:
        macro_steps = self.get_macro_text()
        if not macro_steps:
            return
        command = macro_steps[0].split()
        params = tuple(command)
        self.window.log_sent_messages(params)
        self.window.serial.transmit_queue(*params)
        self.repopulate_macro(macro_steps[1:])

    def run_macro(self) -> None:
        steps = self.get_macro_text()
        if not steps:
            return

        self._active = True
        self._runs_completed = 0
        self._prepare_run_state(steps)

        ui = self.window.ui
        if ui.run_variable_rb.isChecked():
            self._total_runs_requested = self.number_of_runs
            ui.run_count.setText(f"Run Count: 1/{self.number_of_runs}")
        else:
            self._total_runs_requested = None

        self.manage_macro()

    def set_number_of_runs(self, *_: object, **__: object) -> None:
        ui = self.window.ui
        if ui.run_once_rb.isChecked():
            self.number_of_runs = 1
        elif ui.run_variable_rb.isChecked():
            try:
                self.number_of_runs = int(ui.variable_amount_value.text())
                ui.run_count.setText(f"Run Count: 0/{self.number_of_runs}")
            except ValueError:
                self.logger.warning("Macro run count must be an integer. Received: %s", ui.variable_amount_value.text())

    def manage_macro(self, *_, **__) -> None:
        if not self._active:
            return
        if self._awaiting_completion:
            return

        next_command = self._next_command()
        if next_command is None:
            self._handle_run_complete()
            return

        self._dispatch_command(next_command)

    def on_command_complete(self, command: object, status: object) -> None:
        if getattr(command, "context", None) != "macro":
            return
        if not self._active:
            return

        self._awaiting_completion = False
        self.manage_macro()

    def repopulate_macro(self, macro_list: Iterable[str]) -> None:
        self.macro_list = list(macro_list)
        self.window.macro_text.clear()
        for cmd in self.macro_list:
            self.window.macro_text.append(cmd)

    def _prepare_run_state(self, steps: Sequence[str]) -> None:
        self.macro_list = list(steps)
        self.macro_list_copy = list(steps)
        self._raw_steps = list(steps)
        self._loop_bounds = self._compute_loop_bounds(self._raw_steps)
        self._loop_stack = []
        self._current_index = 0
        self._awaiting_completion = False
        self.repopulate_macro(self._raw_steps)

    def _compute_loop_bounds(self, steps: Sequence[str]) -> Dict[int, int]:
        bounds: Dict[int, int] = {}
        stack: list[int] = []
        for idx, raw in enumerate(steps):
            token = raw.strip().lower()
            if token.startswith("loop"):
                stack.append(idx)
            elif token == "end":
                if not stack:
                    self.logger.warning("Encountered 'end' without matching 'loop' at index %s", idx)
                    continue
                start_idx = stack.pop()
                bounds[start_idx] = idx
        if stack:
            self.logger.warning("Loop(s) without matching 'end': %s", stack)
        return bounds

    def _next_command(self) -> Optional[str]:
        steps = self._raw_steps
        while self._current_index < len(steps):
            raw = steps[self._current_index]
            token = raw.strip().lower()

            if token.startswith("loop"):
                count = self._parse_loop_count(raw)
                end_idx = self._loop_bounds.get(self._current_index)
                if end_idx is None:
                    self.logger.warning("No matching 'end' for loop starting at index %s", self._current_index)
                    self._current_index += 1
                    continue
                if count <= 0:
                    self.logger.warning("Ignoring non-positive loop count '%s'", raw)
                    self._current_index = end_idx + 1
                    continue
                frame = LoopFrame(start_index=self._current_index + 1, end_index=end_idx, remaining=count)
                self._loop_stack.append(frame)
                self._current_index += 1
                continue

            if token == "end":
                if not self._loop_stack:
                    self.logger.warning("Encountered 'end' without active loop at index %s", self._current_index)
                    self._current_index += 1
                    continue
                frame = self._loop_stack[-1]
                frame.remaining -= 1
                if frame.remaining > 0:
                    self._current_index = frame.start_index
                else:
                    self._loop_stack.pop()
                    self._current_index = frame.end_index + 1
                continue

            self._current_index += 1
            self._update_macro_display()
            return raw

        return None

    def _dispatch_command(self, command: str) -> None:
        parts = command.split()
        if not parts:
            return

        self._awaiting_completion = True
        params: Tuple[str, ...]
        if len(parts) >= 3:
            node_id, cmd = parts[0], parts[1]
            param = " ".join(parts[2:]) if len(parts) > 3 else parts[2]
            params = (node_id, cmd, param)
            self.window.log_sent_messages(params)
            self.window.serial.transmit_queue(
                node_id,
                cmd,
                param,
                await_completion=True,
                context="macro",
            )
        elif len(parts) == 2:
            node_id, cmd = parts
            params = (node_id, cmd)
            self.window.log_sent_messages(params)
            self.window.serial.transmit_queue(
                node_id,
                cmd,
                await_completion=True,
                context="macro",
            )
        else:
            self.logger.warning("Macro command '%s' is incomplete and will be skipped.", command)
            self._awaiting_completion = False
            self.manage_macro()

    def _handle_run_complete(self) -> None:
        ui = self.window.ui
        if ui.run_forever_rb.isChecked():
            self._prepare_run_state(self.macro_list_copy or [])
            self.manage_macro()
            return

        if ui.run_variable_rb.isChecked():
            self._runs_completed += 1
            total = self._total_runs_requested or 0
            ui.run_count.setText(f"Run Count: {self._runs_completed}/{total}")
            if self._runs_completed >= total:
                self._active = False
                return
            self._prepare_run_state(self.macro_list_copy or [])
            next_run = min(self._runs_completed + 1, total)
            ui.run_count.setText(f"Run Count: {next_run}/{total}")
            self.manage_macro()
            return

        self._active = False

    def _parse_loop_count(self, raw: str) -> int:
        parts = raw.split()
        if len(parts) < 2:
            self.logger.warning("Loop command missing count: %s", raw)
            return 0
        try:
            return int(parts[1])
        except ValueError:
            self.logger.warning("Invalid loop count '%s'", parts[1])
            return 0

    def _update_macro_display(self) -> None:
        remaining = self._raw_steps[self._current_index :]
        self.repopulate_macro(remaining)


class NodeSettingsController:
    """Encapsulates the UI-heavy node settings coordination logic."""

    def __init__(self, window, logger: Optional[logging.Logger] = None) -> None:
        self.window = window
        self.logger = logger or logging.getLogger(__name__)

    @staticmethod
    def format_stage_values(stage) -> str:
        return ",".join(str(value) for value in (stage.stage, stage.travel, stage.gh, stage.tpi, stage.cpr))

    def snapshot_stage(self, node_id: str) -> str:
        return self.window.node_manager.get_stage_values(node_id)

    def snapshot_pid(self, node_id: str) -> str:
        return self.window.node_manager.get_pid_values(node_id)

    def snapshot_motion(self, node_id: str) -> str:
        return self.window.node_manager.get_motion_values(node_id)

    def snapshot_advanced(self, node_id: str) -> str:
        return self.window.node_manager.get_advanced_values(node_id)

    def refresh_stage_values(self) -> None:
        self.window.callbacks.append(self.update_stage_values)
        self.window.send_command(("stg",), callback=True)

    def update_stage_values(self, *args, **__) -> None:
        node_manager = self.window.node_manager
        node_id = node_manager.current_node_id
        node = node_manager.get_stage(node_id)
        stage_type, travel_unt, gh, tpi, cpr = "Linear", "encoder_counts", 0, 0, 0
        try:
            values = args[0].split(",")
            values = [v.strip() for v in values if v.strip()]
            stage_type, travel_unt, gh, tpi, cpr = values
        except ValueError as ve:
            self.logger.error("ValueError in update_stage_values: %s. Args: %s", ve, args)

        ui = self.window.ui
        for index in range(ui.stage_type_combo.count()):
            if stage_type == ui.stage_type_combo.itemText(index):
                ui.stage_type_combo.setCurrentIndex(index)
                node.update({"Stage": index})

        for index in range(ui.travel_unit_combo.count()):
            if travel_unt == ui.travel_unit_combo.itemText(index):
                ui.travel_unit_combo.setCurrentIndex(index)
                node.update({"Travel": index})

        ui.gh_value_label.setText(f"GH: {gh}")
        node.update({"GH": gh})
        ui.tpi_value_label.setText(f"TPI: {tpi}")
        node.update({"TPI": tpi})
        ui.cpr_value_label.setText(f"CPR: {cpr}")
        node.update({"CPR": cpr})

    def update_unit_travel(self, *args, **__) -> None:
        node_manager = self.window.node_manager
        node_id = node_manager.current_node_id
        node = node_manager.get_stage(node_id)
        unit_travel = args[0]
        ui = self.window.ui
        for index in range(ui.travel_unit_combo.count()):
            if unit_travel == ui.travel_unit_combo.itemText(index):
                ui.travel_unit_combo.setCurrentIndex(index)
                node.update({"Travel": index})

    def set_stage_type(self) -> None:
        index = self.window.ui.stage_type_combo.currentIndex() + 1
        self.window.send_command((f"sst {index}",))
        node_manager = self.window.node_manager
        node_id = node_manager.current_node_id
        node = node_manager.get_stage(node_id)
        node.update({"Stage": f"{index}"})

    def set_unit_travel(self) -> None:
        index = self.window.ui.travel_unit_combo.currentIndex() + 1
        self.window.send_command((f"sut {index}",))
        node_manager = self.window.node_manager
        node_id = node_manager.current_node_id
        node = node_manager.get_stage(node_id)
        node.update({"Travel": f"{index}"})

    def set_stage_gh(self) -> None:
        try:
            gh = int(self.window.ui.GH_input.text())
            self.window.send_command((f"ghr {gh}",))
            self.window.ui.gh_value_label.setText(f"GH: {gh}")
            node = self.window.node_manager.get_stage(self.window.node_manager.current_node_id)
            node.update({"GH": gh})
        except ValueError:
            self.logger.error("Value must be int. Value received: %s", self.window.ui.GH_input.text())

    def set_stage_tpi(self) -> None:
        try:
            tpi = int(self.window.ui.TPI_input.text())
            self.window.send_command((f"tpi {tpi}",))
            self.window.ui.tpi_value_label.setText(f"TPI: {tpi}")
            node = self.window.node_manager.get_stage(self.window.node_manager.current_node_id)
            node.update({"TPI": tpi})
        except ValueError:
            self.logger.error("Value must be int. Value received: %s", self.window.ui.TPI_input.text())

    def set_stage_cpr(self) -> None:
        try:
            cpr = int(self.window.ui.CPR_input.text())
            self.window.send_command((f"cpr {cpr}",))
            self.window.ui.cpr_value_label.setText(f"CPR: {cpr}")
            node = self.window.node_manager.get_stage(self.window.node_manager.current_node_id)
            node.update({"CPR": cpr})
        except ValueError:
            self.logger.error("Value must be int. Value received: %s", self.window.ui.CPR_input.text())

    def refresh_pid_values(self) -> None:
        self.window.callbacks.append(self.update_pid_values)
        self.window.send_command(("pid",), callback=True)

    def update_pid_values(self, *args, **__) -> None:
        node_manager = self.window.node_manager
        node_id = node_manager.current_node_id
        node = node_manager.get_pid(node_id)
        kp, ki, kd, int_lmt, sample = 0, 0, 0, 0, 0
        try:
            values = args[0].split(",")
            values = [v.strip() for v in values if v.strip()]
            kp, ki, kd, int_lmt, sample = values
        except ValueError as ve:
            self.logger.error("ValueError in update_pid_values: %s. Args: %s", ve, args)

        ui = self.window.ui
        ui.kp_value_label.setText(f"KP: {kp}")
        node.update({"KP": kp})
        ui.ki_value_label.setText(f"KI: {ki}")
        node.update({"KI": ki})
        ui.kd_value_label.setText(f"KD: {kd}")
        node.update({"KD": kd})
        ui.int_lmt_value_label.setText(f"Integrator Lmt: {int_lmt}")
        node.update({"Int": int_lmt})
        ui.sample_rate_value_label.setText(f"Sample Rate: {sample}")
        node.update({"Rate": sample})

    def set_kp(self) -> None:
        self._update_pid_value(
            input_attr="kp_input",
            label_attr="kp_value_label",
            label_prefix="KP",
            node_key="KP",
            command="kp",
            caster=float,
        )

    def set_ki(self) -> None:
        self._update_pid_value(
            input_attr="ki_input",
            label_attr="ki_value_label",
            label_prefix="KI",
            node_key="KI",
            command="ki",
            caster=float,
        )

    def set_kd(self) -> None:
        self._update_pid_value(
            input_attr="kd_input",
            label_attr="kd_value_label",
            label_prefix="KD",
            node_key="KD",
            command="kd",
            caster=float,
        )

    def set_integrator(self) -> None:
        self._update_pid_value(
            input_attr="int_lmt_input",
            label_attr="int_lmt_value_label",
            label_prefix="Int Lmt",
            node_key="Int",
            command="ilm",
            caster=int,
        )

    def set_sample_rate(self) -> None:
        self._update_pid_value(
            input_attr="sample_rate_input",
            label_attr="sample_rate_value_label",
            label_prefix="Sample Rate",
            node_key="Rate",
            command="spl",
            caster=int,
        )

    def refresh_motion_values(self) -> None:
        self.window.callbacks.append(self.update_motion_values)
        self.window.send_command(("prf",), callback=True)

    def update_motion_values(self, *args, **__) -> None:
        node_manager = self.window.node_manager
        node_id = node_manager.current_node_id
        node = node_manager.get_motion(node_id)
        accel, vel, decel, err = None, None, None, None
        try:
            values = args[0].split(",")
            values = [v.strip() for v in values if v.strip()]
            accel, vel, decel, err = values
        except ValueError as ve:
            self.logger.error("Value Error in update_motion_values: %s. Values: %s", ve, args)

        ui = self.window.ui
        ui.accel_value_label.setText(f"Acceleration: {accel}")
        node.update({"Accel": accel})
        ui.vel_value_label.setText(f"Velocity: {vel}")
        node.update({"Velo": vel})
        ui.decel_value_label.setText(f"Deceleration: {decel}")
        node.update({"Decel": decel})
        ui.err_value_label.setText(f"Error Limit: {err}")
        node.update({"Error": err})

    def update_jog_values(self) -> None:
        node = self.window.node_manager.get_motion(self.window.node_manager.current_node_id)
        self.window.ui.jog_label.setText(f"Jog: {node['JogValue']}")
        self.window.ui.hs_jog_label.setText(f"HS Jog: {node['HSValue']}")

    def set_motion_accel(self) -> None:
        self._update_motion_value(
            input_attr="accel_input",
            label_attr="accel_value_label",
            label_prefix="Acceleration",
            node_key="Accel",
            command="acc",
        )

    def set_motion_vel(self) -> None:
        self._update_motion_value(
            input_attr="vel_input",
            label_attr="vel_value_label",
            label_prefix="Velocity",
            node_key="Velo",
            command="vel",
        )

    def set_motion_decel(self) -> None:
        self._update_motion_value(
            input_attr="decel_input",
            label_attr="decel_value_label",
            label_prefix="Deceleration",
            node_key="Decel",
            command="dec",
        )

    def set_motion_err(self) -> None:
        self._update_motion_value(
            input_attr="err_input",
            label_attr="err_value_label",
            label_prefix="Error Limit",
            node_key="Error",
            command="erl",
        )

    def set_jog(self) -> None:
        node = self.window.node_manager.get_motion(self.window.comboBox.currentText())
        try:
            jog = int(self.window.ui.jog_input.text())
            node["JogValue"] = str(jog)
            self.window.ui.jog_label.setText(f"Jog: {jog}")
            motor_stat = self.window.motor_stats[self.window.comboBox.currentIndex()]
            motor_stat.set_jog()
        except ValueError:
            self.logger.error("Value must be int. Value received: %s", self.window.ui.jog_input.text())

    def set_hs_jog(self) -> None:
        node = self.window.node_manager.get_motion(self.window.comboBox.currentText())
        try:
            hs_jog = int(self.window.ui.hs_jog_input.text())
            node["HSValue"] = str(hs_jog)
            self.window.ui.hs_jog_label.setText(f"HS Jog: {hs_jog}")
            motor_stat = self.window.motor_stats[self.window.comboBox.currentIndex()]
            motor_stat.set_jog()
        except ValueError:
            self.logger.error("Value must be int. Value received: %s", self.window.ui.hs_jog_input.text())

    def refresh_advanced_values(self) -> None:
        self.window.callbacks.append(self.update_advanced_values)
        self.window.send_command(("swl",), callback=True)

    def update_advanced_values(self, *args, **__) -> None:
        lower, upper = "0", "0"
        try:
            values = args[0].split(",")
            values = [v.strip() for v in values if v.strip()]
            lower, upper = values
        except Exception as exc:
            self.logger.error("Failed to parse advanced values: %s", exc)

        ui = self.window.ui
        ui.lower_limit_value.setText(f"Lower Limit: {lower}")
        ui.upper_limit_value.setText(f"Upper Limit: {upper}")

    def set_lower_limit(self) -> None:
        limit = int(self.window.ui.lower_limit_input.text())
        self.window.send_command((f"sll {limit}",))
        self.window.ui.lower_limit_value.setText(f"Lower Limit: {limit}")
        node = self.window.node_manager.get_advanced(self.window.node_manager.current_node_id)
        node.update({"Lower": limit})

    def set_upper_limit(self) -> None:
        limit = int(self.window.ui.upper_limit_input.text())
        self.window.send_command((f"slu {limit}",))
        self.window.ui.upper_limit_value.setText(f"Upper Limit: {limit}")
        node = self.window.node_manager.get_advanced(self.window.node_manager.current_node_id)
        node.update({"Upper": limit})

    def set_tolerance(self) -> None:
        tolerance = int(self.window.ui.pos_tolerance_input.text())
        self.window.send_command((f"tol {tolerance}",))
        self.window.ui.pos_tolerance_value.setText(f"Position Tolerance: {tolerance}")
        node = self.window.node_manager.get_advanced(self.window.node_manager.current_node_id)
        node.update({"Tolerance": tolerance})

    def _update_pid_value(
        self,
        *,
        input_attr: str,
        label_attr: str,
        label_prefix: str,
        node_key: str,
        command: str,
        caster: Callable,
    ) -> None:
        ui = self.window.ui
        try:
            value = caster(getattr(ui, input_attr).text())
            self.window.send_command((f"{command} {value}",))
            getattr(ui, label_attr).setText(f"{label_prefix}: {value}")
            node = self.window.node_manager.get_pid(self.window.node_manager.current_node_id)
            node.update({node_key: value})
        except ValueError:
            self.logger.error("Value must be %s. Value received: %s", caster.__name__, getattr(ui, input_attr).text())

    def _update_motion_value(
        self,
        *,
        input_attr: str,
        label_attr: str,
        label_prefix: str,
        node_key: str,
        command: str,
    ) -> None:
        try:
            value = int(getattr(self.window.ui, input_attr).text())
            self.window.send_command((f"{command} {value}",))
            getattr(self.window.ui, label_attr).setText(f"{label_prefix}: {value}")
            node = self.window.node_manager.get_motion(self.window.node_manager.current_node_id)
            node.update({node_key: value})
        except ValueError:
            self.logger.error("Value must be int. Value received: %s", getattr(self.window.ui, input_attr).text())
