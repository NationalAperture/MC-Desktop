# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'connection_form.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QSizePolicy, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_Connection_Form(object):
    def setupUi(self, Connection_Form):
        if not Connection_Form.objectName():
            Connection_Form.setObjectName(u"Connection_Form")
        Connection_Form.resize(504, 522)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Connection_Form.sizePolicy().hasHeightForWidth())
        Connection_Form.setSizePolicy(sizePolicy)
        Connection_Form.setMinimumSize(QSize(504, 522))
        Connection_Form.setMaximumSize(QSize(504, 522))
        self.verticalLayout_4 = QVBoxLayout(Connection_Form)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.tabWidget = QTabWidget(Connection_Form)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_2 = QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(self.tab)
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

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        font1 = QFont()
        font1.setPointSize(13)
        font1.setBold(True)
        font1.setItalic(True)
        self.label.setFont(font1)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label, 2, 0, 1, 1)

        self.port_list = QListWidget(self.groupBox)
        self.port_list.setObjectName(u"port_list")

        self.gridLayout_2.addWidget(self.port_list, 1, 0, 1, 2)

        self.search_ports_btn = QPushButton(self.groupBox)
        self.search_ports_btn.setObjectName(u"search_ports_btn")
        self.search_ports_btn.setMinimumSize(QSize(0, 50))
        self.search_ports_btn.setFont(font1)

        self.gridLayout_2.addWidget(self.search_ports_btn, 0, 0, 1, 2)

        self.connect_btn = QPushButton(self.groupBox)
        self.connect_btn.setObjectName(u"connect_btn")
        self.connect_btn.setMinimumSize(QSize(0, 50))
        self.connect_btn.setFont(font1)

        self.gridLayout_2.addWidget(self.connect_btn, 3, 0, 1, 2)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_3 = QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox_2 = QGroupBox(self.tab_2)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy1)
        self.gridLayout = QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.update_node_btn = QPushButton(self.groupBox_2)
        self.update_node_btn.setObjectName(u"update_node_btn")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.update_node_btn.sizePolicy().hasHeightForWidth())
        self.update_node_btn.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.update_node_btn, 3, 1, 1, 1)

        self.update_node_value = QLineEdit(self.groupBox_2)
        self.update_node_value.setObjectName(u"update_node_value")

        self.gridLayout.addWidget(self.update_node_value, 3, 0, 1, 1)

        self.remove_node_btn = QPushButton(self.groupBox_2)
        self.remove_node_btn.setObjectName(u"remove_node_btn")
        sizePolicy2.setHeightForWidth(self.remove_node_btn.sizePolicy().hasHeightForWidth())
        self.remove_node_btn.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.remove_node_btn, 2, 1, 1, 1)

        self.add_node_btn = QPushButton(self.groupBox_2)
        self.add_node_btn.setObjectName(u"add_node_btn")
        sizePolicy2.setHeightForWidth(self.add_node_btn.sizePolicy().hasHeightForWidth())
        self.add_node_btn.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.add_node_btn, 1, 1, 1, 1)

        self.remove_node_combo = QComboBox(self.groupBox_2)
        self.remove_node_combo.setObjectName(u"remove_node_combo")

        self.gridLayout.addWidget(self.remove_node_combo, 2, 0, 1, 1)

        self.add_node_value = QLineEdit(self.groupBox_2)
        self.add_node_value.setObjectName(u"add_node_value")

        self.gridLayout.addWidget(self.add_node_value, 1, 0, 1, 1)


        self.verticalLayout_3.addWidget(self.groupBox_2)

        self.tabWidget.addTab(self.tab_2, "")

        self.verticalLayout_4.addWidget(self.tabWidget)


        self.retranslateUi(Connection_Form)

        self.tabWidget.setCurrentIndex(0)


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

        self.label.setText(QCoreApplication.translate("Connection_Form", u"Select Baud Rate:", None))
        self.search_ports_btn.setText(QCoreApplication.translate("Connection_Form", u"Search for Ports", None))
        self.connect_btn.setText(QCoreApplication.translate("Connection_Form", u"Connect To Port", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Connection_Form", u"Ports", None))
        self.groupBox_2.setTitle("")
        self.update_node_btn.setText(QCoreApplication.translate("Connection_Form", u"Update Node ID", None))
        self.remove_node_btn.setText(QCoreApplication.translate("Connection_Form", u"Remove Node ID", None))
        self.add_node_btn.setText(QCoreApplication.translate("Connection_Form", u"Add Node ID", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Connection_Form", u"Devices", None))
    # retranslateUi

