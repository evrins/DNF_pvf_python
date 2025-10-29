# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'empty.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    Qt,
)
from PySide6.QtWidgets import QLabel, QVBoxLayout


class Ui_empty(object):
    def setupUi(self, empty):
        if not empty.objectName():
            empty.setObjectName('empty')
        empty.resize(400, 300)
        self.verticalLayout = QVBoxLayout(empty)
        self.verticalLayout.setObjectName('verticalLayout')
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.empty_label = QLabel(empty)
        self.empty_label.setObjectName('empty_label')
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.empty_label)

        self.retranslateUi(empty)

        QMetaObject.connectSlotsByName(empty)

    # setupUi

    def retranslateUi(self, empty):
        empty.setWindowTitle(QCoreApplication.translate('empty', 'Form', None))
        self.empty_label.setText(
            QCoreApplication.translate(
                'empty', '\u9009\u62e9\u7269\u54c1\u7f16\u8f91', None
            )
        )

    # retranslateUi
