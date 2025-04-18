# src/ftml_studio/syntax/toml_highlighter.py
from .base_highlighter import BaseHighlighter

class TOMLHighlighter(BaseHighlighter):
    """Syntax highlighter for TOML documents"""

    def __init__(self, document, theme_manager=None):
        super().__init__(document, theme_manager)
        self.create_highlighting_rules()

    def create_highlighting_rules(self):
        """Create TOML specific highlighting rules"""
        # Clear existing rules
        self.highlighting_rules = []

        # Comments
        self.add_rule(r'#.*$', "comment")

        # Section headers
        self.add_rule(r'^\s*\[\s*[^\]]+\s*\]\s*', "key")  # [section]
        self.add_rule(r'^\s*\[\s*[^\]]+\.[^\]]+\s*\]\s*', "key")  # [section.subsection]

        # Keys
        self.add_rule(r'^[A-Za-z0-9_.-]+(?=\s*=)', "key")  # Keys at start of line
        self.add_rule(r'(?<=\n)[A-Za-z0-9_.-]+(?=\s*=)', "key")  # Keys after newline

        # String values
        self.add_rule(r'"""(?:.|\n)*?"""', "string")  # Multiline strings with """
        self.add_rule(r"'''(?:.|\n)*?'''", "string")  # Multiline strings with '''
        self.add_rule(r'"(?:\\.|[^"\\])*"', "string")  # Double-quoted strings
        self.add_rule(r"'(?:\\.|[^'\\])*'", "string")  # Single-quoted strings

        # Numbers - improved to handle different number formats
        self.add_rule(r'(?<=\s|=|\[|,)[-+]?(?:\d+_)*\d+\.\d+([eE][+-]?\d+)?', "number")  # Float with underscores
        self.add_rule(r'(?<=\s|=|\[|,)[-+]?(?:\d+_)*\d+([eE][+-]?\d+)?', "number")  # Integer with underscores
        self.add_rule(r'(?<=\s|=|\[|,)0x[0-9A-Fa-f]+', "number")  # Hexadecimal
        self.add_rule(r'(?<=\s|=|\[|,)0o[0-7]+', "number")  # Octal
        self.add_rule(r'(?<=\s|=|\[|,)0b[01]+', "number")  # Binary

        # Boolean values
        self.add_rule(r'(?<=\s|=|\[|,)(true|false)', "boolean")

        # Date and time values - special for TOML
        self.add_rule(r'\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}:\d{2})?(\.\d+)?([Zz]|[+-]\d{2}:\d{2})?', "string")

        # Symbols
        self.add_rule(r'[=,\[\]]', "symbol")

    def initialize_formats(self):
        """Initialize text formats with custom colors"""
        super().initialize_formats()

        # TOML-specific formatting adjustments
        self._create_format("key", foreground="#007799", bold=True)