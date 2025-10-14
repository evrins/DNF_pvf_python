import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QPushButton,
    QWidget,
)

from dnfpkgtool.repo.equipment_repo import EquipmentRepo
from dnfpkgtool.repo.item_repo import ItemRepo
from ui.equipment_search import EquipmentSearch
from ui.item_search import ItemSearch
from ui.signals import SubmitSignal, SubmitType


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        btn1 = QPushButton("Open Item Search")
        btn1.clicked.connect(self.open_item_search)
        layout.addWidget(btn1)

        btn2 = QPushButton("Open Equipment Search")
        btn2.clicked.connect(self.open_equipment_search)
        layout.addWidget(btn2)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        self.submit_signal = SubmitSignal()

        equipment_file_path = "/Users/evrins/workspace/python/DNF_pvf_python/dnfpkgtool/repo/data/equipments.parquet"
        self.equipment_repo = EquipmentRepo(equipment_file_path)
        self.equip_search = EquipmentSearch(self.equipment_repo, self.submit_signal)

        equipment_file_path = "/Users/evrins/workspace/python/DNF_pvf_python/dnfpkgtool/repo/data/items.parquet"
        self.items_repo = ItemRepo(equipment_file_path)
        self.item_search = ItemSearch(self.items_repo, self.submit_signal)

        self.status_bar = self.statusBar()
        self.status_bar.showMessage("hello world!")

        self.submit_signal.on_submit.connect(self.handle_submit_to_mail)

    def open_item_search(self):
        self.item_search.show()

    def open_equipment_search(self):
        self.equip_search.show()

    def handle_submit_to_mail(self, submit_type: SubmitType, id_: int):
        print(f"submit {submit_type}  {id_} to mail")

    def closeEvent(self, event):
        if self.equip_search:
            self.equip_search.close()

        if self.item_search:
            self.item_search.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setStyle("Fusion")
    mw = MainWindow()
    mw.show()
    app.exec()
