import signal
import sys
from pathlib import Path
from time import localtime, strftime

from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from dnfpkgtool.db.service.item_service import get_item_service
from ui.components.cargo_table_model import CargoTableModel


class Backend(QObject):
    updated = Signal(str, arguments=['time'])

    def __init__(self, parent=None):
        super().__init__(parent)
        print('Backend initialized')

        self._current_time = '00:00:00'

        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update_time)
        self.timer.start()
        print('Timer started')

    def update_time(self):
        curr_time = strftime('%H:%M:%S', localtime())
        self._current_time = curr_time
        self.updated.emit(curr_time)

    @Property(str, notify=updated)
    def currentTime(self):
        return self._current_time

    @Slot()
    def on_button_clicked(self):
        print('Backend: button_clicked')

    @Slot(result=bool)
    def isReady(self):
        """Method to check if backend is properly initialized"""
        return True


shutdown_requested = False


def signal_handler(signum, frame):
    global shutdown_requested
    print(f'Signal {signum} received, requesting shutdown.')
    shutdown_requested = True


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    app = QGuiApplication(sys.argv)

    def check_for_shutdown():
        if shutdown_requested:
            print('Shutdown flag detected, quitting event loop.')
            app.quit()

    timer = QTimer()
    timer.setInterval(1000)
    timer.timeout.connect(check_for_shutdown)
    timer.start()

    # Create backend instance first
    backend = Backend()

    # Create QML engine
    engine = QQmlApplicationEngine()
    engine.quit.connect(app.quit)

    # Set context property BEFORE loading QML
    engine.rootContext().setContextProperty('backend', backend)

    item_svc = get_item_service()

    model = CargoTableModel(item_svc.get_current_account_cargo())

    engine.rootContext().setContextProperty('cargoModel', model)

    # Get the correct path to the QML file
    current_dir = Path(__file__).parent
    qml_file = current_dir / 'main.qml'

    # Check if QML file exists
    if not qml_file.exists():
        print(f'Error: QML file not found at {qml_file}')
        sys.exit(-1)

    # Load the QML file
    engine.load(QUrl.fromLocalFile(str(qml_file)))

    # Check if QML loaded successfully
    if not engine.rootObjects():
        print('Error: Failed to load QML file')
        sys.exit(-1)

    print('QML application started successfully')

    sys.exit(app.exec())
