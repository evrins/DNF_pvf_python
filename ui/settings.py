from loguru import logger
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from dnfpkgtool.db import check_mysql_config


class Setting(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        self.form_width = 240

        db_form_layout = QFormLayout()

        size_policy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        title_label = QLabel('DB Config')
        title_label.setSizePolicy(size_policy)

        db_form_layout.addRow(title_label)

        self.db_host_combox = QComboBox()
        self.db_host_combox.addItem('127.0.0.1')
        self.db_host_combox.setEditable(True)
        self.db_host_combox.setSizePolicy(size_policy)

        db_form_layout.addRow('&Host', self.db_host_combox)

        self.db_port_combox = QComboBox()
        self.db_port_combox.addItem('3306')
        self.db_port_combox.setEditable(True)
        self.db_port_combox.setSizePolicy(size_policy)

        db_form_layout.addRow('&Port', self.db_port_combox)

        self.db_username_combox = QComboBox()
        self.db_username_combox.addItem('game')
        self.db_username_combox.setEditable(True)
        self.db_username_combox.setSizePolicy(size_policy)

        db_form_layout.addRow('&Username', self.db_username_combox)

        self.db_password_combox = QComboBox()
        self.db_password_combox.addItem('uu5!^%jg')
        self.db_password_combox.addItem('123456')
        self.db_password_combox.setEditable(True)
        self.db_password_combox.setSizePolicy(size_policy)

        db_form_layout.addRow('&Password', self.db_password_combox)

        # Connection status label
        self.status_label = QLabel('Ready')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f5f5f5;
                color: #666;
            }
        """)
        db_form_layout.addRow('Status:', self.status_label)

        self.save_btn = QPushButton('Test && Save')
        self.save_btn.clicked.connect(self.save_and_test)
        self.save_btn.setSizePolicy(size_policy)

        db_form_layout.addRow(self.save_btn)

        db_form_container = QWidget()
        db_form_container.setLayout(db_form_layout)

        db_form_container.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        db_form_container.setFixedWidth(
            self.form_width
        )  # Set a fixed width for the form

        # Add form container with top-left alignment
        layout.addWidget(
            db_form_container,
            stretch=0,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )

        pvf_form_layout = QFormLayout()

        self.pvf_combox = QComboBox()
        # todo load cache

        self.pvf_combox.setSizePolicy(size_policy)

        pvf_form_layout.addRow('&PVF', self.pvf_combox)
        add_pvf_btn = QPushButton('Add PVF')
        add_pvf_btn.clicked.connect(self.handle_add_pvf)
        add_pvf_btn.setSizePolicy(size_policy)

        pvf_form_layout.addRow(add_pvf_btn)

        pvf_form_container = QWidget()
        pvf_form_container.setLayout(pvf_form_layout)
        pvf_form_container.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )

        layout.addWidget(
            pvf_form_container,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )

        self.setLayout(layout)

    def save_and_test(self):
        """Test MySQL connection and provide user feedback."""
        host = self.db_host_combox.currentText().strip()
        port_text = self.db_port_combox.currentText().strip()
        username = self.db_username_combox.currentText().strip()
        password = self.db_password_combox.currentText().strip()

        # Validate input fields
        if not all([host, port_text, username, password]):
            self._show_error_status('Missing fields')
            return

        try:
            port = int(port_text)
        except ValueError:
            self._show_error_status('Invalid port')
            return

        # Show testing status
        self._show_testing_status()

        # Disable button during test
        self.save_btn.setEnabled(False)

        # Test connection
        try:
            valid = check_mysql_config(host, port, username, password)

            if valid:
                self._show_success_status('Success')
                self._save_settings(host, port_text, username, password)
            else:
                self._show_error_status('Failed')

        except Exception as e:
            self._show_error_status(f'Connection error: {str(e)}')

        finally:
            # Re-enable button after test
            QTimer.singleShot(100, lambda: self.save_btn.setEnabled(True))

    def _show_testing_status(self):
        """Show testing in progress status."""
        self.status_label.setText('🔄 Testing connection...')
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                border: 1px solid #2196F3;
                border-radius: 4px;
                background-color: #E3F2FD;
                color: #1976D2;
                font-weight: bold;
            }
        """)

    def _show_success_status(self, message: str):
        """Show success status with green styling."""
        self.status_label.setText(f'✅ {message}')
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                border: 1px solid #4CAF50;
                border-radius: 4px;
                background-color: #E8F5E8;
                color: #2E7D32;
                font-weight: bold;
            }
        """)

        # Show success message box
        QMessageBox.information(
            self,
            'Connection Successful',
            'MySQL connection test passed successfully!\nSettings have been saved.',
        )

    def _show_error_status(self, message: str):
        """Show error status with red styling."""
        self.status_label.setText(f'❌ {message}')
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                border: 1px solid #F44336;
                border-radius: 4px;
                background-color: #FFEBEE;
                color: #C62828;
                font-weight: bold;
            }
        """)

        # Show error message box
        QMessageBox.critical(
            self,
            'Connection Failed',
            f'MySQL connection test failed:\n\n{message}\n\nPlease check your database settings and try again.',
        )

    def _save_settings(self, host: str, port: str, username: str, password: str):
        """Save the MySQL settings (placeholder for actual implementation)."""
        # TODO: Implement actual settings persistence
        # This could save to a config file, registry, or database
        print(f'Saving settings: {host}:{port} user={username}')

        # Add to combobox history if not already present
        self._add_to_history(self.db_host_combox, host)
        self._add_to_history(self.db_port_combox, port)
        self._add_to_history(self.db_username_combox, username)
        self._add_to_history(self.db_password_combox, password)

    def _add_to_history(self, combobox: QComboBox, value: str):
        """Add value to combobox history if not already present."""
        if combobox.findText(value) == -1:
            combobox.insertItem(0, value)
            combobox.setCurrentText(value)

    def handle_add_pvf(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Select PVF', '', 'All Files (*.*);;Pvf Files (*.pvf)'
        )
        if not file_name:
            logger.warning('No file selected')
            return
        print(f'selected file: {file_name}')
