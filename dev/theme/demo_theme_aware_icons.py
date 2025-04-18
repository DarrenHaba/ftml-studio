import sys
import os
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter

# Import theme manager
# Adjust the import path as needed for your project structure
from src.ftml_studio.ui.themes.theme_manager import ThemeManager

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("icon_theme_demo")

# Create theme manager instance
theme_manager = ThemeManager()

class ThemedIconButton(QPushButton):
    """Button with theme-aware icon that adapts to light/dark mode"""

    def __init__(self, icon_name, text="", parent=None):
        super().__init__(text, parent)
        self.icon_name = icon_name
        self.icon_path = self.get_icon_path(icon_name)

        # Set button properties
        self.setIconSize(QSize(24, 24))
        self.setFixedSize(QSize(40, 40))

        # Update icon based on current theme
        self.update_icon()

    def get_icon_path(self, icon_name):
        """Get the path to the icon file"""
        # Try to find the icon in the project structure
        # Adjust these paths as needed for your project
        possible_paths = [
            f"{icon_name}.png",  # Current directory
            f"src/ftml_studio/ui/icons/{icon_name}.png",  # Project structure
            os.path.join(os.path.dirname(__file__), f"icons/{icon_name}.png")  # Relative to script
        ]

        for path in possible_paths:
            if os.path.exists(path):
                logger.debug(f"Found icon at: {path}")
                return path

        logger.warning(f"Icon '{icon_name}' not found in any of the expected locations")
        return None

    def update_icon(self):
        """Update the icon based on the current theme"""
        if not self.icon_path or not os.path.exists(self.icon_path):
            logger.warning("Cannot update icon: icon path is invalid")
            return

        # Load the original icon
        pixmap = QPixmap(self.icon_path)

        # Check if we need to tint the icon for light theme
        is_dark = theme_manager.get_active_theme() == theme_manager.DARK

        if not is_dark:
            # Apply tinting for light theme (assuming white icons)
            pixmap = self.tint_icon(pixmap, QColor(40, 40, 40))

        # Set the icon
        self.setIcon(QIcon(pixmap))

    def tint_icon(self, pixmap, color):
        """Tint the icon using source-in composition mode"""
        if pixmap.isNull():
            return pixmap

        # Create a new pixmap with the same size
        result = QPixmap(pixmap.size())
        result.fill(Qt.transparent)  # Start with transparent background

        # Create a painter
        painter = QPainter(result)

        # Draw the original pixmap
        painter.drawPixmap(0, 0, pixmap)

        # Apply color using SourceIn composition mode
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(result.rect(), color)
        painter.end()

        return result


class IconThemeDemo(QMainWindow):
    """Demo application showing theme-aware icons"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme-Aware Icon Demo")
        self.resize(600, 300)

        # Create and set up UI
        self.setup_ui()

    def setup_ui(self):
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
        self.theme_combo.addItems([theme_manager.LIGHT, theme_manager.DARK, theme_manager.AUTO])
        self.theme_combo.setCurrentText(theme_manager.current_theme)
        self.theme_combo.currentTextChanged.connect(self.change_theme)

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()

        main_layout.addLayout(theme_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # Demo area title
        title = QLabel("Icon Theme Adaptation Demo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title)

        # Icon demo container
        demo_layout = QHBoxLayout()

        # Create themed icon button
        self.icon_button = ThemedIconButton("settings")

        # Create explanation label
        self.explanation_label = QLabel()
        self.explanation_label.setWordWrap(True)
        self.update_explanation_text()

        # Add to layout
        demo_layout.addWidget(self.icon_button)
        demo_layout.addWidget(self.explanation_label, 1)  # Give the label stretch

        main_layout.addLayout(demo_layout)
        main_layout.addStretch(1)  # Push everything to the top

    def change_theme(self, theme):
        """Change the application theme"""
        # Update theme manager
        theme_manager.set_theme(theme)

        # Apply the theme to the application
        app = QApplication.instance()
        theme_manager.apply_theme(app)

        # Update the icon
        self.icon_button.update_icon()

        # Update explanation text
        self.update_explanation_text()

        # Update status bar
        is_dark = theme_manager.get_active_theme() == theme_manager.DARK
        theme_name = theme_manager.get_active_theme()
        self.statusBar().showMessage(f"Applied {theme_name} theme ({theme})")

    def update_explanation_text(self):
        """Update the explanation text based on the current theme"""
        is_dark = theme_manager.get_active_theme() == theme_manager.DARK
        theme_name = theme_manager.get_active_theme()

        if is_dark:
            explanation = (
                "<b>Dark Theme Active:</b> Using original white icon<br><br>"
                "In dark mode, the white icon is displayed as-is, since white "
                "provides good contrast against the dark background. No tinting is needed."
            )
        else:
            explanation = (
                "<b>Light Theme Active:</b> Using tinted (dark) icon<br><br>"
                "In light mode, the original white icon is dynamically tinted to dark gray "
                "using QPainter's CompositionMode_SourceIn. This preserves the icon's shape and "
                "transparency while changing its color to provide good contrast against "
                "the light background."
            )

        self.explanation_label.setText(explanation)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply initial theme
    theme_manager.apply_theme(app)

    window = IconThemeDemo()
    window.show()
    sys.exit(app.exec())