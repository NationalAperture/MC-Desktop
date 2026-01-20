from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Optional, Sequence, Tuple

try:  # pragma: no cover - allow tests without PySide6
    from PySide6.QtWidgets import QFileDialog, QInputDialog
except ModuleNotFoundError:  # pragma: no cover
    QFileDialog = None  # type: ignore[assignment]
    QInputDialog = None  # type: ignore[assignment]

from ..commands import (
    CMD_GET_MOTION_VALUES,
    CMD_GET_PID_VALUES,
    CMD_GET_SOFT_LIMITS,
    CMD_GET_STAGE_VALUES,
    CMD_LOAD_ABSOLUTE,
    CMD_LOAD_RELATIVE,
    CMD_MOVE_ABSOLUTE,
    CMD_MOVE_RELATIVE,
    CMD_SET_ACCEL,
    CMD_SET_CPR,
    CMD_SET_DECEL,
    CMD_SET_ERROR_LIMIT,
    CMD_SET_GH,
    CMD_SET_HOME,
    CMD_SET_INTEGRATOR_LIMIT,
    CMD_SET_KD,
    CMD_SET_KI,
    CMD_SET_KP,
    CMD_SET_LOWER_LIMIT,
    CMD_SET_SAMPLE_RATE,
    CMD_SET_STAGE_TYPE,
    CMD_SET_TOLERANCE,
    CMD_SET_TPI,
    CMD_SET_UNIT_TRAVEL,
    CMD_SET_UPPER_LIMIT,
    CMD_SET_VEL,
)


@dataclass(frozen=True)
class PromptConfig:
    command: str
    title: str
    prompt: str


class CommandDispatcher:
    """Declarative registry for prompt-based motion commands."""

    _PROMPTS: Dict[str, PromptConfig] = {
        "set_home": PromptConfig(CMD_SET_HOME, "Set Home Position", "Enter Home Position"),
        "move_absolute": PromptConfig(CMD_MOVE_ABSOLUTE, "Move Absolute", "Where would you like to move?"),
        "load_absolute": PromptConfig(CMD_LOAD_ABSOLUTE, "Load Absolute", "Where would you like to load?"),
        "move_relative": PromptConfig(CMD_MOVE_RELATIVE, "Move Relative", "Where would you like to move?"),
        "load_relative": PromptConfig(CMD_LOAD_RELATIVE, "Load Relative", "Where would you like to load?"),
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


@dataclass(frozen=True)
class MacroCommand:
    node_id: str
    command: str
    param: Optional[str] = None

    def as_params(self) -> Tuple[str, ...]:
        if self.param is None:
            return (self.node_id, self.command)
        return (self.node_id, self.command, self.param)


class MacroRunner:
    """Encapsulates macro state management and execution helpers."""

    def __init__(self, window, logger: Optional[logging.Logger] = None) -> None:
        self.window = window
        self.logger = logger or logging.getLogger(__name__)
        self._validation_labels = {
            "GH_input": ("gh_value_label", "GH"),
            "TPI_input": ("tpi_value_label", "TPI"),
            "CPR_input": ("cpr_value_label", "CPR"),
            "kp_input": ("kp_value_label", "KP"),
            "ki_input": ("ki_value_label", "KI"),
            "kd_input": ("kd_value_label", "KD"),
            "int_lmt_input": ("int_lmt_value_label", "Integrator Lmt"),
            "sample_rate_input": ("sample_rate_value_label", "Sample Rate"),
            "accel_input": ("accel_value_label", "Acceleration"),
            "vel_input": ("vel_value_label", "Velocity"),
            "decel_input": ("decel_value_label", "Deceleration"),
            "err_input": ("err_value_label", "Error Limit"),
            "jog_input": ("jog_label", "Jog"),
            "hs_jog_input": ("hs_jog_label", "HS Jog"),
            "lower_limit_input": ("lower_limit_value", "Lower Limit"),
            "upper_limit_input": ("upper_limit_value", "Upper Limit"),
            "pos_tolerance_input": ("pos_tolerance_value", "Position Tolerance"),
        }
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
        self._paused: bool = False
        self._steps_executed: int = 0
        self._steps_total: int = 0

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
        self._paused = False
        self._runs_completed = 0
        self._prepare_run_state(steps)
        self.window.set_macro_pause_state(True, False)

        ui = self.window.ui
        if ui.run_variable_rb.isChecked():
            self._total_runs_requested = self.number_of_runs
            ui.run_count.setText(f"Run Count: 1/{self.number_of_runs}")
        else:
            self._total_runs_requested = None

        self.manage_macro()

    def toggle_pause(self) -> None:
        if not self._active:
            return
        self._paused = not self._paused
        self.window.set_macro_pause_state(True, self._paused)
        if not self._paused and not self._awaiting_completion:
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
        if self._paused:
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
        if self._paused:
            return
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
        self._steps_executed = 0
        self._steps_total = self._compute_total_steps(self._raw_steps)
        self.window.set_macro_progress(0, self._steps_total)
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
        parsed = self._parse_macro_command(command)
        if parsed is None:
            self._awaiting_completion = False
            self.manage_macro()
            return

        self._awaiting_completion = True
        params = parsed.as_params()
        self.window.log_sent_messages(params)
        self.window.serial.transmit_queue(
            parsed.node_id,
            parsed.command,
            parsed.param,
            await_completion=True,
            context="macro",
        )
        self._steps_executed += 1
        self.window.set_macro_progress(self._steps_executed, self._steps_total)

    def _parse_macro_command(self, command: str) -> Optional[MacroCommand]:
        parts = command.split()
        if len(parts) < 2:
            self.logger.warning("Macro command '%s' is incomplete and will be skipped.", command)
            return None
        node_id, cmd = parts[0], parts[1]
        param = " ".join(parts[2:]) if len(parts) > 2 else None
        return MacroCommand(node_id=node_id, command=cmd, param=param)

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
                self._paused = False
                self.window.set_macro_pause_state(False, False)
                self.window.set_macro_progress(self._steps_total, self._steps_total)
                self.repopulate_macro(self._raw_steps)
                return
            self._prepare_run_state(self.macro_list_copy or [])
            next_run = min(self._runs_completed + 1, total)
            ui.run_count.setText(f"Run Count: {next_run}/{total}")
            self.manage_macro()
            return

        self._active = False
        self._paused = False
        self.window.set_macro_pause_state(False, False)
        self.window.set_macro_progress(self._steps_total, self._steps_total)
        self.repopulate_macro(self._raw_steps)

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

    def _compute_total_steps(self, steps: Sequence[str]) -> int:
        def count_range(start: int, end: int) -> int:
            total = 0
            idx = start
            while idx < end:
                raw = steps[idx]
                token = raw.strip().lower()
                if token.startswith("loop"):
                    end_idx = self._loop_bounds.get(idx)
                    count = self._parse_loop_count(raw)
                    if end_idx is None or count <= 0:
                        idx += 1
                        continue
                    inner = count_range(idx + 1, end_idx)
                    total += inner * count
                    idx = end_idx + 1
                    continue
                if token == "end":
                    idx += 1
                    continue
                total += 1
                idx += 1
            return total

        return count_range(0, len(steps))


class NodeSettingsController:
    """Encapsulates the UI-heavy node settings coordination logic."""

    _DEFAULT_VALIDATION_LABELS = {
        "GH_input": ("gh_value_label", "GH"),
        "TPI_input": ("tpi_value_label", "TPI"),
        "CPR_input": ("cpr_value_label", "CPR"),
        "kp_input": ("kp_value_label", "KP"),
        "ki_input": ("ki_value_label", "KI"),
        "kd_input": ("kd_value_label", "KD"),
        "int_lmt_input": ("int_lmt_value_label", "Integrator Lmt"),
        "sample_rate_input": ("sample_rate_value_label", "Sample Rate"),
        "accel_input": ("accel_value_label", "Acceleration"),
        "vel_input": ("vel_value_label", "Velocity"),
        "decel_input": ("decel_value_label", "Deceleration"),
        "err_input": ("err_value_label", "Error Limit"),
        "jog_input": ("jog_label", "Jog"),
        "hs_jog_input": ("hs_jog_label", "HS Jog"),
        "lower_limit_input": ("lower_limit_value", "Lower Limit"),
        "upper_limit_input": ("upper_limit_value", "Upper Limit"),
        "pos_tolerance_input": ("pos_tolerance_value", "Position Tolerance"),
    }

    def __init__(self, window: object, logger: Optional[logging.Logger] = None) -> None:
        self.window = window
        self.logger = logger or logging.getLogger(__name__)
        self._validation_labels = dict(self._DEFAULT_VALIDATION_LABELS)

    @staticmethod
    def format_stage_values(stage: object) -> str:
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
        self.window.send_command((CMD_GET_STAGE_VALUES,), callback=True)

    def update_stage_values(self, *args: str, **__: object) -> None:
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

    def update_unit_travel(self, *args: str, **__: object) -> None:
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
        self.window.send_command((f"{CMD_SET_STAGE_TYPE} {index}",))
        node_manager = self.window.node_manager
        node_id = node_manager.current_node_id
        node = node_manager.get_stage(node_id)
        node.update({"Stage": f"{index}"})

    def set_unit_travel(self) -> None:
        index = self.window.ui.travel_unit_combo.currentIndex() + 1
        self.window.send_command((f"{CMD_SET_UNIT_TRAVEL} {index}",))
        node_manager = self.window.node_manager
        node_id = node_manager.current_node_id
        node = node_manager.get_stage(node_id)
        node.update({"Travel": f"{index}"})

    def set_stage_gh(self) -> None:
        try:
            gh = int(self.window.ui.GH_input.text())
            self.window.send_command((f"{CMD_SET_GH} {gh}",))
            self.window.ui.gh_value_label.setText(f"GH: {gh}")
            node = self.window.node_manager.get_stage(self.window.node_manager.current_node_id)
            node.update({"GH": gh})
            self._mark_input_valid("GH_input")
        except ValueError:
            self._warn_invalid_input("GH_input", "an integer", self.window.ui.GH_input.text())

    def set_stage_tpi(self) -> None:
        try:
            tpi = int(self.window.ui.TPI_input.text())
            self.window.send_command((f"{CMD_SET_TPI} {tpi}",))
            self.window.ui.tpi_value_label.setText(f"TPI: {tpi}")
            node = self.window.node_manager.get_stage(self.window.node_manager.current_node_id)
            node.update({"TPI": tpi})
            self._mark_input_valid("TPI_input")
        except ValueError:
            self._warn_invalid_input("TPI_input", "an integer", self.window.ui.TPI_input.text())

    def set_stage_cpr(self) -> None:
        try:
            cpr = int(self.window.ui.CPR_input.text())
            self.window.send_command((f"{CMD_SET_CPR} {cpr}",))
            self.window.ui.cpr_value_label.setText(f"CPR: {cpr}")
            node = self.window.node_manager.get_stage(self.window.node_manager.current_node_id)
            node.update({"CPR": cpr})
            self._mark_input_valid("CPR_input")
        except ValueError:
            self._warn_invalid_input("CPR_input", "an integer", self.window.ui.CPR_input.text())

    def refresh_pid_values(self) -> None:
        self.window.callbacks.append(self.update_pid_values)
        self.window.send_command((CMD_GET_PID_VALUES,), callback=True)

    def update_pid_values(self, *args: str, **__: object) -> None:
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
            command=CMD_SET_KP,
            caster=float,
        )

    def set_ki(self) -> None:
        self._update_pid_value(
            input_attr="ki_input",
            label_attr="ki_value_label",
            label_prefix="KI",
            node_key="KI",
            command=CMD_SET_KI,
            caster=float,
        )

    def set_kd(self) -> None:
        self._update_pid_value(
            input_attr="kd_input",
            label_attr="kd_value_label",
            label_prefix="KD",
            node_key="KD",
            command=CMD_SET_KD,
            caster=float,
        )

    def set_integrator(self) -> None:
        self._update_pid_value(
            input_attr="int_lmt_input",
            label_attr="int_lmt_value_label",
            label_prefix="Int Lmt",
            node_key="Int",
            command=CMD_SET_INTEGRATOR_LIMIT,
            caster=int,
        )

    def set_sample_rate(self) -> None:
        self._update_pid_value(
            input_attr="sample_rate_input",
            label_attr="sample_rate_value_label",
            label_prefix="Sample Rate",
            node_key="Rate",
            command=CMD_SET_SAMPLE_RATE,
            caster=int,
        )

    def refresh_motion_values(self) -> None:
        self.window.callbacks.append(self.update_motion_values)
        self.window.send_command((CMD_GET_MOTION_VALUES,), callback=True)

    def update_motion_values(self, *args: str, **__: object) -> None:
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
            command=CMD_SET_ACCEL,
        )

    def set_motion_vel(self) -> None:
        self._update_motion_value(
            input_attr="vel_input",
            label_attr="vel_value_label",
            label_prefix="Velocity",
            node_key="Velo",
            command=CMD_SET_VEL,
        )

    def set_motion_decel(self) -> None:
        self._update_motion_value(
            input_attr="decel_input",
            label_attr="decel_value_label",
            label_prefix="Deceleration",
            node_key="Decel",
            command=CMD_SET_DECEL,
        )

    def set_motion_err(self) -> None:
        self._update_motion_value(
            input_attr="err_input",
            label_attr="err_value_label",
            label_prefix="Error Limit",
            node_key="Error",
            command=CMD_SET_ERROR_LIMIT,
        )

    def set_jog(self) -> None:
        node = self.window.node_manager.get_motion(self.window.comboBox.currentText())
        try:
            jog = int(self.window.ui.jog_input.text())
            node["JogValue"] = str(jog)
            self.window.ui.jog_label.setText(f"Jog: {jog}")
            motor_stat = self.window.motor_stats[self.window.comboBox.currentIndex()]
            motor_stat.set_jog()
            self._mark_input_valid("jog_input")
        except ValueError:
            self._warn_invalid_input("jog_input", "an integer", self.window.ui.jog_input.text())

    def set_hs_jog(self) -> None:
        node = self.window.node_manager.get_motion(self.window.comboBox.currentText())
        try:
            hs_jog = int(self.window.ui.hs_jog_input.text())
            node["HSValue"] = str(hs_jog)
            self.window.ui.hs_jog_label.setText(f"HS Jog: {hs_jog}")
            motor_stat = self.window.motor_stats[self.window.comboBox.currentIndex()]
            motor_stat.set_jog()
            self._mark_input_valid("hs_jog_input")
        except ValueError:
            self._warn_invalid_input("hs_jog_input", "an integer", self.window.ui.hs_jog_input.text())

    def refresh_advanced_values(self) -> None:
        self.window.callbacks.append(self.update_advanced_values)
        self.window.send_command((CMD_GET_SOFT_LIMITS,), callback=True)

    def update_advanced_values(self, *args: str, **__: object) -> None:
        node_manager = self.window.node_manager
        node_id = node_manager.current_node_id
        node = node_manager.get_advanced(node_id)
        lower, upper = "0", "0"
        try:
            values = args[0].split(",")
            values = [v.strip() for v in values if v.strip()]
            lower, upper = values[0], values[1]
        except Exception as exc:
            self.logger.error("Failed to parse advanced values: %s", exc)


        ui = self.window.ui
        ui.lower_limit_value.setText(f"Lower Limit: {lower}")
        node.update({"Lower": lower})
        ui.upper_limit_value.setText(f"Upper Limit: {upper}")
        node.update({"Upper": upper})

    def set_lower_limit(self) -> None:
        try:
            limit = int(self.window.ui.lower_limit_input.text())
        except ValueError:
            self._warn_invalid_input("lower_limit_input", "an integer", self.window.ui.lower_limit_input.text())
            return
        self.window.send_command((f"{CMD_SET_LOWER_LIMIT} {limit}",))
        self.window.ui.lower_limit_value.setText(f"Lower Limit: {limit}")
        node = self.window.node_manager.get_advanced(self.window.node_manager.current_node_id)
        node.update({"Lower": limit})
        self._mark_input_valid("lower_limit_input")

    def set_upper_limit(self) -> None:
        try:
            limit = int(self.window.ui.upper_limit_input.text())
        except ValueError:
            self._warn_invalid_input("upper_limit_input", "an integer", self.window.ui.upper_limit_input.text())
            return
        self.window.send_command((f"{CMD_SET_UPPER_LIMIT} {limit}",))
        self.window.ui.upper_limit_value.setText(f"Upper Limit: {limit}")
        node = self.window.node_manager.get_advanced(self.window.node_manager.current_node_id)
        node.update({"Upper": limit})
        self._mark_input_valid("upper_limit_input")

    def set_tolerance(self) -> None:
        try:
            tolerance = int(self.window.ui.pos_tolerance_input.text())
        except ValueError:
            self._warn_invalid_input("pos_tolerance_input", "an integer", self.window.ui.pos_tolerance_input.text())
            return
        self.window.send_command((f"{CMD_SET_TOLERANCE} {tolerance}",))
        self.window.ui.pos_tolerance_value.setText(f"Position Tolerance: {tolerance}")
        node = self.window.node_manager.get_advanced(self.window.node_manager.current_node_id)
        node.update({"Tolerance": tolerance})
        self._mark_input_valid("pos_tolerance_input")

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
            self._mark_input_valid(input_attr)
        except ValueError:
            self._warn_invalid_input(
                input_attr,
                caster.__name__,
                getattr(ui, input_attr).text(),
            )

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
            self._mark_input_valid(input_attr)
        except ValueError:
            self._warn_invalid_input(input_attr, "an integer", getattr(self.window.ui, input_attr).text())

    def _warn_invalid_input(self, input_attr: str, expected: str, value: str) -> None:
        widget = getattr(self.window.ui, input_attr, None)
        if widget is not None:
            widget.setStyleSheet("border: 1px solid #e74c3c;")
        labels = getattr(self, "_validation_labels", self._DEFAULT_VALIDATION_LABELS)
        label_attr, label_prefix = labels.get(input_attr, (None, None))
        if label_attr is not None:
            label = getattr(self.window.ui, label_attr, None)
            if label is not None:
                label.setStyleSheet("color: #e74c3c;")
                label.setText(f"{label_prefix}: Invalid (expected {expected})")
        message = f"Invalid value '{value}'. Expected {expected}."
        self.logger.error(message)

    def _mark_input_valid(self, input_attr: str) -> None:
        widget = getattr(self.window.ui, input_attr, None)
        if widget is not None:
            widget.setStyleSheet("")
        labels = getattr(self, "_validation_labels", self._DEFAULT_VALIDATION_LABELS)
        label_attr, _ = labels.get(input_attr, (None, None))
        if label_attr is not None:
            label = getattr(self.window.ui, label_attr, None)
            if label is not None:
                label.setStyleSheet("")
