# src/ftml_studio/ui/test_window.py
from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QVBoxLayout, QWidget

class WindowFoo(QMainWindow):
    """A simple test window to verify PySide6 is working"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FTML Test Window")
        self.resize(400, 300)

        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Add a simple label
        label = QLabel("FTML Test Window is working!")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)

# Allow standalone execution
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)  # Create QApplication FIRST
    window = WindowFoo()
    window.show()
    sys.exit(app.exec())  # Start the event loop