# src/ftml_studio/ui/themes/theme_manager.py
import logging
import sys
from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt, QSettings

logger = logging.getLogger("theme_manager")

class ThemeManager:
    """Theme manager with consistent palette and stylesheet application"""

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

        # Initialize color schemes
        self.initialize_color_schemes()

    def _load_saved_theme(self):
        """Load the saved theme from settings"""
        saved_theme = self.settings.value("theme", self.AUTO)
        if saved_theme in self.THEMES:
            self.current_theme = saved_theme

    def save_theme(self):
        """Save the current theme to settings"""
        self.settings.setValue("theme", self.current_theme)

    def initialize_color_schemes(self):
        """Initialize color schemes for both themes"""
        # Light theme colors
        self.light_colors = {
            # UI Colors
            "window": "#f5f5f5",
            "windowText": "#333333",
            "base": "#ffffff",
            "alternateBase": "#f0f0f0",
            "text": "#333333",
            "button": "#e0e0e0",
            "buttonText": "#333333",
            "highlight": "#4a86e8",
            "highlightedText": "#ffffff",

            # Custom UI Colors
            "accent": "#388e3c",        # Dark green
            "accentHover": "#2e7d32",   # Darker green for hover states
            "accentText": "#ffffff",    # White text on accent
            "buttonHover": "#d0d0d0",   # Slightly darker button for hover
            "borderColor": "#d0d0d0",   # Light border
            "hoverBg": "#e8e8e8",       # Light hover background

            # Syntax Colors
            "keyword": "#0033b3",       # Keywords and keys
            "function": "#7a3e9d",      # Functions
            "string": "#067d17",        # String literals
            "number": "#ff8c00",        # Numeric literals (orange)
            "boolean": "#9900cc",       # Boolean literals (purple)
            "null": "#9900cc",          # Null literal (purple)
            "comment": "#737373",       # Comments
            "docComment": "#7ea7b8",    # Documentation comments
            "symbol": "#555555",        # Punctuation and symbols
            "operator": "#555555",      # Operators
            "error": "#ff0000",         # Errors
            "editorBg": "#ffffff",      # Editor background
            "lineNumber": "#999999",    # Line numbers
            "selection": "#add8e6"      # Selected text background
        }

        # Dark theme colors
        self.dark_colors = {
            # UI Colors
            "window": "#2d2d2d",
            "windowText": "#f5f5f5",
            "base": "#1e1e1e",
            "alternateBase": "#353535",
            "text": "#f5f5f5",
            "button": "#454545",
            "buttonText": "#f5f5f5",
            "highlight": "#4a86e8",
            "highlightedText": "#ffffff",

            # Custom UI Colors
            "accent": "#43a047",        # Green (slightly brighter for dark theme)
            "accentHover": "#388e3c",   # Darker green for hover states
            "accentText": "#ffffff",    # White text on accent
            "buttonHover": "#555555",   # Slightly lighter button for hover
            "borderColor": "#555555",   # Dark border
            "hoverBg": "#404040",       # Dark hover background

            # Syntax Colors
            "keyword": "#569cd6",       # Keywords and keys (blue)
            "function": "#dcdcaa",      # Functions
            "string": "#6aaa64",        # String literals (green)
            "number": "#ff8c00",        # Numeric literals (orange)  
            "boolean": "#bb86fc",       # Boolean literals (purple)
            "null": "#bb86fc",          # Null literal (purple)
            "comment": "#7c7c7c",       # Comments
            "docComment": "#bcbcbc",    # Documentation comments
            "symbol": "#d4d4d4",        # Punctuation and symbols
            "operator": "#a9a9a9",      # Operators (light gray)
            "error": "#ff5555",         # Errors
            "editorBg": "#1e1e1e",      # Editor background
            "lineNumber": "#858585",    # Line numbers
            "selection": "#264f78"      # Selected text background
        }

    def get_color(self, key):
        """Get a color for the current theme"""
        active_theme = self.get_active_theme()
        colors = self.dark_colors if active_theme == self.DARK else self.light_colors

        if key in colors:
            return colors[key]
        else:
            logger.warning(f"Color '{key}' not found")
            return "#000000"  # Default black

    def get_syntax_color(self, key):
        """Get a syntax highlighting color for the current theme"""
        # Map legacy syntax keys to our color scheme
        mapping = {
            "keyword": "keyword",
            "function": "function",
            "string": "string",
            "number": "number",
            "boolean": "boolean",
            "null": "null",
            "comment": "comment",
            "docComment": "docComment",
            "symbol": "symbol",
            "operator": "operator",
            "error": "error",
            "background": "editorBg",
            "lineNumber": "lineNumber",
            "selection": "selection",
            "accent": "accent"
        }

        mapped_key = mapping.get(key, key)
        return self.get_color(mapped_key)

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

        # 1. Set application style to Fusion for consistency
        app.setStyle("Fusion")

        # 2. Apply palette
        self._apply_palette(app, active_theme)

        # 3. Apply consistent stylesheet
        self._apply_stylesheet(app, active_theme)

        # 4. Set application class name for CSS selectors
        app.setProperty("themeClass", active_theme)

    def _apply_palette(self, app, active_theme):
        """Apply color palette based on theme"""
        # Get colors for current theme
        colors = self.dark_colors if active_theme == self.DARK else self.light_colors

        # Create palette
        palette = QPalette()

        # Set standard palette colors
        palette.setColor(QPalette.Window, QColor(colors["window"]))
        palette.setColor(QPalette.WindowText, QColor(colors["windowText"]))
        palette.setColor(QPalette.Base, QColor(colors["base"]))
        palette.setColor(QPalette.AlternateBase, QColor(colors["alternateBase"]))
        palette.setColor(QPalette.Text, QColor(colors["text"]))
        palette.setColor(QPalette.Button, QColor(colors["button"]))
        palette.setColor(QPalette.ButtonText, QColor(colors["buttonText"]))
        palette.setColor(QPalette.BrightText, QColor("#ffffff"))
        palette.setColor(QPalette.Highlight, QColor(colors["highlight"]))
        palette.setColor(QPalette.HighlightedText, QColor(colors["highlightedText"]))

        # Border colors
        border_color = QColor(colors["borderColor"])
        palette.setColor(QPalette.Light, border_color.lighter(120))
        palette.setColor(QPalette.Midlight, border_color)
        palette.setColor(QPalette.Mid, border_color.darker(110))
        palette.setColor(QPalette.Dark, border_color.darker(130))

        # Shadow
        shadow_color = QColor("#999999") if active_theme == self.LIGHT else QColor("#000000")
        palette.setColor(QPalette.Shadow, shadow_color)

        # Tooltip
        tooltip_bg = QColor("#f0f0f0") if active_theme == self.LIGHT else QColor("#383838")
        tooltip_text = QColor("#333333") if active_theme == self.LIGHT else QColor("#f5f5f5")
        palette.setColor(QPalette.ToolTipBase, tooltip_bg)
        palette.setColor(QPalette.ToolTipText, tooltip_text)

        # Placeholder text
        placeholder = QColor("#808080") if active_theme == self.LIGHT else QColor("#aaaaaa")
        palette.setColor(QPalette.PlaceholderText, placeholder)

        # Apply palette
        app.setPalette(palette)

    def _apply_stylesheet(self, app, active_theme):
        """Apply stylesheet with consistent styling"""
        # Get colors for current theme
        colors = self.dark_colors if active_theme == self.DARK else self.light_colors

        # Create stylesheet
        stylesheet = f"""
        /* Global button styling */
        QPushButton {{
            border-radius: 4px;
            padding: 6px 12px;
            border: 1px solid {colors["borderColor"]};
            background-color: {colors["button"]};
            color: {colors["buttonText"]};
        }}
        
        QPushButton:hover {{
            background-color: {colors["buttonHover"]};
        }}
        
        /* Tab button styling (consistent sizing and appearance) */
        #headerTab {{
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
            min-width: 120px;
            background-color: {colors["button"]};
            color: {colors["buttonText"]};
            border: 1px solid {colors["borderColor"]};
        }}
        
        #headerTab:checked {{
            background-color: {colors["accent"]};
            color: {colors["accentText"]};
            border: 1px solid {colors["accentHover"]};
        }}
        
        #headerTab:hover:!checked {{
            background-color: {colors["buttonHover"]};
        }}
        
        /* Convert button - slightly less prominent */
        #convertButton {{
            background-color: {colors["accent"]};
            color: {colors["accentText"]};
            border: none;
            padding: 6px 16px;
            font-weight: bold;
        }}
        
        #convertButton:hover {{
            background-color: {colors["accentHover"]};
        }}
        
        /* Settings button */
        #settingsButton {{
            font-size: 18px;
            border-radius: 15px;
            border: none;
            background-color: transparent;
            color: {colors["buttonText"]};
            padding: 4px;
        }}
        
        #settingsButton:hover {{
            background-color: {colors["hoverBg"]};
        }}
        
        /* Close button */
        #closeButton {{
            font-size: 12px;
            border-radius: 12px;
            border: none;
            font-weight: bold;
            background-color: transparent;
            color: {colors["buttonText"]};
            padding: 4px;
        }}
        
        #closeButton:hover {{
            background-color: {colors["hoverBg"]};
        }}
        
        /* Header */
        #header {{
            background-color: {colors["window"]};
            border-bottom: 1px solid {colors["borderColor"]};
        }}
        
        /* Sidebar */
        #sidebar {{
            background-color: {colors["window"]};
            border-right: 1px solid {colors["borderColor"]};
        }}
        
        /* Settings panel */
        #settingsPanel {{
            background-color: {colors["window"]};
            border-left: 1px solid {colors["borderColor"]};
        }}
        
        #settingsHeader {{
            color: {colors["windowText"]};
            font-size: 18px;
            font-weight: bold;
        }}
        
        #settingsLabel {{
            font-weight: bold;
            color: {colors["windowText"]};
        }}
        
        /* Checkable buttons (consistent with tabs) */
        QPushButton[checkable="true"] {{
            border-radius: 4px;
            padding: 6px 12px;
            min-width: 100px;
            background-color: {colors["button"]};
            color: {colors["buttonText"]};
            border: 1px solid {colors["borderColor"]};
        }}
        
        QPushButton[checkable="true"]:checked {{
            background-color: {colors["accent"]};
            color: {colors["accentText"]};
            border: 1px solid {colors["accentHover"]};
        }}
        
        QPushButton[checkable="true"]:hover:!checked {{
            background-color: {colors["buttonHover"]};
        }}
        
        /* Splitter handle */
        QSplitter::handle {{
            background-color: {colors["borderColor"]};
            width: 1px;
        }}
        
        /* Dropdown styling */
        QComboBox {{
            border: 1px solid {colors["borderColor"]};
            border-radius: 4px;
            padding: 5px;
            background-color: {colors["button"]};
            color: {colors["buttonText"]};
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: right;
            width: 20px;
            border-left: 1px solid {colors["borderColor"]};
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors["base"]};
            color: {colors["text"]};
            selection-background-color: {colors["accent"]};
            selection-color: {colors["accentText"]};
        }}
        """

        # Apply stylesheet
        app.setStyleSheet(stylesheet)