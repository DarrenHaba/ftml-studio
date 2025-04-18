# src/ftml_studio/ui/elements/editor.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QApplication, QSplitter,
                               QTextEdit)
from PySide6.QtCore import Qt, QSettings, QTimer
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
import ftml
from ftml.exceptions import FTMLParseError

from src.ftml_studio.components.enhanced_text_edit import EnhancedTextEdit
from src.ftml_studio.ui.themes import theme_manager
from src.ftml_studio.syntax import FTMLASTHighlighter
from src.ftml_studio.logger import setup_logger

# Configure logging
logger = setup_logger("ftml_studio.editor_window")


class FTMLEditorWidget(QWidget):
    """Widget for the FTML AST Highlighter with theme support"""

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("Initializing FTML AST Demo")

        # Settings for preferences
        self.settings = QSettings("FTMLStudio", "ASTHighlighterDemo")

        # Get the global error indicator setting
        app_settings = QSettings("FTMLStudio", "AppSettings")
        self.error_highlighting_enabled = app_settings.value("editor/showErrorIndicators", True, type=bool)

        self.setup_ui()

        logger.debug("UI setup complete")

    def setup_ui(self):
        logger.debug("Setting up UI components")
        # Main layout - directly applied to this widget
        main_layout = QVBoxLayout(self)

        # Description
        desc_label = QLabel("Edit FTML content below to see syntax highlighting based on the AST.")
        main_layout.addWidget(desc_label)

        # Create a splitter for the editor and output
        splitter = QSplitter(Qt.Vertical)

        # Editor - using our enhanced text edit
        self.editor = EnhancedTextEdit()
        self.editor.setObjectName("codeEditor")  # For stylesheet targeting
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

        # Apply highlighter with theme support and error highlighting based on global setting
        self.highlighter = FTMLASTHighlighter(
            self.editor.document(),
            theme_manager,
            error_highlighting=self.error_highlighting_enabled,
            parse_delay=500
        )

        # Connect the editor with the highlighter
        self.editor.setHighlighter(self.highlighter)

        # Connect highlighter errors signal to update error display
        self.highlighter.errorsChanged.connect(self.update_error_display)

        logger.debug(f"Applied FTMLASTHighlighter with theme support and error highlighting={self.error_highlighting_enabled}")

        # Parse status
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")  # For stylesheet targeting

        # Parse button
        parse_btn = QPushButton("Parse FTML")
        parse_btn.clicked.connect(self.parse_ftml)

        # Debug buttons
        debug_btn = QPushButton("Debug Highlight")
        debug_btn.clicked.connect(self.debug_highlight)

        test_btn = QPushButton("Test Direct Highlight")
        test_btn.clicked.connect(self.test_direct_highlight)

        # Output area
        self.output = EnhancedTextEdit()  # Also using EnhancedTextEdit for output
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
        self.editor.textChanged.connect(self.on_text_changed)
        logger.debug("Connected textChanged signal to update handler")

        # Initial status update
        self.update_status()

    def recreate_highlighter(self):
        """Recreate the highlighter to apply new theme colors"""
        # Store cursor position
        cursor_pos = self.editor.textCursor().position()

        # Get the current app settings for error highlighting
        app_settings = QSettings("FTMLStudio", "AppSettings")
        self.error_highlighting_enabled = app_settings.value("editor/showErrorIndicators", True, type=bool)

        # Delete and recreate highlighter
        if hasattr(self, 'highlighter'):
            # Disconnect old signals if any
            if hasattr(self.highlighter, 'errorsChanged'):
                self.highlighter.errorsChanged.disconnect()

            # Get current parse_delay setting
            parse_delay = getattr(self.highlighter, 'parse_delay', 500)

            del self.highlighter

        # Create new highlighter with current theme and settings
        self.highlighter = FTMLASTHighlighter(
            self.editor.document(),
            theme_manager,
            error_highlighting=self.error_highlighting_enabled,
            parse_delay=parse_delay
        )

        # Connect editor with new highlighter
        self.editor.setHighlighter(self.highlighter)

        # Reconnect signals
        self.highlighter.errorsChanged.connect(self.update_error_display)

        # Restore cursor position
        cursor = self.editor.textCursor()
        cursor.setPosition(cursor_pos)
        self.editor.setTextCursor(cursor)

        logger.debug(f"Recreated highlighter with error_highlighting={self.error_highlighting_enabled}")

    def on_text_changed(self):
        """Handle text changes"""
        # Update status immediately
        self.update_status()

    def update_error_display(self, errors):
        """Update the error display based on errors from the highlighter"""
        logger.debug(f"Updating error display with {len(errors)} errors")

        # Get current application setting for error highlighting
        app_settings = QSettings("FTMLStudio", "AppSettings")
        self.error_highlighting_enabled = app_settings.value("editor/showErrorIndicators", True, type=bool)

        # Apply error highlights if showing errors is enabled
        if self.error_highlighting_enabled and hasattr(self.highlighter, 'error_highlighting') and self.highlighter.error_highlighting:
            # Store errors in the editor for tooltip display
            self.editor.error_positions = []

            for error in errors:
                line = error.get('line', 0)
                col = error.get('col', 0)
                message = error.get('message', '')

                # Create cursor to get character position
                cursor = QTextCursor(self.editor.document())
                cursor.movePosition(QTextCursor.Start)

                # Move to correct line
                for _ in range(line - 1):
                    cursor.movePosition(QTextCursor.NextBlock)

                # Move to correct column
                for _ in range(col - 1):
                    cursor.movePosition(QTextCursor.Right)

                # Add error position and message for tooltip display
                self.editor.error_positions.append({
                    'position': cursor.position(),
                    'message': message
                })

            logger.debug(f"Stored {len(self.editor.error_positions)} error positions for tooltips")

            # Apply error highlights
            self.apply_error_highlights()
        else:
            self.clear_error_highlights()

        # Update status label to show error if present
        if errors:
            error_message = errors[0].get('message', 'Error detected')
            self.status_label.setText(f"✗ {error_message}")
            self.status_label.setStyleSheet("color: red;")
        else:
            # Check if we had a successful parse
            if hasattr(self.highlighter, 'ast') and self.highlighter.ast is not None:
                self.status_label.setText("✓ Valid FTML")
                self.status_label.setStyleSheet("color: green;")
            else:
                self.status_label.setText("Document parsed")
                self.status_label.setStyleSheet("color: gray;")

    def update_error_highlighting(self, enabled):
        """Update the error highlighting based on the provided enabled state"""
        logger.debug(f"Updating error highlighting to: {enabled}")

        # Update highlighter settings
        if hasattr(self, 'highlighter'):
            self.highlighter.error_highlighting = enabled

            # Force rehighlight to apply/remove error indicators
            self.highlighter.rehighlight()

            # Store the setting
            self.error_highlighting_enabled = enabled

            # Update error display
            if enabled and hasattr(self.highlighter, 'errors'):
                self.update_error_display(self.highlighter.errors)
            else:
                self.clear_error_highlights()

    def clear_error_highlights(self):
        """Clear all error highlights"""
        self.editor.setExtraSelections([])
        self.editor.error_positions = []

    def apply_error_highlights(self):
        """Apply all error highlights from the highlighter's errors list"""
        # Check if error highlighting is enabled
        if not self.error_highlighting_enabled or not hasattr(self.highlighter, 'errors'):
            self.clear_error_highlights()
            return

        # Get errors from highlighter
        errors = self.highlighter.errors

        # Create a list for all error selections
        selections = []
        error_positions = []

        for error in errors:
            line = error.get('line', 0)
            col = error.get('col', 0)
            message = error.get('message', '')

            try:
                # Create a cursor at the error position
                cursor = QTextCursor(self.editor.document())
                cursor.movePosition(QTextCursor.Start)

                # Move to the correct line
                for i in range(line - 1):
                    if not cursor.movePosition(QTextCursor.NextBlock):
                        logger.warning(f"Could not move to line {line}, stopped at line {i+1}")
                        break

                # Check if we reached the target line
                if cursor.blockNumber() != line - 1:
                    logger.warning(f"Failed to reach line {line}, ended at line {cursor.blockNumber() + 1}")
                    continue

                # Move to the column
                if col > 1:
                    for i in range(col - 1):
                        if not cursor.movePosition(QTextCursor.Right):
                            logger.warning(f"Could not move to column {col}, stopped at column {i+1}")
                            break

                # Store the cursor position for the error
                error_pos = cursor.position()

                # Store position info for tooltips
                error_positions.append({
                    'position': error_pos,
                    'message': message
                })

                # Create error format using theme colors
                error_format = QTextCharFormat()

                # Use theme error color
                error_color = QColor(theme_manager.get_syntax_color("error"))

                # Very light background so it doesn't interfere with syntax highlighting
                bg_color = QColor(error_color)
                bg_color.setAlpha(20)  # Very transparent
                error_format.setBackground(bg_color)

                # Set wave underline
                error_format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
                error_format.setUnderlineColor(error_color)

                # Create an extra selection
                selection = QTextEdit.ExtraSelection()
                selection.format = error_format
                selection.cursor = cursor

                # Try to find the specific error token if it's provided
                if "token" in error:
                    # Look for this token in the text
                    error_token = error["token"]
                    token_pos = cursor.block().text().find(error_token, col - 1)
                    if token_pos >= 0:
                        # Move to token position
                        cursor.setPosition(cursor.block().position() + token_pos)
                        # Select the token
                        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(error_token))
                        selection.cursor = cursor
                    else:
                        # Just select one character at the error position
                        selection.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 1)
                else:
                    # Select just the character at the error position
                    selection.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 1)

                selections.append(selection)

            except Exception as e:
                logger.error(f"Error in apply_error_highlights: {str(e)}", exc_info=True)

        # Apply all selections
        self.editor.error_positions = error_positions
        self.editor.setExtraSelections(selections)

        # Force update
        self.editor.update()

    def debug_highlight(self):
        """Test function to highlight a specific position"""
        logger.debug("Debug highlight button clicked")

        # Add a test error to the highlighter
        if hasattr(self.highlighter, 'errors'):
            self.highlighter.errors = [{'line': 3, 'col': 5, 'message': "This is a test error highlight"}]

            # Emit the signal to update UI
            if hasattr(self.highlighter, 'errorsChanged'):
                self.highlighter.errorsChanged.emit(self.highlighter.errors)

            # Force rehighlight
            self.highlighter.rehighlight()

        self.output.setPlainText("Highlighted test error at line 3, column 5")

    def test_direct_highlight(self):
        """Test wave underline highlighting directly"""
        logger.debug("Testing direct wave underline highlight")

        cursor = QTextCursor(self.editor.document())
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, 3)  # Move to line 4
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, 5)  # Move to column 6

        # Create a format with wave underline using theme colors
        fmt = QTextCharFormat()

        error_color = QColor(theme_manager.get_syntax_color("error"))

        fmt.setUnderlineStyle(QTextCharFormat.WaveUnderline)
        fmt.setUnderlineColor(error_color)

        # Very light background
        bg_color = QColor(error_color)
        bg_color.setAlpha(20)  # Very transparent
        fmt.setBackground(bg_color)

        # Create selection
        selection = QTextEdit.ExtraSelection()
        selection.format = fmt
        selection.cursor = cursor
        selection.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 1)  # Select just one char

        # Apply selection
        logger.debug("Applying direct test wave underline")
        self.editor.setExtraSelections([selection])

        # Store error info for tooltip
        self.editor.error_positions = [{
            'position': cursor.position(),
            'message': "Direct test wave underline"
        }]

        # Log the result
        logger.debug(f"Selection applied. Length of extraSelections: {len(self.editor.extraSelections())}")
        self.output.setPlainText("Applied direct test wave underline at line 4, column 6")

    def update_status(self):
        """Update the parse status based on highlighter state"""
        content = self.editor.toPlainText()

        if not content:
            self.status_label.setText("Empty document")
            self.status_label.setStyleSheet("color: gray;")
            return

        # Let the highlighter handle the parsing
        # We'll update the status when we receive the errorsChanged signal

    def parse_ftml(self):
        """Parse the FTML and show the result"""
        logger.debug("Parse button clicked")
        content = self.editor.toPlainText()
        if not content:
            self.output.setPlainText("No content to parse")
            return

        try:
            # Parse the FTML
            logger.debug("Parsing FTML for output")
            data = ftml.load(content)
            logger.debug("FTML parsed successfully for output")

            # Format and display the output
            import json
            formatted = json.dumps(data, indent=2)
            self.output.setPlainText(formatted)

            # Set success status
            self.status_label.setText("✓ Valid FTML")
            self.status_label.setStyleSheet("color: green;")

        except FTMLParseError as e:
            error_message = str(e)
            logger.debug(f"FTML parse error in parse_ftml: {error_message}")
            self.output.setPlainText(f"Error parsing FTML:\n{error_message}")

            # Set error status
            self.status_label.setText(f"✗ Parse error: {error_message}")
            self.status_label.setStyleSheet("color: red;")

        except Exception as e:
            logger.debug(f"Other error in parse_ftml: {str(e)}")
            self.output.setPlainText(f"Error parsing FTML:\n{str(e)}")

            # Set error status
            self.status_label.setText(f"✗ Error: {str(e)}")
            self.status_label.setStyleSheet("color: red;")