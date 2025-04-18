import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QCheckBox, QComboBox, QRadioButton
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStyleFactory

# Import our simple theme manager
from src.ftml_studio.ui.themes import theme_manager

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("style_demo")

class SimpleStyleDemo(QMainWindow):
    """Basic demo to test built-in Qt styles"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt Style Demo")
        self.resize(600, 400)

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

        # Style selector
        style_layout = QHBoxLayout()

        style_label = QLabel("Qt Style:")
        self.style_combo = QComboBox()
        self.style_combo.addItems(QStyleFactory.keys())

        # Set current style in combo box
        current_style = QApplication.instance().style().objectName()
        index = self.style_combo.findText(current_style, Qt.MatchFixedString)
        if index >= 0:
            self.style_combo.setCurrentIndex(index)

        apply_btn = QPushButton("Apply Style")
        apply_btn.clicked.connect(self.apply_style)

        style_layout.addWidget(style_label)
        style_layout.addWidget(self.style_combo)
        style_layout.addWidget(apply_btn)
        style_layout.addStretch()

        main_layout.addLayout(style_layout)

        # Basic UI elements layout
        elements_layout = QVBoxLayout()
        elements_layout.setSpacing(15)

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

        # Add all rows
        elements_layout.addLayout(buttons_layout)
        elements_layout.addLayout(checkable_layout)
        elements_layout.addLayout(checkbox_layout)
        elements_layout.addLayout(radio_layout)

        main_layout.addLayout(elements_layout)
        main_layout.addStretch()

        # Status bar
        self.statusBar().showMessage("Ready")

    def apply_style(self):
        """Apply the selected style"""
        style_name = self.style_combo.currentText()
        app = QApplication.instance()

        # Set the style in theme manager
        theme_manager.set_style(style_name)

        # Apply the style
        success = theme_manager.apply_style(app)

        if success:
            self.statusBar().showMessage(f"Applied style: {style_name}")
        else:
            self.statusBar().showMessage(f"Failed to apply style: {style_name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Theme manager is a singleton, already imported at the top
    # Apply default style
    theme_manager.apply_style(app)

    window = SimpleStyleDemo()
    window.show()
    sys.exit(app.exec())