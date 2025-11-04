# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'motor_stats.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QGroupBox, QLabel, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_Motor_Form(object):
    def setupUi(self, Motor_Form):
        if not Motor_Form.objectName():
            Motor_Form.setObjectName(u"Motor_Form")
        Motor_Form.resize(683, 191)
        self.verticalLayout = QVBoxLayout(Motor_Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.node_id = QGroupBox(Motor_Form)
        self.node_id.setObjectName(u"node_id")
        self.gridLayout = QGridLayout(self.node_id)
        self.gridLayout.setObjectName(u"gridLayout")
        self.volt_value = QLabel(self.node_id)
        self.volt_value.setObjectName(u"volt_value")
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setItalic(True)
        self.volt_value.setFont(font)
        self.volt_value.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.volt_value, 0, 0, 1, 1)

        self.position = QLabel(self.node_id)
        self.position.setObjectName(u"position")
        self.position.setFont(font)

        self.gridLayout.addWidget(self.position, 0, 1, 1, 1)

        self.enable_drive_cb = QCheckBox(self.node_id)
        self.enable_drive_cb.setObjectName(u"enable_drive_cb")
        self.enable_drive_cb.setFont(font)
        self.enable_drive_cb.setChecked(False)

        self.gridLayout.addWidget(self.enable_drive_cb, 0, 2, 1, 1)

        self.hs_jog_cb = QCheckBox(self.node_id)
        self.hs_jog_cb.setObjectName(u"hs_jog_cb")
        self.hs_jog_cb.setFont(font)

        self.gridLayout.addWidget(self.hs_jog_cb, 2, 2, 1, 1)

        self.label = QLabel(self.node_id)
        self.label.setObjectName(u"label")
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)

        self.limit_behavior_cb = QComboBox(self.node_id)
        self.limit_behavior_cb.addItem("")
        self.limit_behavior_cb.addItem("")
        self.limit_behavior_cb.addItem("")
        self.limit_behavior_cb.setObjectName(u"limit_behavior_cb")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.limit_behavior_cb.sizePolicy().hasHeightForWidth())
        self.limit_behavior_cb.setSizePolicy(sizePolicy)
        self.limit_behavior_cb.setFont(font)

        self.gridLayout.addWidget(self.limit_behavior_cb, 2, 1, 1, 1)


        self.verticalLayout.addWidget(self.node_id)


        self.retranslateUi(Motor_Form)

        QMetaObject.connectSlotsByName(Motor_Form)
    # setupUi

    def retranslateUi(self, Motor_Form):
        Motor_Form.setWindowTitle(QCoreApplication.translate("Motor_Form", u"Form", None))
        self.node_id.setTitle(QCoreApplication.translate("Motor_Form", u"GroupBox", None))
        self.volt_value.setText(QCoreApplication.translate("Motor_Form", u"Position:", None))
        self.position.setText(QCoreApplication.translate("Motor_Form", u"0", None))
        self.enable_drive_cb.setText(QCoreApplication.translate("Motor_Form", u"Enable Drive", None))
        self.hs_jog_cb.setText(QCoreApplication.translate("Motor_Form", u"HS Jog", None))
        self.label.setText(QCoreApplication.translate("Motor_Form", u"<html><head/><body><p>Limit Behavior: </p></body></html>", None))
        self.limit_behavior_cb.setItemText(0, QCoreApplication.translate("Motor_Form", u"Offset Stage", None))
        self.limit_behavior_cb.setItemText(1, QCoreApplication.translate("Motor_Form", u"Stop Only", None))
        self.limit_behavior_cb.setItemText(2, QCoreApplication.translate("Motor_Form", u"Off", None))

    # retranslateUi

