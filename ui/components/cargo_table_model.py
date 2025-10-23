from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class CargoTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []
        self._headers = ['display_idx', 'display_name', 'num_grade', 'id', 'display_rarity_name']

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)  # name, age, occupation

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._data):
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            row_data = self._data[index.row()]
            col_key = self._headers[index.column()]
            if col_key == 'num_grade' and row_data.type == 0x01:
                return 1
            return str(row_data.__dict__[col_key])

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def setData(self, new_data):
        """Method to update the model data"""
        self.beginResetModel()
        self._data = new_data or []
        self.endResetModel()
