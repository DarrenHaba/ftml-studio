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
    
        # XML Element brackets - highlight these as operators
        self.add_rule(r'<(?=/|[a-zA-Z0-9_:-])', "operator")  # Opening bracket
        self.add_rule(r'</(?=[a-zA-Z0-9_:-])', "operator")   # Closing tag start
        self.add_rule(r'(?<=[a-zA-Z0-9_:-])>', "operator")   # Closing bracket
        self.add_rule(r'(?<=[a-zA-Z0-9_:-])/>', "operator")  # Self-closing tag end
    
        # XML Element tag names (just the name part)
        self.add_rule(r'(?<=<)[a-zA-Z0-9_:-]+', "key")       # Opening tag name
        self.add_rule(r'(?<=</)[a-zA-Z0-9_:-]+', "key")      # Closing tag name
    
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
    
        # XML-specific formatting adjustments using theme colors
        if self.theme_manager:
            self._create_format("key", foreground=self.theme_manager.get_syntax_color("keyword"), bold=True)  # Tags
            self._create_format("symbol", foreground=self.theme_manager.get_syntax_color("operator"))  # Attributes
            self._create_format("string", foreground=self.theme_manager.get_syntax_color("string"))  # Values
            self._create_format("number", foreground=self.theme_manager.get_syntax_color("number"))  # Entities
        else:
            # Fallback colors if no theme manager
            self._create_format("key", foreground="#0000aa", bold=True)
            self._create_format("symbol", foreground="#660066")
            self._create_format("string", foreground="#006600")
            self._create_format("number", foreground="#cc6600")

    def highlightBlock(self, text):
        """Apply highlighting rules to the given block of text"""
        # First, reset the state
        self.setCurrentBlockState(0)

        # Apply standard highlighting rules
        super().highlightBlock(text)

        # Process text content between tags
        self._highlight_text_content(text)

    def _highlight_text_content(self, text):
        """Highlight text content between tags with type detection"""
        # Define regex to find text content between tags
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
            start_pos = match.capturedStart(1)
            length = match.capturedLength(1)
    
            # Only apply if there's content
            if length > 0:
                # Attempt to detect the content type and use appropriate formatting
                content_stripped = content.strip()
    
                # Check if it's a number (integer or float)
                number_regex = QRegularExpression(r'^-?[0-9]+(\.[0-9]+)?$')
                if number_regex.match(content_stripped).hasMatch():
                    self.setFormat(start_pos, length, self.formats["number"])
                    continue
    
                # Check if it's a boolean (true/false, True/False)
                if content_stripped.lower() in ["true", "false"]:
                    self.setFormat(start_pos, length, self.formats["boolean"])
                    continue
    
                # Check if it's null (null, None, nil)
                if content_stripped.lower() in ["null", "none", "nil"]:
                    self.setFormat(start_pos, length, self.formats["null"])
                    continue
    
                # Default to string for all other content
                self.setFormat(start_pos, length, self.formats["string"])