# src/ftml_studio/syntax/ast_highlighter.py
import logging
import re
from PySide6.QtCore import QRegularExpression, QTimer
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextCursor

import ftml
from ftml.exceptions import FTMLParseError
from ftml.parser.ast import Node, KeyValueNode, ScalarNode, ObjectNode, ListNode, Comment

from .base_highlighter import BaseHighlighter

# Configure logging
logger = logging.getLogger("ftml_ast_highlighter")

class FTMLASTHighlighter(BaseHighlighter):
    """AST-based syntax highlighter for FTML documents with theme support"""

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

        # Start initial parsing timer
        self.document().contentsChange.connect(self.handle_content_change)
        self.parse_timer.start(500)  # Parse after 500ms

    def initialize_ast_formats(self):
        """Initialize text formats for AST-specific elements using theme"""
        # Create formats using theme semantic roles
        self._create_format("key", role="keyword", bold=True)
        self._create_format("equals", role="operator", bold=True)
        self._create_format("string", role="string")
        self._create_format("number", role="number")
        self._create_format("boolean", role="boolean", bold=True)
        self._create_format("null", role="null", bold=True)
        self._create_format("symbol", role="symbol")
        self._create_format("comment", role="comment", italic=True)
        self._create_format("doc_comment", role="docComment", italic=True)
        self._create_format("inner_doc_comment", role="docComment", italic=True)
        self._create_format("outer_doc_comment", role="docComment", italic=True)

        # Special handling for error format - use wave underline
        error_format = QTextCharFormat()
        if self.theme_manager:
            error_color = QColor(self.theme_manager.get_syntax_color("error"))
        else:
            error_color = QColor("#ff0000")  # Default red

        error_format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
        error_format.setUnderlineColor(error_color)
        # Light background to highlight error position
        background_color = QColor(error_color)
        background_color.setAlpha(20)  # Very transparent
        error_format.setBackground(background_color)

        self.formats["error"] = error_format

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
                # If AST is not available, don't highlight
                self.ast = None
                logger.debug("Parsed FTML but AST not available")
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

        # Try to highlight comments first - these should always be highlighted
        # even if AST highlighting fails
        self.highlight_comments(text)

        # Apply AST-based highlighting if available
        if self.ast:
            self.apply_ast_highlighting(text)

        # Always highlight errors
        self.highlight_errors(text)

    def highlight_comments(self, text):
        """Highlight all types of comments regardless of AST status"""
        # Regular comments //
        comment_regex = QRegularExpression(r'//(?![!/]).*$')
        match_iterator = comment_regex.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats["comment"])

        # Inner doc comments //!
        inner_doc_regex = QRegularExpression(r'//!.*$')
        match_iterator = inner_doc_regex.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats["inner_doc_comment"])

        # Outer doc comments ///
        outer_doc_regex = QRegularExpression(r'///.*$')
        match_iterator = outer_doc_regex.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats["outer_doc_comment"])

    def apply_ast_highlighting(self, text):
        """Apply highlighting based on AST nodes"""
        block_number = self.currentBlock().blockNumber() + 1  # 1-based line numbers

        # Root level key-value pairs
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
                        self.highlight_value_node(node.value, text)

                # Highlight comments
                if hasattr(node, "leading_comments"):
                    for comment in node.leading_comments:
                        if hasattr(comment, 'line') and comment.line == block_number:
                            self.highlight_comment_node(comment, text)

                if hasattr(node, "inline_comment") and node.inline_comment and hasattr(node.inline_comment, 'line') and node.inline_comment.line == block_number:
                    self.highlight_comment_node(node.inline_comment, text)

    def highlight_value_node(self, node, text):
        """Recursively highlight a value node and its children"""
        if not node:
            return

        # Check if node is on the current line
        block_number = self.currentBlock().blockNumber() + 1
        if hasattr(node, 'line') and node.line != block_number:
            return  # Skip nodes on other lines

        # Handle different node types
        if isinstance(node, ScalarNode):
            # CRITICAL: Order matters here - check specific types before general types
            # 1. String values
            if isinstance(node.value, str):
                # Find quoted strings in the text - this handles both single and double quotes
                pattern = QRegularExpression(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
                match_iterator = pattern.globalMatch(text)
                while match_iterator.hasNext():
                    match = match_iterator.next()
                    self.setFormat(match.capturedStart(), match.capturedLength(), self.formats["string"])

            # 2. Boolean values
            elif isinstance(node.value, bool):
                # Find boolean value in the text
                value_str = str(node.value).lower()  # FTML uses lowercase true/false
                pos = text.find(value_str)
                if pos >= 0:
                    self.setFormat(pos, len(value_str), self.formats["boolean"])

            # 3. Null values
            elif node.value is None:
                # Find "null" in the text
                pos = text.find("null")
                if pos >= 0:
                    self.setFormat(pos, 4, self.formats["null"])

            # 4. Number values - check last so it doesn't try to find booleans as numbers
            elif isinstance(node.value, (int, float)):
                # Find the number in the text
                value_str = str(node.value)
                pos = text.find(value_str)
                if pos >= 0:
                    self.setFormat(pos, len(value_str), self.formats["number"])

        elif isinstance(node, ObjectNode):
            self.highlight_object_node(node, text)

        elif isinstance(node, ListNode):
            self.highlight_list_node(node, text)

    def highlight_object_node(self, node, text):
        """Highlight an object node and its contents"""
        # Highlight object braces
        lbrace_pos = text.find("{")
        if lbrace_pos >= 0:
            self.setFormat(lbrace_pos, 1, self.formats["symbol"])

        rbrace_pos = text.rfind("}")
        if rbrace_pos >= 0:
            self.setFormat(rbrace_pos, 1, self.formats["symbol"])

        # Process contents if this is a multiline object
        # (contents of objects on other lines will be processed in their own blocks)
        block_number = self.currentBlock().blockNumber() + 1
        if hasattr(node, 'items'):
            for key, kv_node in node.items.items():
                if hasattr(kv_node, 'line') and kv_node.line == block_number:
                    # Highlight key
                    key_pos = text.find(key)
                    if key_pos >= 0:
                        self.setFormat(key_pos, len(key), self.formats["key"])

                    # Highlight equals sign
                    equals_pos = text.find("=", key_pos + len(key) if key_pos >= 0 else 0)
                    if equals_pos >= 0:
                        self.setFormat(equals_pos, 1, self.formats["equals"])

                    # Highlight value
                    if kv_node.value:
                        self.highlight_value_node(kv_node.value, text)

                # Process comments
                if hasattr(kv_node, "leading_comments"):
                    for comment in kv_node.leading_comments:
                        if hasattr(comment, 'line') and comment.line == block_number:
                            self.highlight_comment_node(comment, text)

                if hasattr(kv_node, "inline_comment") and kv_node.inline_comment and hasattr(kv_node.inline_comment, 'line') and kv_node.inline_comment.line == block_number:
                    self.highlight_comment_node(kv_node.inline_comment, text)

    def highlight_list_node(self, node, text):
        """Highlight a list node and its contents"""
        # Highlight list brackets
        lbracket_pos = text.find("[")
        if lbracket_pos >= 0:
            self.setFormat(lbracket_pos, 1, self.formats["symbol"])

        rbracket_pos = text.rfind("]")
        if rbracket_pos >= 0:
            self.setFormat(rbracket_pos, 1, self.formats["symbol"])

        # Highlight commas
        for i, char in enumerate(text):
            if char == ',':
                self.setFormat(i, 1, self.formats["symbol"])

        # Process elements if this is a multiline list
        # (elements on other lines will be processed in their own blocks)
        block_number = self.currentBlock().blockNumber() + 1
        if hasattr(node, 'elements'):
            for elem in node.elements:
                if hasattr(elem, 'line') and elem.line == block_number:
                    self.highlight_value_node(elem, text)

    def highlight_comment_node(self, comment, text):
        """Highlight a comment node"""
        if not comment:
            return

        block_number = self.currentBlock().blockNumber() + 1

        if hasattr(comment, 'line') and comment.line == block_number:
            # Determine comment format based on type
            format_key = "doc_comment"
            if comment.text.startswith("//!"):
                format_key = "inner_doc_comment"
            elif comment.text.startswith("///"):
                format_key = "outer_doc_comment"
            elif comment.text.startswith("//"):
                format_key = "comment"

            # Find the comment in the current line
            comment_pos = text.find("//")
            if comment_pos >= 0:
                self.setFormat(comment_pos, len(text) - comment_pos, self.formats[format_key])

    def highlight_errors(self, text):
        """Highlight parse errors in the text with wave underlines"""
        block_number = self.currentBlock().blockNumber() + 1

        for error in self.errors:
            if error["line"] == block_number:
                # Get error position and adjust if needed
                col = max(0, error["col"] - 1)  # Convert 1-based to 0-based, ensure not negative
                length = max(1, error["length"])  # Ensure at least 1 char highlighted

                # Check if position is within text bounds
                if col < len(text):
                    # Adjust length to not go beyond end of line
                    length = min(length, len(text) - col)

                    # Apply error format (wave underline)
                    self.setFormat(col, length, self.formats["error"])

                    # Set block state to indicate error
                    self.setCurrentBlockState(1)  # Use state 1 to indicate error