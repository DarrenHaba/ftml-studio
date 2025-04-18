# src/ftml_studio/syntax/ast_highlighter.py
import logging
import re
from PySide6.QtCore import QRegularExpression, QTimer, Signal, QObject
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextCursor

import ftml
from ftml.exceptions import FTMLParseError
from ftml.parser.ast import Node, KeyValueNode, ScalarNode, ObjectNode, ListNode, Comment

from .base_highlighter import BaseHighlighter

# Configure logging
logger = logging.getLogger("ftml_ast_highlighter")

# Helper class to emit signals (since QSyntaxHighlighter doesn't inherently support signals)
class ErrorSignaler(QObject):
    errorsChanged = Signal(list)  # Signal emitted when errors change

class FTMLASTHighlighter(BaseHighlighter):
    """AST-based syntax highlighter for FTML documents with theme support and error resilience"""

    def __init__(self, document, theme_manager=None, error_highlighting=True, parse_delay=500):
        super().__init__(document, theme_manager)

        # Create signal emitter for errors
        self._signaler = ErrorSignaler()
        self.errorsChanged = self._signaler.errorsChanged

        # Configure options
        self.error_highlighting = error_highlighting  # Whether to highlight errors directly
        self.parse_delay = parse_delay  # Delay in milliseconds before parsing after content change

        # Initialize formats specific to AST highlighting
        self.initialize_ast_formats()

        # Analysis timer to prevent excessive parsing attempts while typing
        self.parse_timer = QTimer()
        self.parse_timer.setSingleShot(True)
        self.parse_timer.timeout.connect(self.parse_document)

        # Current AST and parse errors
        self.ast = None
        self.parse_error = None
        self.errors = []

        # The document content that was successfully parsed
        self.valid_content = ""

        # A flag to indicate if we're using partial highlighting
        self.using_partial_highlighting = False

        # Start initial parsing timer
        self.document().contentsChange.connect(self.handle_content_change)
        self.parse_timer.start(self.parse_delay)  # Parse after delay

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
        self._create_format("error_token", role="error")  # For highlighting error tokens in red

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
        # Reset the timer to parse after delay of inactivity
        self.parse_timer.start(self.parse_delay)

    def set_parse_delay(self, delay_ms):
        """Set the delay before parsing after content changes"""
        self.parse_delay = max(100, delay_ms)  # Ensure minimum 100ms delay

    def parse_document(self):
        """Parse the entire document to build AST"""
        content = self.document().toPlainText()

        # Reset errors and flags
        old_errors = self.errors.copy()
        self.errors = []
        self.using_partial_highlighting = False
        self.valid_content = content  # Assume content is valid until proven otherwise

        if not content.strip():
            self.ast = None
            self.parse_error = None
            self.rehighlight()

            # Emit errors changed signal if errors were cleared
            if old_errors and not self.errors:
                self._signaler.errorsChanged.emit(self.errors)
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
                # If AST is not available, use partial highlighting
                self.ast = None
                self.using_partial_highlighting = True
                logger.debug("Parsed FTML but AST not available, using partial highlighting")

        except FTMLParseError as e:
            # Handle parse error - still try to partially highlight
            self.ast = None
            self.parse_error = e
            self.using_partial_highlighting = True

            # Record error for highlighting
            if hasattr(e, "line") and hasattr(e, "col"):
                self.errors.append({
                    "line": e.line,
                    "col": e.col,
                    "message": str(e),
                    "length": 1  # Default to 1 character
                })

                # Try to find the specific error token
                token_match = re.search(r'Got\s+\w+\s+[\'"]?([^\'"]+)[\'"]?', str(e))
                if token_match:
                    error_token = token_match.group(1)
                    self.errors[-1]["token"] = error_token
                    self.errors[-1]["length"] = len(error_token)

            logger.debug(f"FTML parse error: {str(e)}")

            # If we have an error location, try to highlight content up to that point
            if hasattr(e, "line") and hasattr(e, "col"):
                # This is a simplification - in reality, you'd need a more sophisticated 
                # way to extract valid content up to the error
                content_lines = content.splitlines()
                valid_lines = content_lines[:e.line-1]  # Lines before error

                if e.line <= len(content_lines):
                    # Add the portion of the error line up to the error
                    error_line = content_lines[e.line-1]
                    if e.col <= len(error_line):
                        valid_lines.append(error_line[:e.col-1])

                self.valid_content = '\n'.join(valid_lines)

                # Try to parse the valid portion, if possible
                try:
                    if self.valid_content:
                        data = ftml.load(self.valid_content, preserve_comments=True)
                        if hasattr(data, "_ast_node"):
                            self.ast = data._ast_node
                            logger.debug("Successfully parsed partial FTML document")
                except Exception:
                    # If that fails, we'll still do regex-based highlighting
                    self.ast = None

        except Exception as e:
            # Handle other errors - fall back to regex highlighting
            self.ast = None
            self.parse_error = e
            self.using_partial_highlighting = True
            logger.debug(f"Error parsing FTML: {str(e)}")

        # Emit signal if errors changed
        if old_errors != self.errors:
            self._signaler.errorsChanged.emit(self.errors)

        # Reapply highlighting after any change (success or failure)
        self.rehighlight()

    def highlightBlock(self, text):
        """Apply highlighting to the given block of text"""
        # Set default block state
        self.setCurrentBlockState(0)

        # Always highlight comments first - these should always be highlighted
        # even if AST highlighting fails
        self.highlight_comments(text)

        # Apply AST-based highlighting if available
        if self.ast:
            try:
                self.apply_ast_highlighting(text)
            except Exception as e:
                logger.error(f"Error in AST highlighting: {str(e)}", exc_info=True)
                # If AST highlighting fails, we'll still have comment highlighting
        elif self.using_partial_highlighting:
            # Fall back to regex-based highlighting for core elements
            self.apply_fallback_highlighting(text)

        # Always highlight errors if error highlighting is enabled
        if self.error_highlighting:
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

        # Process all elements on this line
        self.process_elements_on_line(self.ast, text, block_number)

    def apply_fallback_highlighting(self, text):
        """Apply basic highlighting when AST is not available"""
        # This is a simplified fallback that uses regex patterns for basic highlighting

        # ================================================================
        # Keys and equals signs
        # ================================================================
        # Match keys (rule: [A-Za-z_][A-Za-z0-9_]* at the start of a line followed by =)
        key_regex = QRegularExpression(r"^[ \t]*([A-Za-z_][A-Za-z0-9_]*)[ \t]*(?==)")
        match_iterator = key_regex.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            # Highlight the key
            self.setFormat(match.capturedStart(1), match.capturedLength(1), self.formats["key"])

            # Find the equals sign after the key
            equals_regex = QRegularExpression(r"=")
            equals_match = equals_regex.match(text, match.capturedEnd(1))
            if equals_match.hasMatch():
                self.setFormat(equals_match.capturedStart(), equals_match.capturedLength(), self.formats["equals"])

        # ================================================================
        # Strings
        # ================================================================
        # Double-quoted strings
        string_regex = QRegularExpression(r'"(?:\\.|[^"\\])*"')
        match_iterator = string_regex.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats["string"])

        # Single-quoted strings
        string_regex = QRegularExpression(r"'(?:\\.|[^'\\])*'")
        match_iterator = string_regex.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats["string"])

        # ================================================================
        # Numbers
        # ================================================================
        # Integer numbers
        number_regex = QRegularExpression(r'\b-?\d+\b')
        match_iterator = number_regex.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats["number"])

        # Floating point numbers
        float_regex = QRegularExpression(r'\b-?\d+\.\d+\b')
        match_iterator = float_regex.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats["number"])

        # ================================================================
        # Booleans and null
        # ================================================================
        # Boolean values
        boolean_regex = QRegularExpression(r'\b(true|false)\b')
        match_iterator = boolean_regex.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats["boolean"])

        # Null value
        null_regex = QRegularExpression(r'\bnull\b')
        match_iterator = null_regex.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats["null"])

        # ================================================================
        # Braces, brackets and commas
        # ================================================================
        # Braces
        for i, char in enumerate(text):
            if char in "{},[]":
                self.setFormat(i, 1, self.formats["symbol"])

    def process_elements_on_line(self, node, text, block_number):
        """
        Process all elements in the AST that might be on the current line.
        This includes top-level items and nested items.
        """
        # Process root level items
        if hasattr(node, "items") and isinstance(node.items, dict):
            for key, kv_node in node.items.items():
                # Process the key-value pair itself if it's on this line
                if hasattr(kv_node, 'line') and kv_node.line == block_number:
                    self.process_key_value_node(kv_node, text)

                # Even if the key-value pair itself isn't on this line,
                # its value might have elements on this line
                if hasattr(kv_node, 'value'):
                    if isinstance(kv_node.value, ObjectNode):
                        self.process_object_node(kv_node.value, text, block_number)
                    elif isinstance(kv_node.value, ListNode):
                        self.process_list_node(kv_node.value, text, block_number)

                # Process comments
                if hasattr(kv_node, "leading_comments"):
                    for comment in kv_node.leading_comments:
                        if hasattr(comment, 'line') and comment.line == block_number:
                            self.highlight_comment_node(comment, text)

                if hasattr(kv_node, "inline_comment") and kv_node.inline_comment and hasattr(kv_node.inline_comment, 'line') and kv_node.inline_comment.line == block_number:
                    self.highlight_comment_node(kv_node.inline_comment, text)

    def process_key_value_node(self, node, text):
        """Process a key-value node, highlighting the key, equals sign and value"""
        if not isinstance(node, KeyValueNode):
            return

        # Highlight key
        key = node.key
        key_pos = text.find(key)
        if key_pos >= 0:
            self.setFormat(key_pos, len(key), self.formats["key"])

        # Highlight equals sign
        equals_pos = text.find("=", key_pos + len(key) if key_pos >= 0 else 0)
        if equals_pos >= 0:
            self.setFormat(equals_pos, 1, self.formats["equals"])

        # Highlight value if it's a scalar
        if node.value and isinstance(node.value, ScalarNode):
            self.highlight_value_node(node.value, text)

    def process_object_node(self, node, text, block_number):
        """Process an object node, looking for elements on the current line"""
        if not isinstance(node, ObjectNode):
            return

        # Highlight braces if they're on this line
        if hasattr(node, 'line') and node.line == block_number:
            # Opening brace is on this line
            lbrace_pos = text.find("{")
            if lbrace_pos >= 0:
                self.setFormat(lbrace_pos, 1, self.formats["symbol"])

        # Check for closing brace on this line
        # This is a simplification - we'd need more info to know for sure
        # if a closing brace belongs to this specific object
        rbrace_pos = text.rfind("}")
        if rbrace_pos >= 0:
            self.setFormat(rbrace_pos, 1, self.formats["symbol"])

        # Process items in the object
        if hasattr(node, 'items'):
            for key, item_node in node.items.items():
                # Check if this key-value pair is on this line
                if hasattr(item_node, 'line') and item_node.line == block_number:
                    # Highlight the key
                    key_pos = text.find(key)
                    if key_pos >= 0:
                        self.setFormat(key_pos, len(key), self.formats["key"])

                    # Highlight equals sign
                    equals_pos = text.find("=", key_pos + len(key) if key_pos >= 0 else 0)
                    if equals_pos >= 0:
                        self.setFormat(equals_pos, 1, self.formats["equals"])

                    # Highlight the value
                    if item_node.value:
                        self.highlight_value_node(item_node.value, text)

                # Check for nested objects and lists
                if hasattr(item_node, 'value'):
                    if isinstance(item_node.value, ObjectNode):
                        self.process_object_node(item_node.value, text, block_number)
                    elif isinstance(item_node.value, ListNode):
                        self.process_list_node(item_node.value, text, block_number)

                # Process comments
                if hasattr(item_node, "leading_comments"):
                    for comment in item_node.leading_comments:
                        if hasattr(comment, 'line') and comment.line == block_number:
                            self.highlight_comment_node(comment, text)

                if hasattr(item_node, "inline_comment") and item_node.inline_comment and hasattr(item_node.inline_comment, 'line') and item_node.inline_comment.line == block_number:
                    self.highlight_comment_node(item_node.inline_comment, text)

    def process_list_node(self, node, text, block_number):
        """Process a list node, looking for elements on the current line"""
        if not isinstance(node, ListNode):
            return

        # Highlight brackets if they're on this line
        if hasattr(node, 'line') and node.line == block_number:
            # Opening bracket is on this line
            lbracket_pos = text.find("[")
            if lbracket_pos >= 0:
                self.setFormat(lbracket_pos, 1, self.formats["symbol"])

        # Check for closing bracket on this line
        rbracket_pos = text.rfind("]")
        if rbracket_pos >= 0:
            self.setFormat(rbracket_pos, 1, self.formats["symbol"])

        # Highlight commas on this line
        for i, char in enumerate(text):
            if char == ',':
                self.setFormat(i, 1, self.formats["symbol"])

        # Process elements in the list
        if hasattr(node, 'elements'):
            for elem in node.elements:
                # Check if this element is on this line
                if hasattr(elem, 'line') and elem.line == block_number:
                    # Highlight the element
                    self.highlight_value_node(elem, text)

                # Check for nested objects and lists
                if isinstance(elem, ObjectNode):
                    self.process_object_node(elem, text, block_number)
                elif isinstance(elem, ListNode):
                    self.process_list_node(elem, text, block_number)

    def highlight_value_node(self, node, text):
        """Highlight a scalar value node"""
        if not isinstance(node, ScalarNode):
            return

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

    def highlight_comment_node(self, comment, text):
        """Highlight a comment node"""
        if not comment:
            return

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
        """Highlight parse errors in the text with wave underlines or red text"""
        block_number = self.currentBlock().blockNumber() + 1

        for error in self.errors:
            if error["line"] == block_number:
                # Get error position and adjust if needed
                col = max(0, error["col"] - 1)  # Convert 1-based to 0-based, ensure not negative
                length = max(1, error.get("length", 1))  # Use length from error or default to 1

                # Try to find the specific error token if it's provided
                if "token" in error:
                    # Look for this token in the text
                    error_token = error["token"]
                    token_pos = text.find(error_token, col)
                    if token_pos >= 0:
                        # Found the token, use its position and length
                        col = token_pos
                        length = len(error_token)

                # Check if position is within text bounds
                if col < len(text):
                    # Adjust length to not go beyond end of line
                    length = min(length, len(text) - col)

                    # Apply error format (wave underline or red text)
                    self.setFormat(col, length, self.formats["error"])

                    # Set block state to indicate error
                    self.setCurrentBlockState(1)  # Use state 1 to indicate error
