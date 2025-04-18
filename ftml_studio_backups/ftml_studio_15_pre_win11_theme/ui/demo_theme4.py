import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QCheckBox, QComboBox, QGroupBox,
    QRadioButton, QTextEdit, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Import our theme manager
from src.ftml_studio.ui.themes import theme_manager

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("theme_demo")

class SimpleThemeDemo(QMainWindow):
    """Simple demo window to test our theme application"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FTML Studio Theme Demo")
        self.resize(800, 600)

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

        # Theme selector
        theme_group = QGroupBox("Theme Selection")
        theme_layout = QHBoxLayout(theme_group)

        theme_label = QLabel("Select Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Auto (System)"])

        # Set current theme in combo box
        current_theme = theme_manager.current_theme
        if current_theme == theme_manager.LIGHT:
            self.theme_combo.setCurrentIndex(0)
        elif current_theme == theme_manager.DARK:
            self.theme_combo.setCurrentIndex(1)
        else:  # AUTO
            self.theme_combo.setCurrentIndex(2)

        # Connect theme change
        self.theme_combo.currentIndexChanged.connect(self.change_theme)

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()

        main_layout.addWidget(theme_group)

        # Header tabs demo - THIS SHOWS THE TARGETED HEADER TABS
        header_group = QGroupBox("Header Tabs (Custom Styled)")
        header_layout = QHBoxLayout(header_group)

        self.tab1 = QPushButton("FTML Editor")
        self.tab1.setObjectName("headerTab")  # Important for CSS targeting
        self.tab1.setCheckable(True)
        self.tab1.setChecked(True)

        self.tab2 = QPushButton("Format Converter")
        self.tab2.setObjectName("headerTab")  # Important for CSS targeting
        self.tab2.setCheckable(True)

        # Connect tab buttons to toggle each other
        self.tab1.clicked.connect(lambda: self.toggle_tabs(0))
        self.tab2.clicked.connect(lambda: self.toggle_tabs(1))

        header_layout.addWidget(self.tab1)
        header_layout.addWidget(self.tab2)
        header_layout.addStretch()

        main_layout.addWidget(header_group)

        # Standard UI elements
        standard_group = QGroupBox("Standard UI Elements")
        standard_layout = QVBoxLayout(standard_group)

        # Buttons row
        buttons_layout = QHBoxLayout()

        standard_btn = QPushButton("Standard Button")

        # This is our custom styled convert button
        self.convert_btn = QPushButton("Convert →")
        self.convert_btn.setObjectName("convertButton")  # Important for CSS targeting

        buttons_layout.addWidget(standard_btn)
        buttons_layout.addWidget(self.convert_btn)
        buttons_layout.addStretch()

        # Checkboxes row
        checkbox_layout = QHBoxLayout()

        checkbox1 = QCheckBox("Option 1")
        checkbox2 = QCheckBox("Option 2")
        checkbox2.setChecked(True)

        checkbox_layout.addWidget(checkbox1)
        checkbox_layout.addWidget(checkbox2)
        checkbox_layout.addStretch()

        # Radio buttons row
        radio_layout = QHBoxLayout()

        radio1 = QRadioButton("Choice A")
        radio2 = QRadioButton("Choice B")
        radio1.setChecked(True)

        radio_layout.addWidget(radio1)
        radio_layout.addWidget(radio2)
        radio_layout.addStretch()

        # Add all rows to the standard group
        standard_layout.addLayout(buttons_layout)
        standard_layout.addLayout(checkbox_layout)
        standard_layout.addLayout(radio_layout)

        main_layout.addWidget(standard_group)

        # Text editor (to demonstrate text colors)
        editor_group = QGroupBox("Text Editor")
        editor_layout = QVBoxLayout(editor_group)

        self.text_edit = QTextEdit()
        self.text_edit.setPlainText("This is sample text to demonstrate the theme colors.\n" * 3)

        editor_layout.addWidget(self.text_edit)

        main_layout.addWidget(editor_group)

        # Add stretch to push everything up
        main_layout.addStretch()

        # Status bar
        self.statusBar().showMessage("Ready")

    def toggle_tabs(self, tab_index):
        """Toggle between tabs"""
        if tab_index == 0:
            self.tab1.setChecked(True)
            self.tab2.setChecked(False)
        else:
            self.tab1.setChecked(False)
            self.tab2.setChecked(True)

    def change_theme(self, index):
        """Change the application theme based on combo box selection"""
        if index == 0:
            new_theme = theme_manager.LIGHT
        elif index == 1:
            new_theme = theme_manager.DARK
        else:
            new_theme = theme_manager.AUTO

        logger.debug(f"Changing theme to {new_theme}")

        # Set theme in global theme manager
        theme_manager.set_theme(new_theme)

        # Apply the theme
        app = QApplication.instance()
        theme_manager.apply_theme(app)

        # Update status
        active_theme = "Light" if theme_manager.get_active_theme() == theme_manager.LIGHT else "Dark"
        self.statusBar().showMessage(f"Applied {active_theme} theme")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply theme from global theme manager
    theme_manager.apply_theme(app)

    window = SimpleThemeDemo()
    window.show()
    sys.exit(app.exec())