# src/ftml_studio/ui/themes/theme_manager.py
import logging
import sys
from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt, QSettings

logger = logging.getLogger("theme_manager")

class ThemeManager:
    """Simplified theme manager that uses direct palette application"""

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
        self._load_saved_theme()

        # Initialize syntax highlighting colors for both themes
        self.initialize_syntax_colors()

    def _load_saved_theme(self):
        """Load the saved theme from settings"""
        saved_theme = self.settings.value("theme", self.AUTO)
        if saved_theme in self.THEMES:
            self.current_theme = saved_theme

    def save_theme(self):
        """Save the current theme to settings"""
        self.settings.setValue("theme", self.current_theme)

    def initialize_syntax_colors(self):
        """Initialize syntax highlighting color schemes"""
        # Light theme syntax colors
        self.light_syntax = {
            "keyword": "#0033b3",      # Keywords and keys
            "function": "#7a3e9d",     # Functions
            "string": "#067d17",       # String literals
            "number": "#ff8c00",       # Numeric literals - changed to orange
            "boolean": "#9900cc",      # Boolean literals - changed to purple
            "null": "#9900cc",         # Null literal - changed to purple
            "comment": "#737373",      # Comments
            "docComment": "#7ea7b8",   # Documentation comments
            "symbol": "#555555",       # Punctuation and symbols
            "operator": "#555555",     # Operators
            "error": "#ff0000",        # Errors
            "background": "#ffffff",   # Editor background
            "lineNumber": "#999999",   # Line numbers
            "selection": "#add8e6"     # Selected text background
        }
    
        # Dark theme syntax colors
        self.dark_syntax = {
            "keyword": "#569cd6",      # Keywords and keys (blue)
            "function": "#dcdcaa",     # Functions
            "string": "#6aaa64",       # String literals (green)
            "number": "#ff8c00",       # Numeric literals (orange)  
            "boolean": "#bb86fc",      # Boolean literals (medium purple)
            "null": "#bb86fc",         # Null literal (medium purple)
            "comment": "#7c7c7c",      # Comments (gray-green)
            "docComment": "#bcbcbc",   # Documentation comments
            "symbol": "#d4d4d4",       # Punctuation and symbols
            "operator": "#a9a9a9",     # Operators (light gray)
            "error": "#ff5555",        # Errors
            "background": "#1e1e1e",   # Editor background
            "lineNumber": "#858585",   # Line numbers
            "selection": "#264f78"     # Selected text background
        }

    def get_syntax_color(self, key):
        """Get a syntax highlighting color for the current theme"""
        active_theme = self.get_active_theme()
        colors = self.dark_syntax if active_theme == self.DARK else self.light_syntax

        if key in colors:
            return colors[key]
        else:
            logger.warning(f"Syntax color '{key}' not found")
            return "#000000"  # Default black

    def _detect_system_theme(self):
        """
        Detect if the system is using a dark theme
        Returns True for dark theme, False for light theme
        """
        if not QApplication.instance():
            return False  # Default to light if no app instance

        # Check the operating system
        if sys.platform == 'win32':
            # Windows-specific detection
            try:
                import winreg
                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return value == 0  # 0 means dark theme
            except Exception as e:
                logger.warning(f"Error detecting Windows theme: {e}")
                # Fallback to color detection

        elif sys.platform == 'darwin':
            # macOS detection
            try:
                import subprocess
                result = subprocess.run(
                    ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                    capture_output=True, text=True
                )
                return 'Dark' in result.stdout
            except Exception as e:
                logger.warning(f"Error detecting macOS theme: {e}")
                # Fallback to color detection

        # Fallback method: check system colors
        palette = QApplication.palette()
        background_color = palette.color(QPalette.Window)
        return background_color.lightness() < 128  # Dark if lightness is low

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

    def apply_theme(self, app):
        """Apply the current theme to the application"""
        active_theme = self.get_active_theme()
        logger.debug(f"Applying theme: {self.current_theme} (resolved to {active_theme})")

        if active_theme == self.DARK:
            self.apply_dark_theme(app)
        else:
            self.apply_light_theme(app)

    def apply_light_theme(self, app):
        """Apply light theme to the application"""
        # Using Fusion style for consistency
        app.setStyle("Fusion")

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

    def apply_dark_theme(self, app):
        """Apply dark theme to the application"""
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