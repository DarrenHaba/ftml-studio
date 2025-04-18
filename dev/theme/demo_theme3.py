import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QWidget
from PySide6.QtGui import QPalette, QColor

class MenuBarTest2(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menu Bar Theme Test")

        # Create menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("New")
        file_menu.addAction("Open")
        file_menu.addAction("Save")
        file_menu.addSeparator()
        file_menu.addAction("Exit")

        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction("Cut")
        edit_menu.addAction("Copy")
        edit_menu.addAction("Paste")

        # Add central widget
        self.setCentralWidget(QWidget())
        self.resize(400, 300)

        # Add theme toggle function
        self.is_dark = False
        self.toggle_theme()

    def toggle_theme(self):
        self.is_dark = not self.is_dark

        palette = QPalette()
        if self.is_dark:
            # Dark theme
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
            palette.setColor(QPalette.Base, QColor(42, 42, 42))
            palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
            palette.setColor(QPalette.Text, QColor(255, 255, 255))
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

            # Style menu bar explicitly
            # self.menuBar().setStyleSheet("""
            #     QMenuBar {
            #         background-color: #333333;
            #         color: white;
            #     }
            #     QMenu {
            #         background-color: #333333;
            #         color: white;
            #     }
            # """)
        else:
            # Light theme
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
            palette.setColor(QPalette.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.AlternateBase, QColor(233, 233, 233))
            palette.setColor(QPalette.Text, QColor(0, 0, 0))
            palette.setColor(QPalette.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
            palette.setColor(QPalette.Link, QColor(0, 0, 255))
            palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
            palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

            # Style menu bar explicitly
            self.menuBar().setStyleSheet("""
                QMenuBar {
                    background-color: #f0f0f0;
                    color: black;
                }
                QMenu {
                    background-color: #f0f0f0;
                    color: black;
                }
            """)

        # QApplication.instance().setPalette(palette)
        # self.statusBar().showMessage(f"{'Dark' if self.is_dark else 'Light'} theme applied")

    def mousePressEvent(self, event):
        # Toggle theme on mouse click for easy testing
        self.toggle_theme()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("windows11")

    window = MenuBarTest2()
    window.show()
    sys.exit(app.exec())