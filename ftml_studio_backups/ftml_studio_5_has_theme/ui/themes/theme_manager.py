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

    def _is_system_dark_theme(self):
        """Detect if the system is using a dark theme"""
        # This is a simplified check
        palette = QApplication.palette()
        bg_color = palette.color(QPalette.Window)
        return bg_color.lightness() < 128

    def apply_theme(self, app, theme=None):
        """Apply the specified theme to the application"""
        if theme is not None and theme in self.THEMES:
            self.current_theme = theme
            self._save_theme()

        # Determine which theme to actually use
        active_theme = self.current_theme
        if active_theme == "auto":
            active_theme = "dark" if self._is_system_dark_theme() else "light"

        # Apply the theme
        if active_theme == "dark":
            self._apply_dark_palette(app)
        else:
            self._apply_light_palette(app)

        # Apply custom component styles
        app.setStyleSheet(self._get_component_styles(active_theme))

        logger.debug(f"Applied theme: {self.current_theme} (resolved to {active_theme})")

    def _apply_light_palette(self, app):
        """Apply the light palette to the application"""
        # Use Qt's default light palette with minimal overrides
        app.setStyle("Fusion")  # Use Fusion style for consistency

        # Use default palette (which is light)
        palette = QPalette()
        app.setPalette(palette)

    def _apply_dark_palette(self, app):
        """Apply the dark palette to the application"""
        app.setStyle("Fusion")  # Use Fusion style for consistency

        # Create dark palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)

        app.setPalette(palette)

    def _get_component_styles(self, theme):
        """Get component-specific styles for the theme"""
        # Only override specific components
        if theme == "dark":
            return """
            /* Specific component overrides for dark theme */
            QLabel#conversionInfo {
                background-color: #3d3d3d;
                color: #90caf9;
                border: 1px solid #555;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
            }
            QSplitter::handle {
                background-color: #555;
            }
            QPushButton#convertButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                font-weight: bold;
                border-radius: 4px;
                border: none;
            }
            QPushButton#convertButton:hover {
                background-color: #45a049;
            }
            QPushButton#convertButton:pressed {
                background-color: #3d8b40;
            }
            """
        else:
            return """
            /* Specific component overrides for light theme */
            QLabel#conversionInfo {
                background-color: #f0f0f0;
                color: #2196F3;
                border: 1px solid #ddd;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
            }
            QSplitter::handle {
                background-color: #ddd;
            }
            QPushButton#convertButton {
                background-color: #4a86e8;
                color: white;
                padding: 12px;
                font-weight: bold;
                border-radius: 4px;
                border: none;
            }
            QPushButton#convertButton:hover {
                background-color: #3a76d8;
            }
            QPushButton#convertButton:pressed {
                background-color: #2a66c8;
            }
            """

    def get_color(self, role, theme=None):
        """Get a specific color for the current theme"""
        if theme is None:
            theme = self.current_theme

        if theme == "auto":
            theme = "dark" if self._is_system_dark_theme() else "light"

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
                "text": "#f5f5f5",
                "border": "#555555"
            }
        }

        return colors[theme].get(role, "#000000")