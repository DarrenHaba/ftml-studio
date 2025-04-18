# # src/ftml_studio/ui/widgets/ftml_editor.py
# from PySide6.QtWidgets import QTextEdit, QWidget
# from PySide6.QtGui import QFont, QColor, QPainter, QTextFormat
# from PySide6.QtCore import Qt, QRect, QSize
# 
# 
# class LineNumberArea(QWidget):
#     def __init__(self, editor):
#         super().__init__(editor)
#         self.editor = editor
# 
#     def sizeHint(self):
#         return QSize(self.editor.line_number_area_width(), 0)
# 
#     def paintEvent(self, event):
#         self.editor.line_number_area_paint_event(event)
# 
# class FTMLEditor(QTextEdit):
#     """Rich text editor for FTML content with syntax highlighting"""
# 
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self._configure()
# 
#     def _configure(self):
#         """Configure the editor appearance and behavior"""
#         # Set monospace font
#         font = QFont("Courier New", 10)
#         font.setFixedPitch(True)
#         self.setFont(font)
# 
#         # Set tab width (4 spaces)
#         self.setTabStopDistance(40)
# 
#         # Set line wrap mode
#         self.setLineWrapMode(QTextEdit.NoWrap)
# 
#         # Set background color (light theme)
#         self.setStyleSheet("""
#             QTextEdit {
#                 background-color: #f8f8f8;
#                 color: #333;
#                 border: 1px solid #ddd;
#                 font-family: "Courier New", monospace;
#             }
#         """)
# 
#         # Enable auto-indentation
#         self.setAutoFormatting(QTextEdit.AutoNone)
