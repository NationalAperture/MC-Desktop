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
from pathlib import Path
from logging.handlers import RotatingFileHandler
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QComboBox, QTableWidgetItem, QSpacerItem, \
    QSizePolicy, QMessageBox, QInputDialog, QTextEdit, QDialog
from PySide6.QtGui import QShortcut, QKeySequence, QAction, Qt, QFont
from PySide6.QtCore import Qt
from ui_connection_form import Ui_Connection_Form
from serial.tools import list_ports
from ui_form import Ui_MainWindow
from communication import CommunicationManager
from node_config import NodeManager
from ui_motor_stats import Ui_Motor_Form
from ui_record_bus import Ui_Dialog

logger = logging.getLogger(__name__) # Create Logger

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

def open_file(file_path):
    try:
        with open(file_path, "r") as file:
            content = file.read()
            return content
    except FileNotFoundError:
        logger.error(f"Could not open file {file_path}")

def candidate_ports():
        """
        Return a list of serial port candidates across Windows, Linux, and macOS.
        """
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
        self.ui.remove_node_combo.addItem(node_id)
        self.parent.add_node(node_id)
        self.parent.comboBox.setCurrentIndex(self.parent.comboBox.count() - 1)
        self.parent.get_node_values(node_id)

    def remove_node(self):
        node_index = self.ui.remove_node_combo.currentIndex()
        self.ui.remove_node_combo.removeItem(node_index)
        self.parent.remove_node(node_index)

    def update_node(self):
        # This changes the currently selected node's id, to the new id the user has just entered.
        current_node = self.parent.node_manager.current_node_id
        new_node = self.ui.update_node_value.text()
        for i in range(self.ui.remove_node_combo.count()):
            if self.ui.remove_node_combo.itemText(i) == current_node:
                self.ui.remove_node_combo.setItemText(i, new_node)
                self.parent.update_node_id(i, new_node)

    def select_port(self):
        port = self.ui.port_list.selectedItems()[0].text()
        self.parent.serial.port = port
        self.parent.serial.baudrate = self.ui.baud_rates.currentText()
        successful = self.parent.serial.setup_connection()
        if successful:
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
        for index in range(self.ui.limit_behavior_cb.count()):
            if behavior == self.ui.limit_behavior_cb.itemText(index):
                self.ui.limit_behavior_cb.setCurrentIndex(index)

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
        self.ui = Ui_Dialog()
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

# ToDo: Set key bindings for the left and right arrow keys to jog the stage.
class MainWindow(QMainWindow):
    def __init__(self, log=None):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.__setup__(log)

    def __setup__(self, log):
        self.connection = Connection(self)
        self.record = RecordBus(self)
        self.serial = CommunicationManager(self, log)
        self.serial.signals.log.connect(self.log_received_messages)
        self.serial.signals.main_thread.connect(self.manage_callback)
        self.serial.signals.poll.connect(self.update_node_motor_values)
        self.node_manager = NodeManager()
        self.motor_stats = []
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.ui.system_monitor.layout().addItem(self.verticalSpacer)
        self.setWindowTitle("NAI Mover")
        self.column_count = self.ui.com_bus_table.columnCount()
        self.comboBox = QComboBox()
        self.comboBox.setFont(QFont("Arial", 15))
        self.comboBox.currentIndexChanged.connect(self.selected_new_node)
        self.ui.menubar.setCornerWidget(self.comboBox, corner=Qt.Corner.TopRightCorner)
        self.callbacks = []

        self.macro_text = QTextEdit()
        self.macro_text.setFont(QFont("Arial", 15))
        self.ui.macro_group_box.layout().addWidget(self.macro_text, 1, 0, 1, 5)
        self.macro_list = None
        self.macro_list_copy = None
        self.number_of_runs = 1
        self.loop_iterations = 2
        self.loop = []
        self.loop_copy = []

        self.current_node_id = None
        self.node_index = {}

        # Commands UI
        self.ui.move_btn.pressed.connect(self.move_cmd)
        self.ui.front_lmt_btn.pressed.connect(self.forward)
        self.ui.rear_lmt_btn.pressed.connect(self.backward)
        self.ui.forward_btn.pressed.connect(self.forward)
        self.ui.forward_btn.released.connect(self.stop)
        self.ui.backward_btn.pressed.connect(self.backward)
        self.ui.backward_btn.released.connect(self.stop)
        self.ui.stop_btn.pressed.connect(self.stop)
        self.ui.move_abs_btn.pressed.connect(self.move_abs)
        self.ui.load_abs_btn.pressed.connect(self.load_abs)
        self.ui.move_rel_btn.pressed.connect(self.move_rel)
        self.ui.load_rel_btn.pressed.connect(self.load_rel)
        self.ui.set_home_btn.clicked.connect(self.set_defined_pos)

        # Macro UI
        self.ui.load_macro_btn.pressed.connect(self.load_macro)
        self.ui.save_macro_btn.pressed.connect(self.save_macro)
        self.ui.step_macro_btn.pressed.connect(self.step_through_macro)
        self.ui.run_macro_btn.pressed.connect(self.run_macro)
        self.ui.run_once_rb.clicked.connect(self.set_number_of_runs)
        self.ui.run_variable_rb.clicked.connect(self.set_number_of_runs)
        self.ui.variable_amount_value.textChanged.connect(self.set_number_of_runs)

        # Settings UI
        self.ui.save_config_btn.clicked.connect(self.save_configuration)
        self.ui.load_config_btn.clicked.connect(self.load_configuration)
        self.ui.erase_config_btn.clicked.connect(self.erase_configuration)

        self.ui.refresh_stage_btn.clicked.connect(self.get_stage_values)
        self.ui.stage_type_combo.currentIndexChanged.connect(self.set_stage_type)
        self.ui.travel_unit_combo.currentIndexChanged.connect(self.set_unit_travel)
        self.ui.update_gh_btn.clicked.connect(self.set_stage_gh)
        self.ui.update_tpi_btn.clicked.connect(self.set_stage_tpi)
        self.ui.update_cpr_btn.clicked.connect(self.set_stage_cpr)

        self.ui.refresh_pid_btn.clicked.connect(self.get_pid_values)
        self.ui.kp_update_btn.clicked.connect(self.set_kp)
        self.ui.ki_update_btn.clicked.connect(self.set_ki)
        self.ui.kd_update_btn.clicked.connect(self.set_kd)
        self.ui.int_lmt_update_btn.clicked.connect(self.set_integrator)
        self.ui.sample_rate_update_btn.clicked.connect(self.set_sample_rate)

        self.ui.refresh_motion_btn.clicked.connect(self.get_motion_values)
        self.ui.accel_update_btn.clicked.connect(self.set_motion_accel)
        self.ui.vel_update_btn.clicked.connect(self.set_motion_vel)
        self.ui.decel_update_btn.clicked.connect(self.set_motion_decel)
        self.ui.err_update_btn.clicked.connect(self.set_motion_err)
        self.ui.jog_update_btn.clicked.connect(self.set_jog)
        self.ui.hs_jog_update_btn.clicked.connect(self.set_hs_jog)

        self.ui.refresh_advanced_btn.clicked.connect(self.get_advanced_values)
        self.ui.update_lower_btn.clicked.connect(self.set_lower_limit)
        self.ui.update_upper_btn.clicked.connect(self.set_upper_limit)
        self.ui.update_pos_tol_btn.clicked.connect(self.set_tolerance)

        self.actionConnect = QAction("Connection", self)
        self.actionConnect.triggered.connect(self.show_connection)
        self.actionRecord = QAction("Motion", self)
        self.actionRecord.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.actionSettings = QAction("Settings", self)
        self.actionSettings.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))

        self.ui.menubar.addAction(self.actionConnect)
        self.ui.menubar.addAction(self.actionRecord)
        self.ui.menubar.addAction(self.actionSettings)

    def show_connection(self):
        self.connection.close()
        self.connection.show()

    """COMMANDS IMPLEMENTATION"""

    def set_defined_pos(self):
        value, ok = QInputDialog.getText(self, "Set Home Position", "Enter Home Position")
        if ok:
            cmd = ("hom", value)
            self.send_command(cmd)

    def move_abs(self):
        value, ok = QInputDialog.getText(self, "Move Absolute", "Where would you like to move?")
        if ok:
            cmd = ("mva", value)
            self.send_command(cmd)

    def load_abs(self):
        value, ok = QInputDialog.getText(self, "Load Absolute", "Where would you like to load?")
        if ok:
            cmd = ("lpa", value)
            self.send_command(cmd)

    def move_rel(self):
        value, ok = QInputDialog.getText(self, "Move Relative", "Where would you like to move?")
        if ok:
            cmd = ("mvr", value)
            self.send_command(cmd)

    def load_rel(self):
        value, ok = QInputDialog.getText(self, "Load Relative", "Where would you like to load?")
        if ok:
            cmd = ("lpr", value)
            self.send_command(cmd)

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

    """MACRO IMPLEMENTATION"""
    def load_macro(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "macros/", "Text Files (*.txt)")
        content = self.macro_text.toPlainText()
        if file_path:
            new_content = open_file(file_path)
            content += new_content

        self.macro_text.setPlainText(content)

    def save_macro(self):
        txt = self.macro_text.toPlainText()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Macro", "/macros/", "Text Files (*.txt);;All Files (*)")
        if file_path:
            with open(f"{file_path}.txt", "w") as file:
                file.write(txt)

    def get_macro_text(self):
        steps = self.macro_text.toPlainText().strip().split("\n")
        if steps[0] == '' and len(steps) == 1:
            # This means there was no macro command entered in list
            return None
        else:
            return steps

    def step_through_macro(self):
        macro_steps = self.get_macro_text()
        if macro_steps:
            command = macro_steps[0].split()
            params = tuple(command)
            self.log_sent_messages(params)
            self.serial.transmit_queue(*params)
            self.repopulate_macro(macro_steps[1:])

    def run_macro(self):
        #ToDo: When sending a command make sure to set the callback to allow the next command to be sent
        self.macro_list = self.get_macro_text()
        if self.macro_list:
            self.macro_list_copy = self.macro_list.copy()
            if self.ui.run_variable_rb.isChecked():
                self.ui.run_count.setText(f"Run Count: 1/{self.number_of_runs}")
            self.manage_macro()

    def set_number_of_runs(self):
        if self.ui.run_once_rb.isChecked():
            self.number_of_runs = 1
        elif self.ui.run_variable_rb.isChecked():
            try:
                self.number_of_runs = int(self.ui.variable_amount_value.text())
                self.ui.run_count.setText(f"Run Count: 0/{self.number_of_runs}")
            except ValueError:
                print("value must be int")

    def reset_macro(self):
        self.number_of_runs -= 1
        self.repopulate_macro(self.macro_list_copy)
        self.macro_list = self.macro_list_copy.copy()
        if self.ui.run_variable_rb.isChecked():
            total = int(self.ui.variable_amount_value.text())
            self.ui.run_count.setText(f"Run Count: {total - self.number_of_runs}/{total}")

    def manage_macro(self, *args, **kwargs):
        if len(self.macro_list) == 0:
            self.reset_macro()

        if self.ui.run_forever_rb.isChecked() or self.number_of_runs > 0:
            self.repopulate_macro(self.macro_list)
            self.execute_task(macro_tasks=self.macro_list)
        else:
            self.set_number_of_runs()
            return

    def execute_task(self, *args, **kwargs):
        if "macro_tasks" in kwargs:
            tasks = kwargs.get("macro_tasks")
            cmd = tasks.pop(0).rstrip()
            cmd = tuple(map(str, cmd.split(" ")))
            if "end" in cmd:
                print("end is command")
                cmd = tasks.pop(0).rstrip()
                cmd = tuple(map(str, cmd.split(" ")))
            elif "loop" in cmd:
                self.loop_iterations = int(cmd[1])
                self.start_loop(tasks)
                return

            self.callbacks.append(self.manage_macro)
        elif "loop_tasks" in kwargs:
            tasks = kwargs.get("loop_tasks")
            cmd = tasks.pop(0).rstrip()
            cmd = tuple(map(str, cmd.split(" ")))
        else:
            print("No tasks defined")
            return
        self.serial.node_id = cmd[0]
        self.serial.transmit_queue(*cmd, callback=True)
        self.log_sent_messages(cmd)

    def repopulate_macro(self, macro_steps):
        macro = ""
        for macro_step in macro_steps:
            macro += macro_step + "\n"

        self.macro_text.setText(macro)

    def start_loop(self, tasks):
        cmd = tasks.pop(0)
        while "end" not in cmd:
            self.loop.append(cmd)
            cmd = tasks.pop(0)
        self.macro_list.insert(0, cmd)
        self.loop_copy = self.loop.copy()
        self.manage_loop()

    def manage_loop(self, *args, **kwargs):
        if len(self.loop) == 0:
            self.loop_iterations -= 1
            if self.loop_iterations >= 1:
                self.loop = self.loop_copy.copy()

        if self.loop_iterations >= 1:
            if (self.loop_iterations - 1 == 0) and (len(self.loop) - 1 == 0):
                self.callbacks.append(self.manage_macro)
            else:
                self.callbacks.append(self.manage_loop)

            self.execute_task(loop_tasks=self.loop)
            self.repopulate_loop()

    def repopulate_loop(self):
        tasks = self.loop.copy() + self.macro_list.copy()
        self.repopulate_macro(tasks)

    """END OF MACRO IMPLEMENTATION"""

    """ SETTINGS IMPLEMENTATION """
    def selected_node_change(self, node_id, get_values=False):
        if get_values:
            sn, vn = self.node_manager.get_config_values(node_id)
            self.set_serial_number(sn)
            self.set_version_number(vn)
            stage = self.node_manager.get_stage_values(node_id)
            self.update_stage_values(stage)
            pid = self.node_manager.get_pid_values(node_id)
            self.update_pid_values(pid)
            motion = self.node_manager.get_motion_values(node_id)
            self.update_motion_values(motion)
            self.update_jog_values()
            advanced = self.node_manager.get_advanced_values(node_id)
            self.update_advanced_values(advanced)

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
        self.callbacks.append(self.update_stage_values)
        self.send_command(("stg",), callback=True)

    def update_stage_values(self, *args, **kwargs):
        node_id = self.node_manager.current_node_id
        node = self.node_manager.get_stage(node_id)
        stage_type, travel_unt, gh, tpi, cpr = "Linear", "encoder_counts", 0, 0, 0
        try:
            values = args[0].split(",")
            values = [v.strip() for v in values if v.strip()]
            stage_type, travel_unt, gh, tpi, cpr = values
        except ValueError as ve:
            logger.error(f"ValueError in update_stage_values: {ve}. Args: {values}")

        for index in range(self.ui.stage_type_combo.count()):
            if stage_type == self.ui.stage_type_combo.itemText(index):
                self.ui.stage_type_combo.setCurrentIndex(index)
                node.update({"Stage": index})

        for index in range(self.ui.travel_unit_combo.count()):
            if travel_unt == self.ui.travel_unit_combo.itemText(index):
                self.ui.travel_unit_combo.setCurrentIndex(index)
                node.update({"Travel": index})

        self.ui.gh_value_label.setText(f"GH: {gh}")
        node.update({"GH": gh})
        self.ui.tpi_value_label.setText(f"TPI: {tpi}")
        node.update({"TPI": tpi})
        self.ui.cpr_value_label.setText(f"CPR: {cpr}")
        node.update({"CPR": cpr})

    def update_unit_travel(self, *args, **kwargs):
        node_id = self.node_manager.current_node_id
        node = self.node_manager.get_stage(node_id)
        unit_travel = args[0]
        for index in range(self.ui.travel_unit_combo.count()):
            if unit_travel == self.ui.travel_unit_combo.itemText(index):
                self.ui.travel_unit_combo.setCurrentIndex(index)
                node.update({"Travel": index})

    def set_stage_type(self):
        index = self.ui.stage_type_combo.currentIndex() + 1
        self.send_command((f"sst {index}",))
        node_id = self.node_manager.current_node_id
        node = self.node_manager.get_stage(node_id)
        node.update({"Stage": f"{index}"})

    def set_unit_travel(self):
        index = self.ui.travel_unit_combo.currentIndex() + 1
        self.send_command((f"sut {index}",))
        node_id = self.node_manager.current_node_id
        node = self.node_manager.get_stage(node_id)
        node.update({"Travel": f"{index}"})

    def set_stage_gh(self):
        try:
            gh = int(self.ui.GH_input.text())
            self.send_command((f"ghr {gh}",))
            self.ui.gh_value_label.setText(f"GH: {gh}")
            node_id = self.node_manager.current_node_id
            node = self.node_manager.get_stage(node_id)
            node.update({"GH": gh})
        except ValueError:
            logger.error(f"Value must be int. Value received: {self.ui.GH_input.text()}")

    def set_stage_tpi(self):
        try:
            tpi = int(self.ui.TPI_input.text())
            self.send_command((f"tpi {tpi}",))
            self.ui.tpi_value_label.setText(f"TPI: {tpi}")
            node_id = self.node_manager.current_node_id
            node = self.node_manager.get_stage(node_id)
            node.update({"TPI": tpi})
        except ValueError:
            logger.error(f"Value must be int. Value received: {self.ui.TPI_input.text()}")

    def set_stage_cpr(self):
        try:
            cpr = int(self.ui.CPR_input.text())
            self.send_command((f"cpr {cpr}",))
            self.ui.cpr_value_label.setText(f"CPR: {cpr}")
            node_id = self.node_manager.current_node_id
            node = self.node_manager.get_stage(node_id)
            node.update({"CPR": cpr})
        except ValueError:
            logger.error(f"Value must be int. Value received: {self.ui.CPR_input.text()}")

    def get_pid_values(self):
        self.callbacks.append(self.update_pid_values)
        self.send_command(("pid",), callback=True)

    def update_pid_values(self, *args, **kwargs):
        node_id = self.node_manager.current_node_id
        node = self.node_manager.get_pid(node_id)
        kp, ki, kd, int_lmt, sample = 0, 0, 0, 0, 0
        try:
            values = args[0].split(",")
            values = [v.strip() for v in values if v.strip()]
            kp, ki, kd, int_lmt, sample = values
        except ValueError as ve:
            logger.error(f"ValueError in update_pid_values: {ve}. Args: {args}")

        self.ui.kp_value_label.setText(f"KP: {kp}")
        node.update({"KP": kp})
        self.ui.ki_value_label.setText(f"KI: {ki}")
        node.update({"KI": ki})
        self.ui.kd_value_label.setText(f"KD: {kd}")
        node.update({"KD": kd})
        self.ui.int_lmt_value_label.setText(f"Integrator Lmt: {int_lmt}")
        node.update({"Int": int_lmt})
        self.ui.sample_rate_value_label.setText(f"Sample Rate: {sample}")
        node.update({"Rate": sample})

    def set_kp(self):
        try:
            kp = float(self.ui.kp_input.text())
            self.send_command((f"skp {kp}",))
            self.ui.kp_value_label.setText(f"KP: {kp}")
            node_id = self.node_manager.current_node_id
            node = self.node_manager.get_pid(node_id)
            node.update({"KP": kp})
        except ValueError:
            logger.error(f"Value must be int. Value received: {self.ui.kp_input.text()}")

    def set_ki(self):
        try:
            ki = float(self.ui.ki_input.text())
            self.send_command((f"ski {ki}",))
            self.ui.ki_value_label.setText(f"KI: {ki}")
            node_id = self.node_manager.current_node_id
            node = self.node_manager.get_pid(node_id)
            node.update({"KI": ki})
        except ValueError:
            logger.error(f"Value must be int. Value received: {self.ui.ki_input.text()}")

    def set_kd(self):
        try:
            kd = float(self.ui.kd_input.text())
            self.send_command((f"skd {kd}",))
            self.ui.kd_value_label.setText(f"KD: {kd}")
            node_id = self.node_manager.current_node_id
            node = self.node_manager.get_pid(node_id)
            node.update({"KD": kd})
        except ValueError:
            logger.error(f"Value must be int. Value received: {self.ui.kd_input.text()}")

    def set_integrator(self):
        try:
            integrator = int(self.ui.int_lmt_input.text())
            self.send_command((f"ilm {integrator}",))
            self.ui.int_lmt_value_label.setText(f"Int Lmt: {integrator}")
            node_id = self.node_manager.current_node_id
            node = self.node_manager.get_pid(node_id)
            node.update({"Int": integrator})
        except ValueError:
            logger.error(f"Value must be int. Value received: {self.ui.int_lmt_input.text()}")

    def set_sample_rate(self):
        try:
            sample_rate = int(self.ui.sample_rate_input.text())
            self.send_command((f"spl {sample_rate}",))
            self.ui.sample_rate_value_label.setText(f"Sample Rate: {sample_rate}")
            node_id = self.node_manager.current_node_id
            node = self.node_manager.get_pid(node_id)
            node.update({"Rate": sample_rate})
        except ValueError:
            logger.error(f"Value must be int. Value received: {self.ui.sample_rate_input.text()}")

    def get_motion_values(self):
        self.callbacks.append(self.update_motion_values)
        self.send_command(("prf",), callback=True)

    def update_motion_values(self, *args, **kwargs):
        accel, vel, decel, err = None, None, None, None
        node_id = self.node_manager.current_node_id
        node = self.node_manager.get_motion(node_id)
        try:
            values = args[0].split(",")
            values = [v.strip() for v in values if v.strip()]
            accel, vel, decel, err = values
        except ValueError as ve:
            logger.error(f"Value Error in update_motion_values: {ve}. Values: {values}")

        self.ui.accel_value_label.setText(f"Acceleration: {accel}")
        node.update({"Accel": accel})
        self.ui.vel_value_label.setText(f"Velocity: {vel}")
        node.update({"Velo": vel})
        self.ui.decel_value_label.setText(f"Deceleration: {decel}")
        node.update({"Decel": decel})
        self.ui.err_value_label.setText(f"Error Limit: {err}")
        node.update({"Error": err})

    def update_jog_values(self):
        node_id = self.node_manager.current_node_id
        node = self.node_manager.get_motion(node_id)
        self.ui.jog_label.setText(f"Jog: {node["JogValue"]}")
        self.ui.hs_jog_label.setText(f"HS Jog: {node["HSValue"]}")

    def set_motion_accel(self):
        try:
            accel = int(self.ui.accel_input.text())
            self.send_command((f"acc {accel}",))
            self.ui.accel_value_label.setText(f"Acceleration: {accel}")
            node_id = self.node_manager.current_node_id
            node = self.node_manager.get_motion(node_id)
            node.update({"Accel": accel})
        except ValueError:
            logger.error(f"Value must be int. Value received: {self.ui.accel_input.text()}")

    def set_motion_vel(self):
        try:
            vel = int(self.ui.vel_input.text())
            self.send_command((f"vel {vel}",))
            self.ui.vel_value_label.setText(f"Velocity: {vel}")
            node_id = self.node_manager.current_node_id
            node = self.node_manager.get_motion(node_id)
            node.update({"Velo": vel})
        except ValueError:
            logger.error(f"Value must be int. Value received: {self.ui.vel_input.text()}")

    def set_motion_decel(self):
        try:
            decel = int(self.ui.decel_input.text())
            self.send_command((f"dec {decel}",))
            self.ui.decel_value_label.setText(f"Deceleration: {decel}")
            node_id = self.node_manager.current_node_id
            node = self.node_manager.get_motion(node_id)
            node.update({"Decel": decel})
        except ValueError:
            logger.error(f"Value must be int. Value received: {self.ui.decel_input.text()}")

    def set_motion_err(self):
        try:
            err = int(self.ui.err_input.text())
            self.send_command((f"erl {err}",))
            self.ui.err_value_label.setText(f"Error Limit: {err}")
            node_id = self.node_manager.current_node_id
            node = self.node_manager.get_motion(node_id)
            node.update({"Error": err})
        except ValueError:
            logger.error(f"Value must be int. Value received: {self.ui.err_input.text()}")

    def set_jog(self):
        node = self.node_manager.get_motion(self.comboBox.currentText())
        try:
            jog = int(self.ui.jog_input.text())
            node["JogValue"] = str(jog)
            self.ui.jog_label.setText(f"Jog: {jog}")
            motor_stat = self.motor_stats[self.comboBox.currentIndex()]
            motor_stat.set_jog()
        except ValueError:
            logger.error(f"Value must be int. Value received: {self.ui.jog_input.text()}")

    def set_hs_jog(self):
        node = self.node_manager.get_motion(self.comboBox.currentText())
        try:
            hs_jog = int(self.ui.hs_jog_input.text())
            node["HSValue"] = str(hs_jog)
            self.ui.hs_jog_label.setText(f"HS Jog: {hs_jog}")
            motor_stat = self.motor_stats[self.comboBox.currentIndex()]
            motor_stat.set_jog()
        except ValueError:
            logger.error(f"Value must be int. Value received: {self.ui.hs_jog_input.text()}")

    def get_advanced_values(self):
        self.callbacks.append(self.update_advanced_values)
        self.send_command(("swl",), callback=True)


    def update_advanced_values(self, *args, **kwargs):
        lower, upper = "0", "0"
        try:
            print(args)
            values = args[0].split(",")
            values = [v.strip() for v in values if v.strip()]
            lower, upper = values
        except Exception as e:
            print(e)

        self.ui.lower_limit_value.setText(f"Lower Limit: {lower}")
        self.ui.upper_limit_value.setText(f"Upper Limit: {upper}")


    def set_lower_limit(self):
        limit = int(self.ui.lower_limit_input.text())
        self.send_command((f"sll {limit}",))
        self.ui.lower_limit_value.setText(f"Lower Limit: {limit}")
        node_id = self.node_manager.current_node_id
        node = self.node_manager.get_advanced(node_id)
        node.update({"Lower": limit})

    def set_upper_limit(self):
        limit = int(self.ui.upper_limit_input.text())
        self.send_command((f"slu {limit}",))
        self.ui.upper_limit_value.setText(f"Upper Limit: {limit}")
        node_id = self.node_manager.current_node_id
        node = self.node_manager.get_advanced(node_id)
        node.update({"Upper": limit})

    def set_tolerance(self):
        tolerance = int(self.ui.pos_tolerance_input.text())
        self.send_command((f"tol {tolerance}",))
        self.ui.pos_tolerance_value.setText(f"Position Tolerance: {tolerance}")
        node_id = self.node_manager.current_node_id
        node = self.node_manager.get_advanced(node_id)
        node.update({"Tolerance": tolerance})


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
        pass

    def update_node_motor_values(self, node_id, values):
        node_index = self.node_index.get(node_id)
        if node_index is not None and node_index >= 0:
            motor_stat = self.motor_stats[node_index]
            motor_stat.update_motor_values(values)

    def add_node(self, node_id):
        self.comboBox.addItem(node_id)
        self.node_manager.add_node(node_id)
        self.node_index.update({node_id: self.comboBox.count() -1 })
        motor_stat = MotorStats(self, node_id)
        self.motor_stats.append(motor_stat)
        self.repopulate_layout()


    def remove_node(self, node_index):
        self.comboBox.removeItem(node_index)
        self.node_manager.remove_node(node_index)
        del self.motor_stats[node_index]
        self.repopulate_layout()

    def repopulate_layout(self):
        clear_layout(self.ui.system_monitor.layout(), False)
        for motor_stat in self.motor_stats:
            self.ui.system_monitor.layout().addWidget(motor_stat)
        self.ui.system_monitor.layout().addItem(self.verticalSpacer)

    def update_node_id(self, index, node_value):
        self.comboBox.setItemText(index, node_value)
        motor_stat = self.motor_stats[index]
        motor_stat.set_group_box_title(node_value)
        cmd = ("adr", node_value)
        self.send_command(cmd)
        self.serial.node_id = node_value
        self.node_manager.update_node_id(node_value)

    def selected_new_node(self):
        node_id = self.comboBox.currentText()
        self.serial.node_id = node_id
        self.node_manager.current_node_id = node_id
        self.selected_node_change(node_id, True)

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

    def log_received_messages(self, message):
        self.ui.com_bus_table.insertRow(0)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        items = (f"Node Id: {self.node_manager.current_node_id}", message, timestamp)
        for col, value in zip(range(self.column_count), items):
            item = QTableWidgetItem(str(value))
            self.ui.com_bus_table.setItem(0, col, item)

    def closeEvent(self, event):
        self.serial.close()
        QApplication.closeAllWindows()

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler('logs/info.log', maxBytes=10240, backupCount=3)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Application started")

    try:
        app = QApplication(sys.argv)
        app.setStyleSheet(Path(f"Diffnes-Gold.qss").read_text())
        widget = MainWindow(logger)
        widget.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.exception("Main crashed. Error: %s", e)
    finally:
        logger.info("Application shutdown\r\n")
