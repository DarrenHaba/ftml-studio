# src/ftml_studio/syntax/json_highlighter.py
from PySide6.QtCore import QRegularExpression
from .base_highlighter import BaseHighlighter

class JSONHighlighter(BaseHighlighter):
    """Syntax highlighter for JSON documents"""

    def __init__(self, document, theme_manager=None):
        super().__init__(document, theme_manager)
        self.create_highlighting_rules()

    def create_highlighting_rules(self):
        """Create JSON specific highlighting rules"""
        # Clear existing rules
        self.highlighting_rules = []

        # Keys (property names in quotes) - BLUE
        self.add_rule(r'"(?:\\.|[^"\\])*"(?=\s*:)', "key")  # This rule makes keys blue

        # Strings (quoted values) - GREEN
        # Important: We need to check that these strings are NOT followed by a colon
        # (to avoid matching keys, which we want to be blue)
        self.add_rule(r'^\s*"(?:\\.|[^"\\])*"(?!\s*:)', "string")  # String at start of line 
        self.add_rule(r'(?<=:|\[|,)\s*"(?:\\.|[^"\\])*"', "string")  # String after delimiter

        # Numbers
        self.add_rule(r'^\s*-?\d+\.\d+([eE][+-]?\d+)?(?=\s*[,\}\]]|$)', "number")  # Float at start of line
        self.add_rule(r'(?<=:|\[|,)\s*-?\d+\.\d+([eE][+-]?\d+)?(?=\s*[,\}\]]|$)', "number")  # Float after delimiter

        self.add_rule(r'^\s*-?\d+(?=\s*[,\}\]]|$)', "number")  # Integer at start of line
        self.add_rule(r'(?<=:|\[|,)\s*-?\d+(?=\s*[,\}\]]|$)', "number")  # Integer after delimiter

        # Booleans
        self.add_rule(r'^\s*(true|false)(?=\s*[,\}\]]|$)', "boolean")  # Boolean at start of line
        self.add_rule(r'(?<=:|\[|,)\s*(true|false)(?=\s*[,\}\]]|$)', "boolean")  # Boolean after delimiter

        # Null
        self.add_rule(r'^\s*null(?=\s*[,\}\]]|$)', "null")  # Null at start of line
        self.add_rule(r'(?<=:|\[|,)\s*null(?=\s*[,\}\]]|$)', "null")  # Null after delimiter

        # Symbols
        self.add_rule(r'[:{}\[\],]', "symbol")

    def highlightBlock(self, text):
        """Apply highlighting rules to the given block of text"""
        # Call the base implementation
        super().highlightBlock(text)