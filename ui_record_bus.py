# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'record_bus.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QLabel, QLineEdit, QRadioButton,
    QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 216)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.whole_table_rb = QRadioButton(Dialog)
        self.whole_table_rb.setObjectName(u"whole_table_rb")
        font = QFont()
        font.setPointSize(15)
        font.setItalic(True)
        self.whole_table_rb.setFont(font)
        self.whole_table_rb.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.whole_table_rb.setChecked(True)

        self.gridLayout.addWidget(self.whole_table_rb, 0, 0, 1, 1)

        self.selected_row_rb = QRadioButton(Dialog)
        self.selected_row_rb.setObjectName(u"selected_row_rb")
        self.selected_row_rb.setEnabled(True)
        self.selected_row_rb.setFont(font)

        self.gridLayout.addWidget(self.selected_row_rb, 0, 1, 1, 1)

        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setEnabled(False)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setEnabled(False)
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.gridLayout.addWidget(self.label_2, 1, 1, 1, 1)

        self.start_row_value = QLineEdit(Dialog)
        self.start_row_value.setObjectName(u"start_row_value")
        self.start_row_value.setEnabled(False)
        font1 = QFont()
        font1.setPointSize(15)
        self.start_row_value.setFont(font1)

        self.gridLayout.addWidget(self.start_row_value, 2, 0, 1, 1)

        self.end_row_value = QLineEdit(Dialog)
        self.end_row_value.setObjectName(u"end_row_value")
        self.end_row_value.setEnabled(False)
        self.end_row_value.setFont(font1)

        self.gridLayout.addWidget(self.end_row_value, 2, 1, 1, 1)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.whole_table_rb.setText(QCoreApplication.translate("Dialog", u"Whole Table", None))
        self.selected_row_rb.setText(QCoreApplication.translate("Dialog", u"Selected Range", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Starting Row", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Ending Row", None))
    # retranslateUi

