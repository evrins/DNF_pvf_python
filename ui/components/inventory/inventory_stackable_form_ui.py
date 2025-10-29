# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'inventory_stackable_form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
)
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QWidget,
)


class Ui_inventory_stackable_form(object):
    def setupUi(self, inventory_stackable_form):
        if not inventory_stackable_form.objectName():
            inventory_stackable_form.setObjectName('inventory_stackable_form')
        inventory_stackable_form.resize(270, 161)
        self.formLayout = QFormLayout(inventory_stackable_form)
        self.formLayout.setObjectName('formLayout')
        self.id_label = QLabel(inventory_stackable_form)
        self.id_label.setObjectName('id_label')

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.id_label)

        self.id_line_edit = QLineEdit(inventory_stackable_form)
        self.id_line_edit.setObjectName('id_line_edit')
        self.id_line_edit.setReadOnly(True)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.id_line_edit)

        self.name_label = QLabel(inventory_stackable_form)
        self.name_label.setObjectName('name_label')

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.name_label)

        self.name_line_edit = QLineEdit(inventory_stackable_form)
        self.name_line_edit.setObjectName('name_line_edit')
        self.name_line_edit.setReadOnly(True)

        self.formLayout.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.name_line_edit
        )

        self.num_label = QLabel(inventory_stackable_form)
        self.num_label.setObjectName('num_label')

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.num_label)

        self.num_spin_box = QSpinBox(inventory_stackable_form)
        self.num_spin_box.setObjectName('num_spin_box')
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.num_spin_box.sizePolicy().hasHeightForWidth())
        self.num_spin_box.setSizePolicy(sizePolicy)
        self.num_spin_box.setMaximum(999999999)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.num_spin_box)

        self.btn_group = QWidget(inventory_stackable_form)
        self.btn_group.setObjectName('btn_group')
        self.horizontalLayout_7 = QHBoxLayout(self.btn_group)
        self.horizontalLayout_7.setObjectName('horizontalLayout_7')
        self.save_btn = QPushButton(self.btn_group)
        self.save_btn.setObjectName('save_btn')

        self.horizontalLayout_7.addWidget(self.save_btn)

        self.reset_btn = QPushButton(self.btn_group)
        self.reset_btn.setObjectName('reset_btn')

        self.horizontalLayout_7.addWidget(self.reset_btn)

        self.delete_btn = QPushButton(self.btn_group)
        self.delete_btn.setObjectName('delete_btn')

        self.horizontalLayout_7.addWidget(self.delete_btn)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.btn_group)

        self.retranslateUi(inventory_stackable_form)

        QMetaObject.connectSlotsByName(inventory_stackable_form)

    # setupUi

    def retranslateUi(self, inventory_stackable_form):
        inventory_stackable_form.setWindowTitle(
            QCoreApplication.translate('inventory_stackable_form', 'Form', None)
        )
        self.id_label.setText(
            QCoreApplication.translate('inventory_stackable_form', 'ID', None)
        )
        self.name_label.setText(
            QCoreApplication.translate('inventory_stackable_form', '\u540d\u79f0', None)
        )
        self.num_label.setText(
            QCoreApplication.translate('inventory_stackable_form', '\u6570\u91cf', None)
        )
        self.save_btn.setText(
            QCoreApplication.translate('inventory_stackable_form', 'Save', None)
        )
        self.reset_btn.setText(
            QCoreApplication.translate('inventory_stackable_form', 'Reset', None)
        )
        self.delete_btn.setText(
            QCoreApplication.translate('inventory_stackable_form', 'Delete', None)
        )

    # retranslateUi
