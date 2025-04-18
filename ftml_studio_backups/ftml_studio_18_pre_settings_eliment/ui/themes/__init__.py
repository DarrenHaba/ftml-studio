# src/ftml_studio/ui/themes/__init__.py
from .theme_manager import ThemeManager

# Create a singleton instance
theme_manager = ThemeManager()

# Export the singleton
__all__ = ['theme_manager']