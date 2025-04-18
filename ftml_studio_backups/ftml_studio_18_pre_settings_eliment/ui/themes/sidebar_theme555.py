# # src/ftml_studio/ui/themes/sidebar_theme.py
# from PySide6.QtGui import QColor
# 
# class SidebarTheme:
#     """Manages sidebar-specific styling"""
# 
#     @staticmethod
#     def get_sidebar_stylesheet(is_dark_theme, accent_color="#4CAF50"):
#         """Get the main sidebar container stylesheet based on theme"""
#         if is_dark_theme:
#             return f"""
#                 #sidebar {{
#                     background-color: #333333;
#                     border-right: 1px solid #555555;
#                 }}
#                 
#                 QFrame#separator {{
#                     background-color: #555555;
#                 }}
#             """
#         else:
#             return f"""
#                 #sidebar {{
#                     background-color: #e0e0e0;
#                     border-right: 1px solid #cccccc;
#                 }}
#                 
#                 QFrame#separator {{
#                     background-color: #cccccc;
#                 }}
#             """
# 
#     @staticmethod
#     def get_hamburger_button_stylesheet(is_dark_theme, accent_color="#4CAF50"):
#         """Get hamburger menu button stylesheet"""
#         if is_dark_theme:
#             return f"""
#                 QPushButton#hamburgerButton {{
#                     text-align: left;
#                     padding-left: 10px;
#                     border: none;
#                     border-radius: 0;
#                     margin: 0;
#                     color: white;
#                     background-color: transparent;
#                 }}
#                 
#                 QPushButton#hamburgerButton:hover {{
#                     background-color: #444444;
#                 }}
#             """
#         else:
#             return f"""
#                 QPushButton#hamburgerButton {{
#                     text-align: left;
#                     padding-left: 10px;
#                     border: none;
#                     border-radius: 0;
#                     margin: 0;
#                     color: #333333;
#                     background-color: transparent;
#                 }}
#                 
#                 QPushButton#hamburgerButton:hover {{
#                     background-color: #d0d0d0;
#                 }}
#             """
# 
#     @staticmethod
#     def get_sidebar_button_stylesheet(is_dark_theme, is_expanded, accent_color="#4CAF50"):
#         """Get sidebar button stylesheet based on theme and sidebar state"""
#         # Base styling with text alignment based on expanded state
#         base_style = f"""
#             QPushButton {{
#                 text-align: {'left' if is_expanded else 'center'};
#                 padding-left: {'10px' if is_expanded else '0px'};
#                 border: none;
#                 border-radius: 0;
#                 margin: 0;
#             }}
#             
#             QPushButton:checked {{
#                 background-color: {accent_color};
#                 color: white;
#             }}
#         """
# 
#         # Add theme-specific styling
#         if is_dark_theme:
#             return base_style + """
#                 QPushButton {
#                     color: white;
#                     background-color: transparent;
#                 }
#                 
#                 QPushButton:hover {
#                     background-color: #444444;
#                 }
#             """
#         else:
#             return base_style + """
#                 QPushButton {
#                     color: #333333;
#                     background-color: transparent;
#                 }
#                 
#                 QPushButton:hover {
#                     background-color: #d0d0d0;
#                 }
#             """