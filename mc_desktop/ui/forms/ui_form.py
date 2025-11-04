# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QGridLayout,
    QGroupBox, QHeaderView, QLabel, QLineEdit,
    QMainWindow, QMenuBar, QPushButton, QRadioButton,
    QSizePolicy, QSplitter, QStackedWidget, QStatusBar,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1920, 1080)
        self.actionSystem_Monitor = QAction(MainWindow)
        self.actionSystem_Monitor.setObjectName(u"actionSystem_Monitor")
        font = QFont()
        font.setPointSize(15)
        font.setBold(False)
        font.setItalic(True)
        self.actionSystem_Monitor.setFont(font)
        self.actionBus_Monitor = QAction(MainWindow)
        self.actionBus_Monitor.setObjectName(u"actionBus_Monitor")
        self.actionBus_Monitor.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.verticalLayout_3 = QVBoxLayout(self.page)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.splitter_4 = QSplitter(self.page)
        self.splitter_4.setObjectName(u"splitter_4")
        self.splitter_4.setOrientation(Qt.Orientation.Horizontal)
        self.groupBox = QGroupBox(self.splitter_4)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMaximumSize(QSize(16777215, 16777215))
        font1 = QFont()
        font1.setPointSize(13)
        font1.setBold(True)
        font1.setItalic(True)
        self.groupBox.setFont(font1)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.forward_btn = QPushButton(self.groupBox)
        self.forward_btn.setObjectName(u"forward_btn")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.forward_btn.sizePolicy().hasHeightForWidth())
        self.forward_btn.setSizePolicy(sizePolicy)
        self.forward_btn.setFont(font1)

        self.verticalLayout_2.addWidget(self.forward_btn)

        self.backward_btn = QPushButton(self.groupBox)
        self.backward_btn.setObjectName(u"backward_btn")
        sizePolicy.setHeightForWidth(self.backward_btn.sizePolicy().hasHeightForWidth())
        self.backward_btn.setSizePolicy(sizePolicy)
        self.backward_btn.setFont(font1)

        self.verticalLayout_2.addWidget(self.backward_btn)

        self.set_home_btn = QPushButton(self.groupBox)
        self.set_home_btn.setObjectName(u"set_home_btn")
        sizePolicy.setHeightForWidth(self.set_home_btn.sizePolicy().hasHeightForWidth())
        self.set_home_btn.setSizePolicy(sizePolicy)
        self.set_home_btn.setFont(font1)

        self.verticalLayout_2.addWidget(self.set_home_btn)

        self.front_lmt_btn = QPushButton(self.groupBox)
        self.front_lmt_btn.setObjectName(u"front_lmt_btn")
        sizePolicy.setHeightForWidth(self.front_lmt_btn.sizePolicy().hasHeightForWidth())
        self.front_lmt_btn.setSizePolicy(sizePolicy)
        self.front_lmt_btn.setFont(font1)

        self.verticalLayout_2.addWidget(self.front_lmt_btn)

        self.rear_lmt_btn = QPushButton(self.groupBox)
        self.rear_lmt_btn.setObjectName(u"rear_lmt_btn")
        sizePolicy.setHeightForWidth(self.rear_lmt_btn.sizePolicy().hasHeightForWidth())
        self.rear_lmt_btn.setSizePolicy(sizePolicy)
        self.rear_lmt_btn.setFont(font1)

        self.verticalLayout_2.addWidget(self.rear_lmt_btn)

        self.move_abs_btn = QPushButton(self.groupBox)
        self.move_abs_btn.setObjectName(u"move_abs_btn")
        sizePolicy.setHeightForWidth(self.move_abs_btn.sizePolicy().hasHeightForWidth())
        self.move_abs_btn.setSizePolicy(sizePolicy)
        self.move_abs_btn.setFont(font1)

        self.verticalLayout_2.addWidget(self.move_abs_btn)

        self.load_abs_btn = QPushButton(self.groupBox)
        self.load_abs_btn.setObjectName(u"load_abs_btn")
        sizePolicy.setHeightForWidth(self.load_abs_btn.sizePolicy().hasHeightForWidth())
        self.load_abs_btn.setSizePolicy(sizePolicy)
        self.load_abs_btn.setFont(font1)

        self.verticalLayout_2.addWidget(self.load_abs_btn)

        self.move_rel_btn = QPushButton(self.groupBox)
        self.move_rel_btn.setObjectName(u"move_rel_btn")
        sizePolicy.setHeightForWidth(self.move_rel_btn.sizePolicy().hasHeightForWidth())
        self.move_rel_btn.setSizePolicy(sizePolicy)
        self.move_rel_btn.setFont(font1)

        self.verticalLayout_2.addWidget(self.move_rel_btn)

        self.load_rel_btn = QPushButton(self.groupBox)
        self.load_rel_btn.setObjectName(u"load_rel_btn")
        sizePolicy.setHeightForWidth(self.load_rel_btn.sizePolicy().hasHeightForWidth())
        self.load_rel_btn.setSizePolicy(sizePolicy)
        self.load_rel_btn.setFont(font1)

        self.verticalLayout_2.addWidget(self.load_rel_btn)

        self.move_btn = QPushButton(self.groupBox)
        self.move_btn.setObjectName(u"move_btn")
        sizePolicy.setHeightForWidth(self.move_btn.sizePolicy().hasHeightForWidth())
        self.move_btn.setSizePolicy(sizePolicy)
        self.move_btn.setFont(font1)

        self.verticalLayout_2.addWidget(self.move_btn)

        self.stop_btn = QPushButton(self.groupBox)
        self.stop_btn.setObjectName(u"stop_btn")
        sizePolicy.setHeightForWidth(self.stop_btn.sizePolicy().hasHeightForWidth())
        self.stop_btn.setSizePolicy(sizePolicy)
        self.stop_btn.setFont(font1)

        self.verticalLayout_2.addWidget(self.stop_btn)

        self.splitter_4.addWidget(self.groupBox)
        self.splitter_2 = QSplitter(self.splitter_4)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Orientation.Horizontal)
        self.system_monitor = QGroupBox(self.splitter_2)
        self.system_monitor.setObjectName(u"system_monitor")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.system_monitor.sizePolicy().hasHeightForWidth())
        self.system_monitor.setSizePolicy(sizePolicy1)
        self.system_monitor.setMinimumSize(QSize(0, 0))
        self.system_monitor.setBaseSize(QSize(800, 0))
        self.system_monitor.setFont(font1)
        self.verticalLayout_5 = QVBoxLayout(self.system_monitor)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.splitter_2.addWidget(self.system_monitor)
        self.splitter = QSplitter(self.splitter_2)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.splitter_3 = QSplitter(self.splitter)
        self.splitter_3.setObjectName(u"splitter_3")
        self.splitter_3.setOrientation(Qt.Orientation.Vertical)
        self.macro_group_box = QGroupBox(self.splitter_3)
        self.macro_group_box.setObjectName(u"macro_group_box")
        self.macro_group_box.setFont(font1)
        self.gridLayout_4 = QGridLayout(self.macro_group_box)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.run_variable_rb = QRadioButton(self.macro_group_box)
        self.run_variable_rb.setObjectName(u"run_variable_rb")
        font2 = QFont()
        font2.setPointSize(15)
        font2.setBold(True)
        font2.setItalic(True)
        self.run_variable_rb.setFont(font2)

        self.gridLayout_4.addWidget(self.run_variable_rb, 0, 2, 1, 1)

        self.run_once_rb = QRadioButton(self.macro_group_box)
        self.run_once_rb.setObjectName(u"run_once_rb")
        self.run_once_rb.setFont(font2)
        self.run_once_rb.setChecked(True)

        self.gridLayout_4.addWidget(self.run_once_rb, 0, 0, 1, 1)

        self.load_macro_btn = QPushButton(self.macro_group_box)
        self.load_macro_btn.setObjectName(u"load_macro_btn")
        sizePolicy.setHeightForWidth(self.load_macro_btn.sizePolicy().hasHeightForWidth())
        self.load_macro_btn.setSizePolicy(sizePolicy)

        self.gridLayout_4.addWidget(self.load_macro_btn, 2, 0, 1, 1)

        self.variable_amount_value = QLineEdit(self.macro_group_box)
        self.variable_amount_value.setObjectName(u"variable_amount_value")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.variable_amount_value.sizePolicy().hasHeightForWidth())
        self.variable_amount_value.setSizePolicy(sizePolicy2)

        self.gridLayout_4.addWidget(self.variable_amount_value, 0, 3, 1, 1)

        self.save_macro_btn = QPushButton(self.macro_group_box)
        self.save_macro_btn.setObjectName(u"save_macro_btn")
        self.save_macro_btn.setMinimumSize(QSize(0, 80))

        self.gridLayout_4.addWidget(self.save_macro_btn, 2, 1, 1, 1)

        self.run_forever_rb = QRadioButton(self.macro_group_box)
        self.run_forever_rb.setObjectName(u"run_forever_rb")
        self.run_forever_rb.setFont(font2)

        self.gridLayout_4.addWidget(self.run_forever_rb, 0, 1, 1, 1)

        self.step_macro_btn = QPushButton(self.macro_group_box)
        self.step_macro_btn.setObjectName(u"step_macro_btn")
        self.step_macro_btn.setMinimumSize(QSize(0, 80))

        self.gridLayout_4.addWidget(self.step_macro_btn, 2, 2, 1, 1)

        self.run_count = QLabel(self.macro_group_box)
        self.run_count.setObjectName(u"run_count")

        self.gridLayout_4.addWidget(self.run_count, 0, 4, 1, 1)

        self.run_macro_btn = QPushButton(self.macro_group_box)
        self.run_macro_btn.setObjectName(u"run_macro_btn")
        sizePolicy.setHeightForWidth(self.run_macro_btn.sizePolicy().hasHeightForWidth())
        self.run_macro_btn.setSizePolicy(sizePolicy)
        self.run_macro_btn.setMinimumSize(QSize(0, 80))

        self.gridLayout_4.addWidget(self.run_macro_btn, 2, 3, 1, 2)

        self.gridLayout_4.setColumnStretch(0, 1)
        self.gridLayout_4.setColumnStretch(1, 1)
        self.gridLayout_4.setColumnStretch(2, 1)
        self.gridLayout_4.setColumnStretch(4, 1)
        self.splitter_3.addWidget(self.macro_group_box)
        self.groupBox_4 = QGroupBox(self.splitter_3)
        self.groupBox_4.setObjectName(u"groupBox_4")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy3)
        self.groupBox_4.setMaximumSize(QSize(16777215, 16777215))
        self.groupBox_4.setFont(font1)
        self.gridLayout_3 = QGridLayout(self.groupBox_4)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.com_bus_table = QTableWidget(self.groupBox_4)
        if (self.com_bus_table.columnCount() < 3):
            self.com_bus_table.setColumnCount(3)
        font3 = QFont()
        font3.setPointSize(13)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setFont(font3);
        self.com_bus_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setFont(font3);
        self.com_bus_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.com_bus_table.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.com_bus_table.setObjectName(u"com_bus_table")
        self.com_bus_table.setEnabled(True)
        self.com_bus_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.com_bus_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.com_bus_table.setAlternatingRowColors(True)
        self.com_bus_table.horizontalHeader().setCascadingSectionResizes(True)
        self.com_bus_table.horizontalHeader().setDefaultSectionSize(350)
        self.com_bus_table.horizontalHeader().setStretchLastSection(True)

        self.gridLayout_3.addWidget(self.com_bus_table, 0, 0, 1, 1)

        self.splitter_3.addWidget(self.groupBox_4)
        self.splitter.addWidget(self.splitter_3)
        self.splitter_2.addWidget(self.splitter)
        self.splitter_4.addWidget(self.splitter_2)

        self.verticalLayout_3.addWidget(self.splitter_4)

        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.gridLayout_5 = QGridLayout(self.page_2)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.groupBox_10 = QGroupBox(self.page_2)
        self.groupBox_10.setObjectName(u"groupBox_10")
        sizePolicy.setHeightForWidth(self.groupBox_10.sizePolicy().hasHeightForWidth())
        self.groupBox_10.setSizePolicy(sizePolicy)
        self.groupBox_10.setMinimumSize(QSize(0, 350))
        self.groupBox_10.setFont(font1)
        self.gridLayout_8 = QGridLayout(self.groupBox_10)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.VN_label = QLabel(self.groupBox_10)
        self.VN_label.setObjectName(u"VN_label")
        self.VN_label.setFont(font2)

        self.gridLayout_8.addWidget(self.VN_label, 1, 1, 1, 1)

        self.label_11 = QLabel(self.groupBox_10)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setMinimumSize(QSize(0, 30))
        self.label_11.setFont(font2)
        self.label_11.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_8.addWidget(self.label_11, 0, 0, 1, 1)

        self.SN_label = QLabel(self.groupBox_10)
        self.SN_label.setObjectName(u"SN_label")
        self.SN_label.setFont(font2)

        self.gridLayout_8.addWidget(self.SN_label, 0, 1, 1, 1)

        self.label_12 = QLabel(self.groupBox_10)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setMinimumSize(QSize(0, 30))
        self.label_12.setFont(font2)
        self.label_12.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_8.addWidget(self.label_12, 1, 0, 1, 1)

        self.save_config_btn = QPushButton(self.groupBox_10)
        self.save_config_btn.setObjectName(u"save_config_btn")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.save_config_btn.sizePolicy().hasHeightForWidth())
        self.save_config_btn.setSizePolicy(sizePolicy4)
        self.save_config_btn.setMinimumSize(QSize(0, 60))
        self.save_config_btn.setFont(font2)

        self.gridLayout_8.addWidget(self.save_config_btn, 3, 0, 1, 1)

        self.load_config_btn = QPushButton(self.groupBox_10)
        self.load_config_btn.setObjectName(u"load_config_btn")
        sizePolicy4.setHeightForWidth(self.load_config_btn.sizePolicy().hasHeightForWidth())
        self.load_config_btn.setSizePolicy(sizePolicy4)
        self.load_config_btn.setMinimumSize(QSize(0, 60))
        self.load_config_btn.setFont(font2)

        self.gridLayout_8.addWidget(self.load_config_btn, 3, 1, 1, 1)

        self.erase_config_btn = QPushButton(self.groupBox_10)
        self.erase_config_btn.setObjectName(u"erase_config_btn")
        sizePolicy4.setHeightForWidth(self.erase_config_btn.sizePolicy().hasHeightForWidth())
        self.erase_config_btn.setSizePolicy(sizePolicy4)
        self.erase_config_btn.setMinimumSize(QSize(0, 60))
        self.erase_config_btn.setFont(font2)

        self.gridLayout_8.addWidget(self.erase_config_btn, 4, 0, 1, 1)


        self.gridLayout_5.addWidget(self.groupBox_10, 0, 0, 1, 1)

        self.groupBox_14 = QGroupBox(self.page_2)
        self.groupBox_14.setObjectName(u"groupBox_14")
        sizePolicy.setHeightForWidth(self.groupBox_14.sizePolicy().hasHeightForWidth())
        self.groupBox_14.setSizePolicy(sizePolicy)
        self.groupBox_14.setMinimumSize(QSize(0, 350))
        self.groupBox_14.setFont(font2)
        self.gridLayout = QGridLayout(self.groupBox_14)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lower_limit_value = QLabel(self.groupBox_14)
        self.lower_limit_value.setObjectName(u"lower_limit_value")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.lower_limit_value.sizePolicy().hasHeightForWidth())
        self.lower_limit_value.setSizePolicy(sizePolicy5)
        self.lower_limit_value.setFont(font2)

        self.gridLayout.addWidget(self.lower_limit_value, 1, 0, 1, 1)

        self.update_upper_btn = QPushButton(self.groupBox_14)
        self.update_upper_btn.setObjectName(u"update_upper_btn")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.update_upper_btn.sizePolicy().hasHeightForWidth())
        self.update_upper_btn.setSizePolicy(sizePolicy6)
        self.update_upper_btn.setFont(font2)

        self.gridLayout.addWidget(self.update_upper_btn, 3, 3, 1, 1)

        self.update_lower_btn = QPushButton(self.groupBox_14)
        self.update_lower_btn.setObjectName(u"update_lower_btn")
        sizePolicy6.setHeightForWidth(self.update_lower_btn.sizePolicy().hasHeightForWidth())
        self.update_lower_btn.setSizePolicy(sizePolicy6)
        self.update_lower_btn.setFont(font2)

        self.gridLayout.addWidget(self.update_lower_btn, 1, 3, 1, 1)

        self.upper_limit_value = QLabel(self.groupBox_14)
        self.upper_limit_value.setObjectName(u"upper_limit_value")
        sizePolicy5.setHeightForWidth(self.upper_limit_value.sizePolicy().hasHeightForWidth())
        self.upper_limit_value.setSizePolicy(sizePolicy5)
        self.upper_limit_value.setFont(font2)

        self.gridLayout.addWidget(self.upper_limit_value, 3, 0, 1, 1)

        self.upper_limit_input = QLineEdit(self.groupBox_14)
        self.upper_limit_input.setObjectName(u"upper_limit_input")
        sizePolicy2.setHeightForWidth(self.upper_limit_input.sizePolicy().hasHeightForWidth())
        self.upper_limit_input.setSizePolicy(sizePolicy2)
        self.upper_limit_input.setMinimumSize(QSize(0, 0))
        self.upper_limit_input.setFont(font1)

        self.gridLayout.addWidget(self.upper_limit_input, 3, 1, 1, 1)

        self.pos_tolerance_input = QLineEdit(self.groupBox_14)
        self.pos_tolerance_input.setObjectName(u"pos_tolerance_input")
        sizePolicy2.setHeightForWidth(self.pos_tolerance_input.sizePolicy().hasHeightForWidth())
        self.pos_tolerance_input.setSizePolicy(sizePolicy2)
        self.pos_tolerance_input.setMinimumSize(QSize(0, 0))
        self.pos_tolerance_input.setFont(font1)

        self.gridLayout.addWidget(self.pos_tolerance_input, 5, 1, 1, 1)

        self.lower_limit_input = QLineEdit(self.groupBox_14)
        self.lower_limit_input.setObjectName(u"lower_limit_input")
        sizePolicy2.setHeightForWidth(self.lower_limit_input.sizePolicy().hasHeightForWidth())
        self.lower_limit_input.setSizePolicy(sizePolicy2)
        self.lower_limit_input.setMinimumSize(QSize(0, 0))
        self.lower_limit_input.setFont(font1)

        self.gridLayout.addWidget(self.lower_limit_input, 1, 1, 1, 1)

        self.pos_tolerance_value = QLabel(self.groupBox_14)
        self.pos_tolerance_value.setObjectName(u"pos_tolerance_value")
        sizePolicy5.setHeightForWidth(self.pos_tolerance_value.sizePolicy().hasHeightForWidth())
        self.pos_tolerance_value.setSizePolicy(sizePolicy5)
        self.pos_tolerance_value.setFont(font2)

        self.gridLayout.addWidget(self.pos_tolerance_value, 5, 0, 1, 1)

        self.restore_defualt_values_btn = QPushButton(self.groupBox_14)
        self.restore_defualt_values_btn.setObjectName(u"restore_defualt_values_btn")
        sizePolicy6.setHeightForWidth(self.restore_defualt_values_btn.sizePolicy().hasHeightForWidth())
        self.restore_defualt_values_btn.setSizePolicy(sizePolicy6)
        self.restore_defualt_values_btn.setFont(font2)

        self.gridLayout.addWidget(self.restore_defualt_values_btn, 0, 3, 1, 1)

        self.update_pos_tol_btn = QPushButton(self.groupBox_14)
        self.update_pos_tol_btn.setObjectName(u"update_pos_tol_btn")
        sizePolicy6.setHeightForWidth(self.update_pos_tol_btn.sizePolicy().hasHeightForWidth())
        self.update_pos_tol_btn.setSizePolicy(sizePolicy6)
        self.update_pos_tol_btn.setFont(font2)

        self.gridLayout.addWidget(self.update_pos_tol_btn, 5, 3, 1, 1)

        self.refresh_advanced_btn = QPushButton(self.groupBox_14)
        self.refresh_advanced_btn.setObjectName(u"refresh_advanced_btn")
        sizePolicy3.setHeightForWidth(self.refresh_advanced_btn.sizePolicy().hasHeightForWidth())
        self.refresh_advanced_btn.setSizePolicy(sizePolicy3)
        self.refresh_advanced_btn.setFont(font2)

        self.gridLayout.addWidget(self.refresh_advanced_btn, 0, 0, 1, 2)

        self.label_3 = QLabel(self.groupBox_14)
        self.label_3.setObjectName(u"label_3")
        sizePolicy5.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy5)
        self.label_3.setFont(font2)

        self.gridLayout.addWidget(self.label_3, 6, 0, 1, 1)

        self.comboBox = QComboBox(self.groupBox_14)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        sizePolicy2.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy2)
        self.comboBox.setFont(font2)

        self.gridLayout.addWidget(self.comboBox, 6, 1, 1, 1)

        self.pushButton = QPushButton(self.groupBox_14)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy6.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy6)
        self.pushButton.setFont(font2)

        self.gridLayout.addWidget(self.pushButton, 6, 3, 1, 1)


        self.gridLayout_5.addWidget(self.groupBox_14, 1, 1, 1, 1)

        self.groupBox_11 = QGroupBox(self.page_2)
        self.groupBox_11.setObjectName(u"groupBox_11")
        sizePolicy.setHeightForWidth(self.groupBox_11.sizePolicy().hasHeightForWidth())
        self.groupBox_11.setSizePolicy(sizePolicy)
        self.groupBox_11.setMinimumSize(QSize(0, 375))
        self.groupBox_11.setFont(font1)
        self.gridLayout_2 = QGridLayout(self.groupBox_11)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.update_gh_btn = QPushButton(self.groupBox_11)
        self.update_gh_btn.setObjectName(u"update_gh_btn")
        sizePolicy6.setHeightForWidth(self.update_gh_btn.sizePolicy().hasHeightForWidth())
        self.update_gh_btn.setSizePolicy(sizePolicy6)
        self.update_gh_btn.setFont(font2)

        self.gridLayout_2.addWidget(self.update_gh_btn, 3, 3, 1, 1)

        self.TPI_input = QLineEdit(self.groupBox_11)
        self.TPI_input.setObjectName(u"TPI_input")
        sizePolicy2.setHeightForWidth(self.TPI_input.sizePolicy().hasHeightForWidth())
        self.TPI_input.setSizePolicy(sizePolicy2)
        self.TPI_input.setMinimumSize(QSize(0, 0))
        self.TPI_input.setFont(font1)

        self.gridLayout_2.addWidget(self.TPI_input, 4, 2, 1, 1)

        self.GH_input = QLineEdit(self.groupBox_11)
        self.GH_input.setObjectName(u"GH_input")
        sizePolicy2.setHeightForWidth(self.GH_input.sizePolicy().hasHeightForWidth())
        self.GH_input.setSizePolicy(sizePolicy2)
        self.GH_input.setMinimumSize(QSize(0, 0))
        self.GH_input.setFont(font1)

        self.gridLayout_2.addWidget(self.GH_input, 3, 2, 1, 1)

        self.CPR_input = QLineEdit(self.groupBox_11)
        self.CPR_input.setObjectName(u"CPR_input")
        sizePolicy2.setHeightForWidth(self.CPR_input.sizePolicy().hasHeightForWidth())
        self.CPR_input.setSizePolicy(sizePolicy2)
        self.CPR_input.setMinimumSize(QSize(0, 0))
        self.CPR_input.setFont(font1)

        self.gridLayout_2.addWidget(self.CPR_input, 5, 2, 1, 1)

        self.update_cpr_btn = QPushButton(self.groupBox_11)
        self.update_cpr_btn.setObjectName(u"update_cpr_btn")
        sizePolicy6.setHeightForWidth(self.update_cpr_btn.sizePolicy().hasHeightForWidth())
        self.update_cpr_btn.setSizePolicy(sizePolicy6)
        self.update_cpr_btn.setFont(font2)

        self.gridLayout_2.addWidget(self.update_cpr_btn, 5, 3, 1, 1)

        self.update_tpi_btn = QPushButton(self.groupBox_11)
        self.update_tpi_btn.setObjectName(u"update_tpi_btn")
        sizePolicy6.setHeightForWidth(self.update_tpi_btn.sizePolicy().hasHeightForWidth())
        self.update_tpi_btn.setSizePolicy(sizePolicy6)
        self.update_tpi_btn.setFont(font2)

        self.gridLayout_2.addWidget(self.update_tpi_btn, 4, 3, 1, 1)

        self.stage_type_combo = QComboBox(self.groupBox_11)
        self.stage_type_combo.addItem("")
        self.stage_type_combo.addItem("")
        self.stage_type_combo.addItem("")
        self.stage_type_combo.setObjectName(u"stage_type_combo")
        self.stage_type_combo.setFont(font2)

        self.gridLayout_2.addWidget(self.stage_type_combo, 1, 2, 1, 1)

        self.travel_unit_combo = QComboBox(self.groupBox_11)
        self.travel_unit_combo.addItem("")
        self.travel_unit_combo.addItem("")
        self.travel_unit_combo.addItem("")
        self.travel_unit_combo.setObjectName(u"travel_unit_combo")
        self.travel_unit_combo.setFont(font2)

        self.gridLayout_2.addWidget(self.travel_unit_combo, 2, 2, 1, 1)

        self.update_stage_btn = QPushButton(self.groupBox_11)
        self.update_stage_btn.setObjectName(u"update_stage_btn")
        sizePolicy6.setHeightForWidth(self.update_stage_btn.sizePolicy().hasHeightForWidth())
        self.update_stage_btn.setSizePolicy(sizePolicy6)
        self.update_stage_btn.setFont(font2)

        self.gridLayout_2.addWidget(self.update_stage_btn, 1, 3, 1, 1)

        self.update_unit_btn = QPushButton(self.groupBox_11)
        self.update_unit_btn.setObjectName(u"update_unit_btn")
        sizePolicy6.setHeightForWidth(self.update_unit_btn.sizePolicy().hasHeightForWidth())
        self.update_unit_btn.setSizePolicy(sizePolicy6)
        self.update_unit_btn.setFont(font2)

        self.gridLayout_2.addWidget(self.update_unit_btn, 2, 3, 1, 1)

        self.label_2 = QLabel(self.groupBox_11)
        self.label_2.setObjectName(u"label_2")
        sizePolicy5.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy5)
        self.label_2.setMinimumSize(QSize(0, 30))
        self.label_2.setFont(font2)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_2, 1, 1, 1, 1)

        self.label = QLabel(self.groupBox_11)
        self.label.setObjectName(u"label")
        sizePolicy5.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy5)
        self.label.setMinimumSize(QSize(0, 30))
        self.label.setFont(font2)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label, 2, 1, 1, 1)

        self.gh_value_label = QLabel(self.groupBox_11)
        self.gh_value_label.setObjectName(u"gh_value_label")
        sizePolicy5.setHeightForWidth(self.gh_value_label.sizePolicy().hasHeightForWidth())
        self.gh_value_label.setSizePolicy(sizePolicy5)
        self.gh_value_label.setFont(font2)

        self.gridLayout_2.addWidget(self.gh_value_label, 3, 1, 1, 1)

        self.tpi_value_label = QLabel(self.groupBox_11)
        self.tpi_value_label.setObjectName(u"tpi_value_label")
        sizePolicy5.setHeightForWidth(self.tpi_value_label.sizePolicy().hasHeightForWidth())
        self.tpi_value_label.setSizePolicy(sizePolicy5)
        self.tpi_value_label.setFont(font2)

        self.gridLayout_2.addWidget(self.tpi_value_label, 4, 1, 1, 1)

        self.cpr_value_label = QLabel(self.groupBox_11)
        self.cpr_value_label.setObjectName(u"cpr_value_label")
        sizePolicy5.setHeightForWidth(self.cpr_value_label.sizePolicy().hasHeightForWidth())
        self.cpr_value_label.setSizePolicy(sizePolicy5)
        self.cpr_value_label.setFont(font2)

        self.gridLayout_2.addWidget(self.cpr_value_label, 5, 1, 1, 1)

        self.refresh_stage_btn = QPushButton(self.groupBox_11)
        self.refresh_stage_btn.setObjectName(u"refresh_stage_btn")
        sizePolicy6.setHeightForWidth(self.refresh_stage_btn.sizePolicy().hasHeightForWidth())
        self.refresh_stage_btn.setSizePolicy(sizePolicy6)
        self.refresh_stage_btn.setFont(font2)

        self.gridLayout_2.addWidget(self.refresh_stage_btn, 0, 1, 1, 2)


        self.gridLayout_5.addWidget(self.groupBox_11, 0, 1, 1, 1)

        self.groupBox_12 = QGroupBox(self.page_2)
        self.groupBox_12.setObjectName(u"groupBox_12")
        sizePolicy.setHeightForWidth(self.groupBox_12.sizePolicy().hasHeightForWidth())
        self.groupBox_12.setSizePolicy(sizePolicy)
        self.groupBox_12.setMinimumSize(QSize(0, 400))
        self.groupBox_12.setFont(font1)
        self.gridLayout_7 = QGridLayout(self.groupBox_12)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.kp_input = QLineEdit(self.groupBox_12)
        self.kp_input.setObjectName(u"kp_input")
        sizePolicy2.setHeightForWidth(self.kp_input.sizePolicy().hasHeightForWidth())
        self.kp_input.setSizePolicy(sizePolicy2)
        self.kp_input.setMinimumSize(QSize(0, 0))
        self.kp_input.setFont(font1)

        self.gridLayout_7.addWidget(self.kp_input, 1, 1, 1, 1)

        self.kd_value_label = QLabel(self.groupBox_12)
        self.kd_value_label.setObjectName(u"kd_value_label")
        sizePolicy5.setHeightForWidth(self.kd_value_label.sizePolicy().hasHeightForWidth())
        self.kd_value_label.setSizePolicy(sizePolicy5)
        self.kd_value_label.setFont(font2)

        self.gridLayout_7.addWidget(self.kd_value_label, 3, 0, 1, 1)

        self.ki_input = QLineEdit(self.groupBox_12)
        self.ki_input.setObjectName(u"ki_input")
        sizePolicy2.setHeightForWidth(self.ki_input.sizePolicy().hasHeightForWidth())
        self.ki_input.setSizePolicy(sizePolicy2)
        self.ki_input.setMinimumSize(QSize(0, 0))
        self.ki_input.setFont(font1)

        self.gridLayout_7.addWidget(self.ki_input, 2, 1, 1, 1)

        self.kp_update_btn = QPushButton(self.groupBox_12)
        self.kp_update_btn.setObjectName(u"kp_update_btn")
        sizePolicy6.setHeightForWidth(self.kp_update_btn.sizePolicy().hasHeightForWidth())
        self.kp_update_btn.setSizePolicy(sizePolicy6)
        self.kp_update_btn.setFont(font2)

        self.gridLayout_7.addWidget(self.kp_update_btn, 1, 2, 1, 1)

        self.kd_input = QLineEdit(self.groupBox_12)
        self.kd_input.setObjectName(u"kd_input")
        sizePolicy2.setHeightForWidth(self.kd_input.sizePolicy().hasHeightForWidth())
        self.kd_input.setSizePolicy(sizePolicy2)
        self.kd_input.setMinimumSize(QSize(0, 0))
        self.kd_input.setFont(font1)

        self.gridLayout_7.addWidget(self.kd_input, 3, 1, 1, 1)

        self.int_lmt_input = QLineEdit(self.groupBox_12)
        self.int_lmt_input.setObjectName(u"int_lmt_input")
        sizePolicy2.setHeightForWidth(self.int_lmt_input.sizePolicy().hasHeightForWidth())
        self.int_lmt_input.setSizePolicy(sizePolicy2)
        self.int_lmt_input.setMinimumSize(QSize(0, 0))
        self.int_lmt_input.setFont(font1)

        self.gridLayout_7.addWidget(self.int_lmt_input, 4, 1, 1, 1)

        self.ki_update_btn = QPushButton(self.groupBox_12)
        self.ki_update_btn.setObjectName(u"ki_update_btn")
        sizePolicy6.setHeightForWidth(self.ki_update_btn.sizePolicy().hasHeightForWidth())
        self.ki_update_btn.setSizePolicy(sizePolicy6)
        self.ki_update_btn.setFont(font2)

        self.gridLayout_7.addWidget(self.ki_update_btn, 2, 2, 1, 1)

        self.int_lmt_update_btn = QPushButton(self.groupBox_12)
        self.int_lmt_update_btn.setObjectName(u"int_lmt_update_btn")
        sizePolicy6.setHeightForWidth(self.int_lmt_update_btn.sizePolicy().hasHeightForWidth())
        self.int_lmt_update_btn.setSizePolicy(sizePolicy6)
        self.int_lmt_update_btn.setFont(font2)

        self.gridLayout_7.addWidget(self.int_lmt_update_btn, 4, 2, 1, 1)

        self.ki_value_label = QLabel(self.groupBox_12)
        self.ki_value_label.setObjectName(u"ki_value_label")
        sizePolicy5.setHeightForWidth(self.ki_value_label.sizePolicy().hasHeightForWidth())
        self.ki_value_label.setSizePolicy(sizePolicy5)
        self.ki_value_label.setFont(font2)

        self.gridLayout_7.addWidget(self.ki_value_label, 2, 0, 1, 1)

        self.int_lmt_value_label = QLabel(self.groupBox_12)
        self.int_lmt_value_label.setObjectName(u"int_lmt_value_label")
        sizePolicy5.setHeightForWidth(self.int_lmt_value_label.sizePolicy().hasHeightForWidth())
        self.int_lmt_value_label.setSizePolicy(sizePolicy5)
        self.int_lmt_value_label.setFont(font2)

        self.gridLayout_7.addWidget(self.int_lmt_value_label, 4, 0, 1, 1)

        self.refresh_pid_btn = QPushButton(self.groupBox_12)
        self.refresh_pid_btn.setObjectName(u"refresh_pid_btn")
        sizePolicy4.setHeightForWidth(self.refresh_pid_btn.sizePolicy().hasHeightForWidth())
        self.refresh_pid_btn.setSizePolicy(sizePolicy4)
        self.refresh_pid_btn.setFont(font2)

        self.gridLayout_7.addWidget(self.refresh_pid_btn, 0, 0, 1, 2)

        self.kp_value_label = QLabel(self.groupBox_12)
        self.kp_value_label.setObjectName(u"kp_value_label")
        sizePolicy5.setHeightForWidth(self.kp_value_label.sizePolicy().hasHeightForWidth())
        self.kp_value_label.setSizePolicy(sizePolicy5)
        self.kp_value_label.setFont(font2)

        self.gridLayout_7.addWidget(self.kp_value_label, 1, 0, 1, 1)

        self.kd_update_btn = QPushButton(self.groupBox_12)
        self.kd_update_btn.setObjectName(u"kd_update_btn")
        sizePolicy6.setHeightForWidth(self.kd_update_btn.sizePolicy().hasHeightForWidth())
        self.kd_update_btn.setSizePolicy(sizePolicy6)
        self.kd_update_btn.setFont(font2)

        self.gridLayout_7.addWidget(self.kd_update_btn, 3, 2, 1, 1)

        self.sample_rate_update_btn = QPushButton(self.groupBox_12)
        self.sample_rate_update_btn.setObjectName(u"sample_rate_update_btn")
        sizePolicy6.setHeightForWidth(self.sample_rate_update_btn.sizePolicy().hasHeightForWidth())
        self.sample_rate_update_btn.setSizePolicy(sizePolicy6)
        self.sample_rate_update_btn.setFont(font2)

        self.gridLayout_7.addWidget(self.sample_rate_update_btn, 5, 2, 1, 1)

        self.sample_rate_value_label = QLabel(self.groupBox_12)
        self.sample_rate_value_label.setObjectName(u"sample_rate_value_label")
        sizePolicy5.setHeightForWidth(self.sample_rate_value_label.sizePolicy().hasHeightForWidth())
        self.sample_rate_value_label.setSizePolicy(sizePolicy5)
        self.sample_rate_value_label.setFont(font2)

        self.gridLayout_7.addWidget(self.sample_rate_value_label, 5, 0, 1, 1)

        self.sample_rate_input = QLineEdit(self.groupBox_12)
        self.sample_rate_input.setObjectName(u"sample_rate_input")
        sizePolicy2.setHeightForWidth(self.sample_rate_input.sizePolicy().hasHeightForWidth())
        self.sample_rate_input.setSizePolicy(sizePolicy2)
        self.sample_rate_input.setMinimumSize(QSize(0, 0))
        self.sample_rate_input.setFont(font1)

        self.gridLayout_7.addWidget(self.sample_rate_input, 5, 1, 1, 1)


        self.gridLayout_5.addWidget(self.groupBox_12, 0, 2, 1, 1)

        self.groupBox_13 = QGroupBox(self.page_2)
        self.groupBox_13.setObjectName(u"groupBox_13")
        sizePolicy.setHeightForWidth(self.groupBox_13.sizePolicy().hasHeightForWidth())
        self.groupBox_13.setSizePolicy(sizePolicy)
        self.groupBox_13.setMinimumSize(QSize(0, 470))
        self.groupBox_13.setFont(font1)
        self.gridLayout_9 = QGridLayout(self.groupBox_13)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.decel_update_btn = QPushButton(self.groupBox_13)
        self.decel_update_btn.setObjectName(u"decel_update_btn")
        sizePolicy6.setHeightForWidth(self.decel_update_btn.sizePolicy().hasHeightForWidth())
        self.decel_update_btn.setSizePolicy(sizePolicy6)
        self.decel_update_btn.setFont(font2)

        self.gridLayout_9.addWidget(self.decel_update_btn, 3, 2, 1, 1)

        self.jog_label = QLabel(self.groupBox_13)
        self.jog_label.setObjectName(u"jog_label")
        sizePolicy5.setHeightForWidth(self.jog_label.sizePolicy().hasHeightForWidth())
        self.jog_label.setSizePolicy(sizePolicy5)
        self.jog_label.setFont(font2)

        self.gridLayout_9.addWidget(self.jog_label, 5, 0, 1, 1)

        self.hs_jog_label = QLabel(self.groupBox_13)
        self.hs_jog_label.setObjectName(u"hs_jog_label")
        sizePolicy5.setHeightForWidth(self.hs_jog_label.sizePolicy().hasHeightForWidth())
        self.hs_jog_label.setSizePolicy(sizePolicy5)
        self.hs_jog_label.setFont(font2)

        self.gridLayout_9.addWidget(self.hs_jog_label, 6, 0, 1, 1)

        self.hs_jog_input = QLineEdit(self.groupBox_13)
        self.hs_jog_input.setObjectName(u"hs_jog_input")
        sizePolicy2.setHeightForWidth(self.hs_jog_input.sizePolicy().hasHeightForWidth())
        self.hs_jog_input.setSizePolicy(sizePolicy2)
        self.hs_jog_input.setMinimumSize(QSize(200, 0))
        self.hs_jog_input.setFont(font1)

        self.gridLayout_9.addWidget(self.hs_jog_input, 6, 1, 1, 1)

        self.accel_update_btn = QPushButton(self.groupBox_13)
        self.accel_update_btn.setObjectName(u"accel_update_btn")
        sizePolicy6.setHeightForWidth(self.accel_update_btn.sizePolicy().hasHeightForWidth())
        self.accel_update_btn.setSizePolicy(sizePolicy6)
        self.accel_update_btn.setFont(font2)

        self.gridLayout_9.addWidget(self.accel_update_btn, 1, 2, 1, 1)

        self.hs_jog_update_btn = QPushButton(self.groupBox_13)
        self.hs_jog_update_btn.setObjectName(u"hs_jog_update_btn")
        sizePolicy6.setHeightForWidth(self.hs_jog_update_btn.sizePolicy().hasHeightForWidth())
        self.hs_jog_update_btn.setSizePolicy(sizePolicy6)
        self.hs_jog_update_btn.setFont(font2)

        self.gridLayout_9.addWidget(self.hs_jog_update_btn, 6, 2, 1, 1)

        self.jog_update_btn = QPushButton(self.groupBox_13)
        self.jog_update_btn.setObjectName(u"jog_update_btn")
        sizePolicy6.setHeightForWidth(self.jog_update_btn.sizePolicy().hasHeightForWidth())
        self.jog_update_btn.setSizePolicy(sizePolicy6)
        self.jog_update_btn.setFont(font2)

        self.gridLayout_9.addWidget(self.jog_update_btn, 5, 2, 1, 1)

        self.accel_input = QLineEdit(self.groupBox_13)
        self.accel_input.setObjectName(u"accel_input")
        sizePolicy2.setHeightForWidth(self.accel_input.sizePolicy().hasHeightForWidth())
        self.accel_input.setSizePolicy(sizePolicy2)
        self.accel_input.setMinimumSize(QSize(0, 0))
        self.accel_input.setFont(font1)

        self.gridLayout_9.addWidget(self.accel_input, 1, 1, 1, 1)

        self.decel_input = QLineEdit(self.groupBox_13)
        self.decel_input.setObjectName(u"decel_input")
        sizePolicy2.setHeightForWidth(self.decel_input.sizePolicy().hasHeightForWidth())
        self.decel_input.setSizePolicy(sizePolicy2)
        self.decel_input.setMinimumSize(QSize(0, 0))
        self.decel_input.setFont(font1)

        self.gridLayout_9.addWidget(self.decel_input, 3, 1, 1, 1)

        self.decel_value_label = QLabel(self.groupBox_13)
        self.decel_value_label.setObjectName(u"decel_value_label")
        sizePolicy5.setHeightForWidth(self.decel_value_label.sizePolicy().hasHeightForWidth())
        self.decel_value_label.setSizePolicy(sizePolicy5)
        self.decel_value_label.setFont(font2)

        self.gridLayout_9.addWidget(self.decel_value_label, 3, 0, 1, 1)

        self.vel_value_label = QLabel(self.groupBox_13)
        self.vel_value_label.setObjectName(u"vel_value_label")
        sizePolicy5.setHeightForWidth(self.vel_value_label.sizePolicy().hasHeightForWidth())
        self.vel_value_label.setSizePolicy(sizePolicy5)
        self.vel_value_label.setFont(font2)

        self.gridLayout_9.addWidget(self.vel_value_label, 2, 0, 1, 1)

        self.vel_update_btn = QPushButton(self.groupBox_13)
        self.vel_update_btn.setObjectName(u"vel_update_btn")
        sizePolicy6.setHeightForWidth(self.vel_update_btn.sizePolicy().hasHeightForWidth())
        self.vel_update_btn.setSizePolicy(sizePolicy6)
        self.vel_update_btn.setFont(font2)

        self.gridLayout_9.addWidget(self.vel_update_btn, 2, 2, 1, 1)

        self.err_update_btn = QPushButton(self.groupBox_13)
        self.err_update_btn.setObjectName(u"err_update_btn")
        sizePolicy6.setHeightForWidth(self.err_update_btn.sizePolicy().hasHeightForWidth())
        self.err_update_btn.setSizePolicy(sizePolicy6)
        self.err_update_btn.setFont(font2)

        self.gridLayout_9.addWidget(self.err_update_btn, 4, 2, 1, 1)

        self.accel_value_label = QLabel(self.groupBox_13)
        self.accel_value_label.setObjectName(u"accel_value_label")
        sizePolicy5.setHeightForWidth(self.accel_value_label.sizePolicy().hasHeightForWidth())
        self.accel_value_label.setSizePolicy(sizePolicy5)
        self.accel_value_label.setFont(font2)

        self.gridLayout_9.addWidget(self.accel_value_label, 1, 0, 1, 1)

        self.vel_input = QLineEdit(self.groupBox_13)
        self.vel_input.setObjectName(u"vel_input")
        sizePolicy2.setHeightForWidth(self.vel_input.sizePolicy().hasHeightForWidth())
        self.vel_input.setSizePolicy(sizePolicy2)
        self.vel_input.setMinimumSize(QSize(0, 0))
        self.vel_input.setFont(font1)

        self.gridLayout_9.addWidget(self.vel_input, 2, 1, 1, 1)

        self.err_value_label = QLabel(self.groupBox_13)
        self.err_value_label.setObjectName(u"err_value_label")
        sizePolicy5.setHeightForWidth(self.err_value_label.sizePolicy().hasHeightForWidth())
        self.err_value_label.setSizePolicy(sizePolicy5)
        self.err_value_label.setFont(font2)

        self.gridLayout_9.addWidget(self.err_value_label, 4, 0, 1, 1)

        self.jog_input = QLineEdit(self.groupBox_13)
        self.jog_input.setObjectName(u"jog_input")
        sizePolicy2.setHeightForWidth(self.jog_input.sizePolicy().hasHeightForWidth())
        self.jog_input.setSizePolicy(sizePolicy2)
        self.jog_input.setMinimumSize(QSize(0, 0))
        self.jog_input.setFont(font1)

        self.gridLayout_9.addWidget(self.jog_input, 5, 1, 1, 1)

        self.refresh_motion_btn = QPushButton(self.groupBox_13)
        self.refresh_motion_btn.setObjectName(u"refresh_motion_btn")
        sizePolicy4.setHeightForWidth(self.refresh_motion_btn.sizePolicy().hasHeightForWidth())
        self.refresh_motion_btn.setSizePolicy(sizePolicy4)
        self.refresh_motion_btn.setFont(font2)

        self.gridLayout_9.addWidget(self.refresh_motion_btn, 0, 0, 1, 2)

        self.err_input = QLineEdit(self.groupBox_13)
        self.err_input.setObjectName(u"err_input")
        sizePolicy2.setHeightForWidth(self.err_input.sizePolicy().hasHeightForWidth())
        self.err_input.setSizePolicy(sizePolicy2)
        self.err_input.setMinimumSize(QSize(0, 0))
        self.err_input.setFont(font1)

        self.gridLayout_9.addWidget(self.err_input, 4, 1, 1, 1)


        self.gridLayout_5.addWidget(self.groupBox_13, 1, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_2)

        self.verticalLayout.addWidget(self.stackedWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1920, 29))
        font4 = QFont()
        font4.setPointSize(15)
        font4.setItalic(True)
        self.menubar.setFont(font4)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionSystem_Monitor.setText(QCoreApplication.translate("MainWindow", u"System Monitor", None))
        self.actionBus_Monitor.setText(QCoreApplication.translate("MainWindow", u"Bus Monitor", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"COMMANDS", None))
        self.forward_btn.setText(QCoreApplication.translate("MainWindow", u"Forward", None))
        self.backward_btn.setText(QCoreApplication.translate("MainWindow", u"Backward", None))
        self.set_home_btn.setText(QCoreApplication.translate("MainWindow", u"Set Home Position", None))
        self.front_lmt_btn.setText(QCoreApplication.translate("MainWindow", u"Hit Front Limit Switch", None))
        self.rear_lmt_btn.setText(QCoreApplication.translate("MainWindow", u"Hit Rear Limit Switch", None))
        self.move_abs_btn.setText(QCoreApplication.translate("MainWindow", u"Move Absolute Position", None))
        self.load_abs_btn.setText(QCoreApplication.translate("MainWindow", u"Load Absolute Position", None))
        self.move_rel_btn.setText(QCoreApplication.translate("MainWindow", u"Move Reletive Position", None))
        self.load_rel_btn.setText(QCoreApplication.translate("MainWindow", u"Load Reletive Position", None))
        self.move_btn.setText(QCoreApplication.translate("MainWindow", u"Move", None))
        self.stop_btn.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.system_monitor.setTitle(QCoreApplication.translate("MainWindow", u"SYSTEM MONITOR", None))
        self.macro_group_box.setTitle(QCoreApplication.translate("MainWindow", u"MACRO", None))
        self.run_variable_rb.setText(QCoreApplication.translate("MainWindow", u"Run X Amount Of Times", None))
        self.run_once_rb.setText(QCoreApplication.translate("MainWindow", u"Run Once", None))
        self.load_macro_btn.setText(QCoreApplication.translate("MainWindow", u"Load Macro", None))
        self.variable_amount_value.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.save_macro_btn.setText(QCoreApplication.translate("MainWindow", u"Save Macro", None))
        self.run_forever_rb.setText(QCoreApplication.translate("MainWindow", u"Run Forever", None))
        self.step_macro_btn.setText(QCoreApplication.translate("MainWindow", u"Step Through Macro", None))
        self.run_count.setText(QCoreApplication.translate("MainWindow", u"Run Count: 0/2", None))
        self.run_macro_btn.setText(QCoreApplication.translate("MainWindow", u"Run Macro", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"BUS MONITOR", None))
        ___qtablewidgetitem = self.com_bus_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Device", None));
        ___qtablewidgetitem1 = self.com_bus_table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Message", None));
        ___qtablewidgetitem2 = self.com_bus_table.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Time Stamp", None));
        self.groupBox_10.setTitle(QCoreApplication.translate("MainWindow", u"Configuration", None))
        self.VN_label.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Serial Number:", None))
        self.SN_label.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Version Number:", None))
        self.save_config_btn.setText(QCoreApplication.translate("MainWindow", u"Save Configuration", None))
        self.load_config_btn.setText(QCoreApplication.translate("MainWindow", u"Load Configuration", None))
        self.erase_config_btn.setText(QCoreApplication.translate("MainWindow", u"Erase Configuration", None))
        self.groupBox_14.setTitle(QCoreApplication.translate("MainWindow", u"Advanced", None))
        self.lower_limit_value.setText(QCoreApplication.translate("MainWindow", u"Lower Limit: N/A", None))
        self.update_upper_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.update_lower_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.upper_limit_value.setText(QCoreApplication.translate("MainWindow", u"Upper Limit: N/A", None))
        self.upper_limit_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Upper Limit", None))
        self.pos_tolerance_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Position Tolerance", None))
        self.lower_limit_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Lower Limit", None))
        self.pos_tolerance_value.setText(QCoreApplication.translate("MainWindow", u"Pos Tol: N/A", None))
        self.restore_defualt_values_btn.setText(QCoreApplication.translate("MainWindow", u"Restore Defualt Values", None))
        self.update_pos_tol_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.refresh_advanced_btn.setText(QCoreApplication.translate("MainWindow", u"Refresh Advanced Information", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Buad Rate:", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"9600", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"14400", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"19200", None))
        self.comboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"38400", None))
        self.comboBox.setItemText(4, QCoreApplication.translate("MainWindow", u"57600", None))
        self.comboBox.setItemText(5, QCoreApplication.translate("MainWindow", u"115200", None))

        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.groupBox_11.setTitle(QCoreApplication.translate("MainWindow", u"Stage", None))
        self.update_gh_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.TPI_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Turn Per Inch", None))
        self.GH_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Gear Head ", None))
        self.CPR_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Count Per Rev", None))
        self.update_cpr_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.update_tpi_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.stage_type_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"Linear", None))
        self.stage_type_combo.setItemText(1, QCoreApplication.translate("MainWindow", u"Rotory", None))
        self.stage_type_combo.setItemText(2, QCoreApplication.translate("MainWindow", u"Goniometer", None))

        self.travel_unit_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"Encoder Counts", None))
        self.travel_unit_combo.setItemText(1, QCoreApplication.translate("MainWindow", u"Millimeters", None))
        self.travel_unit_combo.setItemText(2, QCoreApplication.translate("MainWindow", u"Inches", None))

        self.update_stage_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.update_unit_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Stage Type:", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Travel Unit:", None))
        self.gh_value_label.setText(QCoreApplication.translate("MainWindow", u"GH: N/A", None))
        self.tpi_value_label.setText(QCoreApplication.translate("MainWindow", u"TPI: N/A", None))
        self.cpr_value_label.setText(QCoreApplication.translate("MainWindow", u"CPR: N/A", None))
        self.refresh_stage_btn.setText(QCoreApplication.translate("MainWindow", u"Refresh Stage Information", None))
        self.groupBox_12.setTitle(QCoreApplication.translate("MainWindow", u"PID", None))
        self.kp_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter KP", None))
        self.kd_value_label.setText(QCoreApplication.translate("MainWindow", u"KD: N/A", None))
        self.ki_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter KI", None))
        self.kp_update_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.kd_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter KD", None))
        self.int_lmt_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Integrator Limit", None))
        self.ki_update_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.int_lmt_update_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.ki_value_label.setText(QCoreApplication.translate("MainWindow", u"KI: N/A", None))
        self.int_lmt_value_label.setText(QCoreApplication.translate("MainWindow", u"Int Lmt: N/A", None))
        self.refresh_pid_btn.setText(QCoreApplication.translate("MainWindow", u"Refresh PID Information", None))
        self.kp_value_label.setText(QCoreApplication.translate("MainWindow", u"KP: N/A", None))
        self.kd_update_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.sample_rate_update_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.sample_rate_value_label.setText(QCoreApplication.translate("MainWindow", u"Rate: N/A", None))
        self.sample_rate_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Sample Rate", None))
        self.groupBox_13.setTitle(QCoreApplication.translate("MainWindow", u"Motion", None))
        self.decel_update_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.jog_label.setText(QCoreApplication.translate("MainWindow", u"Jog: 500", None))
        self.hs_jog_label.setText(QCoreApplication.translate("MainWindow", u"HS Jog: 850", None))
        self.hs_jog_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter High Speed Jog", None))
        self.accel_update_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.hs_jog_update_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.jog_update_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.accel_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Acceleration", None))
        self.decel_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Deceleration", None))
        self.decel_value_label.setText(QCoreApplication.translate("MainWindow", u"Deceleration: N/A", None))
        self.vel_value_label.setText(QCoreApplication.translate("MainWindow", u"Velocity: N/A", None))
        self.vel_update_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.err_update_btn.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.accel_value_label.setText(QCoreApplication.translate("MainWindow", u"Acceleration: N/A", None))
        self.vel_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Velocity", None))
        self.err_value_label.setText(QCoreApplication.translate("MainWindow", u"Error Limit: N/A", None))
        self.jog_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Jog", None))
        self.refresh_motion_btn.setText(QCoreApplication.translate("MainWindow", u"Refresh Motion Information", None))
        self.err_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Error Limit", None))
    # retranslateUi

