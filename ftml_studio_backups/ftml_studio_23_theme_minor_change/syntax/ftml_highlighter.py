# # src/ftml_studio/syntax/ftml_highlighter.py
# from PySide6.QtCore import QRegularExpression, QTimer
# from PySide6.QtGui import QTextCursor
# from .base_highlighter import BaseHighlighter
# 
# class FTMLHighlighter(BaseHighlighter):
#     """Syntax highlighter for FTML documents"""
# 
#     def __init__(self, document, theme_manager=None):
#         super().__init__(document, theme_manager)
#         self.create_highlighting_rules()
# 
#         # For potential future AST-based highlighting
#         self.parse_timer = QTimer()
#         self.parse_timer.setSingleShot(True)
#         self.parse_timer.timeout.connect(self.parse_document)
# 
#     def create_highlighting_rules(self):
#         """Create FTML specific highlighting rules"""
#         # Clear existing rules
#         self.highlighting_rules = []
# 
#         # Process in this specific order for proper string handling:
# 
#         # 1. Comments (always take precedence)
#         self.add_rule(r'//!.*$', "comment")     # Inner doc comments
#         self.add_rule(r'///.*$', "comment")     # Outer doc comments
#         self.add_rule(r'//.*$', "comment")      # Regular comments
# 
#         # 2. Strings (process these early to prevent number highlighting inside them)
#         self.add_rule(r'"(?:\\.|[^"\\])*"', "string")
#         self.add_rule(r"'(?:\\.|[^'\\])*'", "string")
# 
#         # 3. Keys
#         self.add_rule(r"^[ \t]*[A-Za-z_][A-Za-z0-9_]*(?=[ \t]*=)", "key")
#         self.add_rule(r"(?<=\{)[ \t\r\n]*[A-Za-z_][A-Za-z0-9_]*(?=[ \t]*=)", "key")
#         self.add_rule(r"(?<=,)[ \t\r\n]*[A-Za-z_][A-Za-z0-9_]*(?=[ \t]*=)", "key")
# 
#         # 4. Symbols
#         self.add_rule(r'[=\{\}\[\],]', "symbol")
# 
#         # 5. Values
#         # Booleans - make sure they're standalone values not part of identifiers
#         self.add_rule(r'(?<![A-Za-z0-9_])(true|false)(?![A-Za-z0-9_])', "boolean")
# 
#         # Null
#         self.add_rule(r'(?<![A-Za-z0-9_])null(?![A-Za-z0-9_])', "null")
# 
#         # Numbers
#         self.add_rule(r'(?<![A-Za-z0-9_"])[-+]?\b\d+\.\d+\b', "number")  # Float
#         self.add_rule(r'(?<![A-Za-z0-9_"])[-+]?\b\d+\b', "number")       # Integer
# 
#     def initialize_formats(self):
#         """Initialize text formats with custom colors"""
#         super().initialize_formats()
# 
#         # Change boolean color to be more distinct from keys
#         self._create_format("boolean", foreground="#9900cc", bold=True)  # Purple shade
# 
#     def parse_document(self):
#         """
#         Parse the entire document for more accurate highlighting.
#         This is a placeholder for future AST-based highlighting.
#         """
#         # This method would use the actual FTML parser
#         # For now, we'll rely on our regex-based approach
#         pass
# 
#     def highlightBlock(self, text):
#         """Apply highlighting rules to the given block of text"""
#         # Set current block state to continue multi-line highlighting
#         previous_block_state = self.previousBlockState()
#         current_state = previous_block_state if previous_block_state != -1 else 0
# 
#         # Track which parts of the text have been highlighted
#         # This helps prevent values from being highlighted inside strings
#         highlighted_positions = [False] * len(text)
# 
#         # Apply highlighting rules in order
#         for pattern, format in self.highlighting_rules:
#             match_iterator = pattern.globalMatch(text)
#             while match_iterator.hasNext():
#                 match = match_iterator.next()
#                 start = match.capturedStart()
#                 length = match.capturedLength()
#                 end = start + length
# 
#                 # Special handling for string and comment formats
#                 # Always apply these, regardless of what's already highlighted
#                 if format == self.formats["string"] or format == self.formats["comment"]:
#                     self.setFormat(start, length, format)
#                     # Mark these positions as highlighted
#                     for i in range(start, min(end, len(highlighted_positions))):
#                         highlighted_positions[i] = True
#                 # For other formats, only apply if the position isn't already highlighted
#                 else:
#                     # Check if any part of this match is already highlighted
#                     already_highlighted = False
#                     for i in range(start, min(end, len(highlighted_positions))):
#                         if highlighted_positions[i]:
#                             already_highlighted = True
#                             break
# 
#                     # Only apply format if not already highlighted
#                     if not already_highlighted:
#                         self.setFormat(start, length, format)
#                         # Mark these positions as highlighted
#                         for i in range(start, min(end, len(highlighted_positions))):
#                             highlighted_positions[i] = True
# 
#         # Update state for multi-line tracking
#         open_braces = text.count("{")
#         close_braces = text.count("}")
#         open_brackets = text.count("[")
#         close_brackets = text.count("]")
# 
#         # Approximate state tracking
#         if previous_block_state == 1:  # Inside object
#             if close_braces > open_braces:
#                 current_state = 0  # Exit object
#             else:
#                 current_state = 1  # Still in object
#         elif previous_block_state == 2:  # Inside list
#             if close_brackets > open_brackets:
#                 current_state = 0  # Exit list
#             else:
#                 current_state = 2  # Still in list
#         else:  # Default state
#             if open_braces > close_braces:
#                 current_state = 1  # Enter object
#             elif open_brackets > close_brackets:
#                 current_state = 2  # Enter list
# 
#         self.setCurrentBlockState(current_state)
#         