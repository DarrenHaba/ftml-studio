# src/ftml_studio/syntax/schema_highlighter.py
import logging
from PySide6.QtCore import QTimer

import ftml
from ftml.exceptions import FTMLParseError

from .base_highlighter import BaseHighlighter

# Configure logging
logger = logging.getLogger("ftml_schema_highlighter")


class SchemaHighlighter(BaseHighlighter):
    """Syntax highlighter for FTML Schema documents"""

    def __init__(self, document, theme_manager=None):
        super().__init__(document, theme_manager)

        # Create highlighter formats
        self.initialize_formats()

        # Create highlighting rules
        self.create_highlighting_rules()

        # Analysis timer to prevent excessive parsing attempts while typing
        self.parse_timer = QTimer()
        self.parse_timer.setSingleShot(True)
        self.parse_timer.timeout.connect(self.parse_schema)

        # Schema errors to highlight
        self.errors = []

        # Start initial parsing timer
        self.document().contentsChange.connect(self.handle_content_change)
        self.parse_timer.start(500)  # Parse after 500ms

    def initialize_formats(self):
        """Initialize text formats with custom colors"""
        super().initialize_formats()

        # Schema-specific formats
        self._create_format("type", foreground="#0000ff", bold=True)
        self._create_format("constraint", foreground="#cc6600")
        self._create_format("constraint_value", foreground="#008800")
        self._create_format("union", foreground="#666666", bold=True)
        self._create_format("optional", foreground="#9900cc", bold=True)
        self._create_format("default", foreground="#666666", bold=True)
        self._create_format("colon", foreground="#666666", bold=True)
        self._create_format("doc_comment", foreground="#336699", italic=True)

    def create_highlighting_rules(self):
        """Create schema-specific highlighting rules"""
        self.highlighting_rules = []

        # Comments
        self.add_rule(r'//!.*$', "doc_comment")
        self.add_rule(r'///.*$', "doc_comment")
        self.add_rule(r'//.*$', "comment")

        # Keys and colons
        self.add_rule(r"^[ \t]*[A-Za-z_][A-Za-z0-9_]*(?=[ \t]*:)", "key")
        self.add_rule(r"(?<=\{)[ \t\r\n]*[A-Za-z_][A-Za-z0-9_]*(?=[ \t]*:)", "key")
        self.add_rule(r"(?<=,)[ \t\r\n]*[A-Za-z_][A-Za-z0-9_]*(?=[ \t]*:)", "key")

        # Optional marker
        self.add_rule(r"\?(?=\s*:)", "optional")

        # Colon
        self.add_rule(r":", "colon")

        # Type names
        self.add_rule(r"(?<=:[ \t]*)(str|int|float|bool|null|any|date|time|datetime|timestamp)\b",
                      "type")

        # Default value marker
        self.add_rule(r"=(?=[ \t]*[\"\'\d\[\{tfn])", "default")

        # Union pipe
        self.add_rule(r"\|", "union")

        # Constraints
        self.add_rule(r"<[^>]*>", "constraint")

        # Constraint values
        self.add_rule(r'(?<=<[^>]*=)[^,>]*(?=[,>])', "constraint_value")

        # Symbols
        self.add_rule(r'[{}\[\],]', "symbol")

        # Strings in default values
        self.add_rule(r'"(?:\\.|[^"\\])*"', "string")
        self.add_rule(r"'(?:\\.|[^'\\])*'", "string")

        # Numbers in default values
        self.add_rule(r'\b-?\d+\.\d+\b', "number")
        self.add_rule(r'\b-?\d+\b', "number")

        # Booleans in default values
        self.add_rule(r'\b(true|false)\b', "boolean")

        # Null in default values
        self.add_rule(r'\bnull\b', "null")

    def handle_content_change(self, position, removed, added):
        """Handle document content changes"""
        # Reset the timer to parse after 500ms of inactivity
        self.parse_timer.start(500)

    def parse_schema(self):
        """Parse the schema document to check for errors"""
        content = self.document().toPlainText()

        # Reset errors
        self.errors = []

        if not content.strip():
            return

        try:
            # Try to parse the schema using FTML
            ftml.load_schema(content)
            logger.debug("Successfully parsed FTML schema")

        except FTMLParseError as e:
            # Handle parse error
            if hasattr(e, "line") and hasattr(e, "col"):
                self.errors.append({
                    "line": e.line,
                    "col": e.col,
                    "message": str(e),
                    "length": 1  # Default to 1 character
                })

            logger.debug(f"FTML schema parse error: {str(e)}")

        except Exception as e:
            # Handle other errors
            logger.debug(f"Error parsing FTML schema: {str(e)}")

        # Reapply highlighting
        self.rehighlight()

    def highlightBlock(self, text):
        """Apply highlighting to the given block of text"""
        # Set default block state
        self.setCurrentBlockState(0)

        # Apply base regex highlighting
        super().highlightBlock(text)

        # Highlight errors
        self.highlight_errors(text)

    def highlight_errors(self, text):
        """Highlight parse errors in the text"""
        block_number = self.currentBlock().blockNumber() + 1

        for error in self.errors:
            if error["line"] == block_number:
                # Highlight the error position
                self.setFormat(error["col"] - 1, error["length"], self.formats["error"])

                # Set block state to indicate error
                self.setCurrentBlockState(1)  # Use state 1 to indicate error
