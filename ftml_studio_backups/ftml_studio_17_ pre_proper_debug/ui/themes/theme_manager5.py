# src/ftml_studio/ui/themes/theme_manager.py
import logging
from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtGui import QPalette, QColor

logger = logging.getLogger("theme_manager")

class ThemeManager:
    """Simple theme manager that changes Qt styles and accent color"""

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
        self.current_style = "Fusion"  # Default style
        self.accent_color = "#4a86e8"  # Default accent color (blue)

    def get_available_styles(self):
        """Get all available Qt styles"""
        return QStyleFactory.keys()

    def set_style(self, style_name):
        """Set the current style"""
        if style_name in self.get_available_styles():
            self.current_style = style_name
            logger.debug(f"Style set to {style_name}")
            return True
        else:
            logger.warning(f"Style not found: {style_name}")
            return False

    def set_accent_color(self, color):
        """Set the accent color
        
        Args:
            color: A color string (hex) or QColor object
        """
        if isinstance(color, QColor):
            self.accent_color = color.name()
        else:
            self.accent_color = color
        logger.debug(f"Accent color set to {self.accent_color}")

    def apply_style(self, app):
        """Apply the current style to the application"""
        if self.current_style in self.get_available_styles():
            app.setStyle(self.current_style)
    
            # Apply the accent color regardless of style
            self._apply_accent_color(app)
    
            logger.debug(f"Applied style: {self.current_style} with accent color: {self.accent_color}")
            return True
        else:
            logger.warning(f"Could not apply style: {self.current_style}")
            return False

    def _apply_accent_color(self, app):
        """Apply the accent color to the application palette"""
        # Get the current palette
        palette = app.palette()
    
        # Create QColor from our accent color
        accent = QColor(self.accent_color)
    
        # Set standard palette colors for all styles
        palette.setColor(QPalette.Highlight, accent)
        palette.setColor(QPalette.Link, accent)
    
        # For Windows style, we need to use a specific approach
        if "Windows" in self.current_style:
            # In Qt 6.6+, there's a dedicated Accent role
            try:
                # QPalette.Accent was added in Qt 6.6
                palette.setColor(QPalette.Accent, accent)
            except AttributeError:
                # For older Qt versions, we use a different strategy
                app.setStyleSheet(f"""
                    QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
                        border: none;
                        background-color: {accent.name()};
                    }}
                """)
    
        # Apply the modified palette
        app.setPalette(palette)