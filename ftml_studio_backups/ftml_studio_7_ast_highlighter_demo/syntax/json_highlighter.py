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

        # Keys (property names in quotes)
        self.add_rule(r'"(?:\\.|[^"\\])*"(?=\s*:)', "key")

        # Strings (quoted values)
        self.add_rule(r'(?<=:)\s*"(?:\\.|[^"\\])*"', "string")
        self.add_rule(r'(?<=,|\[)\s*"(?:\\.|[^"\\])*"', "string")

        # Numbers - improved to avoid capturing parts of strings
        self.add_rule(r'(?<=:|\[|,)\s*-?\d+\.\d+([eE][+-]?\d+)?(?=\s*[,\}\]]|$)', "number") # Float
        self.add_rule(r'(?<=:|\[|,)\s*-?\d+(?=\s*[,\}\]]|$)', "number")  # Integer

        # Booleans
        self.add_rule(r'(?<=:|\[|,)\s*(true|false)(?=\s*[,\}\]]|$)', "boolean")

        # Null
        self.add_rule(r'(?<=:|\[|,)\s*null(?=\s*[,\}\]]|$)', "null")

        # Symbols
        self.add_rule(r'[:{}\[\],]', "symbol")

    def highlightBlock(self, text):
        """Apply highlighting rules to the given block of text"""
        # Call the base implementation
        super().highlightBlock(text)

        # Additional processing could be added here for multi-line constructs
