import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QCheckBox, QComboBox, QRadioButton,
    QColorDialog, QTabWidget, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QStyleFactory

# Import our simple theme manager
from src.ftml_studio.ui.themes import theme_manager

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("style_demo")

class ColorPreviewWidget(QWidget):
    """Widget to preview and select a color"""

    def __init__(self, initial_color="#4a86e8", parent=None):
        super().__init__(parent)
        self.color = QColor(initial_color)
        self.setMinimumSize(30, 20)
        self.setMaximumHeight(20)
        self.setStyleSheet(f"background-color: {self.color.name()}; border: 1px solid #888888;")

    def set_color(self, color):
        """Set the preview color"""
        self.color = QColor(color)
        self.setStyleSheet(f"background-color: {self.color.name()}; border: 1px solid #888888;")

    def get_color(self):
        """Get the current color"""
        return self.color.name()

class SimpleStyleDemo(QMainWindow):
    """Demo to test built-in Qt styles and accent color"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt Style Demo")
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

        style_layout.addWidget(style_label)
        style_layout.addWidget(self.style_combo)
        style_layout.addStretch()

        main_layout.addLayout(style_layout)

        # Accent color selector
        accent_layout = QHBoxLayout()

        accent_label = QLabel("Accent Color:")
        self.color_preview = ColorPreviewWidget(theme_manager.accent_color)
        self.color_button = QPushButton("Choose Color...")
        self.color_button.clicked.connect(self.choose_accent_color)

        accent_layout.addWidget(accent_label)
        accent_layout.addWidget(self.color_preview)
        accent_layout.addWidget(self.color_button)
        accent_layout.addStretch()

        main_layout.addLayout(accent_layout)

        # Apply button
        apply_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply Style & Color")
        apply_btn.clicked.connect(self.apply_style)
        apply_layout.addWidget(apply_btn)
        apply_layout.addStretch()

        main_layout.addLayout(apply_layout)

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

        # Combo box for testing highlight color
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

        # Third tab - More Controls
        tab3 = QWidget()
        tab3_layout = QVBoxLayout(tab3)
        tab3_layout.addWidget(QLabel("This tab can have more controls if needed."))
        tab3_layout.addStretch()

        # Add tabs to tab widget
        self.tab_widget.addTab(tab1, "Controls")
        self.tab_widget.addTab(tab2, "Text Editor")
        self.tab_widget.addTab(tab3, "Extra")

        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)

        # Status bar
        self.statusBar().showMessage("Ready")

    def choose_accent_color(self):
        """Open a color dialog to choose the accent color"""
        current_color = QColor(self.color_preview.get_color())
        color = QColorDialog.getColor(current_color, self, "Choose Accent Color")

        if color.isValid():
            self.color_preview.set_color(color.name())
            self.statusBar().showMessage(f"Selected color: {color.name()}")

    def apply_style(self):
        """Apply the selected style and accent color"""
        # Get selected style
        style_name = self.style_combo.currentText()

        # Get selected accent color
        accent_color = self.color_preview.get_color()

        app = QApplication.instance()

        # Set the style and accent color in theme manager
        theme_manager.set_style(style_name)
        theme_manager.set_accent_color(accent_color)

        # Apply the style and accent color
        success = theme_manager.apply_style(app)

        if success:
            self.statusBar().showMessage(f"Applied style: {style_name} with accent color: {accent_color}")
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