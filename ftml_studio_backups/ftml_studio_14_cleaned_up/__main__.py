# src/ftml_studio/__main__.py
"""
FTML Studio - A modern editor for FTML markup language

This is the main entry point when running the package directly:
python -m ftml_studio
"""

import sys
from src.ftml_studio.cli import main


# import sys
# from PySide6.QtWidgets import QApplication, QMessageBox
# 
# 
# def main():
#     # Show a message box to confirm code execution
#     app = QApplication(sys.argv)
#     # QMessageBox.information(None, "Debug", "FTML Studio starting - Debug Mode")
# 
#     # Continue with normal initialization
#     from src.ftml_studio.ui.main_window import MainWindow
# 
#     window = MainWindow()
#     window.show()
# 
#     # Override close event to show another message
#     # original_close = window.closeEvent
# 
#     # def debug_close(event):
#     #     QMessageBox.information(None, "Debug", "FTML Studio closing")
#     #     original_close(event)
# 
#     # window.closeEvent = debug_close
# 
#     return app.exec()


if __name__ == "__main__":
    sys.exit(main())
