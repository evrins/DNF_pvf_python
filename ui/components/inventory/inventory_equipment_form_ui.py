# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'inventory_equipment_form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    QSize,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QWidget,
)


class Ui_inventory_equipment_form(object):
    def setupUi(self, inventory_equipment_form):
        if not inventory_equipment_form.objectName():
            inventory_equipment_form.setObjectName('inventory_equipment_form')
        inventory_equipment_form.resize(305, 588)
        self.formLayout = QFormLayout(inventory_equipment_form)
        self.formLayout.setObjectName('formLayout')
        self.id_label = QLabel(inventory_equipment_form)
        self.id_label.setObjectName('id_label')

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.id_label)

        self.id_line_edit = QLineEdit(inventory_equipment_form)
        self.id_line_edit.setObjectName('id_line_edit')
        self.id_line_edit.setReadOnly(True)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.id_line_edit)

        self.name_label = QLabel(inventory_equipment_form)
        self.name_label.setObjectName('name_label')

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.name_label)

        self.name_line_edit = QLineEdit(inventory_equipment_form)
        self.name_line_edit.setObjectName('name_line_edit')
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.name_line_edit.sizePolicy().hasHeightForWidth()
        )
        self.name_line_edit.setSizePolicy(sizePolicy)
        self.name_line_edit.setReadOnly(True)

        self.formLayout.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.name_line_edit
        )

        self.is_sealed_label = QLabel(inventory_equipment_form)
        self.is_sealed_label.setObjectName('is_sealed_label')

        self.formLayout.setWidget(
            2, QFormLayout.ItemRole.LabelRole, self.is_sealed_label
        )

        self.is_sealed_checkbox = QCheckBox(inventory_equipment_form)
        self.is_sealed_checkbox.setObjectName('is_sealed_checkbox')

        self.formLayout.setWidget(
            2, QFormLayout.ItemRole.FieldRole, self.is_sealed_checkbox
        )

        self.seal_count_label = QLabel(inventory_equipment_form)
        self.seal_count_label.setObjectName('seal_count_label')

        self.formLayout.setWidget(
            3, QFormLayout.ItemRole.LabelRole, self.seal_count_label
        )

        self.seal_count_spin_box = QSpinBox(inventory_equipment_form)
        self.seal_count_spin_box.setObjectName('seal_count_spin_box')
        sizePolicy.setHeightForWidth(
            self.seal_count_spin_box.sizePolicy().hasHeightForWidth()
        )
        self.seal_count_spin_box.setSizePolicy(sizePolicy)
        self.seal_count_spin_box.setMaximum(999999999)

        self.formLayout.setWidget(
            3, QFormLayout.ItemRole.FieldRole, self.seal_count_spin_box
        )

        self.grade_label = QLabel(inventory_equipment_form)
        self.grade_label.setObjectName('grade_label')

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.grade_label)

        self.grade_spin_box = QSpinBox(inventory_equipment_form)
        self.grade_spin_box.setObjectName('grade_spin_box')
        sizePolicy.setHeightForWidth(
            self.grade_spin_box.sizePolicy().hasHeightForWidth()
        )
        self.grade_spin_box.setSizePolicy(sizePolicy)
        self.grade_spin_box.setMaximum(999999999)

        self.formLayout.setWidget(
            4, QFormLayout.ItemRole.FieldRole, self.grade_spin_box
        )

        self.endurance_label = QLabel(inventory_equipment_form)
        self.endurance_label.setObjectName('endurance_label')

        self.formLayout.setWidget(
            5, QFormLayout.ItemRole.LabelRole, self.endurance_label
        )

        self.endurance_spin_box = QSpinBox(inventory_equipment_form)
        self.endurance_spin_box.setObjectName('endurance_spin_box')
        self.endurance_spin_box.setMaximum(999999999)

        self.formLayout.setWidget(
            5, QFormLayout.ItemRole.FieldRole, self.endurance_spin_box
        )

        self.reinforce_type_label = QLabel(inventory_equipment_form)
        self.reinforce_type_label.setObjectName('reinforce_type_label')

        self.formLayout.setWidget(
            6, QFormLayout.ItemRole.LabelRole, self.reinforce_type_label
        )

        self.reinforce_type_combox = QComboBox(inventory_equipment_form)
        self.reinforce_type_combox.setObjectName('reinforce_type_combox')

        self.formLayout.setWidget(
            6, QFormLayout.ItemRole.FieldRole, self.reinforce_type_combox
        )

        self.reinforce_value_label = QLabel(inventory_equipment_form)
        self.reinforce_value_label.setObjectName('reinforce_value_label')

        self.formLayout.setWidget(
            7, QFormLayout.ItemRole.LabelRole, self.reinforce_value_label
        )

        self.reinforce_value_spin_box = QSpinBox(inventory_equipment_form)
        self.reinforce_value_spin_box.setObjectName('reinforce_value_spin_box')
        self.reinforce_value_spin_box.setMaximum(999999999)

        self.formLayout.setWidget(
            7, QFormLayout.ItemRole.FieldRole, self.reinforce_value_spin_box
        )

        self.enhance_level_label = QLabel(inventory_equipment_form)
        self.enhance_level_label.setObjectName('enhance_level_label')

        self.formLayout.setWidget(
            8, QFormLayout.ItemRole.LabelRole, self.enhance_level_label
        )

        self.enhance_level_spin_box = QSpinBox(inventory_equipment_form)
        self.enhance_level_spin_box.setObjectName('enhance_level_spin_box')
        self.enhance_level_spin_box.setMaximum(999999999)

        self.formLayout.setWidget(
            8, QFormLayout.ItemRole.FieldRole, self.enhance_level_spin_box
        )

        self.forge_level_label = QLabel(inventory_equipment_form)
        self.forge_level_label.setObjectName('forge_level_label')

        self.formLayout.setWidget(
            9, QFormLayout.ItemRole.LabelRole, self.forge_level_label
        )

        self.forge_level_spin_box = QSpinBox(inventory_equipment_form)
        self.forge_level_spin_box.setObjectName('forge_level_spin_box')
        self.forge_level_spin_box.setMaximum(999999999)

        self.formLayout.setWidget(
            9, QFormLayout.ItemRole.FieldRole, self.forge_level_spin_box
        )

        self.orb_label = QLabel(inventory_equipment_form)
        self.orb_label.setObjectName('orb_label')

        self.formLayout.setWidget(10, QFormLayout.ItemRole.LabelRole, self.orb_label)

        self.orb_container = QWidget(inventory_equipment_form)
        self.orb_container.setObjectName('orb_container')
        self.horizontalLayout_8 = QHBoxLayout(self.orb_container)
        self.horizontalLayout_8.setObjectName('horizontalLayout_8')
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.orb_category = QComboBox(self.orb_container)
        self.orb_category.setObjectName('orb_category')

        self.horizontalLayout_8.addWidget(self.orb_category)

        self.orb_item = QComboBox(self.orb_container)
        self.orb_item.setObjectName('orb_item')

        self.horizontalLayout_8.addWidget(self.orb_item)

        self.formLayout.setWidget(
            10, QFormLayout.ItemRole.FieldRole, self.orb_container
        )

        self.ms_1_label = QLabel(inventory_equipment_form)
        self.ms_1_label.setObjectName('ms_1_label')

        self.formLayout.setWidget(11, QFormLayout.ItemRole.LabelRole, self.ms_1_label)

        self.ms_1_container = QWidget(inventory_equipment_form)
        self.ms_1_container.setObjectName('ms_1_container')
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.ms_1_container.sizePolicy().hasHeightForWidth()
        )
        self.ms_1_container.setSizePolicy(sizePolicy1)
        self.ms_1_container.setMinimumSize(QSize(0, 0))
        self.horizontalLayout_3 = QHBoxLayout(self.ms_1_container)
        self.horizontalLayout_3.setObjectName('horizontalLayout_3')
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.ms_1_combox = QComboBox(self.ms_1_container)
        self.ms_1_combox.setObjectName('ms_1_combox')
        sizePolicy.setHeightForWidth(self.ms_1_combox.sizePolicy().hasHeightForWidth())
        self.ms_1_combox.setSizePolicy(sizePolicy)
        self.ms_1_combox.setFrame(True)

        self.horizontalLayout_3.addWidget(self.ms_1_combox)

        self.ms_1_spin_box = QSpinBox(self.ms_1_container)
        self.ms_1_spin_box.setObjectName('ms_1_spin_box')
        self.ms_1_spin_box.setMaximum(999999999)

        self.horizontalLayout_3.addWidget(self.ms_1_spin_box)

        self.formLayout.setWidget(
            11, QFormLayout.ItemRole.FieldRole, self.ms_1_container
        )

        self.ms_2_label = QLabel(inventory_equipment_form)
        self.ms_2_label.setObjectName('ms_2_label')

        self.formLayout.setWidget(12, QFormLayout.ItemRole.LabelRole, self.ms_2_label)

        self.ms_2_container = QWidget(inventory_equipment_form)
        self.ms_2_container.setObjectName('ms_2_container')
        sizePolicy1.setHeightForWidth(
            self.ms_2_container.sizePolicy().hasHeightForWidth()
        )
        self.ms_2_container.setSizePolicy(sizePolicy1)
        self.ms_2_container.setMinimumSize(QSize(0, 0))
        self.horizontalLayout_4 = QHBoxLayout(self.ms_2_container)
        self.horizontalLayout_4.setObjectName('horizontalLayout_4')
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.ms_2_combox = QComboBox(self.ms_2_container)
        self.ms_2_combox.setObjectName('ms_2_combox')

        self.horizontalLayout_4.addWidget(self.ms_2_combox)

        self.ms_2_spin_box = QSpinBox(self.ms_2_container)
        self.ms_2_spin_box.setObjectName('ms_2_spin_box')
        self.ms_2_spin_box.setMaximum(999999999)

        self.horizontalLayout_4.addWidget(self.ms_2_spin_box)

        self.formLayout.setWidget(
            12, QFormLayout.ItemRole.FieldRole, self.ms_2_container
        )

        self.ms_3_label = QLabel(inventory_equipment_form)
        self.ms_3_label.setObjectName('ms_3_label')

        self.formLayout.setWidget(13, QFormLayout.ItemRole.LabelRole, self.ms_3_label)

        self.ms_3_container = QWidget(inventory_equipment_form)
        self.ms_3_container.setObjectName('ms_3_container')
        self.ms_3_container.setMinimumSize(QSize(0, 0))
        self.horizontalLayout_5 = QHBoxLayout(self.ms_3_container)
        self.horizontalLayout_5.setObjectName('horizontalLayout_5')
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.ms_3_combox = QComboBox(self.ms_3_container)
        self.ms_3_combox.setObjectName('ms_3_combox')

        self.horizontalLayout_5.addWidget(self.ms_3_combox)

        self.ms_3_spin_box = QSpinBox(self.ms_3_container)
        self.ms_3_spin_box.setObjectName('ms_3_spin_box')
        self.ms_3_spin_box.setMaximum(999999999)

        self.horizontalLayout_5.addWidget(self.ms_3_spin_box)

        self.formLayout.setWidget(
            13, QFormLayout.ItemRole.FieldRole, self.ms_3_container
        )

        self.ms_4_label = QLabel(inventory_equipment_form)
        self.ms_4_label.setObjectName('ms_4_label')

        self.formLayout.setWidget(14, QFormLayout.ItemRole.LabelRole, self.ms_4_label)

        self.ms_4_container = QWidget(inventory_equipment_form)
        self.ms_4_container.setObjectName('ms_4_container')
        self.ms_4_container.setMinimumSize(QSize(0, 0))
        self.horizontalLayout_6 = QHBoxLayout(self.ms_4_container)
        self.horizontalLayout_6.setObjectName('horizontalLayout_6')
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.ms_4_combox = QComboBox(self.ms_4_container)
        self.ms_4_combox.setObjectName('ms_4_combox')

        self.horizontalLayout_6.addWidget(self.ms_4_combox)

        self.ms_4_spin_box = QSpinBox(self.ms_4_container)
        self.ms_4_spin_box.setObjectName('ms_4_spin_box')
        self.ms_4_spin_box.setMaximum(999999999)

        self.horizontalLayout_6.addWidget(self.ms_4_spin_box)

        self.formLayout.setWidget(
            14, QFormLayout.ItemRole.FieldRole, self.ms_4_container
        )

        self.btn_group = QWidget(inventory_equipment_form)
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

        self.formLayout.setWidget(15, QFormLayout.ItemRole.SpanningRole, self.btn_group)

        self.retranslateUi(inventory_equipment_form)

        QMetaObject.connectSlotsByName(inventory_equipment_form)

    # setupUi

    def retranslateUi(self, inventory_equipment_form):
        inventory_equipment_form.setWindowTitle(
            QCoreApplication.translate('inventory_equipment_form', 'Form', None)
        )
        self.id_label.setText(
            QCoreApplication.translate('inventory_equipment_form', 'ID', None)
        )
        self.name_label.setText(
            QCoreApplication.translate('inventory_equipment_form', '\u540d\u79f0', None)
        )
        self.is_sealed_label.setText(
            QCoreApplication.translate('inventory_equipment_form', '\u5c01\u88c5', None)
        )
        self.seal_count_label.setText(
            QCoreApplication.translate(
                'inventory_equipment_form', '\u5c01\u88c5\u6b21\u6570', None
            )
        )
        self.grade_label.setText(
            QCoreApplication.translate('inventory_equipment_form', '\u7b49\u7ea7', None)
        )
        self.endurance_label.setText(
            QCoreApplication.translate('inventory_equipment_form', '\u8010\u4e45', None)
        )
        self.reinforce_type_label.setText(
            QCoreApplication.translate(
                'inventory_equipment_form', '\u589e\u5e45\u7c7b\u578b', None
            )
        )
        self.reinforce_value_label.setText(
            QCoreApplication.translate(
                'inventory_equipment_form', '\u589e\u5e45\u503c', None
            )
        )
        self.enhance_level_label.setText(
            QCoreApplication.translate(
                'inventory_equipment_form', '\u5f3a\u5316\u7b49\u7ea7', None
            )
        )
        self.forge_level_label.setText(
            QCoreApplication.translate(
                'inventory_equipment_form', '\u953b\u9020\u7b49\u7ea7', None
            )
        )
        self.orb_label.setText(
            QCoreApplication.translate('inventory_equipment_form', '\u5b9d\u73e0', None)
        )
        self.ms_1_label.setText(
            QCoreApplication.translate(
                'inventory_equipment_form', '\u9b54\u6cd5\u5c01\u5370 1', None
            )
        )
        self.ms_2_label.setText(
            QCoreApplication.translate(
                'inventory_equipment_form', '\u9b54\u6cd5\u5c01\u5370 2', None
            )
        )
        self.ms_3_label.setText(
            QCoreApplication.translate(
                'inventory_equipment_form', '\u9b54\u6cd5\u5c01\u5370 3', None
            )
        )
        self.ms_4_label.setText(
            QCoreApplication.translate(
                'inventory_equipment_form', '\u9b54\u6cd5\u5c01\u5370 4', None
            )
        )
        self.save_btn.setText(
            QCoreApplication.translate('inventory_equipment_form', 'Save', None)
        )
        self.reset_btn.setText(
            QCoreApplication.translate('inventory_equipment_form', 'Reset', None)
        )
        self.delete_btn.setText(
            QCoreApplication.translate('inventory_equipment_form', 'Delete', None)
        )

    # retranslateUi
