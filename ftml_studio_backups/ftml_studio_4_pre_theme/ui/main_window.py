# src/ftml_studio/ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel

from src.ftml_studio.ui.base_window import BaseWindow


class MainWindow(BaseWindow):
    """Main window for FTML Studio with tabs for different components"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FTML Studio")
        self.resize(900, 600)
        self.setup_ui()

    def setup_ui(self):
        # Set up central widget with tabs
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        # Create a simple welcome widget
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_label = QLabel("Welcome to FTML Studio")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        welcome_layout.addWidget(welcome_label)

        # Add tabs
        self.tab_widget.addTab(welcome_widget, "Welcome")

    def add_editor_tab(self):
        """Add editor tab only when needed"""
        from .editor_window import EditorWindow
        self.editor_widget = EditorWindow()
        self.tab_widget.addTab(self.editor_widget, "FTML Editor")

    def add_converter_tab(self):
        """Add converter tab only when needed"""
        from .converter_window import ConverterWindow
        self.converter_widget = ConverterWindow()
        self.tab_widget.addTab(self.converter_widget, "Converter")

# Allow standalone execution
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())