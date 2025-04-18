# src/ftml_studio/syntax/base_highlighter.py
import logging
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import QRegularExpression, Qt

logger = logging.getLogger("syntax_highlighter")

class BaseHighlighter(QSyntaxHighlighter):
    """Base syntax highlighter with improved theme integration"""

    def __init__(self, document, theme_manager=None):
        super().__init__(document)
        self.theme_manager = theme_manager
        self.highlighting_rules = []
        self.formats = {}

        # Initialize format cache
        self.initialize_formats()

    def initialize_formats(self):
        """Initialize text formats based on theme - override in subclasses for custom formats"""
        # Create standard formats using theme colors
        self._create_format("keyword", role="keyword", bold=True)
        self._create_format("function", role="function")
        self._create_format("string", role="string")
        self._create_format("number", role="number")
        self._create_format("boolean", role="boolean", bold=True)
        self._create_format("null", role="null", bold=True)
        self._create_format("comment", role="comment", italic=True)
        self._create_format("docComment", role="docComment", italic=True)
        self._create_format("symbol", role="symbol")
        self._create_format("operator", role="operator")
        self._create_format("error", role="error", underline=True)

        # FTML-specific mappings for compatibility with existing code
        self._create_format("key", role="keyword", bold=True)
        self._create_format("equals", role="operator", bold=True)
        self._create_format("doc_comment", role="docComment", italic=True)

    def _create_format(self, name, role=None, foreground=None, background=None,
                       bold=False, italic=False, underline=False):
        """
        Create a text format with the specified attributes
        
        Args:
            name: Name to reference this format
            role: Semantic role in syntax highlighting (maps to theme color)
            foreground: Optional explicit foreground color (overrides theme)
            background: Optional explicit background color
            bold: Whether to apply bold style
            italic: Whether to apply italic style
            underline: Whether to apply underline style
        """
        fmt = QTextCharFormat()

        # Use theme colors if available and role is specified
        if self.theme_manager and role and not foreground:
            foreground = self.theme_manager.get_syntax_color(role)

        # Apply colors
        if foreground:
            fmt.setForeground(QColor(foreground))
        if background:
            fmt.setBackground(QColor(background))

        # Apply font styles
        if bold:
            fmt.setFontWeight(QFont.Bold)
        if italic:
            fmt.setFontItalic(True)
        if underline:
            fmt.setFontUnderline(True)

        # Store the format
        self.formats[name] = fmt
        return fmt

    def update_formats(self):
        """Update all formats to match current theme - call when theme changes"""
        # Re-initialize formats with current theme colors
        self.initialize_formats()
        # Rehighlight the document with new formats
        self.rehighlight()

    def add_rule(self, pattern, format_name):
        """Add a highlighting rule with the specified pattern and format"""
        if format_name not in self.formats:
            logger.warning(f"Format '{format_name}' not found, using default")
            self._create_format(format_name)  # Create a default format

        self.highlighting_rules.append((
            QRegularExpression(pattern),
            self.formats[format_name]
        ))

    def highlightBlock(self, text):
        """Apply highlighting rules to the given block of text"""
        # Apply each highlighting rule
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)