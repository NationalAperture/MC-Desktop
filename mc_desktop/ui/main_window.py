# This Python file uses the following encoding: utf-8
# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py

import csv
import sys
import os
import logging
from collections import deque
from datetime import datetime

from PySide6.QtCore import Qt, QSettings, QTimer
from PySide6.QtGui import QAction, QColor, QFont, QKeySequence, QPainter, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableWidgetItem,
    QTextEdit,
    QProgressBar,
    QWidget,
)
from ..communication import CommunicationManager
from ..node_manager import NodeManager
from ..updater import UpdateChecker
from ..version import __version__
from .controllers import CommandDispatcher, MacroRunner, NodeSettingsController
from .forms.ui_connection_form import Ui_Connection_Form
from .forms.ui_form import Ui_MainWindow
from .forms.ui_motor_stats import Ui_Motor_Form
from .forms.ui_record_bus import Ui_Dialog as Ui_RecordBus_Dialog
from .update_dialog import UpdateDialog

logger = logging.getLogger(__name__) # Create Logger
COM_BUS_MAX_ROWS = 1000
MOTOR_UPDATE_THROTTLE_MS = 100
CONNECTION_LED_SIZE = 10
CONNECTION_LED_ON_COLOR = "#2ecc71"
CONNECTION_LED_OFF_COLOR = "#e74c3c"

def clear_layout(layout, delete_widgets):
    for i in reversed(range(layout.count())):
        if layout.itemAt(i).widget():
            widget_to_remove = layout.itemAt(i).widget()
            # remove it from the layout list
            layout.removeWidget(widget_to_remove)
            # remove it from the gui
            widget_to_remove.setParent(None)
            # set to be deleted later
            if delete_widgets:
                widget_to_remove.deleteLater()
        else:
            item_to_remove = layout.itemAt(i)
            # remove it from the layout list
            layout.removeItem(item_to_remove)
            # set to be deleted later
            if delete_widgets:
                item_to_remove.deleteLater()

def candidate_ports():
        """
        Return a list of serial port candidates across Windows, Linux, and macOS.
        """
        from serial.tools import list_ports

        ports = []
        for port in list_ports.comports():
            dev = port.device  # actual device name, like "COM3" or "/dev/ttyUSB0"
            dev_lower = dev.lower()

            if sys.platform.startswith("win"):
                # Windows: COM1, COM2, ...
                if "com" in dev_lower:
                    ports.append(port)

            elif sys.platform.startswith("linux"):
                # Linux: USB adapters (/dev/ttyUSBx), onboard UART (/dev/ttyAMAx)
                if "ttyusb" in dev_lower or "ttyama" in dev_lower:
                    ports.append(port)

            elif sys.platform.startswith("darwin"):
                # macOS: /dev/tty.* or /dev/cu.*
                if "tty." in dev_lower or "cu." in dev_lower:
                    ports.append(port)

        return ports

class Connection(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.ui = Ui_Connection_Form()
        self.ui.setupUi(self)
        self.__setup__(parent)

    def __setup__(self, parent):
        self.parent = parent
        # self.ui.remove_node_combo.addItem("1")
        self.ui.search_ports_btn.pressed.connect(self.search_ports)
        self.ui.connect_btn.clicked.connect(self.select_port)
        self.ui.add_node_btn.pressed.connect(self.add_node)
        self.ui.remove_node_btn.pressed.connect(self.remove_node)
        self.ui.update_node_btn.pressed.connect(self.update_node)
        self.ui.baud_rates.currentIndexChanged.connect(self.update_baudrate)

    def update_baudrate(self):
        self.parent.serial.connection.baudrate = self.ui.baud_rates.currentText()

    def add_node(self):
        node_id = self.ui.add_node_value.text()
        if not node_id:
            return
        if self.parent.add_node(node_id):
            self.ui.remove_node_combo.addItem(node_id)
            self.parent.comboBox.setCurrentIndex(self.parent.comboBox.count() - 1)
            self.parent.get_node_values(node_id)

    def remove_node(self):
        node_index = self.ui.remove_node_combo.currentIndex()
        if node_index < 0:
            return
        node_id = self.ui.remove_node_combo.itemText(node_index)
        if self.parent.remove_node(node_id, node_index):
            self.ui.remove_node_combo.removeItem(node_index)

    def update_node(self):
        # This changes the currently selected node's id, to the new id the user has just entered.
        current_node = self.parent.node_manager.current_node_id
        new_node = self.ui.update_node_value.text()
        for i in range(self.ui.remove_node_combo.count()):
            if self.ui.remove_node_combo.itemText(i) == current_node:
                if self.parent.update_node_id(i, current_node, new_node):
                    self.ui.remove_node_combo.setItemText(i, new_node)
                    self.ui.update_node_value.clear()
                break

    def select_port(self):
        port = self.ui.port_list.selectedItems()[0].text()
        self.parent.serial.port = port
        self.parent.serial.baudrate = self.ui.baud_rates.currentText()
        successful = self.parent.serial.setup_connection()
        if successful:
            self.parent.set_connection_status(True)
            self.ui.tabWidget.setCurrentIndex(1)
            # self.parent.get_node_values()

    def search_ports(self):
        self.ui.port_list.clear()

        ports = candidate_ports()
        for port, desc, hwid in ports:
            self.ui.port_list.addItem(port)



class MotorStats(QWidget):
    def __init__(self, parent, title):
        super().__init__()
        self.ui = Ui_Motor_Form()
        self.ui.setupUi(self)
        self.node_id = None
        self.__setup__(parent, title)

    def __setup__(self, parent, title):
        self.parent = parent
        font = QFont()
        font.setBold(True)
        font.setItalic(True)
        self.ui.node_id.setFont(font)
        self.set_group_box_title(title)

        self.ui.hs_jog_cb.clicked.connect(self.set_jog)
        self.ui.enable_drive_cb.clicked.connect(self.set_drive)
        self.ui.limit_behavior_cb.currentIndexChanged.connect(self.limit_behavior_updated)

    def set_limit_behavior(self, behavior):
        self.ui.limit_behavior_cb.blockSignals(True)
        for index in range(self.ui.limit_behavior_cb.count()):
            if behavior == self.ui.limit_behavior_cb.itemText(index):
                self.ui.limit_behavior_cb.setCurrentIndex(index)
        self.ui.limit_behavior_cb.blockSignals(False)

    def limit_behavior_updated(self):
        index = self.ui.limit_behavior_cb.currentIndex() + 1
        self.parent.limit_behavior_updated(str(index), self.node_id)

    def set_jog(self):
        if self.ui.hs_jog_cb.isChecked():
            self.parent.toggle_jog(True, self.node_id)
        else:
            self.parent.toggle_jog(False, self.node_id)

    def set_drive(self):
        if self.ui.enable_drive_cb.isChecked():
            self.parent.toggle_drive(True, self.node_id)
        else:
            self.parent.toggle_drive(False, self.node_id)

    def set_front_lmt(self):
        if self.ui.front_lmt_cb.isChecked():
            self.parent.toggle_front_lmt(True, self.node_id)
        else:
            self.parent.toggle_front_lmt(False, self.node_id)

    def set_rear_lmt(self):
        if self.ui.rear_lmt_cb.isChecked():
            self.parent.toggle_rear_lmt(True, self.node_id)
        else:
            self.parent.toggle_rear_lmt(False, self.node_id)

    def set_group_box_title(self, title):
        self.node_id = title
        self.ui.node_id.setTitle(f"Node ID: {self.node_id}")

    def update_motor_values(self, value):
        try:
            pos = value
            self.ui.position.setText(pos)
            #self.ui.voltage.setText(voltage)
            #self.ui.amps.setText(amps)
            #self.ui.wattage.setText(watts)
        except ValueError:
            logger.error(f"Value received for motor: {value}")

class RecordBus(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_RecordBus_Dialog()
        self.ui.setupUi(self)
        self.__setup__(parent)

    def __setup__(self, parent):
        self.parent = parent
        self.setWindowTitle("Record Bus")
        self.ui.whole_table_rb.clicked.connect(self.selected_whole_table)
        self.ui.selected_row_rb.clicked.connect(self.selected_range)
        self.ui.buttonBox.accepted.connect(self.record_data)

    def selected_range(self):
        self.ui.label.setEnabled(True)
        self.ui.label_2.setEnabled(True)
        self.ui.start_row_value.setEnabled(True)
        self.ui.end_row_value.setEnabled(True)

    def selected_whole_table(self):
        self.ui.label.setEnabled(False)
        self.ui.label_2.setEnabled(False)
        self.ui.start_row_value.setEnabled(False)
        self.ui.end_row_value.setEnabled(False)

    def record_data(self):
        # Need to determin if whole table or just selected rows.
        # If selected rows must make sure they are within table range.
        # Have this all done in the parent.
        if self.ui.whole_table_rb.isChecked():
            self.parent.record_data()
        else:
            start = self.ui.start_row_value.text()
            end = self.ui.end_row_value.text()
            self.parent.record_data(int(start), int(end))
        pass

class MainWindow(QMainWindow):
    def __init__(self, log=None):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.__setup__(log)

    def __setup__(self, log):
        self.connection = None
        self.record = None
        self.serial = CommunicationManager(self, log)
        self.serial.signals.log.connect(self.log_received_messages)
        self.serial.signals.main_thread.connect(self.manage_callback)
        self.serial.signals.poll.connect(self.update_node_motor_values)
        self.node_manager = NodeManager()
        self.motor_stats = []
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.ui.system_monitor.layout().addItem(self.verticalSpacer)
        self.setWindowTitle("NAI Mover")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.column_count = self.ui.com_bus_table.columnCount()
        self.com_bus_max_rows = COM_BUS_MAX_ROWS
        self._pending_motor_updates = {}
        self._motor_update_timer = QTimer(self)
        self._motor_update_timer.setSingleShot(True)
        self._motor_update_timer.setInterval(MOTOR_UPDATE_THROTTLE_MS)
        self._motor_update_timer.timeout.connect(self._flush_pending_motor_updates)
        self.comboBox = QComboBox()
        self.comboBox.setFont(QFont("Arial", 15))
        self.comboBox.currentIndexChanged.connect(self.selected_new_node)
        self.ui.menubar.setCornerWidget(self.comboBox, corner=Qt.Corner.TopRightCorner)
        self.callbacks = []

        self.macro_text = QTextEdit()
        self.macro_text.setFont(QFont("Arial", 15))
        self.ui.macro_group_box.layout().addWidget(self.macro_text, 1, 0, 1, 5)
        self.macro_progress = QProgressBar()
        self.macro_progress.setRange(0, 1)
        self.macro_progress.setValue(0)
        self.macro_progress.setFormat("Step %v/%m")
        self.ui.macro_group_box.layout().addWidget(self.macro_progress, 3, 0, 1, 4)
        self.pause_macro_btn = QPushButton("Pause")
        self.pause_macro_btn.setEnabled(False)
        self.ui.macro_group_box.layout().addWidget(self.pause_macro_btn, 3, 4, 1, 1)
        self.macros = MacroRunner(self, logger=log or logger)
        self.serial.signals.command_complete.connect(self.macros.on_command_complete)
        self.settings = NodeSettingsController(self, logger=log or logger)
        self.command_dispatcher = CommandDispatcher(self, self.send_command, logger=log or logger)

        self.current_node_id = None
        self.node_index = {}
        self._jog_key_active = None



        # Commands UI
        self._connect_signals(
            (self.ui.move_btn.pressed, self.move_cmd),
            (self.ui.front_lmt_btn.pressed, self.forward),
            (self.ui.rear_lmt_btn.pressed, self.backward),
            (self.ui.forward_btn.pressed, self.forward),
            (self.ui.forward_btn.released, self.stop),
            (self.ui.backward_btn.pressed, self.backward),
            (self.ui.backward_btn.released, self.stop),
            (self.ui.stop_btn.pressed, self.stop),
        )
        self._connect_signals(
            (self.ui.move_abs_btn.pressed, lambda: self.command_dispatcher.execute("move_absolute")),
            (self.ui.load_abs_btn.pressed, lambda: self.command_dispatcher.execute("load_absolute")),
            (self.ui.move_rel_btn.pressed, lambda: self.command_dispatcher.execute("move_relative")),
            (self.ui.load_rel_btn.pressed, lambda: self.command_dispatcher.execute("load_relative")),
            (self.ui.set_home_btn.clicked, lambda: self.command_dispatcher.execute("set_home")),
        )

        # Macro UI
        self._connect_signals(
            (self.ui.load_macro_btn.pressed, self.macros.load_macro),
            (self.ui.save_macro_btn.pressed, self.macros.save_macro),
            (self.ui.step_macro_btn.pressed, self.macros.step_through_macro),
            (self.ui.run_macro_btn.pressed, self.macros.run_macro),
            (self.ui.run_once_rb.clicked, self.macros.set_number_of_runs),
            (self.ui.run_variable_rb.clicked, self.macros.set_number_of_runs),
            (self.ui.variable_amount_value.textChanged, self.macros.set_number_of_runs),
        )
        self.pause_macro_btn.clicked.connect(self.macros.toggle_pause)

        # Settings UI
        self.ui.save_config_btn.clicked.connect(self.save_configuration)
        self.ui.load_config_btn.clicked.connect(self.load_configuration)
        self.ui.erase_config_btn.clicked.connect(self.erase_configuration)

        self._connect_signals(
            (self.ui.refresh_stage_btn.clicked, self.settings.refresh_stage_values),
            (self.ui.stage_type_combo.currentIndexChanged, self.settings.set_stage_type),
            (self.ui.travel_unit_combo.currentIndexChanged, self.settings.set_unit_travel),
            (self.ui.update_gh_btn.clicked, self.settings.set_stage_gh),
            (self.ui.update_tpi_btn.clicked, self.settings.set_stage_tpi),
            (self.ui.update_cpr_btn.clicked, self.settings.set_stage_cpr),
            (self.ui.refresh_pid_btn.clicked, self.settings.refresh_pid_values),
            (self.ui.kp_update_btn.clicked, self.settings.set_kp),
            (self.ui.ki_update_btn.clicked, self.settings.set_ki),
            (self.ui.kd_update_btn.clicked, self.settings.set_kd),
            (self.ui.int_lmt_update_btn.clicked, self.settings.set_integrator),
            (self.ui.sample_rate_update_btn.clicked, self.settings.set_sample_rate),
            (self.ui.refresh_motion_btn.clicked, self.settings.refresh_motion_values),
            (self.ui.accel_update_btn.clicked, self.settings.set_motion_accel),
            (self.ui.vel_update_btn.clicked, self.settings.set_motion_vel),
            (self.ui.decel_update_btn.clicked, self.settings.set_motion_decel),
            (self.ui.err_update_btn.clicked, self.settings.set_motion_err),
            (self.ui.jog_update_btn.clicked, self.settings.set_jog),
            (self.ui.hs_jog_update_btn.clicked, self.settings.set_hs_jog),
            (self.ui.refresh_advanced_btn.clicked, self.settings.refresh_advanced_values),
            (self.ui.update_lower_btn.clicked, self.settings.set_lower_limit),
            (self.ui.update_upper_btn.clicked, self.settings.set_upper_limit),
            (self.ui.update_pos_tol_btn.clicked, self.settings.set_tolerance),
        )
        self.ui.update_baud_rate_btn.clicked.connect(self.set_baud_rate)

        self.actionConnect = QAction("Connection", self)
        self.actionConnect.triggered.connect(self.show_connection)
        self.actionRecord = QAction("Motion", self)
        self.actionRecord.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.actionSettings = QAction("Settings", self)
        self.actionSettings.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))

        self.ui.menubar.addAction(self.actionConnect)
        self.ui.menubar.addAction(self.actionRecord)
        self.ui.menubar.addAction(self.actionSettings)

        self.update_checker = UpdateChecker(self)
        self.update_checker.update_available.connect(self._on_update_available)
        self.update_checker.check_failed.connect(self._on_update_check_failed)
        QTimer.singleShot(5000, self._check_for_updates)

        self._connection_led = QLabel()
        self._connection_status_label = QLabel()
        self.ui.statusbar.addPermanentWidget(self._connection_led)
        self.ui.statusbar.addPermanentWidget(self._connection_status_label)
        self._set_connection_indicator(False)

        version_label = QLabel(f"v{__version__}")
        self.ui.statusbar.addPermanentWidget(version_label)

    def show_connection(self):
        if self.connection is None:
            self.connection = Connection(self)
        self.connection.close()
        self.connection.show()

    def _check_for_updates(self):
        self.update_checker.check_for_updates()

    def _on_update_available(
        self,
        new_version: str,
        download_url: str,
        release_notes: str,
        download_size: object,
    ):
        settings = QSettings("NAI", "NAI-Mover")
        skipped = settings.value("skipped_version", "")
        if skipped == new_version:
            return

        dialog = UpdateDialog(new_version, download_url, release_notes, download_size, self)
        dialog.exec()

        if dialog.skip_checkbox.isChecked():
            settings.setValue("skipped_version", new_version)

    def _on_update_check_failed(self, error: str):
        logger.debug("Update check failed: %s", error)

    """COMMANDS IMPLEMENTATION"""

    def move_cmd(self):
        cmd = ("mov",)
        self.send_command(cmd)

    def forward(self):
        node = self.node_manager.get_motion(self.comboBox.currentText())
        speed = node["Jog"]
        cmd = ("jog", speed)
        self.send_command(cmd)

    def backward(self):
        node = self.node_manager.get_motion(self.comboBox.currentText())
        speed = node["Jog"]
        cmd = ("jog", f"-{speed}")
        self.send_command(cmd)

    def stop(self):
        cmd = ("abm",)
        self.send_command(cmd)
    """END OF COMMANDS IMPLEMENTATION """

    def set_macro_progress(self, current_step: int, total_steps: int) -> None:
        total = max(total_steps, 1)
        value = min(max(current_step, 0), total)
        self.macro_progress.setRange(0, total)
        self.macro_progress.setValue(value)

    def set_macro_pause_state(self, enabled: bool, paused: bool) -> None:
        self.pause_macro_btn.setEnabled(enabled)
        self.pause_macro_btn.setText("Resume" if paused else "Pause")

    def set_connection_status(self, connected: bool) -> None:
        self._set_connection_indicator(connected)

    def _set_connection_indicator(self, connected: bool) -> None:
        color = QColor(CONNECTION_LED_ON_COLOR if connected else CONNECTION_LED_OFF_COLOR)
        pixmap = QPixmap(CONNECTION_LED_SIZE, CONNECTION_LED_SIZE)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawEllipse(0, 0, CONNECTION_LED_SIZE, CONNECTION_LED_SIZE)
        painter.end()
        self._connection_led.setPixmap(pixmap)
        self._connection_status_label.setText("Connected" if connected else "Disconnected")

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        if not self.hasFocus():
            return
        key = event.key()
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            high_speed = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
            self._jog_key_active = key
            self._jog_key(high_speed=high_speed, reverse=key == Qt.Key.Key_Left)
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        if not self.hasFocus():
            return
        key = event.key()
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            if self._jog_key_active == key:
                self._jog_key_active = None
            self.stop()
            event.accept()
            return
        super().keyReleaseEvent(event)

    def _jog_key(self, high_speed: bool, reverse: bool) -> None:
        node = self.node_manager.get_motion(self.comboBox.currentText())
        speed = node["HSValue"] if high_speed else node["Jog"]
        command_speed = f"-{speed}" if reverse else speed
        self.send_command(("jog", command_speed))

    """SYSTEM IMPLEMENTATION"""

    def set_limit_behavior(self, behavior):
        motor_stat = self.motor_stats[self.comboBox.currentIndex()]
        motor_stat.set_limit_behavior(behavior)

    def limit_behavior_updated(self, index, node_id):
        self.send_command(("slm", index), node_id=node_id)

    def toggle_jog(self, checked, node_id):
        node = self.node_manager.get_motion(node_id)
        if checked:
            node["Jog"] = node["HSValue"]
        else:
            node["Jog"] = node["JogValue"]

    def toggle_drive(self, checked, node_id):
        if checked:
            self.send_command(("ena", "1"), node_id=node_id)
        else:
            self.send_command(("ena", "0"), node_id=node_id)

    def toggle_front_lmt(self, checked, node_id):
        if checked:
            self.send_command(("ena", "1"), node_id=node_id)
        else:
            self.send_command(("ena", "0"), node_id=node_id)

    def toggle_rear_lmt(self, checked, node_id):
        if checked:
            self.send_command(("ena", "1"), node_id=node_id)
        else:
            self.send_command(("ena", "0"), node_id=node_id)
    """END OF SYSTEM IMPLEMENTATION"""

    """ SETTINGS IMPLEMENTATION """
    def selected_node_change(self, node_id, get_values=False):
        if get_values:
            sn, vn = self.node_manager.get_config_values(node_id)
            self.set_serial_number(sn)
            self.set_version_number(vn)
            stage = self.settings.snapshot_stage(node_id)
            self.settings.update_stage_values(stage)
            pid = self.settings.snapshot_pid(node_id)
            self.settings.update_pid_values(pid)
            motion = self.settings.snapshot_motion(node_id)
            self.settings.update_motion_values(motion)
            self.settings.update_jog_values()
            advanced = self.settings.snapshot_advanced(node_id)
            self.settings.update_advanced_values(advanced)

    def set_serial_number(self, serial_number):
        self.ui.SN_label.setText(serial_number)
        node_id = self.node_manager.current_node_id
        node = self.node_manager.get_config(node_id)
        node.update({"SN": serial_number})

    def set_version_number(self, version_number):
        self.ui.VN_label.setText(version_number)
        node_id = self.node_manager.current_node_id
        node = self.node_manager.get_config(node_id)
        node.update({"VN": version_number})

    def save_configuration(self):
        value, ok = QInputDialog.getText(self, "Save Configuration", "Choose a number between 1 and 16")
        if ok:
            self.send_command(("scf", value))

    def load_configuration(self):
        value, ok = QInputDialog.getText(self, "Load Configuration", "Choose a number between 1 and 16")
        if ok:
            self.send_command(("lcf", value))
            #self.get_node_values()

    def erase_configuration(self):
        self.send_command(("ecf",))

    def get_stage_values(self):
        self.settings.refresh_stage_values()

    def update_stage_values(self, *args, **kwargs):
        self.settings.update_stage_values(*args, **kwargs)

    def update_unit_travel(self, *args, **kwargs):
        self.settings.update_unit_travel(*args, **kwargs)

    def set_stage_type(self):
        self.settings.set_stage_type()

    def set_unit_travel(self):
        self.settings.set_unit_travel()

    def set_stage_gh(self):
        self.settings.set_stage_gh()

    def set_stage_tpi(self):
        self.settings.set_stage_tpi()

    def set_stage_cpr(self):
        self.settings.set_stage_cpr()

    def get_pid_values(self):
        self.settings.refresh_pid_values()

    def update_pid_values(self, *args, **kwargs):
        self.settings.update_pid_values(*args, **kwargs)

    def set_kp(self):
        self.settings.set_kp()

    def set_ki(self):
        self.settings.set_ki()

    def set_kd(self):
        self.settings.set_kd()

    def set_integrator(self):
        self.settings.set_integrator()

    def set_sample_rate(self):
        self.settings.set_sample_rate()

    def get_motion_values(self):
        self.settings.refresh_motion_values()

    def update_motion_values(self, *args, **kwargs):
        self.settings.update_motion_values(*args, **kwargs)

    def update_jog_values(self):
        self.settings.update_jog_values()

    def set_motion_accel(self):
        self.settings.set_motion_accel()

    def set_motion_vel(self):
        self.settings.set_motion_vel()

    def set_motion_decel(self):
        self.settings.set_motion_decel()

    def set_motion_err(self):
        self.settings.set_motion_err()

    def set_jog(self):
        self.settings.set_jog()

    def set_hs_jog(self):
        self.settings.set_hs_jog()

    def get_advanced_values(self):
        self.settings.refresh_advanced_values()


    def update_advanced_values(self, *args, **kwargs):
        self.settings.update_advanced_values(*args, **kwargs)


    def set_lower_limit(self):
        self.settings.set_lower_limit()

    def set_upper_limit(self):
        self.settings.set_upper_limit()

    def set_tolerance(self):
        self.settings.set_tolerance()

    def set_baud_rate(self):
        baud_rate = int(self.ui.baud_rates.currentIndex() + 1)
        self.send_command((f"sbr {baud_rate}",))
        node_id = self.node_manager.current_node_id
        node = self.node_manager.get_advanced(node_id)
        node.update({"Baud_Rate": baud_rate})


    """END OF SETTINGS IMPLEMENTATION """

    def record_data(self, start=None, end=None):
        if start and end:
            path, ok = QFileDialog.getSaveFileName(
                self, 'Save CSV', os.getenv('HOME'), 'CSV(*.csv)')
            if ok:
                columns = range(self.ui.com_bus_table.columnCount())
                header = [self.ui.com_bus_table.horizontalHeaderItem(column).text()
                          for column in columns]
                with open(f"{path}.csv", 'w') as csvfile:
                    writer = csv.writer(
                        csvfile, dialect='excel', lineterminator='\n')
                    writer.writerow(header)
                    for row in range(end - start):
                        writer.writerow(
                            self.ui.com_bus_table.item(start, column).text()
                            for column in columns)
                        start += 1
        else:
            path, ok = QFileDialog.getSaveFileName(
                self, 'Save CSV', os.getenv('HOME'), 'CSV(*.csv)')
            if ok:
                columns = range(self.ui.com_bus_table.columnCount())
                header = [self.ui.com_bus_table.horizontalHeaderItem(column).text()
                          for column in columns]
                with open(f"{path}.csv", 'w') as csvfile:
                    writer = csv.writer(
                        csvfile, dialect='excel', lineterminator='\n')
                    writer.writerow(header)
                    for row in range(self.ui.com_bus_table.rowCount()):
                        writer.writerow(
                            self.ui.com_bus_table.item(row, column).text()
                            for column in columns)

    def manage_callback(self, *args, **kwargs):
        if self.callbacks:
            callback = self.callbacks.pop(0)
            callback(*args, **kwargs)

    def get_node_values(self, node_id=None):
        self.node_manager.current_node_id = node_id
        self.get_serial_number()

    def get_serial_number(self):
        self.callbacks.append(self.get_version_number)
        self.send_command(("srn",), node_id=self.node_manager.current_node_id, callback=True)

    def get_version_number(self, serial_number):
        self.set_serial_number(serial_number)
        self.callbacks.append(self.get_values_stage)
        self.send_command(("vrn",), node_id=self.node_manager.current_node_id, callback=True)

    def get_values_stage(self, version_number):
        self.set_version_number(version_number)
        self.callbacks.append(self.get_values_pid)
        self.send_command(("stg",), node_id=self.node_manager.current_node_id, callback=True)

    def get_values_pid(self, stage_values):
        self.update_stage_values(stage_values)
        self.callbacks.append(self.get_values_motion)
        self.send_command(("pid",), node_id=self.node_manager.current_node_id, callback=True)

    def get_values_motion(self, pid_values):
        self.update_pid_values(pid_values)
        self.callbacks.append(self.get_values_limits)
        self.send_command(("prf",), node_id=self.node_manager.current_node_id, callback=True)

    def get_values_limits(self, motion_values):
        self.update_motion_values(motion_values)
        self.callbacks.append(self.get_values_type)
        self.send_command(("glm",), node_id=self.node_manager.current_node_id, callback=True)

    def get_values_type(self, limits):
        self.set_limit_behavior(limits)
        self.callbacks.append(self.get_values_software)
        self.send_command(("gut",), node_id=self.node_manager.current_node_id, callback=True)

    def get_values_software(self, stage):
        self.update_unit_travel(stage)
        self.callbacks.append(self.set_software_limits)
        self.send_command(("swl",), node_id=self.node_manager.current_node_id, callback=True)

    def set_software_limits(self, limits):
        self.update_advanced_values(limits)


    def update_node_motor_values(self, node_id, values):
        self._pending_motor_updates[node_id] = values
        if self._motor_update_timer.isActive():
            return
        self._apply_motor_update(node_id, values)
        self._pending_motor_updates.pop(node_id, None)
        self._motor_update_timer.start()

    def _flush_pending_motor_updates(self):
        pending = self._pending_motor_updates
        self._pending_motor_updates = {}
        for node_id, values in pending.items():
            self._apply_motor_update(node_id, values)
        if self._pending_motor_updates:
            self._motor_update_timer.start()

    def _apply_motor_update(self, node_id, values):
        node_index = self.node_index.get(node_id)
        if node_index is not None and node_index >= 0:
            motor_stat = self.motor_stats[node_index]
            motor_stat.update_motor_values(values)

    def add_node(self, node_id):
        if not node_id:
            return False
        added = self.node_manager.add_node(node_id)
        if not added:
            logger.warning("Node %s already exists; skipping add.", node_id)
            return False
        self.comboBox.addItem(node_id)
        motor_stat = MotorStats(self, node_id)
        self.motor_stats.append(motor_stat)
        self._rebuild_node_index()
        self.repopulate_layout()
        return True

    def remove_node(self, node_id, index):
        if index < 0 or index >= self.comboBox.count():
            return False
        removed = self.node_manager.remove_node(node_id)
        if not removed:
            logger.warning("Attempted to remove unknown node %s", node_id)
            return False

        self.comboBox.removeItem(index)
        if index < len(self.motor_stats):
            del self.motor_stats[index]
        self._rebuild_node_index()
        new_current = self.node_manager.current_node_id
        if new_current:
            current_index = self.node_index.get(new_current, -1)
            if current_index >= 0:
                self.comboBox.setCurrentIndex(current_index)
                self.serial.node_id = new_current
        self.repopulate_layout()
        return True

    def repopulate_layout(self):
        clear_layout(self.ui.system_monitor.layout(), False)
        for motor_stat in self.motor_stats:
            self.ui.system_monitor.layout().addWidget(motor_stat)
        self.ui.system_monitor.layout().addItem(self.verticalSpacer)

    def update_node_id(self, index, old_node_id, new_node_id):
        if not new_node_id or new_node_id == old_node_id:
            return False

        self.node_manager.current_node_id = old_node_id
        if not self.node_manager.update_node_id(new_node_id):
            logger.warning("Unable to rename node %s -> %s", old_node_id, new_node_id)
            return False

        if index < self.comboBox.count():
            self.comboBox.setItemText(index, new_node_id)
        if index < len(self.motor_stats):
            motor_stat = self.motor_stats[index]
            motor_stat.set_group_box_title(new_node_id)

        self.serial.node_id = new_node_id
        self._rebuild_node_index()

        cmd = ("adr", new_node_id)
        self.send_command(cmd)
        return True

    def _rebuild_node_index(self):
        self.node_index = {self.comboBox.itemText(i): i for i in range(self.comboBox.count())}

    def selected_new_node(self):
        node_id = self.comboBox.currentText()
        self.serial.node_id = node_id
        self.node_manager.current_node_id = node_id
        self.selected_node_change(node_id, True)

    @staticmethod
    def _connect_signals(*connections):
        for signal, slot in connections:
            signal.connect(slot)

    def send_command(self, command, node_id=None, callback=False):
        if node_id is None:
            node_id = self.node_manager.current_node_id
        msg = (node_id,) + command
        self.serial.transmit_queue(*msg, callback=callback)
        self.log_sent_messages(msg)

    def log_sent_messages(self, message):
        #ToDo: Look to see if I can combine this function with the received one.
        #   The only difference is added the PC for "Device".
        self.ui.com_bus_table.insertRow(0)
        cmd = ' '.join(message)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        items = ("PC", cmd, timestamp)
        col = 0
        for item in items:
            self.ui.com_bus_table.setItem(0, col, QTableWidgetItem(item))
            col += 1
        self._trim_com_bus_table()

    def log_received_messages(self, message):
        self.ui.com_bus_table.insertRow(0)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        items = (f"Node Id: {self.node_manager.current_node_id}", message, timestamp)
        for col, value in zip(range(self.column_count), items):
            item = QTableWidgetItem(str(value))
            self.ui.com_bus_table.setItem(0, col, item)
        self._trim_com_bus_table()

    def _trim_com_bus_table(self):
        while self.ui.com_bus_table.rowCount() > self.com_bus_max_rows:
            self.ui.com_bus_table.removeRow(self.ui.com_bus_table.rowCount() - 1)

    def closeEvent(self, event):
        self._set_connection_indicator(False)
        self.serial.close()
        QApplication.closeAllWindows()
