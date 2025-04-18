# ast_highlighter_debug.py
import re
import sys
import logging
from PySide6.QtWidgets import (QApplication, QMainWindow, QSplitter, QTextEdit,
                               QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
                               QLabel, QPlainTextEdit)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat

import ftml
from ftml.exceptions import FTMLParseError
from ftml.parser.ast import Node, KeyValueNode, ScalarNode, ObjectNode, ListNode, Comment

# Configure logging to our custom handler
class QTextEditLogger(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.formatter = logging.Formatter('%(levelname)s - %(message)s')

    def emit(self, record):
        msg = self.formatter.format(record)
        self.text_edit.append(msg)
        # Auto-scroll to bottom
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text_edit.setTextCursor(cursor)

class DebugFTMLASTHighlighter:
    """Standalone AST-based highlighter for debugging"""

    def __init__(self, editor, debug_output):
        self.editor = editor
        self.debug_output = debug_output
        self.ast = None
        self.logger = logging.getLogger("debug_highlighter")

        # Create formats
        self.formats = {}
        self.initialize_formats()

    def initialize_formats(self):
        """Initialize text formats"""
        self._create_format("key", QColor("#0000FF"), bold=True)  # Blue, bold
        self._create_format("equals", QColor("#000000"), bold=True)  # Black, bold
        self._create_format("string", QColor("#008000"))  # Green
        self._create_format("number", QColor("#FF8C00"))  # Orange
        self._create_format("boolean", QColor("#800080"), bold=True)  # Purple, bold
        self._create_format("null", QColor("#800080"), bold=True)  # Purple, bold
        self._create_format("symbol", QColor("#000000"))  # Black
        self._create_format("comment", QColor("#808080"), italic=True)  # Gray, italic
        self._create_format("doc_comment", QColor("#008080"), italic=True)  # Teal, italic
        self._create_format("inner_doc_comment", QColor("#008080"), italic=True)  # Teal, italic
        self._create_format("outer_doc_comment", QColor("#008080"), italic=True)  # Teal, italic
        self._create_format("error", QColor("#FF0000"), underline=True)  # Red, underlined

    def _create_format(self, name, color, bold=False, italic=False, underline=False):
        """Create a text format with specified properties"""
        fmt = QTextCharFormat()
        fmt.setForeground(color)

        if bold:
            fmt.setFontWeight(700)  # Bold
        if italic:
            fmt.setFontItalic(True)
        if underline:
            fmt.setFontUnderline(True)

        self.formats[name] = fmt

    def debug(self, message):
        """Log a debug message"""
        self.logger.debug(message)

    def parse_document(self):
        """Parse the document and build AST"""
        content = self.editor.toPlainText()
        self.debug("Starting AST parsing")

        if not content.strip():
            self.debug("Empty document, nothing to parse")
            self.ast = None
            return

        try:
            # Parse the FTML
            data = ftml.load(content, preserve_comments=True)

            # Extract the AST
            if hasattr(data, "_ast_node"):
                self.ast = data._ast_node
                self.debug(f"Successfully parsed FTML into AST with {len(self.ast.items) if hasattr(self.ast, 'items') else 0} root items")

                # Debug root items
                if hasattr(self.ast, "items"):
                    for key, node in self.ast.items.items():
                        self.debug(f"Root item: {key} = {type(node.value).__name__ if hasattr(node, 'value') else 'Unknown'}")
            else:
                self.debug("Parsed FTML but AST not available")
                self.ast = None

        except FTMLParseError as e:
            self.debug(f"FTML parse error: {str(e)}")
            self.ast = None

        except Exception as e:
            self.debug(f"Unexpected error parsing FTML: {str(e)}")
            self.ast = None

    def highlight_document(self):
        """Highlight the document based on AST"""
        if not self.ast:
            self.debug("No AST available, only highlighting comments")
            self.highlight_comments_only()
            return

        # Clear all formatting
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()

        # First pass: highlight all comments
        self.highlight_comments_only()

        # Second pass: highlight AST structure
        if hasattr(self.ast, "items"):
            for key, node in self.ast.items.items():
                self.debug(f"Processing root item: {key}")

                # Find and highlight key
                self.highlight_key_value_pair(key, node)

    def highlight_comments_only(self):
        """First pass highlighting only comments"""
        content = self.editor.toPlainText()

        # Find and highlight regular comments
        comment_matches = []
        pos = 0
        while True:
            # Find regular comment
            pos = content.find("//", pos)
            if pos == -1 or pos + 2 >= len(content):
                break

            # Skip if this is a doc comment
            if content[pos+2:pos+3] == "!" or content[pos+2:pos+3] == "/":
                pos += 1
                continue

            # Find end of line
            eol = content.find("\n", pos)
            if eol == -1:
                eol = len(content)

            # Add to matches
            comment_matches.append((pos, eol, "comment"))
            pos = eol

        # Find and highlight inner doc comments
        pos = 0
        while True:
            # Find inner doc comment
            pos = content.find("//!", pos)
            if pos == -1:
                break

            # Find end of line
            eol = content.find("\n", pos)
            if eol == -1:
                eol = len(content)

            # Add to matches
            comment_matches.append((pos, eol, "inner_doc_comment"))
            pos = eol

        # Find and highlight outer doc comments
        pos = 0
        while True:
            # Find outer doc comment
            pos = content.find("///", pos)
            if pos == -1:
                break

            # Skip if this is not a doc comment (e.g., "////")
            if pos + 3 < len(content) and content[pos+3] == "/":
                pos += 1
                continue

            # Find end of line
            eol = content.find("\n", pos)
            if eol == -1:
                eol = len(content)

            # Add to matches
            comment_matches.append((pos, eol, "outer_doc_comment"))
            pos = eol

        # Apply comment highlighting
        cursor = self.editor.textCursor()
        for start, end, format_name in comment_matches:
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)
            cursor.setCharFormat(self.formats[format_name])
            cursor.clearSelection()

        self.debug(f"Highlighted {len(comment_matches)} comments")

    def highlight_key_value_pair(self, key, node):
        """Highlight a key-value pair and its value"""
        if not isinstance(node, KeyValueNode):
            self.debug(f"Not a KeyValueNode: {key}")
            return

        content = self.editor.toPlainText()
        cursor = self.editor.textCursor()

        # First, locate the key in the document
        # We need to be careful to find the right occurrence of the key
        key_regex = f"\\b{re.escape(key)}\\s*="
        pos = content.find(key)

        # Make sure we found the key
        if pos == -1:
            self.debug(f"Could not find key '{key}' in document")
            return

        # Highlight the key
        cursor.setPosition(pos)
        cursor.setPosition(pos + len(key), QTextCursor.KeepAnchor)
        cursor.setCharFormat(self.formats["key"])
        cursor.clearSelection()

        # Find the equals sign after the key
        equals_pos = content.find("=", pos + len(key))
        if equals_pos == -1:
            self.debug(f"Could not find equals sign after key '{key}'")
            return

        # Highlight the equals sign
        cursor.setPosition(equals_pos)
        cursor.setPosition(equals_pos + 1, QTextCursor.KeepAnchor)
        cursor.setCharFormat(self.formats["equals"])
        cursor.clearSelection()

        # Now highlight the value
        if node.value:
            self.debug(f"Highlighting value of type {type(node.value).__name__} for key '{key}'")
            value_pos = equals_pos + 1
            # Skip whitespace
            while value_pos < len(content) and content[value_pos].isspace():
                value_pos += 1

            self.highlight_value(node.value, value_pos)

    def highlight_value(self, node, pos):
        """Highlight a value node starting at the given position"""
        if not node:
            return

        content = self.editor.toPlainText()
        cursor = self.editor.textCursor()

        if isinstance(node, ScalarNode):
            self.debug(f"Highlighting scalar of type {type(node.value).__name__}")

            # Handle different scalar types
            if isinstance(node.value, str):
                # Find the string in quotes
                quote_pos = content.find('"', pos)
                if quote_pos == -1:
                    # Try single quotes
                    quote_pos = content.find("'", pos)
                    if quote_pos == -1:
                        self.debug("Could not find string quotes")
                        return

                # Find the end quote
                end_quote = self.find_matching_quote(content, quote_pos)
                if end_quote == -1:
                    self.debug("Could not find end quote for string")
                    return

                # Highlight the string
                cursor.setPosition(quote_pos)
                cursor.setPosition(end_quote + 1, QTextCursor.KeepAnchor)
                cursor.setCharFormat(self.formats["string"])
                cursor.clearSelection()
                self.debug(f"Highlighted string from {quote_pos} to {end_quote}")

            elif isinstance(node.value, bool):
                # Find the boolean
                value_str = str(node.value).lower()
                bool_pos = content.find(value_str, pos)
                if bool_pos == -1:
                    self.debug(f"Could not find boolean '{value_str}'")
                    return

                # Highlight the boolean
                cursor.setPosition(bool_pos)
                cursor.setPosition(bool_pos + len(value_str), QTextCursor.KeepAnchor)
                cursor.setCharFormat(self.formats["boolean"])
                cursor.clearSelection()
                self.debug(f"Highlighted boolean '{value_str}' at {bool_pos}")
                
            elif isinstance(node.value, (int, float)):
                # Find the number
                value_str = str(node.value)
                num_pos = content.find(value_str, pos)
                if num_pos == -1:
                    self.debug(f"Could not find number '{value_str}'")
                    return

                # Highlight the number
                cursor.setPosition(num_pos)
                cursor.setPosition(num_pos + len(value_str), QTextCursor.KeepAnchor)
                cursor.setCharFormat(self.formats["number"])
                cursor.clearSelection()
                self.debug(f"Highlighted number '{value_str}' at {num_pos}")


            elif node.value is None:
                # Find "null"
                null_pos = content.find("null", pos)
                if null_pos == -1:
                    self.debug("Could not find 'null'")
                    return

                # Highlight null
                cursor.setPosition(null_pos)
                cursor.setPosition(null_pos + 4, QTextCursor.KeepAnchor)
                cursor.setCharFormat(self.formats["null"])
                cursor.clearSelection()
                self.debug(f"Highlighted null at {null_pos}")

        elif isinstance(node, ObjectNode):
            self.debug("Highlighting object node")

            # Find opening brace
            brace_pos = content.find("{", pos)
            if brace_pos == -1:
                self.debug("Could not find opening brace '{'")
                return

            # Highlight opening brace
            cursor.setPosition(brace_pos)
            cursor.setPosition(brace_pos + 1, QTextCursor.KeepAnchor)
            cursor.setCharFormat(self.formats["symbol"])
            cursor.clearSelection()

            # Recursively highlight object items
            if hasattr(node, "items"):
                item_pos = brace_pos + 1
                for key, item in node.items.items():
                    # Find key
                    key_pos = content.find(key, item_pos)
                    if key_pos == -1:
                        self.debug(f"Could not find object key '{key}'")
                        continue

                    # Highlight key-value pair
                    self.highlight_key_value_pair_at_pos(key, item, key_pos)
                    item_pos = key_pos + len(key)

            # Find and highlight closing brace
            # This is simplified and might not work for nested objects
            closing_pos = self.find_matching_brace(content, brace_pos)
            if closing_pos != -1:
                cursor.setPosition(closing_pos)
                cursor.setPosition(closing_pos + 1, QTextCursor.KeepAnchor)
                cursor.setCharFormat(self.formats["symbol"])
                cursor.clearSelection()

        elif isinstance(node, ListNode):
            self.debug("Highlighting list node")

            # Find opening bracket
            bracket_pos = content.find("[", pos)
            if bracket_pos == -1:
                self.debug("Could not find opening bracket '['")
                return

            # Highlight opening bracket
            cursor.setPosition(bracket_pos)
            cursor.setPosition(bracket_pos + 1, QTextCursor.KeepAnchor)
            cursor.setCharFormat(self.formats["symbol"])
            cursor.clearSelection()

            # Recursively highlight list elements
            if hasattr(node, "elements"):
                elem_pos = bracket_pos + 1
                for elem in node.elements:
                    # Skip whitespace
                    while elem_pos < len(content) and content[elem_pos].isspace():
                        elem_pos += 1

                    # Highlight element
                    self.debug(f"Highlighting list element of type {type(elem).__name__}")
                    self.highlight_value(elem, elem_pos)

                    # Find next comma or closing bracket
                    comma_pos = content.find(",", elem_pos)
                    bracket_pos = content.find("]", elem_pos)

                    if comma_pos != -1 and (bracket_pos == -1 or comma_pos < bracket_pos):
                        # Highlight comma
                        cursor.setPosition(comma_pos)
                        cursor.setPosition(comma_pos + 1, QTextCursor.KeepAnchor)
                        cursor.setCharFormat(self.formats["symbol"])
                        cursor.clearSelection()
                        elem_pos = comma_pos + 1
                    else:
                        break

            # Find and highlight closing bracket
            closing_pos = self.find_matching_bracket(content, bracket_pos)
            if closing_pos != -1:
                cursor.setPosition(closing_pos)
                cursor.setPosition(closing_pos + 1, QTextCursor.KeepAnchor)
                cursor.setCharFormat(self.formats["symbol"])
                cursor.clearSelection()

    def highlight_key_value_pair_at_pos(self, key, node, pos):
        """Highlight a key-value pair at a specific position"""
        if not isinstance(node, KeyValueNode):
            return

        content = self.editor.toPlainText()
        cursor = self.editor.textCursor()

        # Highlight the key
        cursor.setPosition(pos)
        cursor.setPosition(pos + len(key), QTextCursor.KeepAnchor)
        cursor.setCharFormat(self.formats["key"])
        cursor.clearSelection()

        # Find the equals sign after the key
        equals_pos = content.find("=", pos + len(key))
        if equals_pos == -1:
            return

        # Highlight the equals sign
        cursor.setPosition(equals_pos)
        cursor.setPosition(equals_pos + 1, QTextCursor.KeepAnchor)
        cursor.setCharFormat(self.formats["equals"])
        cursor.clearSelection()

        # Now highlight the value
        if node.value:
            value_pos = equals_pos + 1
            # Skip whitespace
            while value_pos < len(content) and content[value_pos].isspace():
                value_pos += 1

            self.highlight_value(node.value, value_pos)

    def find_matching_quote(self, text, pos):
        """Find the matching quote for a string"""
        if pos >= len(text):
            return -1

        quote_char = text[pos]
        if quote_char not in ('"', "'"):
            return -1

        # Find the next unescaped quote
        i = pos + 1
        while i < len(text):
            if text[i] == quote_char and text[i-1] != '\\':
                return i
            i += 1

        return -1

    def find_matching_brace(self, text, pos):
        """Find the matching closing brace for an object"""
        if pos >= len(text) or text[pos] != '{':
            return -1

        depth = 1
        i = pos + 1
        while i < len(text):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    return i
            i += 1

        return -1

    def find_matching_bracket(self, text, pos):
        """Find the matching closing bracket for a list"""
        if pos >= len(text) or text[pos] != '[':
            return -1

        depth = 1
        i = pos + 1
        while i < len(text):
            if text[i] == '[':
                depth += 1
            elif text[i] == ']':
                depth -= 1
                if depth == 0:
                    return i
            i += 1

        return -1

class ASTHighlighterDebugWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FTML AST Highlighter Debugger")
        self.resize(1200, 800)
        self.setup_ui()

        # Create our debug highlighter
        self.highlighter = DebugFTMLASTHighlighter(self.editor, self.debug_output)

        # Sample FTML content
        self.editor.setPlainText("""//! This is a documentation comment
// This is a regular comment
/// This is an outer doc comment
name = "My FTML Document"
version = 1.0
is_active = true
null_value = null

// An object example
config = {
    server = "localhost",
    port = 8080,
    debug = true,
    options = {
        timeout = 30,
        retry = false
    }
}

// A list example
tags = [
    "syntax",
    "highlighting",
    "ast",
    42,
    null,
    true
]
""")

    def setup_ui(self):
        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout with splitter
        main_layout = QVBoxLayout(central_widget)

        # Header
        header_label = QLabel("FTML AST Highlighter Debugger")
        header_label.setAlignment(Qt.AlignCenter)
        font = header_label.font()
        font.setPointSize(14)
        font.setBold(True)
        header_label.setFont(font)
        main_layout.addWidget(header_label)

        # Splitter for editor and debug output
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)

        editor_label = QLabel("FTML Code")
        editor_label.setAlignment(Qt.AlignCenter)
        editor_layout.addWidget(editor_label)

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Enter FTML code here...")
        font = QFont("Courier New", 10)
        font.setFixedPitch(True)
        self.editor.setFont(font)
        editor_layout.addWidget(self.editor)

        # Buttons for editor actions
        button_layout = QHBoxLayout()

        self.parse_button = QPushButton("Parse AST")
        self.parse_button.clicked.connect(self.parse_ast)
        button_layout.addWidget(self.parse_button)

        self.highlight_button = QPushButton("Highlight Document")
        self.highlight_button.clicked.connect(self.highlight_document)
        button_layout.addWidget(self.highlight_button)

        self.clear_button = QPushButton("Clear Debug Log")
        self.clear_button.clicked.connect(self.clear_debug_log)
        button_layout.addWidget(self.clear_button)

        editor_layout.addLayout(button_layout)

        # Right panel - Debug output
        debug_widget = QWidget()
        debug_layout = QVBoxLayout(debug_widget)

        debug_label = QLabel("Debug Output")
        debug_label.setAlignment(Qt.AlignCenter)
        debug_layout.addWidget(debug_label)

        self.debug_output = QTextEdit()
        self.debug_output.setReadOnly(True)
        self.debug_output.setFont(font)
        debug_layout.addWidget(self.debug_output)

        # AST structure view
        ast_label = QLabel("AST Structure")
        ast_label.setAlignment(Qt.AlignCenter)
        debug_layout.addWidget(ast_label)

        self.ast_view = QTextEdit()
        self.ast_view.setReadOnly(True)
        self.ast_view.setFont(font)
        debug_layout.addWidget(self.ast_view)

        # Add widgets to splitter
        splitter.addWidget(editor_widget)
        splitter.addWidget(debug_widget)
        splitter.setSizes([600, 600])

        # Set up logging
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # Clear all existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Add our custom handler
        handler = QTextEditLogger(self.debug_output)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        # Logger for our debug messages
        self.logger = logging.getLogger("debug_highlighter")

    def parse_ast(self):
        """Parse the AST and display its structure"""
        self.debug_output.clear()
        self.ast_view.clear()

        self.logger.info("Parsing AST...")
        self.highlighter.parse_document()

        # Display AST structure if available
        if self.highlighter.ast:
            try:
                # Try to import from ftml module
                try:
                    from ftml.parser.ast_visualizer import visualize_ast
                    ast_text = "\n".join(visualize_ast(self.highlighter.ast))
                    self.ast_view.setPlainText(ast_text)
                except ImportError:
                    # Fallback to basic representation
                    from pprint import pformat
                    self.ast_view.setPlainText(f"AST Structure:\n{pformat(vars(self.highlighter.ast))}")
            except Exception as e:
                self.logger.error(f"Error displaying AST: {str(e)}")
                self.ast_view.setPlainText(f"Error displaying AST: {str(e)}")
        else:
            self.ast_view.setPlainText("No AST available - parsing failed")

    def highlight_document(self):
        """Highlight the document based on AST"""
        self.logger.info("Highlighting document...")

        # Make sure we have a parsed AST
        if not self.highlighter.ast:
            self.logger.info("No AST available, parsing first...")
            self.highlighter.parse_document()

        # Apply highlighting
        self.highlighter.highlight_document()
        self.logger.info("Highlighting complete")

    def clear_debug_log(self):
        """Clear the debug log"""
        self.debug_output.clear()
        self.logger.info("Debug log cleared")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ASTHighlighterDebugWindow()
    window.show()
    sys.exit(app.exec())