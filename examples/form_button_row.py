import sys

from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)


class MyForm(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Form with Action Buttons')

        # Create the QFormLayout
        form_layout = QFormLayout()

        # Add some input fields to the form
        form_layout.addRow('Name:', QLineEdit())
        form_layout.addRow('Email:', QLineEdit())

        # Create a QHBoxLayout for the action buttons
        button_layout = QHBoxLayout()

        # Create the action buttons
        submit_button = QPushButton('Submit')
        cancel_button = QPushButton('Cancel')
        save_button = QPushButton('Save')

        # Add buttons to the button layout
        button_layout.addWidget(submit_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)

        # Add the button layout to the form layout
        # The layout will span both columns
        form_layout.addRow(button_layout)

        # Set the main layout for the window
        self.setLayout(form_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyForm()
    window.show()
    sys.exit(app.exec())
