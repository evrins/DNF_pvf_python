import json

from config import config
from dnfpkgtool.repo.equipment_repo import EquipmentRepo
from PySide6.QtCore import QAbstractTableModel, QSortFilterProxyModel, Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTableView,
    QWidget,
)

from ui.signals import SubmitSignal, SubmitType
from ui.vars import (
    default_options,
    equipment_name_mapping,
    job_name_mapping,
    main_options,
    minor_options,
    patch_options,
    rarity_list,
)
from ui.widgets.ranged_spin_box import RangedSpinBox


class EquipmentTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self._headers = [
            'id',
            'name',
            'equipment_type_display',
            'level',
            'rarity_display',
        ]
        self._headers_display = ['ID', '名称', '装备类型', '等级', '稀有度']

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            key = self._headers[index.column()]
            return self._data[index.row()][key]
        elif role == Qt.ItemDataRole.ToolTipRole:
            indent = ' ' * 4
            row = self._data[index.row()]
            json_string = row['json']
            d = json.loads(json_string)
            lines = []
            for k, v in d.items():
                lines.append(k)
                if (
                    k == '[basic explain]'
                    or k == '[detail explain]'
                    or k == '[flavor text]'
                ):
                    if v:
                        for it in v:
                            for sub in it.split('\r\n'):
                                sub = sub.strip()
                                lines.append(f'{indent}{sub}')
                    else:
                        lines.append('')
                else:
                    lines.append(f'{indent}{v}')
            return '\n'.join(lines)
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._headers_display[section]
        return None

    def flags(self, index) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable


class EquipmentSearch(QWidget):
    def __init__(self, submit_signal: SubmitSignal):
        super().__init__()
        self.equipment_repo =  EquipmentRepo(config.get_equipment_parquet_file_path())
        self.submit_signal = submit_signal

        self.form_width = 240
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)  # Add small margins to the main layout

        form_layout = QFormLayout()

        # Set margins and spacing for better alignment
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setVerticalSpacing(8)
        form_layout.setHorizontalSpacing(10)

        # Define size policy for all form fields
        size_policy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        self.name_input = QLineEdit()
        self.name_input.returnPressed.connect(self.do_search)
        self.name_input.setSizePolicy(size_policy)

        self.main_combox = QComboBox()
        self.main_combox.addItems(main_options)
        self.main_combox.currentIndexChanged.connect(self.main_option_changed)
        self.main_combox.setSizePolicy(size_policy)

        self.minor_combo = QComboBox()
        self.minor_combo.addItems(default_options)
        self.minor_combo.setEnabled(False)
        self.minor_combo.currentIndexChanged.connect(self.minor_option_changed)
        self.minor_combo.setSizePolicy(size_policy)

        self.patch_combo = QComboBox()
        self.patch_combo.addItems(default_options)
        self.patch_combo.setEnabled(False)
        self.patch_combo.setSizePolicy(size_policy)

        self.rarity_combo = QComboBox()
        self.rarity_combo.addItem('---')
        self.rarity_combo.addItems(rarity_list)
        self.rarity_combo.setSizePolicy(size_policy)

        self.ranged_spinbox = RangedSpinBox()

        # Set size policy to match other form fields
        self.ranged_spinbox.setSizePolicy(size_policy)

        search_btn = QPushButton('Search')
        search_btn.clicked.connect(self.do_search)
        search_btn.setSizePolicy(size_policy)

        submit_btn = QPushButton('Submit to Mail')
        submit_btn.clicked.connect(self.submit_to_mail)
        submit_btn.setSizePolicy(size_policy)

        form_layout.addRow('&Name', self.name_input)
        form_layout.addRow('&Main', self.main_combox)
        form_layout.addRow('&Minor', self.minor_combo)
        form_layout.addRow('&Patch', self.patch_combo)
        form_layout.addRow('&Rarity', self.rarity_combo)
        form_layout.addRow('&Level', self.ranged_spinbox)
        form_layout.addRow(search_btn, submit_btn)

        form_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )

        form_container = QWidget()
        form_container.setLayout(form_layout)

        # Set size policy to maintain fixed width but expand vertically if needed
        form_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        form_container.setFixedWidth(self.form_width)  # Set a fixed width for the form

        # Add form container with top-left alignment
        layout.addWidget(
            form_container,
            stretch=0,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )

        table_model = EquipmentTableModel([])

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(table_model)

        self.table_view = QTableView()
        self.table_view.setModel(proxy_model)
        self.table_view.setSortingEnabled(True)

        # Configure row selection behavior
        self.table_view.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table_view.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        # Add table view with stretch=1 to take up remaining space
        layout.addWidget(self.table_view, stretch=1)

        self.setLayout(layout)

        self.update_title(0)

        # Set size policy to expand with parent
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Set minimum size to ensure usability but allow expansion
        self.setMinimumSize(700, 400)

    def _adjust_table_columns(self):
        """Adjust table column widths to content."""
        self.table_view.resizeColumnsToContents()

    def adjust_size_to_content(self):
        """Public method to adjust table columns to content."""
        self._adjust_table_columns()

    def main_option_changed(self, index: int):
        if index == 0:
            next_minor_options = default_options
            enable_minor_option = False
        else:
            next_minor_options = minor_options.get(main_options[index], None)
            if not next_minor_options:
                next_minor_options = default_options
                enable_minor_option = False
            else:
                enable_minor_option = True

        self.minor_combo.clear()
        self.minor_combo.addItems(next_minor_options)
        self.minor_combo.setEnabled(enable_minor_option)

        # self.patch_combo.clear()
        # self.patch_combo.addItems(default_options)
        # self.patch_combo.setEnabled(False)

    def minor_option_changed(self, index: int):
        if index == 0:
            next_patch_options = default_options
            enable_patch_option = False
        else:
            main_option_index = self.main_combox.currentIndex()
            current_main_option = main_options[main_option_index]
            current_minor_options = minor_options.get(current_main_option, None)
            if current_minor_options:
                next_patch_options = patch_options.get(
                    current_minor_options[index], None
                )
            else:
                next_patch_options = None

            if not next_patch_options:
                next_patch_options = default_options
                enable_patch_option = False
            else:
                enable_patch_option = True

        self.patch_combo.clear()
        self.patch_combo.addItems(next_patch_options)
        self.patch_combo.setEnabled(enable_patch_option)

    def do_search(self, s=None):
        name = self.name_input.text().strip()
        main_idx = self.main_combox.currentIndex()
        minor_idx = self.minor_combo.currentIndex()
        patch_idx = self.patch_combo.currentIndex()

        main_option = main_options[main_idx]
        equipment_type_list = None
        usable_job = None
        item_group_name = None
        armor_type = None

        if main_idx == 0:
            equipment_type_list = None
        elif main_option == '武器':
            equipment_type_list = ['[weapon]']
            if minor_idx != 0:
                minor_option = minor_options[main_option][minor_idx]
                usable_job = job_name_mapping[minor_option]
                if patch_idx != 0:
                    patch_option = patch_options[minor_option][patch_idx]
                    item_group_name = equipment_name_mapping[patch_option]
        elif main_option == '防具':
            equipment_type_list = [
                '[coat]',
                '[waist]',
                '[shoulder]',
                '[shoes]',
                '[pants]',
            ]
            if minor_idx != 0:
                minor_option = minor_options[main_option][minor_idx]
                armor_type = equipment_name_mapping[minor_option]
                if patch_idx != 0:
                    patch_option = patch_options[minor_option][patch_idx]
                    equipment_type_list = [equipment_name_mapping[patch_option]]
        elif main_option == '首饰':
            equipment_type_list = ['[amulet]', '[wrist]', '[ring]']
            if minor_idx != 0:
                minor_option = minor_options[main_option][minor_idx]
                equipment_type_list = [equipment_name_mapping[minor_option]]
        elif main_option == '特殊装备':
            equipment_type_list = ['[support]', '[magic stone]']
            if minor_idx != 0:
                minor_option = minor_options[main_option][minor_idx]
                equipment_type_list = [equipment_name_mapping[minor_option]]
        elif main_option == '装扮':
            equipment_type_list = ['[support]', '[magic stone]']
            if minor_idx != 0:
                minor_option = minor_options[main_option][minor_idx]
                equipment_type_list = [equipment_name_mapping[minor_option]]
        elif main_option == '宠物':
            equipment_type_list = ['[creature]']
        elif main_option == '称号':
            equipment_type_list = ['[title name]']
        elif main_option == '宠物装备':
            equipment_type_list = [
                '[artifact blue]',
                '[artifact green]',
                '[artifact red]',
            ]
        elif main_option == '契约效果':
            equipment_type_list = ['']
        else:
            raise Exception(f'unknown main option: {main_option}')

        min_level = self.ranged_spinbox.min_level_spinbox.value()
        min_level = None if min_level == 0 else int(min_level)
        max_level = self.ranged_spinbox.max_level_spinbox.value()
        max_level = None if max_level == 0 else int(max_level)

        rarity_idx = self.rarity_combo.currentIndex()
        rarity = None if rarity_idx == 0 else rarity_list[rarity_idx - 1]

        data = self.equipment_repo.query(
            name,
            equipment_type_list,
            usable_job,
            item_group_name,
            armor_type,
            min_level=min_level,
            max_level=max_level,
            rarity=rarity,
        )
        self.update_title(len(data))
        table_model = EquipmentTableModel(data)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(table_model)
        self.table_view.setModel(proxy_model)
        self.table_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        # Adjust table columns to content
        QTimer.singleShot(100, self._adjust_table_columns)

    def submit_to_mail(self):
        selected_indexes = self.table_view.selectedIndexes()
        if not selected_indexes:
            return
        select_id = selected_indexes[0].data(Qt.ItemDataRole.DisplayRole)
        print(f'submit {select_id} to mail')
        self.submit_signal.on_submit.emit(SubmitType.Equipment, select_id)

    def update_title(self, n_result: int):
        title = 'Equipment Search'
        if n_result > 0:
            title = f'{title} {n_result} records found'
        self.setWindowTitle(title)
