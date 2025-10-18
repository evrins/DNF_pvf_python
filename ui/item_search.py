import json

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

from dnfpkgtool.repo.item_repo import ItemRepo
from ui.signals import SubmitSignal, SubmitType
from ui.vars import (
    categoryed_stackable_type_dict,
    item_category_key_list,
    item_rarity_list,
)
from ui.widgets.ranged_spin_box import RangedSpinBox


class ItemTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self._headers = [
            'id',
            'name',
            'stackable_type_display',
            'level',
            'rarity_display',
        ]
        self._headers_display = ['ID', '名称', '物品种类', '等级', '稀有度']

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


class ItemSearch(QWidget):
    def __init__(self, item_repo: ItemRepo, submit_signal: SubmitSignal):
        super().__init__()
        self.item_repo = item_repo
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

        self.category_combox = QComboBox()
        self.category_combox.addItem('---')
        self.category_combox.addItems(item_category_key_list)
        self.category_combox.setSizePolicy(size_policy)

        self.rarity_combo = QComboBox()
        self.rarity_combo.addItem('---')
        self.rarity_combo.addItems(item_rarity_list)
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
        form_layout.addRow('&Category', self.category_combox)
        form_layout.addRow('&Rarity', self.rarity_combo)
        form_layout.addRow('&Level', self.ranged_spinbox)
        form_layout.addRow(search_btn, submit_btn)

        form_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )

        form_container = QWidget()
        form_container.setLayout(form_layout)

        # Set fixed size policy to prevent stretching and align to top-left
        form_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        form_container.setFixedWidth(self.form_width)  # Set a fixed width for the form

        # Add form container with top-left alignment
        layout.addWidget(
            form_container,
            stretch=0,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )

        table_model = ItemTableModel([])

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(table_model)

        self.table_view = QTableView()
        self.table_view.setModel(proxy_model)
        self.table_view.setSortingEnabled(True)

        # Add table view with stretch=1 to take up remaining space
        layout.addWidget(self.table_view, stretch=1)

        self.setLayout(layout)

        self.update_title(0)

        self.setMinimumSize(700, 400)  # Minimum size to ensure usability

        # Use QTimer to adjust size after the widget is fully rendered
        QTimer.singleShot(0, self._adjust_size_to_content)

    def _adjust_size_to_content(self):
        """Adjust window size based on table view content width."""
        # Calculate total table width
        table_width = 0
        for column in range(self.table_view.model().columnCount()):
            table_width += self.table_view.columnWidth(column)

        # Add extra space for table margins, scrollbars, and padding
        table_padding = 50  # Space for scrollbars, borders, etc.

        # Form width (fixed at 240px) + margins + table width + padding
        form_width = self.form_width
        layout_margins = 10  # Left and right margins from main layout
        total_width = form_width + layout_margins + table_width + table_padding

        # Set reasonable bounds for the width
        min_width = 600
        max_width = 1200
        calculated_width = max(min_width, min(max_width, total_width))

        # Set height based on content or use default
        calculated_height = 480  # Default height

        # Resize the window
        self.resize(calculated_width, calculated_height)

    def adjust_size_to_content(self):
        """Public method to adjust window size based on current table content."""
        self._adjust_size_to_content()

    def do_search(self, s=None):
        name = self.name_input.text().strip()
        category = self.category_combox.currentText()

        stackable_type_list = categoryed_stackable_type_dict.get(category, None)

        min_level = self.ranged_spinbox.min_level_spinbox.value()
        min_level = None if min_level == 0 else int(min_level)
        max_level = self.ranged_spinbox.max_level_spinbox.value()
        max_level = None if max_level == 0 else int(max_level)

        rarity_idx = self.rarity_combo.currentIndex()
        rarity = None if rarity_idx == 0 else item_rarity_list[rarity_idx - 1]

        data = self.item_repo.query(
            name,
            stackable_type_list=stackable_type_list,
            min_level=min_level,
            max_level=max_level,
            rarity_display=rarity,
        )
        self.update_title(len(data))
        table_model = ItemTableModel(data)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(table_model)
        self.table_view.setModel(proxy_model)

        self.table_view.resizeColumnsToContents()

        # Configure row selection behavior
        self.table_view.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table_view.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        # After search, adjust size to new content
        QTimer.singleShot(100, self._adjust_size_to_content)

    def submit_to_mail(self):
        selected_indexes = self.table_view.selectedIndexes()
        if not selected_indexes:
            return
        select_id = selected_indexes[0].data(Qt.ItemDataRole.DisplayRole)
        print(f'submit {select_id} to mail')
        self.submit_signal.on_submit.emit(SubmitType.Item, select_id)

    def update_title(self, n_result: int):
        title = 'Item Search'
        if n_result > 0:
            title = f'{title} {n_result} records found'
        self.setWindowTitle(title)
