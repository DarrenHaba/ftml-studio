# src/ftml_studio/ui/ftml_ast_demo.py
import re
import sys
import logging
from PySide6.QtWidgets import (QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout,
                               QPushButton, QWidget, QLabel, QApplication, QSplitter, QToolTip)
from PySide6.QtCore import Qt, QSettings, QTimer
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QBrush

import ftml
from ftml.exceptions import FTMLParseError

# Configure logging - set to DEBUG level
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ftml_ast_demo")

# Import highlighter
try:
    from src.ftml_studio.syntax import FTMLASTHighlighter
except ImportError:
    # Try relative import as fallback
    try:
        import sys
        sys.path.insert(0, '..')
        from syntax.ast_highlighter import FTMLASTHighlighter
    except ImportError:
        logger.error("Failed to import FTMLASTHighlighter!")
        # Fallback to dummy class if import fails
        class FTMLASTHighlighter:
            def __init__(self, *args, **kwargs):
                pass

class EnhancedTextEdit(QTextEdit):
    """Enhanced QTextEdit with improved tooltip support for error indicators"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.error_position = -1
        self.error_message = ""
        self.error_selections = []

    def mouseMoveEvent(self, event):
        """Handle mouse movement to show tooltips over error positions"""
        super().mouseMoveEvent(event)

        if self.error_position >= 0:
            cursor = self.cursorForPosition(event.pos())
            pos = cursor.position()

            # logger.debug(f"Mouse position: {pos}, Error position: {self.error_position}")

            # Check if cursor is near the error position
            if self.error_position <= pos < self.error_position + 5:
                logger.debug(f"Showing tooltip: {self.error_message}")
                QToolTip.showText(event.globalPos(), self.error_message)
                return
            else:
                # Hide tooltip if not over an error
                QToolTip.hideText()

    def setExtraSelections(self, selections):
        """Override to log extra selections being applied"""
        logger.debug(f"Setting {len(selections)} extra selections")
        self.error_selections = selections
        super().setExtraSelections(selections)

class FTMLASTDemo(QMainWindow):
    """Simple demo window for the FTML AST Highlighter"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FTML AST Highlighter Demo")
        self.resize(800, 600)
        logger.debug("Initializing FTML AST Demo")
        self.setup_ui()
        logger.debug("UI setup complete")

    def setup_ui(self):
        logger.debug("Setting up UI components")
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header
        header_label = QLabel("FTML AST Highlighter Demo")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(header_label)

        # Description
        desc_label = QLabel("Edit FTML content below to see syntax highlighting based on the AST.")
        main_layout.addWidget(desc_label)

        # Create a splitter for the editor and output
        splitter = QSplitter(Qt.Vertical)

        # Editor - using our enhanced text edit
        self.editor = EnhancedTextEdit()
        self.editor.setPlaceholderText("Enter FTML here...")
        font = QFont("Courier New", 10)
        font.setFixedPitch(True)
        self.editor.setFont(font)
        logger.debug("Created EnhancedTextEdit")

        # Sample content
        self.editor.setPlainText("""//! This is a documentation comment
// This is a regular comment
name = "My FTML Document"
version = 1.0

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

        # Apply highlighter
        self.highlighter = FTMLASTHighlighter(self.editor.document(), None)
        logger.debug("Applied FTMLASTHighlighter")

        # Parse status
        self.status_label = QLabel()
        self.update_status()

        # Parse button
        parse_btn = QPushButton("Parse FTML")
        parse_btn.clicked.connect(self.parse_ftml)

        # TEST BUTTON FOR DEBUGGING
        debug_btn = QPushButton("Debug Highlight")
        debug_btn.clicked.connect(self.debug_highlight)

        # Test with no highlighter button
        test_btn = QPushButton("Test Direct Highlight")
        test_btn.clicked.connect(self.test_direct_highlight)

        # Output area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(font)

        # Add widgets to splitter
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.addWidget(self.editor)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(parse_btn)
        buttons_layout.addWidget(debug_btn)
        buttons_layout.addWidget(test_btn)
        buttons_layout.addWidget(self.status_label)
        buttons_layout.addStretch()

        editor_layout.addLayout(buttons_layout)

        output_container = QWidget()
        output_layout = QVBoxLayout(output_container)
        output_layout.addWidget(QLabel("Parsed Output:"))
        output_layout.addWidget(self.output)

        splitter.addWidget(editor_container)
        splitter.addWidget(output_container)
        splitter.setSizes([400, 200])

        main_layout.addWidget(splitter)

        # Connect editor changes to status updates
        self.editor.textChanged.connect(self.update_status)
        logger.debug("Connected textChanged signal to update_status")

    def debug_highlight(self):
        """Test function to highlight a specific position"""
        logger.debug("Debug highlight button clicked")

        # Force highlight at line 3, column 5
        self.highlight_error_position(3, 5, "This is a test error highlight")
        self.output.setPlainText("Highlighted test error at line 3, column 5")

    def test_direct_highlight(self):
        """Test direct highlighting without using our custom method"""
        logger.debug("Testing direct highlight")

        cursor = QTextCursor(self.editor.document())
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, 3)  # Move to line 4
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, 5)  # Move to column 6

        # Create a format
        fmt = QTextCharFormat()
        fmt.setBackground(QColor(255, 0, 0, 100))  # Semi-transparent red
        fmt.setForeground(QColor(255, 255, 255))   # White text

        # Create selection
        selection = QTextEdit.ExtraSelection()
        selection.format = fmt
        selection.cursor = cursor
        selection.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 5)  # Select 5 chars

        # Apply selection
        logger.debug("Applying direct test selection")
        self.editor.setExtraSelections([selection])

        # Store error info for tooltip
        self.editor.error_position = cursor.position()
        self.editor.error_message = "Direct test highlight"

        # Log the result
        logger.debug(f"Selection applied. Length of extraSelections: {len(self.editor.error_selections)}")
        self.output.setPlainText("Applied direct test highlight at line 4, column 6")

    def highlight_error_position(self, line, col, message):
        """Highlight the error position in the editor with a red indicator"""
        logger.debug(f"Highlighting error at line {line}, col {col}: {message}")

        try:
            # Create a cursor at the error position
            cursor = QTextCursor(self.editor.document())
            cursor.movePosition(QTextCursor.Start)
            for i in range(line - 1):
                if not cursor.movePosition(QTextCursor.NextBlock):
                    logger.warning(f"Could not move to line {line}, stopped at line {i+1}")
                    break

            # Log the document structure for debugging
            doc = self.editor.document()
            logger.debug(f"Document has {doc.blockCount()} blocks (lines)")

            # Check if we reached the target line
            if cursor.blockNumber() != line - 1:
                logger.warning(f"Failed to reach line {line}, ended at line {cursor.blockNumber() + 1}")
                return

            # Move to the column
            if col > 1:
                for i in range(col - 1):
                    if not cursor.movePosition(QTextCursor.Right):
                        logger.warning(f"Could not move to column {col}, stopped at column {i+1}")
                        break

            # Store the cursor position for the error
            error_pos = cursor.position()
            logger.debug(f"Error position is at cursor position {error_pos}")
            self.editor.error_position = error_pos
            self.editor.error_message = message

            # Create a very visible format for the error
            error_format = QTextCharFormat()
            error_format.setBackground(QColor(255, 0, 0, 150))  # Red background with alpha
            error_format.setForeground(QColor(255, 255, 255))   # White text
            error_format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
            error_format.setUnderlineColor(QColor("red"))

            # Create an extra selection
            selection = QTextEdit.ExtraSelection()
            selection.format = error_format
            selection.cursor = cursor
            # Select the character at the error position and some after it for visibility
            selection.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 3)

            # Apply the selection
            logger.debug("Setting extra selection for error")
            self.editor.setExtraSelections([selection])

            # Move cursor near the error position and make it visible
            self.editor.setTextCursor(cursor)
            self.editor.ensureCursorVisible()

            # Force update
            logger.debug("Forcing update of the editor")
            self.editor.update()

            # Log result
            logger.debug(f"Error highlighting complete. Selection length: {len(self.editor.error_selections)}")

        except Exception as e:
            logger.error(f"Error in highlight_error_position: {str(e)}", exc_info=True)

    def update_status(self):
        """Update the parse status and highlight any errors"""
        logger.debug("Updating status")
        content = self.editor.toPlainText()
    
        # Clear any previous error highlighting
        logger.debug("Clearing previous error highlighting")
        self.editor.setExtraSelections([])
        self.editor.error_position = -1
        self.editor.error_message = ""
    
        if not content:
            self.status_label.setText("Empty document")
            self.status_label.setStyleSheet("color: gray;")
            return
    
        try:
            # Try to parse
            logger.debug("Attempting to parse FTML")
            data = ftml.load(content)
            logger.debug("FTML parsed successfully")
            self.status_label.setText("✓ Valid FTML")
            self.status_label.setStyleSheet("color: green;")
        except FTMLParseError as e:
            error_message = str(e)
            logger.debug(f"FTML parse error: {error_message}")
            self.status_label.setText(f"✗ Parse error: {error_message}")
            self.status_label.setStyleSheet("color: red;")
    
            # Extract line and column from error message using regex
            position_match = re.search(r'at line (\d+), col (\d+)', error_message)
            if position_match:
                line = int(position_match.group(1))
                col = int(position_match.group(2))
                logger.debug(f"Extracted position from error message: line {line}, col {col}")
                # Use a timer to ensure the highlighting happens after the current event processing
                QTimer.singleShot(0, lambda: self.highlight_error_position(line, col, error_message))
            elif hasattr(e, "line") and hasattr(e, "col"):
                logger.debug(f"Error has position info: line {e.line}, col {e.col}")
                QTimer.singleShot(0, lambda: self.highlight_error_position(e.line, e.col, error_message))
            else:
                logger.debug("Error has no position info and couldn't extract from message")
        except Exception as e:
            logger.debug(f"Other error: {str(e)}")
            self.status_label.setText(f"✗ Error: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

    def parse_ftml(self):
        """Parse the FTML and show the result"""
        logger.debug("Parse button clicked")
        content = self.editor.toPlainText()
        if not content:
            self.output.setPlainText("No content to parse")
            return
    
        # Clear any previous error highlighting
        logger.debug("Clearing previous error highlighting")
        self.editor.setExtraSelections([])
        self.editor.error_position = -1
        self.editor.error_message = ""
    
        try:
            # Parse the FTML
            logger.debug("Parsing FTML for output")
            data = ftml.load(content)
            logger.debug("FTML parsed successfully for output")
    
            # Format and display the output
            import json
            formatted = json.dumps(data, indent=2)
            self.output.setPlainText(formatted)
    
        except FTMLParseError as e:
            error_message = str(e)
            logger.debug(f"FTML parse error in parse_ftml: {error_message}")
            self.output.setPlainText(f"Error parsing FTML:\n{error_message}")
    
            # Extract line and column from error message using regex
            position_match = re.search(r'at line (\d+), col (\d+)', error_message)
            if position_match:
                line = int(position_match.group(1))
                col = int(position_match.group(2))
                logger.debug(f"Extracted position from error message: line {line}, col {col}")
                self.highlight_error_position(line, col, error_message)
            elif hasattr(e, "line") and hasattr(e, "col"):
                logger.debug(f"Highlighting error from parse_ftml at line {e.line}, col {e.col}")
                self.highlight_error_position(e.line, e.col, error_message)
            else:
                logger.debug("Error has no position info in parse_ftml and couldn't extract from message")
        except Exception as e:
            logger.debug(f"Other error in parse_ftml: {str(e)}")
            self.output.setPlainText(f"Error parsing FTML:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FTMLASTDemo()
    window.show()
    sys.exit(app.exec())