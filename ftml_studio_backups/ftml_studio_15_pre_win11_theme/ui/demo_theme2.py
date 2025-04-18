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

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("theme_tester")

class SimpleThemeDemo(QMainWindow):
    """Minimal window to test theme application"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Theme Testing")
        self.resize(600, 500)

        # Current theme state
        self.dark_mode = False

        # Set up UI
        self.setup_ui()

        # Apply initial theme
        self.apply_light_theme()

    def setup_ui(self):
        """Create a simple UI with various controls to test theme application"""
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Theme toggle button at the top
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_button = QPushButton("Toggle Dark Mode")
        self.theme_button.clicked.connect(self.toggle_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_button)
        theme_layout.addStretch()
        main_layout.addLayout(theme_layout)

        # Create a menu bar
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # File menu
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("New")
        file_menu.addAction("Open")
        file_menu.addAction("Save")
        file_menu.addSeparator()
        file_menu.addAction("Exit")

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction("Cut")
        edit_menu.addAction("Copy")
        edit_menu.addAction("Paste")

        # Group 1: Basic controls
        group1 = QGroupBox("Basic Controls")
        group1_layout = QVBoxLayout(group1)

        # Buttons
        button_layout = QHBoxLayout()
        normal_button = QPushButton("Normal Button")
        styled_button = QPushButton("Styled Button")
        styled_button.setStyleSheet("background-color: green; color: white;")
        button_layout.addWidget(normal_button)
        button_layout.addWidget(styled_button)
        group1_layout.addLayout(button_layout)

        # Checkboxes
        checkbox_layout = QHBoxLayout()
        checkbox1 = QCheckBox("Unchecked Box")
        checkbox2 = QCheckBox("Checked Box")
        checkbox2.setChecked(True)
        checkbox_layout.addWidget(checkbox1)
        checkbox_layout.addWidget(checkbox2)
        group1_layout.addLayout(checkbox_layout)

        # Radio buttons
        radio_layout = QHBoxLayout()
        radio1 = QRadioButton("Option 1")
        radio2 = QRadioButton("Option 2")
        radio1.setChecked(True)
        radio_layout.addWidget(radio1)
        radio_layout.addWidget(radio2)
        group1_layout.addLayout(radio_layout)

        # Combo box
        combo = QComboBox()
        combo.addItems(["Item 1", "Item 2", "Item 3"])
        group1_layout.addWidget(combo)

        # Slider and spin box
        slider_layout = QHBoxLayout()
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(50)
        spin_box = QSpinBox()
        spin_box.setRange(0, 100)
        spin_box.setValue(50)
        slider_layout.addWidget(slider)
        slider_layout.addWidget(spin_box)
        group1_layout.addLayout(slider_layout)

        main_layout.addWidget(group1)

        # Group 2: Text elements
        group2 = QGroupBox("Text Elements")
        group2_layout = QVBoxLayout(group2)

        # Text edit
        text_edit = QTextEdit()
        text_edit.setPlainText("This is a sample text to demonstrate theming.\n" * 5)
        group2_layout.addWidget(text_edit)

        # List widget
        list_widget = QListWidget()
        list_widget.addItems([f"List Item {i+1}" for i in range(10)])
        group2_layout.addWidget(list_widget)

        main_layout.addWidget(group2)

        # Add a scroll area with lots of content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Add many labels to force scrolling
        for i in range(20):
            label = QLabel(f"Scroll content line {i+1}")
            scroll_layout.addWidget(label)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Status bar at the bottom
        self.statusBar().showMessage("Ready")

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.dark_mode = not self.dark_mode

        if self.dark_mode:
            self.apply_dark_theme()
            self.theme_button.setText("Switch to Light Mode")
            self.statusBar().showMessage("Dark theme applied")
        else:
            self.apply_light_theme()
            self.theme_button.setText("Switch to Dark Mode")
            self.statusBar().showMessage("Light theme applied")

    def apply_light_theme(self):
        """Apply light theme to the application"""
        logger.debug("Applying light theme")
        app = QApplication.instance()

        # Using Fusion style for consistency
        # app.setStyle("Fusion")

        # Create and configure the palette
        palette = QPalette()

        # Define light theme colors
        window_color = QColor("#f5f5f5")
        text_color = QColor("#333333")
        base_color = QColor("#ffffff")
        alt_base_color = QColor("#f0f0f0")
        button_color = QColor("#e0e0e0")
        button_text_color = QColor("#333333")
        highlight_color = QColor("#4a86e8")
        highlight_text_color = QColor("#ffffff")
        link_color = QColor("#2979ff")
        border_color = QColor("#aaaaaa")

        # Set colors for all palette roles
        palette.setColor(QPalette.Window, window_color)
        palette.setColor(QPalette.WindowText, text_color)
        palette.setColor(QPalette.Base, base_color)
        palette.setColor(QPalette.AlternateBase, alt_base_color)
        palette.setColor(QPalette.Text, text_color)
        palette.setColor(QPalette.Button, button_color)
        palette.setColor(QPalette.ButtonText, button_text_color)
        palette.setColor(QPalette.BrightText, QColor("#ffffff"))
        palette.setColor(QPalette.Highlight, highlight_color)
        palette.setColor(QPalette.HighlightedText, highlight_text_color)
        palette.setColor(QPalette.Link, link_color)
        palette.setColor(QPalette.LinkVisited, link_color.darker(120))

        # Border colors
        palette.setColor(QPalette.Light, border_color.lighter(120))
        palette.setColor(QPalette.Midlight, border_color)
        palette.setColor(QPalette.Mid, border_color.darker(110))
        palette.setColor(QPalette.Dark, border_color.darker(130))
        palette.setColor(QPalette.Shadow, QColor("#999999"))

        # Tooltip colors
        palette.setColor(QPalette.ToolTipBase, QColor("#f0f0f0"))
        palette.setColor(QPalette.ToolTipText, QColor("#333333"))

        # Placeholder text
        palette.setColor(QPalette.PlaceholderText, QColor("#808080"))

        # Apply the palette
        app.setPalette(palette)

        # Print debug info about key palette colors
        self.debug_palette_colors(palette)

    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        logger.debug("Applying dark theme")
        app = QApplication.instance()

        # Using Fusion style for consistency
        app.setStyle("Fusion")

        # Create and configure the palette
        palette = QPalette()

        # Define dark theme colors
        window_color = QColor("#2d2d2d")
        text_color = QColor("#f5f5f5")
        base_color = QColor("#1e1e1e")
        alt_base_color = QColor("#353535")
        button_color = QColor("#454545")
        button_text_color = QColor("#f5f5f5")
        highlight_color = QColor("#4a86e8")
        highlight_text_color = QColor("#ffffff")
        link_color = QColor("#56a3ff")
        border_color = QColor("#555555")

        # Set colors for all palette roles
        palette.setColor(QPalette.Window, window_color)
        palette.setColor(QPalette.WindowText, text_color)
        palette.setColor(QPalette.Base, base_color)
        palette.setColor(QPalette.AlternateBase, alt_base_color)
        palette.setColor(QPalette.Text, text_color)
        palette.setColor(QPalette.Button, button_color)
        palette.setColor(QPalette.ButtonText, button_text_color)
        palette.setColor(QPalette.BrightText, QColor("#ffffff"))
        palette.setColor(QPalette.Highlight, highlight_color)
        palette.setColor(QPalette.HighlightedText, highlight_text_color)
        palette.setColor(QPalette.Link, link_color)
        palette.setColor(QPalette.LinkVisited, link_color.lighter(120))

        # Border colors
        palette.setColor(QPalette.Light, border_color.lighter(120))
        palette.setColor(QPalette.Midlight, border_color)
        palette.setColor(QPalette.Mid, border_color.darker(110))
        palette.setColor(QPalette.Dark, border_color.darker(130))
        palette.setColor(QPalette.Shadow, QColor("#000000"))

        # Tooltip colors
        palette.setColor(QPalette.ToolTipBase, QColor("#383838"))
        palette.setColor(QPalette.ToolTipText, QColor("#f5f5f5"))

        # Placeholder text
        palette.setColor(QPalette.PlaceholderText, QColor("#aaaaaa"))

        # Apply the palette
        app.setPalette(palette)

        # Print debug info about key palette colors
        self.debug_palette_colors(palette)

    def debug_palette_colors(self, palette):
        """Print key palette colors for debugging"""
        logger.debug("=== Palette Color Debug ===")
        roles = {
            "Window": QPalette.Window,
            "WindowText": QPalette.WindowText,
            "Base": QPalette.Base,
            "AlternateBase": QPalette.AlternateBase,
            "Text": QPalette.Text,
            "Button": QPalette.Button,
            "ButtonText": QPalette.ButtonText,
            "Highlight": QPalette.Highlight,
            "Light": QPalette.Light,
            "Midlight": QPalette.Midlight,
            "Dark": QPalette.Dark,
            "Mid": QPalette.Mid
        }

        for name, role in roles.items():
            color = palette.color(role)
            logger.debug(f"{name}: RGB({color.red()},{color.green()},{color.blue()}) | Hex: {color.name()}")

        logger.debug("=========================")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleThemeDemo()
    window.show()
    sys.exit(app.exec())