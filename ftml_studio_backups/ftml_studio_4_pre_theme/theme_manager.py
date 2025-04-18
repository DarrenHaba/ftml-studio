import json
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal

class ThemeManager(QObject):
    theme_changed = Signal(str)  # Emits theme name when changed

    def __init__(self):
        super().__init__()
        self.config_path = Path.home() / ".ftml_studio" / "config.json"
        self.themes = {
            "dark": str(Path(__file__).parent / "themes/dark.qss"),
            "light": str(Path(__file__).parent / "themes/light.qss"),
            "auto": None
        }
        self.current_theme = "auto"
        self.load_settings()

    def load_settings(self):
        """Load persisted theme preference"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.set_theme(config.get("theme", "auto"), silent=True)
        except (FileNotFoundError, json.JSONDecodeError):
            self.set_theme("auto", silent=True)

    def save_settings(self):
        """Save current theme to config file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({"theme": self.current_theme}, f)

    def set_theme(self, theme_name, silent=False):
        """Apply theme to entire application"""
        if theme_name == "auto":
            self._apply_system_theme()
        else:
            self._load_qss_theme(theme_name)

        self.current_theme = theme_name
        if not silent:
            self.save_settings()
            self.theme_changed.emit(theme_name)

    def _apply_system_theme(self):
        """Detect and apply system theme"""
        # Implement system theme detection logic here
        # For cross-platform compatibility, you might need platform-specific code
        self._load_qss_theme("dark")  # Fallback to dark theme

    def _load_qss_theme(self, theme_name):
        """Load and apply QSS file"""
        if theme_path := self.themes.get(theme_name):
            with open(theme_path, 'r') as f:
                QApplication.instance().setStyleSheet(f.read())
        else:
            QApplication.instance().setStyleSheet("")

# Singleton instance
theme_manager = ThemeManager()