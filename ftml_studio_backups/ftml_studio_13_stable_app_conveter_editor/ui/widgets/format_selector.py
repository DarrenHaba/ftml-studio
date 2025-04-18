# # src/ftml_studio/ui/widgets/format_selector.py
# from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QWidget
# 
# class FormatSelector(QWidget):
#     """Format selector with label"""
# 
#     def __init__(self, label_text, formats, parent=None):
#         super().__init__(parent)
# 
#         layout = QHBoxLayout(self)
#         layout.setContentsMargins(0, 0, 0, 0)
# 
#         self.label = QLabel(label_text)
#         self.combo = QComboBox()
# 
#         for fmt in formats:
#             self.combo.addItem(fmt)
# 
#         layout.addWidget(self.label)
#         layout.addWidget(self.combo)
# 
#     def get_selected_format(self):
#         """Get the currently selected format"""
#         return self.combo.currentText()
# 
#     def set_selected_format(self, format):
#         """Set the selected format"""
#         index = self.combo.findText(format)
#         if index >= 0:
#             self.combo.setCurrentIndex(index)