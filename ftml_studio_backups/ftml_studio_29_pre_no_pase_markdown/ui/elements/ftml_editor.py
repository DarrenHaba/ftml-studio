# src/ftml_studio/ui/elements/editor.py
import logging
import re
import sys
import os

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QApplication,
                               QTextEdit, QFileDialog,
                               QMessageBox, QComboBox, QMainWindow, QStyle)
from PySide6.QtCore import Qt, QSettings, QSize
from PySide6.QtGui import QFont, QTextCursor, QColor, QIcon, QAction
import ftml
from ftml.exceptions import FTMLParseError

from src.ftml_studio.ui.themes import theme_manager
from src.ftml_studio.syntax import FTMLASTHighlighter
from src.ftml_studio.logger import setup_logger, LOG_LEVELS

# Configure logging
logger = setup_logger("ftml_studio.editor_window")


class ThemedIcon:
    """Utility class for theme-aware icons"""

    @staticmethod
    def load(icon_name, parent=None, is_dark_theme=False):
        """Load an icon from the appropriate theme folder or fallback to system icon"""
        # Select folder based on theme
        folder = "light" if is_dark_theme else "dark"

        # Path to the icon file in the theme-specific folder
        icon_path = os.path.join(os.path.dirname(__file__), f"../icons/{folder}/{icon_name}.png")

        # Try fallback path if main path doesn't exist
        if not os.path.exists(icon_path):
            fallback_path = os.path.join(os.path.dirname(__file__), f"../icons/{icon_name}.png")
            if os.path.exists(fallback_path):
                logger.debug(f"Using fallback icon at: {fallback_path}")
                return QIcon(fallback_path)

            # If neither path works, use a system icon
            logger.warning(f"Icon not found: {icon_name}, using system fallback")

            # Map icon names to appropriate system icons
            system_icon_map = {
                "new": QStyle.SP_FileIcon,
                "open": QStyle.SP_DirOpenIcon,
                "save": QStyle.SP_DialogSaveButton,
                "save_as": QStyle.SP_DialogSaveButton
            }

            # Get appropriate system icon or default to file icon
            icon_type = system_icon_map.get(icon_name, QStyle.SP_FileIcon)
            return QApplication.style().standardIcon(icon_type)

        # Return the themed icon if found
        return QIcon(icon_path)


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

        # Error tracking
        self.current_errors = []
        self.error_line_highlighted = None

        self.setup_ui()
        logger.debug("UI setup complete")

    def setup_ui(self):
        logger.debug("Setting up UI components")
        # Main layout - directly applied to this widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Create horizontal toolbar instead of menu bar
        self.setup_toolbar(main_layout)

        # Editor container
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(10, 5, 10, 5)

        # Editor - using standard QTextEdit
        self.editor = QTextEdit()
        self.editor.setObjectName("codeEditor")  # For stylesheet targeting
        self.editor.setPlaceholderText(
            "// Enter your FTML here\n// Example:\n// name = \"My Document\"\n// version = 1.0")
        font = QFont("Courier New", 10)
        font.setFixedPitch(True)
        self.editor.setFont(font)
        logger.debug("Created Editor")

        # Apply highlighter with theme support
        self.highlighter = FTMLASTHighlighter(
            self.editor.document(),
            theme_manager,
            error_highlighting=True
        )

        # Connect highlighter errors signal to update error display
        self.highlighter.errorsChanged.connect(self.update_error_display)

        # Connect text changed to track modifications
        self.editor.textChanged.connect(self.on_text_changed)
        logger.debug("Applied FTMLASTHighlighter with theme support")

        # Add editor to container
        editor_layout.addWidget(self.editor)

        # Status bar at the bottom
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(10, 5, 10, 5)

        # Status label - make it clickable
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")  # For stylesheet targeting
        self.status_label.setCursor(Qt.PointingHandCursor)  # Show hand cursor on hover
        self.status_label.mousePressEvent = self.status_label_clicked  # Handle click events
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        # Add containers to main layout
        main_layout.addWidget(editor_container, 1)  # Editor gets all available space
        main_layout.addWidget(status_container)

        # Initial status update
        self.update_status()

        # Set up context menu for editor
        self.setup_context_menu()

    def setup_toolbar(self, main_layout):
        """Set up the horizontal toolbar with file operations buttons"""
        # Create toolbar layout
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        toolbar_layout.setSpacing(10)

        # Get current theme
        is_dark = theme_manager.get_active_theme() == theme_manager.DARK

        # Create themed buttons
        # New button
        self.new_button = QPushButton()
        self.new_button.setIcon(ThemedIcon.load("new", self, is_dark))
        self.new_button.setToolTip("New (Ctrl+N)")
        self.new_button.setObjectName("toolbarButton")
        self.new_button.setFixedSize(QSize(32, 32))
        self.new_button.clicked.connect(self.new_file)

        # Open button
        self.open_button = QPushButton()
        self.open_button.setIcon(ThemedIcon.load("open", self, is_dark))
        self.open_button.setToolTip("Open (Ctrl+O)")
        self.open_button.setObjectName("toolbarButton")
        self.open_button.setFixedSize(QSize(32, 32))
        self.open_button.clicked.connect(self.open_file)

        # Save button
        self.save_button = QPushButton()
        self.save_button.setIcon(ThemedIcon.load("save", self, is_dark))
        self.save_button.setToolTip("Save (Ctrl+S)")
        self.save_button.setObjectName("toolbarButton")
        self.save_button.setFixedSize(QSize(32, 32))
        self.save_button.clicked.connect(self.save_file)
        # Initially disabled until content is modified
        self.save_button.setEnabled(False)

        # Save As button
        self.save_as_button = QPushButton()
        self.save_as_button.setIcon(ThemedIcon.load("save_as", self, is_dark))
        self.save_as_button.setToolTip("Save As (Ctrl+Shift+S)")
        self.save_as_button.setObjectName("toolbarButton")
        self.save_as_button.setFixedSize(QSize(32, 32))
        self.save_as_button.clicked.connect(self.save_file_as)

        # Add buttons to toolbar layout
        toolbar_layout.addWidget(self.new_button)
        toolbar_layout.addWidget(self.open_button)
        toolbar_layout.addWidget(self.save_button)
        toolbar_layout.addWidget(self.save_as_button)
        toolbar_layout.addStretch(1)  # Push buttons to the left

        # Create a container widget for the toolbar
        self.toolbar_container = QWidget()
        self.toolbar_container.setObjectName("toolbarContainer")
        self.toolbar_container.setLayout(toolbar_layout)

        # Apply stylesheet to the container
        self.toolbar_container.setStyleSheet(self.get_toolbar_style(is_dark))

        # Add toolbar container to main layout
        main_layout.addWidget(self.toolbar_container)

        # Set up keyboard shortcuts
        # New shortcut
        self.new_action = QAction("New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_file)
        self.addAction(self.new_action)

        # Open shortcut
        self.open_action = QAction("Open", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_file)
        self.addAction(self.open_action)

        # Save shortcut
        self.save_action = QAction("Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_file)
        self.addAction(self.save_action)

        # Save As shortcut
        self.save_as_action = QAction("Save As", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self.save_file_as)
        self.addAction(self.save_as_action)

    def get_toolbar_style(self, is_dark):
        """Get theme-aware toolbar style"""
        accent_color = theme_manager.accent_color

        if is_dark:
            return f"""
                #toolbarContainer {{
                    border-left: 0px solid #444444;
                }}

                QPushButton[objectName="toolbarButton"] {{
                    color: white;
                    background-color: transparent;
                    border: none;
                    border-radius: 4px;
                    padding: 4px;
                    margin: 2px;
                }}

                QPushButton[objectName="toolbarButton"]:hover {{
                    background-color: #444444;
                }}

                QPushButton[objectName="toolbarButton"]:pressed {{
                    background-color: {accent_color};
                }}

                QPushButton[objectName="toolbarButton"]:disabled {{
                    opacity: 0.5;
                }}
            """
        else:
            return f"""
                #toolbarContainer {{
                    border-left: 0px solid #cccccc;
                }}

                QPushButton[objectName="toolbarButton"] {{
                    color: #333333;
                    background-color: transparent;
                    border: none;
                    border-radius: 4px;
                    padding: 4px;
                    margin: 2px;
                }}

                QPushButton[objectName="toolbarButton"]:hover {{
                    background-color: #e0e0e0;
                }}

                QPushButton[objectName="toolbarButton"]:pressed {{
                    background-color: {accent_color};
                }}

                QPushButton[objectName="toolbarButton"]:disabled {{
                    opacity: 0.5;
                }}
            """

    def status_label_clicked(self, event):
        """Handle click on the status label for error navigation"""
        if not self.current_errors:
            return  # No errors to navigate to

        # Get the first error's position
        error = self.current_errors[0]
        line = error.get('line', 0)
        col = error.get('col', 0)

        # If we're already highlighting this line, toggle it off
        if self.error_line_highlighted == line:
            self.clear_error_highlight()
            return

        # Navigate to the error position
        self.navigate_to_error(line, col)

        # Highlight the status label to show it's active
        self.status_label.setStyleSheet(
            "color: red; background-color: rgba(255, 0, 0, 0.1); padding: 2px 5px; border-radius: 3px;")

        # Remember which line we highlighted
        self.error_line_highlighted = line

    def navigate_to_error(self, line, col):
        """Navigate to the specified error position and highlight the line"""
        cursor = QTextCursor(self.editor.document())
        cursor.movePosition(QTextCursor.Start)

        # Move to the error line
        for _ in range(line - 1):
            if not cursor.movePosition(QTextCursor.NextBlock):
                break

        # Move to the column if possible
        if col > 1:
            for _ in range(col - 1):
                if not cursor.movePosition(QTextCursor.Right):
                    break

        # Set cursor in the editor
        self.editor.setTextCursor(cursor)

        # Highlight the entire line
        cursor.movePosition(QTextCursor.StartOfBlock)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)

        # Create selection format
        selection = QTextEdit.ExtraSelection()

        error_color = QColor(theme_manager.get_syntax_color("error"))
        highlight_color = QColor(error_color)
        highlight_color.setAlpha(30)  # Very light background

        selection.format.setBackground(highlight_color)
        selection.cursor = cursor

        # Apply the selection
        self.editor.setExtraSelections([selection])

        # Center the error in the view
        self.editor.ensureCursorVisible()

    def clear_error_highlight(self):
        """Clear any error highlighting"""
        self.editor.setExtraSelections([])
        self.error_line_highlighted = None

        # Reset status label style but keep it red for error indication
        self.status_label.setStyleSheet("color: red;")

    def setup_context_menu(self):
        """Set up the context menu for the editor"""
        # Use standard context menu
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
        self.status_label.setStyleSheet("")  # Reset style

        # Clear any error highlights
        self.clear_error_highlight()
        self.current_errors = []

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
                self.status_label.setStyleSheet("")  # Reset style

                # Clear any error highlights
                self.clear_error_highlight()

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
                self.status_label.setStyleSheet("")  # Reset style
                logger.info(f"Saved file: {self.current_file}")
                # Update save button state
                self.save_button.setEnabled(False)
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
                self.status_label.setStyleSheet("")  # Reset style
                logger.info(f"Saved file as: {file_path}")
                # Update save button state
                self.save_button.setEnabled(False)
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

    def update_toolbar_theme(self, is_dark):
        """Update toolbar styling and icons based on theme change"""
        # Update toolbar container styling
        if hasattr(self, 'toolbar_container'):
            self.toolbar_container.setStyleSheet(self.get_toolbar_style(is_dark))
            logger.debug(f"Updated toolbar styling for {'dark' if is_dark else 'light'} theme")

        # Update toolbar icons
        self.update_toolbar_icons(is_dark)

    def update_toolbar_icons(self, is_dark):
        """Update toolbar button icons based on theme"""
        if hasattr(self, 'new_button'):
            self.new_button.setIcon(ThemedIcon.load("new", self, is_dark))

        if hasattr(self, 'open_button'):
            self.open_button.setIcon(ThemedIcon.load("open", self, is_dark))

        if hasattr(self, 'save_button'):
            self.save_button.setIcon(ThemedIcon.load("save", self, is_dark))

        if hasattr(self, 'save_as_button'):
            self.save_as_button.setIcon(ThemedIcon.load("save_as", self, is_dark))

    def on_text_changed(self):
        """Handle text changes"""
        # Update status immediately
        self.update_status()

        # Clear error highlight if it exists
        if self.error_line_highlighted is not None:
            self.clear_error_highlight()

        # Track modifications
        if not self.is_modified:
            self.is_modified = True
            self.update_title()
            self.save_button.setEnabled(True)

    def update_error_display(self, errors):
        """Update error message in the status bar based on errors from the highlighter"""
        logger.debug(f"Updating error display with {len(errors)} errors")

        # Store current errors for navigation
        self.current_errors = errors

        # Clear any existing error highlight
        if self.error_line_highlighted is not None:
            self.clear_error_highlight()

        # Update error message based on errors
        if errors:
            # Format error message directly in the status bar
            first_error = errors[0]
            line = first_error.get('line', 0)
            col = first_error.get('col', 0)
            message = first_error.get('message', 'Unknown error')

            error_text = f"✗ Parsing Error: Line {line}, Column {col} - {message}"
            if len(errors) > 1:
                error_text += f" (+{len(errors) - 1} more errors)"

            self.status_label.setText(error_text)
            self.status_label.setStyleSheet("color: red;")
        else:
            # No errors - show success message
            if hasattr(self.highlighter, 'ast') and self.highlighter.ast is not None:
                self.status_label.setText("✓ Valid FTML")
                self.status_label.setStyleSheet("color: green;")
            else:
                self.status_label.setText("Document parsed")
                self.status_label.setStyleSheet("color: gray;")

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
        """Parse the FTML and update the status display"""
        logger.debug("Parsing FTML")
        content = self.editor.toPlainText()
        if not content:
            self.status_label.setText("Empty document")
            self.status_label.setStyleSheet("color: gray;")
            return

        try:
            # Parse the FTML
            logger.debug("Parsing FTML for validation")
            ftml.load(content)
            logger.debug("FTML parsed successfully")

            # Set success status
            self.status_label.setText("✓ Valid FTML")
            self.status_label.setStyleSheet("color: green;")

            # Clear errors list
            self.current_errors = []

        except FTMLParseError as e:
            error_message = str(e)
            logger.debug(f"FTML parse error in parse_ftml: {error_message}")

            # Extract line and column from error message if available
            line_match = re.search(r'at line (\d+)', error_message)
            col_match = re.search(r'col (\d+)', error_message)

            if line_match and col_match:
                line = int(line_match.group(1))
                col = int(col_match.group(1))
                error_text = f"✗ Parsing Error: Line {line}, Column {col} - {error_message}"

                # Create error entry
                self.current_errors = [{
                    'line': line,
                    'col': col,
                    'message': error_message
                }]
            else:
                error_text = f"✗ Parsing Error: {error_message}"
                self.current_errors = []

            # Set error status
            self.status_label.setText(error_text)
            self.status_label.setStyleSheet("color: red;")

        except Exception as e:
            logger.debug(f"Other error in parse_ftml: {str(e)}")

            # Set error status
            self.status_label.setText(f"✗ Error: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
            self.current_errors = []


class FTMLEditorTestWindow(QMainWindow):
    """Test window for standalone FTML editor testing"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FTML Editor Component Test")
        self.resize(800, 600)

        # Main container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        main_layout = QVBoxLayout(self.central_widget)

        # Create editor widget
        self.editor_widget = FTMLEditorWidget(self)

        # Theme selector
        theme_container = QWidget()
        theme_layout = QHBoxLayout(theme_container)
        theme_layout.setContentsMargins(10, 5, 10, 5)

        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Light")
        self.theme_combo.addItem("Dark")
        self.theme_combo.addItem("Auto (System)")

        # Set current theme in combo box
        current_theme = theme_manager.current_theme
        if current_theme == theme_manager.LIGHT:
            self.theme_combo.setCurrentIndex(0)
        elif current_theme == theme_manager.DARK:
            self.theme_combo.setCurrentIndex(1)
        else:  # AUTO
            self.theme_combo.setCurrentIndex(2)

        # Connect theme change
        self.theme_combo.currentIndexChanged.connect(self.change_theme)

        # Add to layout
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch(1)  # Push to left

        # Add components to main layout
        main_layout.addWidget(theme_container)
        main_layout.addWidget(self.editor_widget, 1)  # stretch=1 to fill space

    def change_theme(self, index):
        """Change theme based on combo selection"""
        if index == 0:
            new_theme = theme_manager.LIGHT
        elif index == 1:
            new_theme = theme_manager.DARK
        else:
            new_theme = theme_manager.AUTO

        # Set theme
        theme_manager.set_theme(new_theme)

        # Apply to application
        app = QApplication.instance()
        theme_manager.apply_theme(app)

        # Update editor styling
        self.editor_widget.recreate_highlighter()

        # Show status
        self.statusBar().showMessage(f"Theme changed to {new_theme}")

    def toggle_error_highlighting(self, state):
        """Toggle error highlighting in the editor"""
        enabled = bool(state)

        # Update editor's error highlighting
        self.editor_widget.update_error_highlighting(enabled)

        # Save the setting globally
        app_settings = QSettings("FTMLStudio", "AppSettings")
        app_settings.setValue("editor/showErrorIndicators", enabled)

        # Show status
        self.statusBar().showMessage(f"Error highlighting {'enabled' if enabled else 'disabled'}")


# Allow standalone execution for testing
if __name__ == "__main__":
    current_level = os.environ.get('FTML_STUDIO_LOG_LEVEL', 'DEBUG')
    logger.setLevel(LOG_LEVELS.get(current_level, logging.DEBUG))
    logger.debug(f"Starting FTML Studio application with log level: {current_level}")

    app = QApplication(sys.argv)

    # Apply initial theme
    theme_manager.apply_theme(app)

    # Create and show test window
    window = FTMLEditorTestWindow()
    window.show()

    sys.exit(app.exec())
