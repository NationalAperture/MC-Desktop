# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'connection_form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QLabel, QListWidget, QListWidgetItem, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget)

class Ui_Connection_Form(object):
    def setupUi(self, Connection_Form):
        if not Connection_Form.objectName():
            Connection_Form.setObjectName(u"Connection_Form")
        Connection_Form.resize(504, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Connection_Form.sizePolicy().hasHeightForWidth())
        Connection_Form.setSizePolicy(sizePolicy)
        Connection_Form.setMinimumSize(QSize(504, 600))
        Connection_Form.setMaximumSize(QSize(504, 600))
        self.verticalLayout_2 = QVBoxLayout(Connection_Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(Connection_Form)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.baud_rates = QComboBox(self.groupBox)
        self.baud_rates.addItem("")
        self.baud_rates.addItem("")
        self.baud_rates.addItem("")
        self.baud_rates.addItem("")
        self.baud_rates.addItem("")
        self.baud_rates.addItem("")
        self.baud_rates.setObjectName(u"baud_rates")
        font = QFont()
        font.setPointSize(13)
        self.baud_rates.setFont(font)

        self.gridLayout_2.addWidget(self.baud_rates, 2, 1, 1, 1)

        self.connect_btn = QPushButton(self.groupBox)
        self.connect_btn.setObjectName(u"connect_btn")
        self.connect_btn.setMinimumSize(QSize(0, 50))
        font1 = QFont()
        font1.setPointSize(13)
        font1.setBold(True)
        font1.setItalic(True)
        self.connect_btn.setFont(font1)

        self.gridLayout_2.addWidget(self.connect_btn, 3, 0, 1, 2)

        self.search_ports_btn = QPushButton(self.groupBox)
        self.search_ports_btn.setObjectName(u"search_ports_btn")
        self.search_ports_btn.setMinimumSize(QSize(0, 50))
        self.search_ports_btn.setFont(font1)

        self.gridLayout_2.addWidget(self.search_ports_btn, 0, 0, 1, 2)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setFont(font1)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label, 2, 0, 1, 1)

        self.scrollArea = QScrollArea(self.groupBox)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 460, 150))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.port_list = QListWidget(self.scrollAreaWidgetContents)
        self.port_list.setObjectName(u"port_list")

        self.verticalLayout.addWidget(self.port_list)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_2.addWidget(self.scrollArea, 1, 0, 1, 2)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.groupBox_3 = QGroupBox(Connection_Form)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setMaximumSize(QSize(16777215, 250))
        self.gridLayout_3 = QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.to_node_IDNs_cb = QComboBox(self.groupBox_3)
        self.to_node_IDNs_cb.setObjectName(u"to_node_IDNs_cb")

        self.gridLayout_3.addWidget(self.to_node_IDNs_cb, 2, 1, 1, 1)

        self.from_node_IDNs_cb = QComboBox(self.groupBox_3)
        self.from_node_IDNs_cb.setObjectName(u"from_node_IDNs_cb")

        self.gridLayout_3.addWidget(self.from_node_IDNs_cb, 2, 0, 1, 1)

        self.add_node_btn = QPushButton(self.groupBox_3)
        self.add_node_btn.setObjectName(u"add_node_btn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.add_node_btn.sizePolicy().hasHeightForWidth())
        self.add_node_btn.setSizePolicy(sizePolicy1)
        font2 = QFont()
        font2.setPointSize(13)
        font2.setBold(True)
        font2.setItalic(False)
        self.add_node_btn.setFont(font2)

        self.gridLayout_3.addWidget(self.add_node_btn, 0, 2, 1, 2)

        self.update_node_btn = QPushButton(self.groupBox_3)
        self.update_node_btn.setObjectName(u"update_node_btn")
        sizePolicy1.setHeightForWidth(self.update_node_btn.sizePolicy().hasHeightForWidth())
        self.update_node_btn.setSizePolicy(sizePolicy1)

        self.gridLayout_3.addWidget(self.update_node_btn, 2, 2, 1, 2)

        self.remove_node_btn = QPushButton(self.groupBox_3)
        self.remove_node_btn.setObjectName(u"remove_node_btn")
        sizePolicy1.setHeightForWidth(self.remove_node_btn.sizePolicy().hasHeightForWidth())
        self.remove_node_btn.setSizePolicy(sizePolicy1)

        self.gridLayout_3.addWidget(self.remove_node_btn, 1, 2, 1, 2)

        self.add_node_IDNs_cb = QComboBox(self.groupBox_3)
        self.add_node_IDNs_cb.addItem("")
        self.add_node_IDNs_cb.addItem("")
        self.add_node_IDNs_cb.addItem("")
        self.add_node_IDNs_cb.addItem("")
        self.add_node_IDNs_cb.addItem("")
        self.add_node_IDNs_cb.addItem("")
        self.add_node_IDNs_cb.addItem("")
        self.add_node_IDNs_cb.addItem("")
        self.add_node_IDNs_cb.addItem("")
        self.add_node_IDNs_cb.addItem("")
        self.add_node_IDNs_cb.addItem("")
        self.add_node_IDNs_cb.setObjectName(u"add_node_IDNs_cb")
        self.add_node_IDNs_cb.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.gridLayout_3.addWidget(self.add_node_IDNs_cb, 0, 1, 1, 1)

        self.remove_node_IDNs_cb = QComboBox(self.groupBox_3)
        self.remove_node_IDNs_cb.setObjectName(u"remove_node_IDNs_cb")

        self.gridLayout_3.addWidget(self.remove_node_IDNs_cb, 1, 1, 1, 1)


        self.verticalLayout_2.addWidget(self.groupBox_3)


        self.retranslateUi(Connection_Form)

        QMetaObject.connectSlotsByName(Connection_Form)
    # setupUi

    def retranslateUi(self, Connection_Form):
        Connection_Form.setWindowTitle(QCoreApplication.translate("Connection_Form", u"Connections", None))
        self.groupBox.setTitle("")
        self.baud_rates.setItemText(0, QCoreApplication.translate("Connection_Form", u"9600", None))
        self.baud_rates.setItemText(1, QCoreApplication.translate("Connection_Form", u"14400", None))
        self.baud_rates.setItemText(2, QCoreApplication.translate("Connection_Form", u"19200", None))
        self.baud_rates.setItemText(3, QCoreApplication.translate("Connection_Form", u"38400", None))
        self.baud_rates.setItemText(4, QCoreApplication.translate("Connection_Form", u"57600", None))
        self.baud_rates.setItemText(5, QCoreApplication.translate("Connection_Form", u"115200", None))

        self.connect_btn.setText(QCoreApplication.translate("Connection_Form", u"Open Port", None))
        self.search_ports_btn.setText(QCoreApplication.translate("Connection_Form", u"Scan Ports", None))
        self.label.setText(QCoreApplication.translate("Connection_Form", u"Set Baud Rate:", None))
        self.groupBox_3.setTitle("")
        self.add_node_btn.setText(QCoreApplication.translate("Connection_Form", u"Add Selected", None))
        self.update_node_btn.setText(QCoreApplication.translate("Connection_Form", u"Change Selected", None))
        self.remove_node_btn.setText(QCoreApplication.translate("Connection_Form", u"Remove Selected", None))
        self.add_node_IDNs_cb.setItemText(0, QCoreApplication.translate("Connection_Form", u"1", None))
        self.add_node_IDNs_cb.setItemText(1, QCoreApplication.translate("Connection_Form", u"2", None))
        self.add_node_IDNs_cb.setItemText(2, QCoreApplication.translate("Connection_Form", u"3", None))
        self.add_node_IDNs_cb.setItemText(3, QCoreApplication.translate("Connection_Form", u"4", None))
        self.add_node_IDNs_cb.setItemText(4, QCoreApplication.translate("Connection_Form", u"5", None))
        self.add_node_IDNs_cb.setItemText(5, QCoreApplication.translate("Connection_Form", u"6", None))
        self.add_node_IDNs_cb.setItemText(6, QCoreApplication.translate("Connection_Form", u"7", None))
        self.add_node_IDNs_cb.setItemText(7, QCoreApplication.translate("Connection_Form", u"8", None))
        self.add_node_IDNs_cb.setItemText(8, QCoreApplication.translate("Connection_Form", u"9", None))
        self.add_node_IDNs_cb.setItemText(9, QCoreApplication.translate("Connection_Form", u"10", None))
        self.add_node_IDNs_cb.setItemText(10, QCoreApplication.translate("Connection_Form", u"11", None))

    # retranslateUi

