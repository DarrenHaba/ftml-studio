# src/ftml_studio/ui/themes/theme_manager.py

# https://fonts.google.com/icons
# icon size: 48px - 36px
# dark icon color: #434343
# light icon color: #ffffff

import logging
import platform
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import QSettings

logger = logging.getLogger("theme_manager")


class ThemeManager:
    """Simplified theme manager using Windows 11 style with green accent"""

    # Theme constants
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"
    THEMES = [LIGHT, DARK, AUTO]

    # Singleton instance
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.current_theme = self.AUTO  # Default theme
        self.settings = QSettings("FTMLStudio", "AppSettings")

        # Define default accent colors for each theme
        self._light_accent_color = "#327334"  # Material Design Green (darker shade)
        self._dark_accent_color = "#67B16A"   # Material Design Green (lighter shade)

        # Load saved settings
        self._load_saved_settings()

        # Initialize minimal syntax highlighting colors
        self._initialize_basic_colors()

    def _load_saved_settings(self):
        """Load all saved settings from QSettings"""
        # Load theme setting
        saved_theme = self.settings.value("theme", self.AUTO)
        if saved_theme in self.THEMES:
            self.current_theme = saved_theme

        # Load accent colors if they exist in settings
        if self.settings.contains("appearance/lightAccentColor"):
            self._light_accent_color = self.settings.value("appearance/lightAccentColor")

        if self.settings.contains("appearance/darkAccentColor"):
            self._dark_accent_color = self.settings.value("appearance/darkAccentColor")

    def save_theme(self):
        """Save the current theme to settings"""
        self.settings.setValue("theme", self.current_theme)

    def _initialize_basic_colors(self):
        """Initialize basic color schemes for syntax highlighting"""
        # Light theme minimal syntax colors
        self.light_colors = {
            "accent": self._light_accent_color,
            "error": "#FF0000",
            # Syntax highlighting colors
            "keyword": "#0033b3",
            "function": "#7a3e9d",
            "string": "#1B5E20",
            "number": "#ff8c00",
            "boolean": "#9900cc",
            "null": "#9900cc",
            "comment": "#7c7c7c",
            "docComment": "#585858",
            "symbol": "#555555",
            "operator": "#555555",
            "editorBg": "#F5F5F5",
            "lineNumber": "#999999",
            "selection": "#E3F2FD"
        }

        # Dark theme minimal syntax colors
        self.dark_colors = {
            "accent": self._dark_accent_color,
            "error": "#FF5252",
            # Syntax highlighting colors
            "keyword": "#569cd6",
            "function": "#dcdcaa",
            "string": "#6aaa64",
            "number": "#ff8c00",
            "boolean": "#bb86fc",
            "null": "#bb86fc",
            "comment": "#7c7c7c",
            "docComment": "#bcbcbc",
            "symbol": "#d4d4d4",
            "operator": "#a9a9a9",
            "editorBg": "#1E1E1E",
            "lineNumber": "#858585",
            "selection": "#264f78"
        }

    @property
    def accent_color(self):
        """Get the accent color for the current active theme"""
        active_theme = self.get_active_theme()
        return self._dark_accent_color if active_theme == self.DARK else self._light_accent_color

    @accent_color.setter
    def accent_color(self, color_value):
        """Set the accent color for the current active theme"""
        active_theme = self.get_active_theme()
        if active_theme == self.DARK:
            self._dark_accent_color = color_value
            self.dark_colors["accent"] = color_value
            self.settings.setValue("appearance/darkAccentColor", color_value)
        else:
            self._light_accent_color = color_value
            self.light_colors["accent"] = color_value
            self.settings.setValue("appearance/lightAccentColor", color_value)

    @property
    def light_accent_color(self):
        """Get the light theme accent color"""
        return self._light_accent_color

    @light_accent_color.setter
    def light_accent_color(self, color_value):
        """Set the light theme accent color"""
        self._light_accent_color = color_value
        self.light_colors["accent"] = color_value
        self.settings.setValue("appearance/lightAccentColor", color_value)

    @property
    def dark_accent_color(self):
        """Get the dark theme accent color"""
        return self._dark_accent_color

    @dark_accent_color.setter
    def dark_accent_color(self, color_value):
        """Set the dark theme accent color"""
        self._dark_accent_color = color_value
        self.dark_colors["accent"] = color_value
        self.settings.setValue("appearance/darkAccentColor", color_value)

    def get_color(self, key):
        """Get a basic color for the current theme"""
        active_theme = self.get_active_theme()
        colors = self.dark_colors if active_theme == self.DARK else self.light_colors

        if key in colors:
            return colors[key]
        else:
            logger.warning(f"Color '{key}' not found")
            return "#000000"  # Default black

    def get_syntax_color(self, key):
        """Get a syntax highlighting color for the current theme"""
        return self.get_color(key)

    def _detect_system_theme(self):
        """
        Detect if the system is using a dark theme
        Returns True for dark theme, False for light theme
        """
        try:
            # Windows-specific detection
            if platform.system() == "Windows":
                import winreg
                registry_key = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key)
                value, _ = winreg.QueryValueEx(reg_key, "AppsUseLightTheme")
                winreg.CloseKey(reg_key)
                return value == 0  # 0 means dark theme

            # macOS detection
            elif platform.system() == "Darwin":
                import subprocess
                result = subprocess.run(
                    ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                    capture_output=True, text=True
                )
                return 'Dark' in result.stdout

        except Exception as e:
            logger.warning(f"Error detecting system theme: {e}")

        # Fallback: check application palette
        if QApplication.instance():
            palette = QApplication.palette()
            bg_color = palette.color(QPalette.Window)
            return bg_color.lightness() < 128  # Dark if lightness is low

        return False  # Default to light theme

    def get_active_theme(self):
        """Get the current active theme (resolving auto if needed)"""
        if self.current_theme == self.AUTO:
            return self.DARK if self._detect_system_theme() else self.LIGHT
        return self.current_theme

    def set_theme(self, theme):
        """Set the current theme and save the preference"""
        if theme in self.THEMES:
            self.current_theme = theme
            self.save_theme()
            logger.debug(f"Theme set to {theme}")
        else:
            logger.warning(f"Invalid theme: {theme}")

    def create_light_palette(self):
        """Create a light palette with custom accent"""
        palette = QPalette()
        accent_color = QColor(self._light_accent_color)

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
        palette.setColor(QPalette.Highlight, accent_color)
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        palette.setColor(QPalette.Link, accent_color)

        try:
            # This is available in PySide6 6.6+
            palette.setColor(QPalette.Accent, accent_color)
        except AttributeError:
            pass

        return palette

    def create_dark_palette(self):
        """Create a dark palette with custom accent"""
        palette = QPalette()
        accent_color = QColor(self._dark_accent_color)

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
        palette.setColor(QPalette.Highlight, accent_color)
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        palette.setColor(QPalette.Link, accent_color)

        try:
            # This is available in PySide6 6.6+
            palette.setColor(QPalette.Accent, accent_color)
        except AttributeError:
            pass

        return palette

    def apply_theme(self, app):
        """Apply the current theme to the application"""
        # Set application style to Windows 11
        app.setStyle("windows11")

        # Get active theme (resolving AUTO if needed)
        active_theme = self.get_active_theme()
        logger.debug(f"Applying theme: {self.current_theme} (resolved to {active_theme})")

        # Apply appropriate palette
        if active_theme == self.LIGHT:
            app.setPalette(self.create_light_palette())
        else:  # DARK
            app.setPalette(self.create_dark_palette())

    def reset_colors(self):
        """Reset accent colors to default values"""
        self._light_accent_color = "#429a44"  # Material Design Green (darker shade)
        self._dark_accent_color = "#327334"   # Material Design Green (lighter shade)

        # Update color dictionaries
        self.light_colors["accent"] = self._light_accent_color
        self.dark_colors["accent"] = self._dark_accent_color

        # Save to settings
        self.settings.setValue("appearance/lightAccentColor", self._light_accent_color)
        self.settings.setValue("appearance/darkAccentColor", self._dark_accent_color)
