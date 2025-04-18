import sys
import logging
import platform
import ctypes
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QCheckBox, QComboBox, QRadioButton, QTabWidget, QTextEdit
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette, QColor

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("windows11_theme_demo")

# Theme Constants
THEME_LIGHT = "light"
THEME_DARK = "dark"
THEME_AUTO = "auto"

def get_windows_theme():
    """Detect if Windows is using light or dark theme"""
    try:
        # Access Windows registry to get theme setting
        # 0 = Light, 1 = Dark
        if platform.system() == "Windows":
            registry_key = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            registry_value = "AppsUseLightTheme"

            # Open registry
            import winreg
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key)
            value, _ = winreg.QueryValueEx(reg_key, registry_value)
            winreg.CloseKey(reg_key)

            return THEME_LIGHT if value == 1 else THEME_DARK
    except Exception as e:
        logger.error(f"Failed to detect system theme: {e}")

    # Default to light theme if detection fails
    return THEME_LIGHT

def create_light_palette():
    """Create a soft gray palette with green accent"""
    palette = QPalette()
    green_accent = QColor("#4CAF50")  # Material Design Green

    # Text colors - slightly softened from pure black
    palette.setColor(QPalette.WindowText, QColor(40, 40, 40))
    palette.setColor(QPalette.Text, QColor(40, 40, 40))
    palette.setColor(QPalette.ButtonText, QColor(40, 40, 40))

    # Background colors - more grayish, less bright white
    palette.setColor(QPalette.Window, QColor(225, 225, 225))
    palette.setColor(QPalette.Base, QColor(235, 235, 235))
    palette.setColor(QPalette.AlternateBase, QColor(215, 215, 215))

    # Button colors
    palette.setColor(QPalette.Button, QColor(220, 220, 220))

    # Highlight colors
    palette.setColor(QPalette.Highlight, green_accent)
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    palette.setColor(QPalette.Link, green_accent)

    try:
        # This is available in Qt 6.6+
        palette.setColor(QPalette.Accent, green_accent)
    except AttributeError:
        pass

    return palette

def create_dark_palette():
    """Create a dark palette with green accent"""
    palette = QPalette()
    green_accent = QColor("#4CAF50")  # Material Design Green

    # Text colors
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))

    # Background colors
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.Base, QColor(42, 42, 42))
    palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))

    # Button colors
    palette.setColor(QPalette.Button, QColor(53, 53, 53))

    # Highlight colors
    palette.setColor(QPalette.Highlight, green_accent)
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    palette.setColor(QPalette.Link, green_accent)

    try:
        # This is available in Qt 6.6+
        palette.setColor(QPalette.Accent, green_accent)
    except AttributeError:
        pass

    return palette

def apply_theme(app, theme):
    """Apply theme to the application"""
    # Get the current palette
    if theme == THEME_LIGHT:
        app.setPalette(create_light_palette())
        logger.debug("Applied light theme with green accent")
    elif theme == THEME_DARK:
        app.setPalette(create_dark_palette())
        logger.debug("Applied dark theme with green accent")
    elif theme == THEME_AUTO:
        # Use system theme
        system_theme = get_windows_theme()
        if system_theme == THEME_LIGHT:
            app.setPalette(create_light_palette())
            logger.debug("Applied light theme (auto) with green accent")
        else:
            app.setPalette(create_dark_palette())
            logger.debug("Applied dark theme (auto) with green accent")


class Windows11ThemeDemo(QMainWindow):
    """Demo with Windows 11 theme and green accent color"""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Windows 11 Theme Demo")
        self.resize(600, 500)
        self.current_theme = THEME_AUTO

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
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([THEME_LIGHT, THEME_DARK, THEME_AUTO])
        self.theme_combo.setCurrentText(self.current_theme)
        self.theme_combo.currentTextChanged.connect(self.change_theme)

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()

        main_layout.addLayout(theme_layout)

        # Status label
        self.status_label = QLabel("Windows 11 Theme with Green Accent")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

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

        # If auto theme, setup timer to check for system theme changes
        if self.current_theme == THEME_AUTO:
            self.theme_timer = QTimer(self)
            self.theme_timer.timeout.connect(self.check_system_theme)
            self.theme_timer.start(5000)  # Check every 5 seconds

    def change_theme(self, theme):
        """Change the theme"""
        self.current_theme = theme
        apply_theme(self.app, theme)

        # Stop or start the theme timer based on selection
        if hasattr(self, 'theme_timer'):
            if theme == THEME_AUTO:
                self.theme_timer.start(5000)
            else:
                self.theme_timer.stop()

        # Update status message
        self.statusBar().showMessage(f"Applied {theme} theme with Green Accent Color")

    def check_system_theme(self):
        """Periodically check if system theme has changed (for auto mode)"""
        if self.current_theme == THEME_AUTO:
            apply_theme(self.app, THEME_AUTO)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set the Windows 11 style
    app.setStyle("windows11")

    # Apply initial theme (auto by default)
    apply_theme(app, THEME_AUTO)

    window = Windows11ThemeDemo(app)
    window.show()
    sys.exit(app.exec())