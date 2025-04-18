# src/ftml_studio/syntax/ast_highlighter.py
import logging
from PySide6.QtCore import QRegularExpression, QTimer
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextCursor

import ftml
from ftml.exceptions import FTMLParseError
from ftml.parser.ast import Node, KeyValueNode, ScalarNode, ObjectNode, ListNode, Comment

from .base_highlighter import BaseHighlighter

# Configure logging
logger = logging.getLogger("ftml_ast_highlighter")

class FTMLASTHighlighter(BaseHighlighter):
    """AST-based syntax highlighter for FTML documents"""

    def __init__(self, document, theme_manager=None):
        super().__init__(document, theme_manager)

        # Initialize formats specific to AST highlighting
        self.initialize_ast_formats()

        # Analysis timer to prevent excessive parsing attempts while typing
        self.parse_timer = QTimer()
        self.parse_timer.setSingleShot(True)
        self.parse_timer.timeout.connect(self.parse_document)

        # Current AST and parse errors
        self.ast = None
        self.parse_error = None

        # Errors to highlight in the document
        self.errors = []

        # Backup regex highlighting for basic coloring when AST is not available
        self.create_fallback_rules()

        # Start initial parsing timer
        self.document().contentsChange.connect(self.handle_content_change)
        self.parse_timer.start(500)  # Parse after 500ms

    def initialize_ast_formats(self):
        """Initialize text formats for AST-specific elements"""
        # Add specific formats for AST nodes
        self._create_format("key", foreground="#0066cc", bold=True)
        self._create_format("equals", foreground="#666666", bold=True)
        self._create_format("string", foreground="#008800")
        self._create_format("number", foreground="#aa6600")
        self._create_format("boolean", foreground="#9900cc", bold=True)
        self._create_format("null", foreground="#880088", bold=True)
        self._create_format("symbol", foreground="#666666")
        self._create_format("comment", foreground="#808080", italic=True)
        self._create_format("doc_comment", foreground="#336699", italic=True)
        self._create_format("error", foreground="#ff0000", underline=True)
        self._create_format("invalid", foreground="#000000", background="#ffeeee", underline=True)  # Light red background with underline

    def create_fallback_rules(self):
        """Create fallback regex-based highlighting rules"""
        # These rules are used when AST parsing fails
        self.fallback_rules = []

        # Comments
        self.fallback_rules.append((
            QRegularExpression(r'//!.*$'),
            self.formats["doc_comment"]
        ))
        self.fallback_rules.append((
            QRegularExpression(r'///.*$'),
            self.formats["doc_comment"]
        ))
        self.fallback_rules.append((
            QRegularExpression(r'//.*$'),
            self.formats["comment"]
        ))

        # Keys
        self.fallback_rules.append((
            QRegularExpression(r"^[ \t]*[A-Za-z_][A-Za-z0-9_]*(?=[ \t]*=)"),
            self.formats["key"]
        ))

        # Equals sign
        self.fallback_rules.append((
            QRegularExpression(r'='),
            self.formats["equals"]
        ))

        # Strings
        self.fallback_rules.append((
            QRegularExpression(r'"(?:\\.|[^"\\])*"'),
            self.formats["string"]
        ))
        self.fallback_rules.append((
            QRegularExpression(r"'(?:\\.|[^'\\])*'"),
            self.formats["string"]
        ))

        # Basic symbols
        self.fallback_rules.append((
            QRegularExpression(r'[{}\[\],]'),
            self.formats["symbol"]
        ))

        # Booleans
        self.fallback_rules.append((
            QRegularExpression(r'\b(true|false)\b'),
            self.formats["boolean"]
        ))

        # Null
        self.fallback_rules.append((
            QRegularExpression(r'\bnull\b'),
            self.formats["null"]
        ))

        # Numbers
        self.fallback_rules.append((
            QRegularExpression(r'\b-?\d+\.\d+\b'),
            self.formats["number"]
        ))
        self.fallback_rules.append((
            QRegularExpression(r'\b-?\d+\b'),
            self.formats["number"]
        ))

    def handle_content_change(self, position, removed, added):
        """Handle document content changes"""
        # Reset the timer to parse after 500ms of inactivity
        self.parse_timer.start(500)

    def parse_document(self):
        """Parse the entire document to build AST"""
        content = self.document().toPlainText()
    
        # Reset errors
        self.errors = []
    
        if not content.strip():
            self.ast = None
            self.parse_error = None
            self.rehighlight()
            return
    
        try:
            # Try to parse using FTML
            data = ftml.load(content, preserve_comments=True)
    
            # Extract the AST from the returned data
            if hasattr(data, "_ast_node"):
                self.ast = data._ast_node
                self.parse_error = None
                logger.debug("Successfully parsed FTML document")
            else:
                # If AST is not available, use fallback
                self.ast = None
                logger.debug("Parsed FTML but AST not available, using fallback")
    
                # Even though we don't have AST, the document is valid, so still apply highlight
                self.rehighlight()
                return
    
        except FTMLParseError as e:
            # Handle parse error
            self.ast = None
            self.parse_error = e
    
            # Record error for highlighting
            if hasattr(e, "line") and hasattr(e, "col"):
                self.errors.append({
                    "line": e.line,
                    "col": e.col,
                    "message": str(e),
                    "length": 1  # Default to 1 character
                })
    
            logger.debug(f"FTML parse error: {str(e)}")
    
        except Exception as e:
            # Handle other errors
            self.ast = None
            self.parse_error = e
            logger.debug(f"Error parsing FTML: {str(e)}")
    
        # Reapply highlighting after any change (success or failure)
        self.rehighlight()

    def highlightBlock(self, text):
        """Apply highlighting to the given block of text"""
        # Set default block state
        self.setCurrentBlockState(0)
    
        # Always apply fallback highlighting first to cover the basics
        self.apply_fallback_highlighting(text)
    
        # If we have AST, use it to enhance highlighting
        if self.ast:
            self.apply_ast_highlighting(text)
    
        # Always highlight errors
        self.highlight_errors(text)

    def apply_ast_highlighting(self, text):
        """Apply highlighting based on AST nodes"""
        block_number = self.currentBlock().blockNumber() + 1  # 1-based line numbers

        # Find nodes that correspond to this line
        if hasattr(self.ast, "items"):
            # Process root level nodes
            for key, node in self.ast.items.items():
                if not isinstance(node, KeyValueNode):
                    continue

                # Check if this node intersects with current block
                if hasattr(node, 'line') and node.line == block_number:
                    # Highlight key - find key position in line
                    key_pos = text.find(key)
                    if key_pos >= 0:
                        self.setFormat(key_pos, len(key), self.formats["key"])

                    # Highlight equals sign - find equals sign
                    equals_pos = text.find("=", key_pos + len(key) if key_pos >= 0 else 0)
                    if equals_pos >= 0:
                        self.setFormat(equals_pos, 1, self.formats["equals"])

                    # Highlight value
                    if node.value:
                        self.highlight_value_node(node.value)

                # Highlight comments
                if hasattr(node, "leading_comments"):
                    for comment in node.leading_comments:
                        if hasattr(comment, 'line') and comment.line == block_number:
                            self.highlight_comment_node(comment)

                if hasattr(node, "inline_comment") and node.inline_comment and hasattr(node.inline_comment, 'line') and node.inline_comment.line == block_number:
                    self.highlight_comment_node(node.inline_comment)

    def highlight_value_node(self, node):
        """Recursively highlight a value node and its children"""
        if not node:
            return

        block_number = self.currentBlock().blockNumber() + 1

        if isinstance(node, ScalarNode) and hasattr(node, 'line') and node.line == block_number:
            # Determine the format based on the value type
            if isinstance(node.value, str):
                # String value - need to find it in the line
                text = self.currentBlock().text()
                # Look for quoted strings
                pattern = QRegularExpression(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
                match_iterator = pattern.globalMatch(text)
                while match_iterator.hasNext():
                    match = match_iterator.next()
                    self.setFormat(match.capturedStart(), match.capturedLength(), self.formats["string"]) 
            elif isinstance(node.value, (int, float)):
                # Number value - need to find it in the line  
                text = self.currentBlock().text()
                # Look for the number representation
                value_str = str(node.value)
                pos = text.find(value_str)
                if pos >= 0:
                    self.setFormat(pos, len(value_str), self.formats["number"])
            elif isinstance(node.value, bool):
                # Boolean value
                text = self.currentBlock().text()
                # Look for "true" or "false"
                value_str = str(node.value).lower()
                pos = text.find(value_str)
                if pos >= 0:
                    self.setFormat(pos, len(value_str), self.formats["boolean"])
            elif node.value is None:
                # Null value
                text = self.currentBlock().text()
                # Look for "null"
                pos = text.find("null")
                if pos >= 0:
                    self.setFormat(pos, 4, self.formats["null"])  # "null" is 4 characters

        elif isinstance(node, ObjectNode) and hasattr(node, 'line') and node.line == block_number:
            # Highlight object braces
            if hasattr(node, 'col') and node.col > 0:
                # Opening brace - find it in the text
                text = self.currentBlock().text()
                brace_pos = text.find("{")
                if brace_pos >= 0:
                    self.setFormat(brace_pos, 1, self.formats["symbol"])

                # If closing brace is on the same line
                closing_pos = text.rfind("}")
                if closing_pos >= 0:
                    self.setFormat(closing_pos, 1, self.formats["symbol"])

            # Recursively highlight object contents
            for key, item in node.items.items():
                if isinstance(item, KeyValueNode) and hasattr(item, 'line') and item.line == block_number:
                    # Highlight key
                    text = self.currentBlock().text()
                    key_pos = text.find(key)
                    if key_pos >= 0:
                        self.setFormat(key_pos, len(key), self.formats["key"])

                    # Highlight equals sign
                    equals_pos = text.find("=", key_pos + len(key) if key_pos >= 0 else 0)
                    if equals_pos >= 0:
                        self.setFormat(equals_pos, 1, self.formats["equals"])

                    # Highlight value
                    if item.value:
                        self.highlight_value_node(item.value)

                # Highlight comments
                if hasattr(item, "leading_comments"):
                    for comment in item.leading_comments:
                        if hasattr(comment, 'line') and comment.line == block_number:
                            self.highlight_comment_node(comment)

                if hasattr(item, "inline_comment") and item.inline_comment and hasattr(item.inline_comment, 'line') and item.inline_comment.line == block_number:
                    self.highlight_comment_node(item.inline_comment)

        elif isinstance(node, ListNode) and hasattr(node, 'line') and node.line == block_number:
            # Highlight list brackets
            text = self.currentBlock().text()
            bracket_pos = text.find("[")
            if bracket_pos >= 0:
                self.setFormat(bracket_pos, 1, self.formats["symbol"])

            closing_pos = text.rfind("]")
            if closing_pos >= 0:
                self.setFormat(closing_pos, 1, self.formats["symbol"])

            # Highlight commas
            for i, char in enumerate(text):
                if char == ',':
                    self.setFormat(i, 1, self.formats["symbol"])

            # Recursively highlight list elements
            for elem in node.elements:
                if hasattr(elem, 'line') and elem.line == block_number:
                    self.highlight_value_node(elem)

    def highlight_comment_node(self, comment):
        """Highlight a comment node"""
        if not comment:
            return

        block_number = self.currentBlock().blockNumber() + 1

        if hasattr(comment, 'line') and comment.line == block_number:
            # Determine comment format based on type
            format_key = "doc_comment" if comment.text.startswith("//!") or comment.text.startswith("///") else "comment"

            # Find the comment in the current line
            text = self.currentBlock().text()
            comment_pos = text.find("//")
            if comment_pos >= 0:
                self.setFormat(comment_pos, len(text) - comment_pos, self.formats[format_key])

    def apply_fallback_highlighting(self, text):
        """Apply fallback regex-based highlighting"""
        # Apply each fallback rule
        for pattern, format in self.fallback_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

    def highlight_errors(self, text):
        """Highlight parse errors in the text"""
        block_number = self.currentBlock().blockNumber() + 1
    
        # If we have specific error locations
        for error in self.errors:
            if error["line"] == block_number:
                # Highlight the error position
                self.setFormat(error["col"] - 1, error["length"], self.formats["error"])
    
                # Set block state to indicate error
                self.setCurrentBlockState(1)  # Use state 1 to indicate error
    
                # Try to highlight remaining text on the line as invalid
                # First, find where the valid part ends
                valid_text_end = error["col"] - 1
    
                # Highlight from the error position to the end of the line as invalid
                if valid_text_end < len(text):
                    self.setFormat(valid_text_end, len(text) - valid_text_end, self.formats["invalid"])
    
        # If we have a parse error but no specific location
        if self.parse_error and not self.errors and self.currentBlockState() != 1:
            # Check if this line has any content that might be invalid
            stripped_text = text.strip()
            if stripped_text and not (
                    stripped_text.startswith("//") or
                    # Looks like a valid key-value pair
                    (any(c in stripped_text for c in "=") and "=" == stripped_text.split()[1])
            ):
                # Might be an invalid line, highlight it
                self.setFormat(0, len(text), self.formats["invalid"])
                self.setCurrentBlockState(1)  # Mark as error
