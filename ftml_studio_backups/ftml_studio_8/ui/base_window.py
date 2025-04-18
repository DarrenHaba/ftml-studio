# src/ftml_studio/ui/base_window.py
from PySide6.QtWidgets import QMainWindow

class BaseWindow(QMainWindow):
    """Base window with common functionality"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI components"""
        raise NotImplementedError
