import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QCheckBox, QScrollArea, QTextEdit,
    QComboBox, QGroupBox, QRadioButton, QSlider, QTabWidget,
    QMenu, QMenuBar, QListWidget, QSpinBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPalette, QColor, QFont

# Import our theme manager
from src.ftml_studio.ui.themes import theme_manager

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("theme_tester")

class ThemeDemo(QMainWindow):
    """Demo window to test our improved theme application"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FTML Studio Theme Demo")
        self.resize(800, 600)

        # Set up UI
        self.setup_ui()

    def setup_ui(self):
        """Create a UI with various controls to test theme application"""
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Theme selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        theme_label.setObjectName("settingsLabel")

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Light")
        self.theme_combo.addItem("Dark")
        self.theme_combo.addItem("Auto (System)")

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

        main_layout.addLayout(theme_layout)

        # Header tabs demo
        header_demo = QGroupBox("Header Tabs")
        header_layout = QHBoxLayout(header_demo)

        self.tab1 = QPushButton("FTML Editor")
        self.tab1.setObjectName("headerTab")
        self.tab1.setCheckable(True)
        self.tab1.setChecked(True)

        self.tab2 = QPushButton("Format Converter")
        self.tab2.setObjectName("headerTab")
        self.tab2.setCheckable(True)

        # Connect tab buttons to toggle each other
        self.tab1.clicked.connect(lambda: self.toggle_tabs(0))
        self.tab2.clicked.connect(lambda: self.toggle_tabs(1))

        header_layout.addWidget(self.tab1)
        header_layout.addWidget(self.tab2)
        header_layout.addStretch()

        main_layout.addWidget(header_demo)

        # Button styles demo
        button_demo = QGroupBox("Button Styles")
        button_layout = QVBoxLayout(button_demo)

        # Regular buttons
        regular_buttons = QHBoxLayout()

        normal_btn = QPushButton("Standard Button")

        convert_btn = QPushButton("Convert →")
        convert_btn.setObjectName("convertButton")

        settings_btn = QPushButton("⚙")
        settings_btn.setObjectName("settingsButton")
        settings_btn.setFixedSize(30, 30)

        regular_buttons.addWidget(normal_btn)
        regular_buttons.addWidget(convert_btn)
        regular_buttons.addWidget(settings_btn)
        regular_buttons.addStretch()

        # Checkable buttons
        checkable_buttons = QHBoxLayout()

        check_btn1 = QPushButton("Option 1")
        check_btn1.setCheckable(True)
        check_btn1.setChecked(True)

        check_btn2 = QPushButton("Option 2")
        check_btn2.setCheckable(True)

        check_btn3 = QPushButton("Option 3")
        check_btn3.setCheckable(True)

        checkable_buttons.addWidget(check_btn1)
        checkable_buttons.addWidget(check_btn2)
        checkable_buttons.addWidget(check_btn3)
        checkable_buttons.addStretch()

        button_layout.addLayout(regular_buttons)
        button_layout.addLayout(checkable_buttons)

        main_layout.addWidget(button_demo)

        # Form controls demo
        form_demo = QGroupBox("Form Controls")
        form_layout = QVBoxLayout(form_demo)

        # Checkboxes
        checkbox_layout = QHBoxLayout()
        checkbox1 = QCheckBox("Enable feature 1")
        checkbox2 = QCheckBox("Enable feature 2")
        checkbox2.setChecked(True)

        checkbox_layout.addWidget(checkbox1)
        checkbox_layout.addWidget(checkbox2)
        checkbox_layout.addStretch()

        # Radio buttons
        radio_layout = QHBoxLayout()
        radio1 = QRadioButton("Option A")
        radio2 = QRadioButton("Option B")
        radio3 = QRadioButton("Option C")
        radio1.setChecked(True)

        radio_layout.addWidget(radio1)
        radio_layout.addWidget(radio2)
        radio_layout.addWidget(radio3)
        radio_layout.addStretch()

        # Combo box
        combo_layout = QHBoxLayout()
        combo_label = QLabel("Selection:")
        combo = QComboBox()
        combo.addItems(["First Choice", "Second Choice", "Third Choice"])

        combo_layout.addWidget(combo_label)
        combo_layout.addWidget(combo)
        combo_layout.addStretch()

        form_layout.addLayout(checkbox_layout)
        form_layout.addLayout(radio_layout)
        form_layout.addLayout(combo_layout)

        main_layout.addWidget(form_demo)

        # Text fields demo
        text_demo = QGroupBox("Text Fields")
        text_layout = QVBoxLayout(text_demo)

        text_edit = QTextEdit()
        text_edit.setPlainText("This is sample text to demonstrate theme application.\n" * 3)

        text_layout.addWidget(text_edit)

        main_layout.addWidget(text_demo)

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
        theme_name = "Light" if theme_manager.get_active_theme() == theme_manager.LIGHT else "Dark"
        self.statusBar().showMessage(f"Applied {theme_name} theme")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply theme from global theme manager
    theme_manager.apply_theme(app)

    window = ThemeDemo()
    window.show()
    sys.exit(app.exec())