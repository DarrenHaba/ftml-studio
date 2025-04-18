# src/ftml_studio/syntax/xml_highlighter.py
from PySide6.QtCore import QRegularExpression, Qt
from .base_highlighter import BaseHighlighter

class XMLHighlighter(BaseHighlighter):
    """Syntax highlighter for XML documents"""

    def __init__(self, document, theme_manager=None):
        super().__init__(document, theme_manager)
        self.create_highlighting_rules()

    def create_highlighting_rules(self):
        """Create XML specific highlighting rules"""
        # Clear existing rules
        self.highlighting_rules = []

        # XML comments
        self.add_rule(r'<!--.*?-->', "comment")

        # XML processing instructions
        self.add_rule(r'<\?.*?\?>', "key")

        # XML CDATA sections
        self.add_rule(r'<!\[CDATA\[.*?\]\]>', "string")

        # XML DOCTYPE declarations
        self.add_rule(r'<!DOCTYPE.*?>', "key")

        # XML Element tag names (opening)
        self.add_rule(r'<[a-zA-Z0-9_:-]+', "key")  # Opening tag

        # XML Element tag names (closing)
        self.add_rule(r'</[a-zA-Z0-9_:-]+>', "key")  # Closing tag

        # Closing bracket of opening tags
        self.add_rule(r'[/]?>', "key")

        # XML Attribute names
        self.add_rule(r'\s+[a-zA-Z0-9_:-]+(?=\s*=\s*["\'])', "symbol")

        # XML Attribute values
        self.add_rule(r'"[^"]*"', "string")  # Double-quoted attribute values
        self.add_rule(r"'[^']*'", "string")  # Single-quoted attribute values

        # XML Entity references
        self.add_rule(r'&[a-zA-Z0-9#]+;', "number")

    def initialize_formats(self):
        """Initialize text formats with custom colors"""
        super().initialize_formats()

        # XML-specific formatting adjustments
        self._create_format("key", foreground="#0000aa", bold=True)  # Tags
        self._create_format("symbol", foreground="#660066")  # Attributes
        self._create_format("string", foreground="#006600")  # Values
        self._create_format("number", foreground="#cc6600")  # Entities
        self._create_format("text", foreground="#000000")  # Text content (will be theme dependent)

    def highlightBlock(self, text):
        """Apply highlighting rules to the given block of text"""
        # First, reset the state
        self.setCurrentBlockState(0)

        # Apply standard highlighting rules
        super().highlightBlock(text)

        # Process text content between tags
        self._highlight_text_content(text)

    def _highlight_text_content(self, text):
        """Highlight text content between tags"""
        # Define regex to find text content between tags
        # This looks for content between > and < characters
        tag_content_regex = QRegularExpression(r'>(.*?)<')

        # Find all matches
        match_iterator = tag_content_regex.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()

            # Get the captured text content (group 1)
            content = match.captured(1)

            # Skip empty or whitespace-only content
            if not content.strip():
                continue

            # Apply the text format to the content
            # +1 to skip the > character
            start_pos = match.capturedStart(1)
            length = match.capturedLength(1)

            # Only apply if there's content
            if length > 0:
                # Use a theme-aware color
                if self.theme_manager and self.theme_manager.current_theme == "dark":
                    text_format = self._create_format("text", foreground="#cccccc")
                else:
                    text_format = self._create_format("text", foreground="#000000")

                self.setFormat(start_pos, length, text_format)