import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from dnfpkgtool.repo.equipment_repo import EquipmentRepo
from dnfpkgtool.repo.item_repo import ItemRepo
from ui.equipment_search import EquipmentSearch
from ui.item_search import ItemSearch
from ui.settings import Setting
from ui.signals import SubmitSignal, SubmitType


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create main tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.submit_signal = SubmitSignal()

        # Initialize repositories
        equipment_file_path = '/Users/evrins/workspace/python/DNF_pvf_python/dnfpkgtool/repo/data/equipments.parquet'
        self.equipment_repo = EquipmentRepo(equipment_file_path)

        items_file_path = '/Users/evrins/workspace/python/DNF_pvf_python/dnfpkgtool/repo/data/items.parquet'
        self.items_repo = ItemRepo(items_file_path)

        # Create search widgets
        self.equip_search = EquipmentSearch(self.equipment_repo, self.submit_signal)
        self.item_search = ItemSearch(self.items_repo, self.submit_signal)

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.equip_search, '🛡️ Equipment Search')
        self.tab_widget.addTab(self.item_search, '📦 Item Search')

        # Add placeholder tabs for future functionality
        self._add_placeholder_tabs()

        # Set up status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready - Select a tab to start searching')

        # Connect signals
        self.submit_signal.on_submit.connect(self.handle_submit_to_mail)

        # Set window properties
        self.setWindowTitle('DNF Package Tool - Search Interface')
        self.resize(1000, 700)  # Set initial size

        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def handle_submit_to_mail(self, submit_type: SubmitType, id_: int):
        """Handle submission to mail system."""
        print(f'Submit {submit_type} ID:{id_} to mail')
        self.status_bar.showMessage(
            f'Submitted {submit_type.value} (ID: {id_}) to mail system'
        )

    def _add_placeholder_tabs(self):
        """Add placeholder tabs for future functionality."""
        # Character Management tab
        character_widget = QWidget()
        character_layout = QVBoxLayout()
        character_layout.addWidget(QPushButton('Character Management - Coming Soon'))
        character_widget.setLayout(character_layout)
        self.tab_widget.addTab(character_widget, '👤 Characters')

        # Mail System tab
        mail_widget = QWidget()
        mail_layout = QVBoxLayout()
        mail_layout.addWidget(QPushButton('Mail System - Coming Soon'))
        mail_widget.setLayout(mail_layout)
        self.tab_widget.addTab(mail_widget, '📧 Mail')

        # Settings tab - using actual Settings widget
        self.settings_widget = Setting()
        self.tab_widget.addTab(self.settings_widget, '⚙️ Settings')

    def _on_tab_changed(self, index: int):
        """Handle tab change events."""
        tab_names = [
            'Equipment Search',
            'Item Search',
            'Character Management',
            'Mail System',
            'Settings',
        ]

        if index < len(tab_names):
            self.status_bar.showMessage(f'Active tab: {tab_names[index]}')

    def closeEvent(self, event):
        """Handle application close event."""
        # The tab widget will automatically handle closing its child widgets
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    mw = MainWindow()
    mw.show()
    app.exec()
