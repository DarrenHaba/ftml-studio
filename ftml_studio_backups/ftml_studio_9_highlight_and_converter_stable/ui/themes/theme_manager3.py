# src/ftml_studio/ui/themes/theme_manager.py
import logging
import sys
from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtGui import QPalette, QColor, QFont
from PySide6.QtCore import Qt, QSettings, QOperatingSystemVersion

logger = logging.getLogger("theme_manager")

class ThemeManager:
    """Hybrid theme manager that preserves native controls while applying theme colors"""

    THEMES = ["light", "dark", "auto"]

    def __init__(self):
        self.current_theme = "auto"  # Default theme
        self.settings = QSettings("FTMLStudio", "AppSettings")
        self._load_saved_theme()

        # Initialize color palettes for light and dark themes
        self.initialize_color_palettes()

    def _load_saved_theme(self):
        """Load the saved theme from settings"""
        saved_theme = self.settings.value("theme", "auto")
        if saved_theme in self.THEMES:
            self.current_theme = saved_theme

    def _save_theme(self):
        """Save the current theme to settings"""
        self.settings.setValue("theme", self.current_theme)

    def initialize_color_palettes(self):
        """Initialize comprehensive color palettes for both themes"""
        # UI Element Colors
        self.light_palette = {
            # Core UI colors
            "window": "#f5f5f5",
            "windowText": "#333333",
            "base": "#ffffff",
            "alternateBase": "#f0f0f0",
            "text": "#333333",
            "button": "#e0e0e0",
            "buttonText": "#333333",
            "highlight": "#4a86e8",
            "highlightedText": "#ffffff",
            "link": "#2979ff",

            # Additional UI colors
            "border": "#c0c0c0",
            "panel": "#f0f0f0",
            "panelText": "#333333",
            "success": "#4caf50",
            "warning": "#ff9800",
            "error": "#f44336",
            "info": "#2196f3",

            # Button states
            "buttonHover": "#d0d0d0",
            "buttonPressed": "#c0c0c0",
            "buttonFocus": "#add8e6",

            # Syntax highlighting colors (semantically named)
            "syntax": {
                "keyword": "#0033b3",      # Keywords and keys
                "function": "#7a3e9d",     # Functions
                "string": "#067d17",       # String literals
                "number": "#1750eb",       # Numeric literals
                "boolean": "#0033b3",      # Boolean literals
                "null": "#0033b3",         # Null literal
                "comment": "#8c8c8c",      # Comments
                "docComment": "#3d5a80",   # Documentation comments
                "symbol": "#555555",       # Punctuation and symbols
                "operator": "#000000",     # Operators
                "error": "#ff0000",        # Errors
                "background": "#ffffff",   # Editor background
                "lineNumber": "#999999",   # Line numbers
                "selection": "#add8e6"     # Selected text background
            }
        }

        self.dark_palette = {
            # Core UI colors
            "window": "#2d2d2d",
            "windowText": "#f5f5f5",
            "base": "#1e1e1e",
            "alternateBase": "#353535",
            "text": "#f5f5f5",
            "button": "#454545",
            "buttonText": "#f5f5f5",
            "highlight": "#4a86e8",
            "highlightedText": "#ffffff",
            "link": "#56a3ff",

            # Additional UI colors
            "border": "#555555",
            "panel": "#383838",
            "panelText": "#f5f5f5",
            "success": "#4caf50",
            "warning": "#ff9800",
            "error": "#f44336",
            "info": "#2196f3",

            # Button states
            "buttonHover": "#555555",
            "buttonPressed": "#666666",
            "buttonFocus": "#49769c",

            # Syntax highlighting colors (semantically named)
            "syntax": {
                "keyword": "#569cd6",      # Keywords and keys
                "function": "#dcdcaa",     # Functions
                "string": "#ce9178",       # String literals
                "number": "#b5cea8",       # Numeric literals  
                "boolean": "#569cd6",      # Boolean literals
                "null": "#569cd6",         # Null literal
                "comment": "#6a9955",      # Comments
                "docComment": "#5e9dd6",   # Documentation comments
                "symbol": "#d4d4d4",       # Punctuation and symbols
                "operator": "#d4d4d4",     # Operators
                "error": "#f14c4c",        # Errors
                "background": "#1e1e1e",   # Editor background
                "lineNumber": "#858585",   # Line numbers
                "selection": "#264f78"     # Selected text background
            }
        }

    def _detect_system_theme(self):
        """
        Improved system theme detection across platforms
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
        if self.current_theme == "auto":
            return "dark" if self._detect_system_theme() else "light"
        return self.current_theme

    def get_color(self, key, category=None):
        """
        Get a color from the current theme
        - key: the color name
        - category: optional subcategory (e.g., "syntax")
        """
        active_theme = self.get_active_theme()
        palette = self.dark_palette if active_theme == "dark" else self.light_palette

        if category:
            if category in palette and key in palette[category]:
                return palette[category][key]
            else:
                logger.warning(f"Color '{key}' not found in category '{category}'")
                return "#000000"  # Default black
        else:
            if key in palette:
                return palette[key]
            else:
                logger.warning(f"Color '{key}' not found in palette")
                return "#000000"  # Default black

    def get_syntax_color(self, key):
        """Shorthand to get a syntax highlighting color"""
        return self.get_color(key, "syntax")

    def apply_theme(self, app, theme=None):
        """Apply the specified theme to the application"""
        if theme is not None and theme in self.THEMES:
            self.current_theme = theme
            self._save_theme()

        # Determine active theme
        active_theme = self.get_active_theme()
        logger.debug(f"Applying theme: {self.current_theme} (resolved to {active_theme})")

        # Get the platform's native style
        default_style = self._get_platform_style()
        app.setStyle(default_style)

        # Apply the palette
        self._apply_palette(app, active_theme)

        # Apply minimal stylesheet (only for specific components)
        app.setStyleSheet(self._get_minimal_stylesheet(active_theme))

    def _get_platform_style(self):
        """Get the best style for the current platform"""
        if sys.platform == "darwin":  # macOS
            return "macintosh"
        elif sys.platform == "win32":  # Windows
            return "windowsvista"
        else:  # Linux and others
            # Try to find the best available style
            available_styles = QStyleFactory.keys()
            preferred_styles = ["Fusion", "GTK+", "Oxygen", "Breeze"]

            for style in preferred_styles:
                if style in available_styles:
                    return style

            # Default to Fusion if no preferred style is available
            return "Fusion"

    def _apply_palette(self, app, active_theme):
        """Apply the color palette to the application"""
        # Get the appropriate palette
        colors = self.dark_palette if active_theme == "dark" else self.light_palette
    
        # Create and configure the palette
        palette = QPalette()
    
        # Set standard colors
        palette.setColor(QPalette.Window, QColor(colors["window"]))
        palette.setColor(QPalette.WindowText, QColor(colors["windowText"]))
        palette.setColor(QPalette.Base, QColor(colors["base"]))
        palette.setColor(QPalette.AlternateBase, QColor(colors["alternateBase"]))
        palette.setColor(QPalette.Text, QColor(colors["text"]))
        palette.setColor(QPalette.Button, QColor(colors["button"]))
        palette.setColor(QPalette.ButtonText, QColor(colors["buttonText"]))
        palette.setColor(QPalette.Highlight, QColor(colors["highlight"]))
        palette.setColor(QPalette.HighlightedText, QColor(colors["highlightedText"]))
        palette.setColor(QPalette.Link, QColor(colors["link"]))
        palette.setColor(QPalette.BrightText, QColor("#ffffff"))
    
        # Add these lines for borders and tooltips
        palette.setColor(QPalette.Light, QColor(colors["border"]))
        palette.setColor(QPalette.Midlight, QColor(colors["border"]))
        palette.setColor(QPalette.Dark, QColor(colors["border"]))
        palette.setColor(QPalette.Mid, QColor(colors["border"]))
        palette.setColor(QPalette.Shadow, QColor(colors["windowText"]))
    
        palette.setColor(QPalette.ToolTipBase, QColor(colors["panel"]))
        palette.setColor(QPalette.ToolTipText, QColor(colors["panelText"]))

        # Set these colors for all color groups (Active, Inactive, Disabled)
        for group in [QPalette.Active, QPalette.Inactive, QPalette.Disabled]:
            palette.setColor(group, QPalette.Window, QColor(colors["window"]))
            palette.setColor(group, QPalette.WindowText, QColor(colors["windowText"]))
            palette.setColor(group, QPalette.Base, QColor(colors["base"]))
            palette.setColor(group, QPalette.AlternateBase, QColor(colors["alternateBase"]))
            palette.setColor(group, QPalette.Text, QColor(colors["text"]))
            palette.setColor(group, QPalette.Button, QColor(colors["button"]))
            palette.setColor(group, QPalette.ButtonText, QColor(colors["buttonText"]))
            palette.setColor(group, QPalette.Highlight, QColor(colors["highlight"]))
            palette.setColor(group, QPalette.HighlightedText, QColor(colors["highlightedText"]))
            palette.setColor(group, QPalette.Link, QColor(colors["link"]))

        # Special handling for disabled state
        palette.setColor(QPalette.Disabled, QPalette.WindowText,
                         self._blend_colors(QColor(colors["window"]), QColor(colors["windowText"]), 0.4))
        palette.setColor(QPalette.Disabled, QPalette.Text,
                         self._blend_colors(QColor(colors["base"]), QColor(colors["text"]), 0.4))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText,
                         self._blend_colors(QColor(colors["button"]), QColor(colors["buttonText"]), 0.4))

        # Apply palette
        app.setPalette(palette)

    def _blend_colors(self, bg_color, fg_color, alpha=0.5):
        """Blend two colors with alpha transparency"""
        r = int((1 - alpha) * bg_color.red() + alpha * fg_color.red())
        g = int((1 - alpha) * bg_color.green() + alpha * fg_color.green())
        b = int((1 - alpha) * bg_color.blue() + alpha * fg_color.blue())
        return QColor(r, g, b)

    def _get_minimal_stylesheet(self, active_theme):
        """
        Get a minimal stylesheet that only overrides specific components
        and preserves native styling for most controls
        """
        colors = self.dark_palette if active_theme == "dark" else self.light_palette

        return f"""
        /* Only override specific components - keep native styling for most controls */
        
        /* Special button styling */
        QPushButton#validateButton, QPushButton#convertButton {{
            background-color: {colors["success"]};
            color: white;
            font-weight: bold;
            padding: 4px 8px;
        }}
        
        QPushButton#validateButton:hover, QPushButton#convertButton:hover {{
            background-color: {self._lighten_or_darken(colors["success"], active_theme == "light")};
        }}
        
        /* Status indicators */
        QLabel#statusLabel[valid="true"] {{
            color: {colors["success"]};
        }}
        
        QLabel#statusLabel[valid="false"] {{
            color: {colors["error"]};
        }}
        
        /* Specialized labels */  
        QLabel#conversionInfo {{
            background-color: {colors["panel"]};
            color: {colors["info"]};
            border: 1px solid {colors["border"]};
            padding: 8px;
            font-weight: bold;
            border-radius: 4px;
        }}
        
        /* Editor styling */
        QTextEdit#codeEditor, QTextEdit#schemaEditor {{
            font-family: "Courier New", monospace;
            font-size: 10pt;
        }}
        """

    def _lighten_or_darken(self, color_str, lighten=True):
        """Lighten or darken a color by 10%"""
        color = QColor(color_str)
        h, s, l, a = color.getHslF()

        if lighten:
            l = min(1.0, l * 1.1)  # Lighten by 10%
        else:
            l = max(0.0, l * 0.9)  # Darken by 10%

        color.setHslF(h, s, l, a)
        return color.name()