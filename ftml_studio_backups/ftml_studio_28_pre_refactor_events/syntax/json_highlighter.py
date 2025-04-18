# src/ftml_studio/syntax/json_highlighter.py
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

        # Important: We need to check that these strings are NOT followed by a colon
        # String at start of line
        self.add_rule(r'^\s*"(?:\\.|[^"\\])*"(?!\s*:)', "string")
        # String after delimiter
        self.add_rule(r'(?<=:|\[|,)\s*"(?:\\.|[^"\\])*"', "string")

        # Numbers
        # Float at start of line
        self.add_rule(r'^\s*-?\d+\.\d+([eE][+-]?\d+)?(?=\s*[,\}\]]|$)', "number")
        # Float after delimiter
        self.add_rule(r'(?<=:|\[|,)\s*-?\d+\.\d+([eE][+-]?\d+)?(?=\s*[,\}\]]|$)', "number")

        # Integer at start of line
        self.add_rule(r'^\s*-?\d+(?=\s*[,\}\]]|$)', "number")
        # Integer after delimiter
        self.add_rule(r'(?<=:|\[|,)\s*-?\d+(?=\s*[,\}\]]|$)', "number")

        # Booleans
        # Boolean at start of line
        self.add_rule(r'^\s*(true|false)(?=\s*[,\}\]]|$)', "boolean")
        # Boolean after delimiter
        self.add_rule(r'(?<=:|\[|,)\s*(true|false)(?=\s*[,\}\]]|$)', "boolean")

        # Null
        # Null at start of line
        self.add_rule(r'^\s*null(?=\s*[,\}\]]|$)', "null")
        # Null after delimiter
        self.add_rule(r'(?<=:|\[|,)\s*null(?=\s*[,\}\]]|$)', "null")

        # Symbols
        self.add_rule(r'[:{}\[\],]', "symbol")

    def highlightBlock(self, text):
        """Apply highlighting rules to the given block of text"""
        # Call the base implementation
        super().highlightBlock(text)
