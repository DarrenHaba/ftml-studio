# src/ftml_studio/ui/themes/theme_manager.py
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt, QSettings

logger = logging.getLogger("theme_manager")


class ThemeManager:
    """Manages application themes and provides consistent styling"""

    THEMES = ["light", "dark", "auto"]

    def __init__(self):
        self.current_theme = "auto"  # Default theme
        self.settings = QSettings("FTMLStudio", "AppSettings")
        self._load_saved_theme()

    def _load_saved_theme(self):
        """Load the saved theme from settings"""
        saved_theme = self.settings.value("theme", "auto")
        if saved_theme in self.THEMES:
            self.current_theme = saved_theme

    def _save_theme(self):
        """Save the current theme to settings"""
        self.settings.setValue("theme", self.current_theme)

    def get_stylesheet(self, theme=None):
        """Get the stylesheet for the specified theme or current theme"""
        if theme is None:
            theme = self.current_theme

        if theme == "auto":
            # Detect system theme
            if self._is_system_dark_theme():
                theme = "dark"
            else:
                theme = "light"

        return self._get_theme_stylesheet(theme)

    def _is_system_dark_theme(self):
        """Detect if the system is using a dark theme"""
        # This is a simplified check that could be improved
        # with platform-specific detection
        palette = QApplication.palette()
        bg_color = palette.color(QPalette.Window)
        return bg_color.lightness() < 128

    def apply_theme(self, app, theme=None):
        """Apply the specified theme to the application"""
        if theme is not None and theme in self.THEMES:
            self.current_theme = theme
            self._save_theme()

        stylesheet = self.get_stylesheet()
        app.setStyleSheet(stylesheet)
        logger.debug(f"Applied theme: {self.current_theme} (resolved to {theme if theme else self.current_theme})")

    def _get_theme_stylesheet(self, theme):
        """Get the stylesheet for the specified theme"""
        if theme == "light":
            return self._get_light_theme()
        elif theme == "dark":
            return self._get_dark_theme()
        return ""

    def _get_light_theme(self):
        """Get the light theme stylesheet"""
        return """
        QWidget {
            background-color: #f5f5f5;
            color: #333333;
        }
        QMainWindow, QDialog {
            background-color: #f8f8f8;
        }
        QTextEdit {
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #cccccc;
            border-radius: 4px;
        }
        QPushButton {
            background-color: #4a86e8;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            border: none;
        }
        QPushButton:hover {
            background-color: #3a76d8;
        }
        QPushButton:pressed {
            background-color: #2a66c8;
        }
        QLabel {
            color: #333333;
        }
        QComboBox {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 4px;
            min-width: 6em;
        }
        QComboBox:drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            border-left: 1px solid #cccccc;
        }
        QSplitter::handle {
            background-color: #dddddd;
        }
        """

    def _get_dark_theme(self):
        """Get the dark theme stylesheet"""
        return """
        QWidget {
            background-color: #2d2d2d;
            color: #cccccc;
        }
        QMainWindow, QDialog {
            background-color: #1e1e1e;
        }
        QTextEdit {
            background-color: #252525;
            color: #e0e0e0;
            border: 1px solid #555555;
            border-radius: 4px;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            border: none;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        QLabel {
            color: #cccccc;
        }
        QComboBox {
            background-color: #3d3d3d;
            color: #cccccc;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 4px;
            min-width: 6em;
        }
        QComboBox:drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            border-left: 1px solid #555555;
        }
        QSplitter::handle {
            background-color: #555555;
        }
        """

    def get_color(self, role, theme=None):
        """Get a specific color for the current theme"""
        # This would be expanded for specific color roles your app needs
        if theme is None:
            theme = self.current_theme

        if theme == "auto":
            # Resolve auto theme
            if self._is_system_dark_theme():
                theme = "dark"
            else:
                theme = "light"

        colors = {
            "light": {
                "primary": "#4a86e8",
                "success": "#4CAF50",
                "warning": "#FFC107",
                "error": "#F44336",
                "background": "#f5f5f5",
                "text": "#333333",
                "border": "#cccccc"
            },
            "dark": {
                "primary": "#4a86e8",
                "success": "#4CAF50",
                "warning": "#FFC107",
                "error": "#F44336",
                "background": "#2d2d2d",
                "text": "#cccccc",
                "border": "#555555"
            }
        }

        return colors[theme].get(role, "#000000")