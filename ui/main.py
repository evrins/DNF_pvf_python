import signal
import sys
import tracemalloc

from loguru import logger
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ui.equipment_search import EquipmentSearch
from ui.inventory_tabview import InventoryTabView
from ui.settings import Setting
from ui.signals import SubmitSignal, SubmitType
from ui.stackable_search import StackableSearch

shutdown_requested = False


def handle_shutdown_signal(sig, frame=None):
    global shutdown_requested
    logger.info(f'signal {sig} received')
    shutdown_requested = True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create main tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.submit_signal = SubmitSignal()

        # Create search widgets
        self.equip_search = EquipmentSearch(self.submit_signal)
        self.tab_widget.addTab(self.equip_search, '🛡️ Equipment Search')

        self.stackable_search = StackableSearch(self.submit_signal)
        self.tab_widget.addTab(self.stackable_search, '📦 Stackable Search')

        self.inventory_tabview = InventoryTabView()
        self.tab_widget.addTab(self.inventory_tabview, 'Inventory')

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

        # set default tab
        self.tab_widget.setCurrentIndex(2)

        self.quit_timer = QTimer(self)
        self.quit_timer.setInterval(1000)
        self.quit_timer.timeout.connect(self.check_for_shutdown)
        self.quit_timer.start()

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
        dump_btn = QPushButton('Dump')
        dump_btn.clicked.connect(self.dump_memory)
        character_layout.addWidget(dump_btn)
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
            'Account Cargo',
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

    def check_for_shutdown(self):
        if shutdown_requested:
            logger.info('Shutdown requested, closing application')
            self.close()

    def dump_memory(self):
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('traceback')
        print('[ Top 10 memory-allocating lines ]')
        for stat in top_stats[:10]:
            print(stat)


if __name__ == '__main__':
    tracemalloc.start()

    signal.signal(signal.SIGINT, handle_shutdown_signal)
    signal.signal(signal.SIGTERM, handle_shutdown_signal)

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    mw = MainWindow()
    mw.show()
    app.exec()
