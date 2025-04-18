# src/ftml_studio/ui/base_window.py
from PySide6.QtWidgets import QMainWindow


class BaseWindow(QMainWindow):
    """Base window with standalone execution capability"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI components"""
        raise NotImplementedError

    def run(self):
        """Run this window as a standalone application"""
        import sys
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance() or QApplication(sys.argv)
        self.show()
        return app.exec()
