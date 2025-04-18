# src/ftml_studio/ui/ftml_ast_demo.py
import sys
import logging
import re
from PySide6.QtWidgets import (QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout,
                               QPushButton, QWidget, QLabel, QApplication, QSplitter,
                               QToolTip, QCheckBox, QMenuBar, QMenu)
from PySide6.QtCore import Qt, QSettings, QTimer
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QBrush, QActionGroup, QAction

import ftml
from ftml.exceptions import FTMLParseError

# Configure logging - set to DEBUG level
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ftml_ast_demo")

# Import theme manager
try:
    from src.ftml_studio.ui.themes import theme_manager
except ImportError:
    # Try relative import as fallback
    try:
        import sys
        sys.path.insert(0, '..')
        from ui.themes import theme_manager
    except ImportError:
        logger.error("Failed to import theme_manager! Using default themes.")
        # Import a dummy theme manager if needed
        from src.ftml_studio.ui.themes.theme_manager import ThemeManager
        theme_manager = ThemeManager()

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
        # Store multiple errors instead of just one
        self.error_positions = []  # List of {position, message} dictionaries
        self.error_selections = []

    def mouseMoveEvent(self, event):
        """Handle mouse movement to show tooltips over error positions"""
        super().mouseMoveEvent(event)

        if not self.error_positions:
            return

        cursor = self.cursorForPosition(event.pos())
        pos = cursor.position()

        # Check if cursor is near any error position
        for error in self.error_positions:
            error_pos = error.get('position', -1)
            error_msg = error.get('message', '')

            # Check if cursor is near the error position (with a small range to make selection easier)
            if error_pos >= 0 and error_pos <= pos < error_pos + 5:
                QToolTip.showText(event.globalPos(), error_msg)
                return

        # Hide tooltip if not over an error
        QToolTip.hideText()

    def setExtraSelections(self, selections):
        """Override to log extra selections being applied"""
        logger.debug(f"Setting {len(selections)} extra selections")
        self.error_selections = selections
        super().setExtraSelections(selections)

class FTMLASTDemo(QMainWindow):
    """Simple demo window for the FTML AST Highlighter with theme support"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FTML AST Highlighter Demo")
        self.resize(800, 600)
        logger.debug("Initializing FTML AST Demo")

        # List to store multiple errors
        self.errors = []

        # Timer for delayed error highlighting
        self.error_highlight_timer = QTimer()
        self.error_highlight_timer.setSingleShot(True)
        self.error_highlight_timer.timeout.connect(self.delayed_error_highlight)

        # Settings for window state and preferences
        self.settings = QSettings("FTMLStudio", "ASTHighlighterDemo")

        self.setup_ui()

        # Apply theme based on settings
        self.apply_saved_theme()

        logger.debug("UI setup complete")

    def setup_ui(self):
        logger.debug("Setting up UI components")
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create menu bar with theme selection
        self.create_menu_bar()

        # Header
        header_label = QLabel("FTML AST Highlighter Demo")
        header_font = header_label.font()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        main_layout.addWidget(header_label)

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

        # Apply highlighter with theme support
        self.highlighter = FTMLASTHighlighter(self.editor.document(), theme_manager)
        logger.debug("Applied FTMLASTHighlighter with theme support")

        # Parse status
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")  # For stylesheet targeting

        # Add checkbox to enable/disable error indicators
        self.show_errors_checkbox = QCheckBox("Show Error Indicators")
        self.show_errors_checkbox.setChecked(True)
        self.show_errors_checkbox.stateChanged.connect(self.on_show_errors_changed)

        # Parse button
        parse_btn = QPushButton("Parse FTML")
        parse_btn.clicked.connect(self.parse_ftml)

        # Debug buttons
        debug_btn = QPushButton("Debug Highlight")
        debug_btn.clicked.connect(self.debug_highlight)

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
        buttons_layout.addWidget(self.show_errors_checkbox)
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

        # Connect editor changes to status updates, but delay error highlighting
        self.editor.textChanged.connect(self.on_text_changed)
        logger.debug("Connected textChanged signal to delayed update handler")

        # Initial status update
        self.update_status()

    def create_menu_bar(self):
        """Create menu bar with theme options"""
        menu_bar = self.menuBar()

        # Create View menu
        view_menu = menu_bar.addMenu("View")

        # Add theme submenu
        theme_menu = QMenu("Theme", self)
        view_menu.addMenu(theme_menu)

        # Create action group for themes (for mutual exclusion)
        theme_group = QActionGroup(self)

        # Add theme options
        light_action = QAction("Light", self, checkable=True)
        dark_action = QAction("Dark", self, checkable=True)
        auto_action = QAction("Auto (System)", self, checkable=True)

        # Add actions to group and menu
        theme_group.addAction(light_action)
        theme_group.addAction(dark_action)
        theme_group.addAction(auto_action)

        theme_menu.addAction(light_action)
        theme_menu.addAction(dark_action)
        theme_menu.addAction(auto_action)

        # Connect actions to theme change
        light_action.triggered.connect(lambda: self.change_theme("light"))
        dark_action.triggered.connect(lambda: self.change_theme("dark"))
        auto_action.triggered.connect(lambda: self.change_theme("auto"))

        # Set initial checked state based on current theme
        self.theme_actions = {
            "light": light_action,
            "dark": dark_action,
            "auto": auto_action
        }

    def apply_saved_theme(self):
        """Apply theme based on saved settings"""
        theme = self.settings.value("theme", "auto")
        if theme not in ["light", "dark", "auto"]:
            theme = "auto"  # Default to auto if invalid

        # Update theme manager
        theme_manager.apply_theme(QApplication.instance(), theme)

        # Update checked state in menu
        if theme in self.theme_actions:
            self.theme_actions[theme].setChecked(True)

        logger.debug(f"Applied saved theme: {theme}")

    def change_theme(self, theme):
        """Change the application theme"""
        if theme in ["light", "dark", "auto"]:
            # Save theme preference
            self.settings.setValue("theme", theme)

            # Apply theme
            theme_manager.apply_theme(QApplication.instance(), theme)

            # Update highlighter for new theme
            self.recreate_highlighter()

            logger.debug(f"Changed theme to {theme}")

    def recreate_highlighter(self):
        """Recreate the highlighter to apply new theme colors"""
        # Store cursor position
        cursor_pos = self.editor.textCursor().position()

        # Delete and recreate highlighter
        if hasattr(self, 'highlighter'):
            del self.highlighter

        # Create new highlighter with current theme
        self.highlighter = FTMLASTHighlighter(self.editor.document(), theme_manager)

        # Restore cursor position
        cursor = self.editor.textCursor()
        cursor.setPosition(cursor_pos)
        self.editor.setTextCursor(cursor)

        # Reapply error highlighting if needed
        if self.show_errors_checkbox.isChecked():
            self.apply_error_highlights()

    def on_text_changed(self):
        """Handle text changes with delayed error highlighting"""
        # Update status immediately
        self.update_status()

        # Reset and restart the error highlight timer
        self.error_highlight_timer.stop()
        self.error_highlight_timer.start(2000)  # 2 seconds delay

    def delayed_error_highlight(self):
        """Apply error highlighting after delay"""
        if self.show_errors_checkbox.isChecked():
            self.apply_error_highlights()

    def on_show_errors_changed(self, state):
        """Handle toggle of error indicators"""
        if state:
            # Re-apply error highlights if enabled
            self.apply_error_highlights()
        else:
            # Clear error highlights if disabled
            self.clear_error_highlights()

    def clear_error_highlights(self):
        """Clear all error highlights"""
        self.editor.setExtraSelections([])
        self.editor.error_positions = []

    def apply_error_highlights(self):
        """Apply all error highlights from the errors list"""
        # Skip if no errors or if showing errors is disabled
        if not self.errors or not self.show_errors_checkbox.isChecked():
            self.clear_error_highlights()
            return

        # Create a list for all error selections
        selections = []
        error_positions = []

        for error in self.errors:
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

                # Use theme error color if available
                if hasattr(theme_manager, 'get_syntax_color'):
                    error_color = QColor(theme_manager.get_syntax_color("error"))
                else:
                    error_color = QColor("#ff0000")  # Default red

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

                # Select just the character at the error position to avoid multiline issues
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

        # Add a test error to the list
        self.errors = [{'line': 3, 'col': 5, 'message': "This is a test error highlight"}]

        # Apply highlighting
        self.apply_error_highlights()

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

        if hasattr(theme_manager, 'get_syntax_color'):
            error_color = QColor(theme_manager.get_syntax_color("error"))
        else:
            error_color = QColor("#ff0000")  # Default red

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
        logger.debug(f"Selection applied. Length of extraSelections: {len(self.editor.error_selections)}")
        self.output.setPlainText("Applied direct test wave underline at line 4, column 6")

    def update_status(self):
        """Update the parse status and collect errors"""
        logger.debug("Updating status")
        content = self.editor.toPlainText()

        # Clear errors list
        self.errors = []

        if not content:
            self.status_label.setText("Empty document")
            self.status_label.setProperty("valid", None)
            self.status_label.setStyleSheet("color: gray;")
            return

        try:
            # Try to parse
            logger.debug("Attempting to parse FTML")
            data = ftml.load(content)
            logger.debug("FTML parsed successfully")

            # Use proper property for styling
            self.status_label.setText("✓ Valid FTML")
            self.status_label.setProperty("valid", True)
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)

            # Clear error highlights since document is valid
            self.clear_error_highlights()

        except FTMLParseError as e:
            error_message = str(e)
            logger.debug(f"FTML parse error: {error_message}")

            # Use proper property for styling
            self.status_label.setText(f"✗ Parse error: {error_message}")
            self.status_label.setProperty("valid", False)
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)

            # Extract line and column from error message using regex
            position_match = re.search(r'at line (\d+), col (\d+)', error_message)
            if position_match:
                line = int(position_match.group(1))
                col = int(position_match.group(2))
                logger.debug(f"Extracted position from error message: line {line}, col {col}")

                # Add to errors list instead of immediately highlighting
                self.errors.append({
                    'line': line,
                    'col': col,
                    'message': error_message
                })

            elif hasattr(e, "line") and hasattr(e, "col"):
                logger.debug(f"Error has position info: line {e.line}, col {e.col}")

                # Add to errors list
                self.errors.append({
                    'line': e.line,
                    'col': e.col,
                    'message': error_message
                })
            else:
                logger.debug("Error has no position info and couldn't extract from message")
        except Exception as e:
            logger.debug(f"Other error: {str(e)}")

            # Use proper property for styling
            self.status_label.setText(f"✗ Error: {str(e)}")
            self.status_label.setProperty("valid", False)
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)

    def parse_ftml(self):
        """Parse the FTML and show the result"""
        logger.debug("Parse button clicked")
        content = self.editor.toPlainText()
        if not content:
            self.output.setPlainText("No content to parse")
            return

        # Clear any previous error highlighting
        self.clear_error_highlights()
        self.errors = []

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

                # Add to errors list
                self.errors.append({
                    'line': line,
                    'col': col,
                    'message': error_message
                })

            elif hasattr(e, "line") and hasattr(e, "col"):
                logger.debug(f"Error has position info from parse_ftml: line {e.line}, col {e.col}")

                # Add to errors list
                self.errors.append({
                    'line': e.line,
                    'col': e.col,
                    'message': error_message
                })
            else:
                logger.debug("Error has no position info in parse_ftml and couldn't extract from message")
        except Exception as e:
            logger.debug(f"Other error in parse_ftml: {str(e)}")
            self.output.setPlainText(f"Error parsing FTML:\n{str(e)}")

        # Apply error highlights if show errors is enabled
        if self.show_errors_checkbox.isChecked():
            self.apply_error_highlights()

    def closeEvent(self, event):
        """Handle window close event - save settings"""
        # Save current settings
        if hasattr(theme_manager, 'current_theme'):
            self.settings.setValue("theme", theme_manager.current_theme)
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply theme to application
    theme_manager.apply_theme(app)

    window = FTMLASTDemo()
    window.show()
    sys.exit(app.exec())