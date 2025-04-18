# src/ftml_studio/ui/editor_window.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QApplication, QSplitter,
                               QTextEdit, QToolBar, QFileDialog, QMessageBox,
                               QMenu)
from PySide6.QtCore import Qt, QSettings, QTimer, QFileInfo
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QIcon
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
        logger.debug("Initializing FTML Editor")

        # Settings for preferences
        self.settings = QSettings("FTMLStudio", "FTMLEditor")

        # Current file path
        self.current_file_path = None
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
        main_layout.setSpacing(0)

        # Top section with description and status
        top_section = QWidget()
        top_layout = QHBoxLayout(top_section)
        top_layout.setContentsMargins(10, 10, 10, 5)

        # Description
        desc_label = QLabel("Edit FTML content below to see syntax highlighting based on the AST.")
        top_layout.addWidget(desc_label)

        # Status indicator
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")  # For stylesheet targeting
        top_layout.addWidget(self.status_label)
        top_layout.addStretch()  # Push everything to the left

        main_layout.addWidget(top_section)

        # Toolbar for file operations
        self.setup_toolbar()

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

        # Connect editor signals
        self.editor.textChanged.connect(self.on_text_changed)

        # Setup context menu
        self.editor.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self.show_context_menu)

        logger.debug(f"Applied FTMLASTHighlighter with theme support and error highlighting={self.error_highlighting_enabled}")

        # Add editor to main layout
        main_layout.addWidget(self.editor)

        # Initial status update
        self.update_status()

        # Setup drag and drop
        self.editor.setAcceptDrops(True)
        self.editor.installEventFilter(self)

    def setup_toolbar(self):
        """Set up the toolbar with file operations"""
        # Create toolbar
        self.toolbar = QToolBar()
        self.toolbar.setObjectName("editorToolbar")
        self.toolbar.setIconSize(Qt.QSize(16, 16))
        self.toolbar.setMovable(False)

        # Determine icon paths based on theme
        is_dark_theme = theme_manager.is_dark_theme()
        icon_subfolder = "light" if is_dark_theme else "dark"
        icon_base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "icons", icon_subfolder)

        # New file action
        self.new_action = QAction("New", self)
        try:
            self.new_action.setIcon(QIcon(os.path.join(icon_base_path, "new_file.png")))
        except:
            # Fallback to text if icon can't be loaded
            logger.warning("Couldn't load new file icon, using text instead")
        self.new_action.setToolTip("Create a new FTML file")
        self.new_action.triggered.connect(self.new_file)
        self.toolbar.addAction(self.new_action)

        # Open file action
        self.open_action = QAction("Open", self)
        try:
            self.open_action.setIcon(QIcon(os.path.join(icon_base_path, "open_file.png")))
        except:
            logger.warning("Couldn't load open file icon, using text instead")
        self.open_action.setToolTip("Open an existing FTML file")
        self.open_action.triggered.connect(self.open_file)
        self.toolbar.addAction(self.open_action)

        # Save file action
        self.save_action = QAction("Save", self)
        try:
            self.save_action.setIcon(QIcon(os.path.join(icon_base_path, "save_file.png")))
        except:
            logger.warning("Couldn't load save file icon, using text instead")
        self.save_action.setToolTip("Save the current FTML file")
        self.save_action.triggered.connect(self.save_file)
        self.toolbar.addAction(self.save_action)

        # Save as action
        self.save_as_action = QAction("Save As", self)
        try:
            self.save_as_action.setIcon(QIcon(os.path.join(icon_base_path, "save_as.png")))
        except:
            logger.warning("Couldn't load save as icon, using text instead")
        self.save_as_action.setToolTip("Save the current FTML file with a new name")
        self.save_as_action.triggered.connect(self.save_file_as)
        self.toolbar.addAction(self.save_as_action)

        # Add toolbar to layout
        layout = self.layout()
        layout.addWidget(self.toolbar)

    def show_context_menu(self, position):
        """Show custom context menu with file operations added"""
        # Get standard context menu
        menu = self.editor.createStandardContextMenu()

        # Add separator
        menu.addSeparator()

        # Add file operations
        menu.addAction(self.save_action)
        menu.addAction(self.save_as_action)
        menu.addAction(self.open_action)

        # Show the menu
        menu.exec(self.editor.mapToGlobal(position))

    def new_file(self):
        """Create a new file, checking for unsaved changes first"""
        if self.check_unsaved_changes():
            self.editor.clear()
            self.current_file_path = None
            self.is_modified = False
            self.update_window_title()
            self.status_label.setText("New file created")

    def open_file(self):
        """Open an FTML file"""
        if self.check_unsaved_changes():
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open FTML File", "", "FTML Files (*.ftml);;All Files (*)"
            )

            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.editor.setPlainText(content)
                    self.current_file_path = file_path
                    self.is_modified = False
                    self.update_window_title()
                    self.status_label.setText(f"Opened: {os.path.basename(file_path)}")
                    logger.info(f"Successfully opened file: {file_path}")
                except Exception as e:
                    logger.error(f"Error opening file: {str(e)}", exc_info=True)
                    QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def save_file(self):
        """Save the current file. If no path, prompt for one."""
        if self.current_file_path:
            self._save_to_file(self.current_file_path)
        else:
            self.save_file_as()

    def save_file_as(self):
        """Save the current content to a new file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save FTML File", "", "FTML Files (*.ftml);;All Files (*)"
        )

        if file_path:
            # Ensure .ftml extension
            if not file_path.lower().endswith('.ftml'):
                file_path += '.ftml'

            self._save_to_file(file_path)

    def _save_to_file(self, file_path):
        """Save content to the specified file path"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.current_file_path = file_path
            self.is_modified = False
            self.update_window_title()
            self.status_label.setText(f"Saved: {os.path.basename(file_path)}")
            logger.info(f"Successfully saved to file: {file_path}")
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

    def check_unsaved_changes(self):
        """Check if there are unsaved changes, prompt user to save. 
        Returns True if it's safe to proceed with operation (new, open, etc.)"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "There are unsaved changes. Do you want to save before continuing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )

            if reply == QMessageBox.Save:
                self.save_file()
                return True
            elif reply == QMessageBox.Discard:
                return True
            else:  # Cancel
                return False

        return True

    def update_window_title(self):
        """Update window title to include file name"""
        # If this widget is inside a MainWindow, update its title
        parent = self.window()
        if parent and hasattr(parent, 'setWindowTitle'):
            if self.current_file_path:
                file_name = os.path.basename(self.current_file_path)
                title = f"FTML Studio - {file_name}"
                if self.is_modified:
                    title += " *"
                parent.setWindowTitle(title)
            else:
                parent.setWindowTitle("FTML Studio")

    def eventFilter(self, obj, event):
        """Handle drag and drop events"""
        from PySide6.QtCore import QEvent
        from PySide6.QtGui import QDragEnterEvent, QDropEvent

        if obj is self.editor:
            # Drag enter event
            if event.type() == QEvent.DragEnter:
                mime_data = event.mimeData()
                if mime_data.hasUrls() and len(mime_data.urls()) == 1:
                    url = mime_data.urls()[0]
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        if file_path.lower().endswith('.ftml'):
                            event.acceptProposedAction()
                            return True

            # Drop event
            elif event.type() == QEvent.Drop:
                mime_data = event.mimeData()
                if mime_data.hasUrls() and len(mime_data.urls()) == 1:
                    url = mime_data.urls()[0]
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        if file_path.lower().endswith('.ftml'):
                            # Check for unsaved changes before opening
                            if self.check_unsaved_changes():
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                    self.editor.setPlainText(content)
                                    self.current_file_path = file_path
                                    self.is_modified = False
                                    self.update_window_title()
                                    self.status_label.setText(f"Opened: {os.path.basename(file_path)}")
                                    logger.info(f"Successfully opened file via drag and drop: {file_path}")
                                    return True
                                except Exception as e:
                                    logger.error(f"Error opening file via drag and drop: {str(e)}", exc_info=True)
                                    QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

        # Call the base class method
        return super().eventFilter(obj, event)

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

        # Mark as modified
        if not self.is_modified:
            self.is_modified = True
            self.update_window_title()

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