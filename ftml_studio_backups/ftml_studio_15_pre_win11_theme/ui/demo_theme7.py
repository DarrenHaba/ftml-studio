import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QCheckBox, QComboBox, QRadioButton, QTabWidget, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("windows11_theme_demo")

class Windows11ThemeDemo(QMainWindow):
    """Demo with Windows 11 theme and green accent color"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows 11 Theme Demo")
        self.resize(600, 500)

        # Set up UI
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface"""
        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Status label
        status_label = QLabel("Windows 11 Theme with Green Accent")
        status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(status_label)

        # Tab widget
        self.tab_widget = QTabWidget()

        # First tab - Basic UI elements
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        tab1_layout.setSpacing(15)

        # Regular buttons
        buttons_layout = QHBoxLayout()
        button1 = QPushButton("Standard Button")
        button2 = QPushButton("Another Button")
        buttons_layout.addWidget(button1)
        buttons_layout.addWidget(button2)
        buttons_layout.addStretch()

        # Checkable buttons
        checkable_layout = QHBoxLayout()
        check_btn1 = QPushButton("Option 1")
        check_btn1.setCheckable(True)
        check_btn1.setChecked(True)
        check_btn2 = QPushButton("Option 2")
        check_btn2.setCheckable(True)
        checkable_layout.addWidget(check_btn1)
        checkable_layout.addWidget(check_btn2)
        checkable_layout.addStretch()

        # Checkboxes
        checkbox_layout = QHBoxLayout()
        checkbox1 = QCheckBox("Check me")
        checkbox2 = QCheckBox("Check me too")
        checkbox2.setChecked(True)
        checkbox_layout.addWidget(checkbox1)
        checkbox_layout.addWidget(checkbox2)
        checkbox_layout.addStretch()

        # Radio buttons
        radio_layout = QHBoxLayout()
        radio1 = QRadioButton("Radio 1")
        radio2 = QRadioButton("Radio 2")
        radio1.setChecked(True)
        radio_layout.addWidget(radio1)
        radio_layout.addWidget(radio2)
        radio_layout.addStretch()

        # Combo box
        combo_layout = QHBoxLayout()
        combo_label = QLabel("Test Dropdown:")
        combo_box = QComboBox()
        combo_box.addItems(["Option 1", "Option 2", "Option 3", "Option 4"])
        combo_layout.addWidget(combo_label)
        combo_layout.addWidget(combo_box)
        combo_layout.addStretch()

        # Add all rows to first tab
        tab1_layout.addLayout(buttons_layout)
        tab1_layout.addLayout(checkable_layout)
        tab1_layout.addLayout(checkbox_layout)
        tab1_layout.addLayout(radio_layout)
        tab1_layout.addLayout(combo_layout)
        tab1_layout.addStretch()

        # Second tab - Text Editor
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        text_edit = QTextEdit()
        text_edit.setPlainText("This is a text editor area. You can type text here.\n\nThe selection highlight will use the accent color.")
        tab2_layout.addWidget(text_edit)

        # Add tabs to tab widget
        self.tab_widget.addTab(tab1, "Controls")
        self.tab_widget.addTab(tab2, "Text Editor")

        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)

        # Status bar
        self.statusBar().showMessage("Windows 11 Theme with Green Accent Color Applied")


def apply_windows11_theme(app):
    """Apply Windows 11 theme with green accent color to the application"""
    # Set the Windows 11 style
    app.setStyle("Windows11")

    # Get the current palette
    palette = app.palette()

    # Set green accent color
    green_accent = QColor("#4CAF50")  # Material Design Green

    # 1. Try newer Qt 6.6+ approach with QPalette.Accent
    try:
        # This is available in Qt 6.6+
        palette.setColor(QPalette.Accent, green_accent)
    except AttributeError:
        logger.debug("QPalette.Accent not available (requires Qt 6.6+)")

    # Apply palette
    app.setPalette(palette)

    logger.debug("Applied Windows 11 theme with green accent color")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply Windows 11 theme with green accent
    apply_windows11_theme(app)

    window = Windows11ThemeDemo()
    window.show()
    sys.exit(app.exec())