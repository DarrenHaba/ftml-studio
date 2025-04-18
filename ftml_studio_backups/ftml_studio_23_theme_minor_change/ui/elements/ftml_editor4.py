# src/ftml_studio/ui/elements/editor.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QApplication, QSplitter,
                               QTextEdit, QMenuBar, QMenu, QFileDialog,
                               QMessageBox)
from PySide6.QtCore import Qt, QSettings, QTimer
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QIcon, QAction
import ftml
import os
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
        logger.debug("Initializing FTML AST Editor")

        # Settings for preferences
        self.settings = QSettings("FTMLStudio", "ASTHighlighterDemo")

        # Current file tracking
        self.current_file = None
        self.is_modified = False

        # Get the global error indicator setting
        app_settings = QSettings("FTMLStudio", "AppSettings")
        self.error_highlighting_enabled = app_settings.value("editor/showErrorIndicators", True, type=bool)

        self.setup_ui()

        logger.debug("UI setup complete")

    def setup_ui(self):
        logger.debug("Setting up UI components")
        # Main layout - directly applied to this widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Create menu bar
        self.setup_menu_bar(main_layout)

        # Description and status
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(10, 5, 10, 5)

        desc_label = QLabel("Edit FTML content below to see syntax highlighting based on the AST.")
        header_layout.addWidget(desc_label)

        # Status label - moved from bottom to header area
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")  # For stylesheet targeting
        header_layout.addWidget(self.status_label)
        header_layout.addStretch()

        main_layout.addWidget(header_container)

        # Create a splitter for the editor and output
        splitter = QSplitter(Qt.Vertical)

        # Editor - using our enhanced text edit
        self.editor = EnhancedTextEdit()
        self.editor.setObjectName("codeEditor")  # For stylesheet targeting
        self.editor.setPlaceholderText("// Enter your FTML here\n// Example:\n// name = \"My Document\"\n// version = 1.0")
        font = QFont("Courier New", 10)
        font.setFixedPitch(True)
        self.editor.setFont(font)
        logger.debug("Created EnhancedTextEdit")

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

        # Connect text changed to track modifications
        self.editor.textChanged.connect(self.on_text_changed)

        logger.debug(f"Applied FTMLASTHighlighter with theme support and error highlighting={self.error_highlighting_enabled}")

        # Output area
        self.output = EnhancedTextEdit()  # Also using EnhancedTextEdit for output
        self.output.setReadOnly(True)
        self.output.setFont(font)

        # Add widgets to splitter
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(10, 0, 10, 0)
        editor_layout.addWidget(self.editor)

        output_container = QWidget()
        output_layout = QVBoxLayout(output_container)
        output_layout.setContentsMargins(10, 0, 10, 0)
        output_layout.addWidget(QLabel("Parsed Output:"))
        output_layout.addWidget(self.output)

        splitter.addWidget(editor_container)
        splitter.addWidget(output_container)
        splitter.setSizes([400, 200])

        main_layout.addWidget(splitter)

        # Initial status update
        self.update_status()

        # Set up context menu for editor
        self.setup_context_menu()

    def setup_menu_bar(self, main_layout):
        """Set up the menu bar with file operations"""
        self.menu_bar = QMenuBar()

        # File menu
        file_menu = QMenu("&File", self)

        # New action
        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)

        # Open action
        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)

        # Save action
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_file)
        self.save_action.setEnabled(False)  # Disabled until content is modified

        # Save As action
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)

        # Add actions to file menu
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(save_as_action)

        # Add file menu to menu bar
        self.menu_bar.addMenu(file_menu)

        # Add menu bar to layout
        main_layout.addWidget(self.menu_bar)

    def setup_context_menu(self):
        """Set up the context menu for the editor"""
        # The EnhancedTextEdit already has a context menu
        # We'll extend it with our file operations
        self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        """Show the context menu with added file operations"""
        # Get the standard context menu
        menu = self.editor.createStandardContextMenu()

        # Add separator
        menu.addSeparator()

        # Add file operations
        save_action = menu.addAction("Save")
        save_action.triggered.connect(self.save_file)
        save_action.setEnabled(self.is_modified)

        save_as_action = menu.addAction("Save As...")
        save_as_action.triggered.connect(self.save_file_as)

        # Show the menu
        menu.exec(self.editor.viewport().mapToGlobal(position))

    def new_file(self):
        """Create a new FTML file"""
        # Check for unsaved changes
        if self.is_modified and self.check_unsaved_changes():
            return

        # Clear editor
        self.editor.clear()
        self.current_file = None
        self.is_modified = False
        self.update_title()
        self.status_label.setText("New file created")

    def open_file(self):
        """Open an FTML file"""
        # Check for unsaved changes
        if self.is_modified and self.check_unsaved_changes():
            return

        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open FTML File", "", "FTML Files (*.ftml);;All Files (*)")

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.editor.setPlainText(content)
                self.current_file = file_path
                self.is_modified = False
                self.update_title()
                self.status_label.setText(f"Opened {os.path.basename(file_path)}")
                logger.info(f"Opened file: {file_path}")
            except Exception as e:
                logger.error(f"Error opening file: {str(e)}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def save_file(self):
        """Save the current FTML file"""
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(self.editor.toPlainText())
                self.is_modified = False
                self.update_title()
                self.status_label.setText(f"Saved {os.path.basename(self.current_file)}")
                logger.info(f"Saved file: {self.current_file}")
            except Exception as e:
                logger.error(f"Error saving file: {str(e)}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
        else:
            self.save_file_as()

    def save_file_as(self):
        """Save the current FTML file with a new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save FTML File", "", "FTML Files (*.ftml);;All Files (*)")

        if file_path:
            # Add .ftml extension if not present and no extension was specified
            if '.' not in os.path.basename(file_path):
                file_path += '.ftml'

            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.editor.toPlainText())
                self.current_file = file_path
                self.is_modified = False
                self.update_title()
                self.status_label.setText(f"Saved {os.path.basename(file_path)}")
                logger.info(f"Saved file as: {file_path}")
            except Exception as e:
                logger.error(f"Error saving file: {str(e)}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

    def check_unsaved_changes(self):
        """
        Check if there are unsaved changes and prompt user
        Returns True if operation should be cancelled
        """
        if not self.is_modified:
            return False

        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            "You have unsaved changes. Do you want to save them?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )

        if reply == QMessageBox.Save:
            self.save_file()
            return False
        elif reply == QMessageBox.Cancel:
            return True
        else:  # Discard
            return False

    def update_title(self):
        """Update the title to show the current file"""
        if hasattr(self, 'parent') and self.parent() and hasattr(self.parent(), 'setWindowTitle'):
            title = "FTML Studio"
            if self.current_file:
                filename = os.path.basename(self.current_file)
                title = f"{filename} - {title}"
                if self.is_modified:
                    title = f"*{title}"
            self.parent().setWindowTitle(title)

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

        # Track modifications
        if not self.is_modified:
            self.is_modified = True
            self.update_title()
            self.save_action.setEnabled(True)

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
        """Parse the FTML and show the result in the output area"""
        logger.debug("Parsing FTML for output display")
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