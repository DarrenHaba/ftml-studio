# src/ftml_studio/ui/elements/editor.py
import logging
import sys
import os

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QApplication,
                               QTextEdit, QFileDialog, QDialog, QSlider,
                               QMessageBox, QCheckBox, QComboBox, QMainWindow, QStyle,
                               QFrame)
from PySide6.QtCore import Qt, QSettings, QSize, QTimer
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QIcon, QAction
import ftml
from ftml.exceptions import FTMLParseError

from src.ftml_studio.components.enhanced_text_edit import EnhancedTextEdit
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
                "save_as": QStyle.SP_DialogSaveButton,
                "settings": QStyle.SP_FileDialogContentsView
            }

            # Get appropriate system icon or default to file icon
            icon_type = system_icon_map.get(icon_name, QStyle.SP_FileIcon)
            return QApplication.style().standardIcon(icon_type)

        # Return the themed icon if found
        return QIcon(icon_path)


class EditorSettingsDialog(QDialog):
    """Dialog for editor settings including error highlighting delay"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editor Settings")
        self.setMinimumWidth(400)

        # Get settings
        self.settings = QSettings("FTMLStudio", "AppSettings")
        self.autoparse_enabled = self.settings.value("editor/autoparseEnabled", True, type=bool)
        self.error_highlight_enabled = self.settings.value("editor/showErrorIndicators", True, type=bool)
        self.error_highlight_delay = self.settings.value("editor/errorHighlightDelay", 1000, type=int)
        self.parse_delay = self.settings.value("editor/parseDelay", 500, type=int)

        # Setup UI
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Autoparse section
        autoparse_layout = QHBoxLayout()
        self.autoparse_checkbox = QCheckBox("Autoparse while typing")
        self.autoparse_checkbox.setChecked(self.autoparse_enabled)
        self.autoparse_checkbox.setToolTip("Automatically parse code as you type")
        self.autoparse_checkbox.stateChanged.connect(self.update_ui_state)
        autoparse_layout.addWidget(self.autoparse_checkbox)
        layout.addLayout(autoparse_layout)

        # Parse delay section
        parse_delay_layout = QHBoxLayout()
        parse_delay_layout.addWidget(QLabel("Parse Delay:"))

        self.parse_delay_slider = QSlider(Qt.Horizontal)
        self.parse_delay_slider.setMinimum(100)
        self.parse_delay_slider.setMaximum(5000)  # 5 seconds in ms
        self.parse_delay_slider.setValue(self.parse_delay)
        self.parse_delay_slider.setTickInterval(500)
        self.parse_delay_slider.setTickPosition(QSlider.TicksBelow)
        self.parse_delay_slider.setToolTip("Delay before code is parsed after typing stops")
        parse_delay_layout.addWidget(self.parse_delay_slider)

        self.parse_delay_label = QLabel(f"{self.parse_delay/1000:.1f}s")
        parse_delay_layout.addWidget(self.parse_delay_label)
        self.parse_delay_slider.valueChanged.connect(self.update_parse_delay_label)

        layout.addLayout(parse_delay_layout)

        # Error highlighting section
        highlight_layout = QHBoxLayout()
        self.highlight_checkbox = QCheckBox("Display Syntax Error Indicators")
        self.highlight_checkbox.setChecked(self.error_highlight_enabled)
        self.highlight_checkbox.setToolTip("Show red underlines for syntax errors")
        self.highlight_checkbox.stateChanged.connect(self.update_ui_state)
        highlight_layout.addWidget(self.highlight_checkbox)
        layout.addLayout(highlight_layout)

        # Error highlighting delay section
        error_delay_layout = QHBoxLayout()
        error_delay_layout.addWidget(QLabel("Error Indicator Delay:"))

        self.error_delay_slider = QSlider(Qt.Horizontal)
        self.error_delay_slider.setMinimum(0)
        self.error_delay_slider.setMaximum(10000)  # 10 seconds in ms
        self.error_delay_slider.setValue(self.error_highlight_delay)
        self.error_delay_slider.setTickInterval(1000)
        self.error_delay_slider.setTickPosition(QSlider.TicksBelow)
        self.error_delay_slider.setToolTip("Additional delay before showing error indicators")
        error_delay_layout.addWidget(self.error_delay_slider)

        self.error_delay_label = QLabel(f"{self.error_highlight_delay/1000:.1f}s")
        error_delay_layout.addWidget(self.error_delay_label)
        self.error_delay_slider.valueChanged.connect(self.update_error_delay_label)

        layout.addLayout(error_delay_layout)

        # Separator
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #cccccc;")
        layout.addWidget(separator)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # Initialize UI state
        self.update_ui_state()

    def update_ui_state(self):
        """Update the enabled state of UI elements based on checkbox states"""
        # Parse delay is only relevant if autoparse is enabled
        autoparse_enabled = self.autoparse_checkbox.isChecked()
        self.parse_delay_slider.setEnabled(autoparse_enabled)

        # Error indicator delay is only relevant if error highlighting is enabled
        error_highlight_enabled = self.highlight_checkbox.isChecked()
        self.error_delay_slider.setEnabled(error_highlight_enabled)

    def update_error_delay_label(self, value):
        """Update the error delay label when the slider changes"""
        self.error_delay_label.setText(f"{value/1000:.1f}s")

    def update_parse_delay_label(self, value):
        """Update the parse delay label when the slider changes"""
        self.parse_delay_label.setText(f"{value/1000:.1f}s")

    def get_settings(self):
        """Get the current settings from the dialog"""
        return {
            "autoparse_enabled": self.autoparse_checkbox.isChecked(),
            "error_highlight_enabled": self.highlight_checkbox.isChecked(),
            "error_highlight_delay": self.error_delay_slider.value(),
            "parse_delay": self.parse_delay_slider.value()
        }


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

        # Get application settings
        app_settings = QSettings("FTMLStudio", "AppSettings")

        # Autoparse setting
        self.autoparse_enabled = app_settings.value("editor/autoparseEnabled", True, type=bool)

        # Error highlighting settings
        self.error_highlighting_enabled = app_settings.value("editor/showErrorIndicators", True, type=bool)
        self.error_highlight_delay = app_settings.value("editor/errorHighlightDelay", 1000, type=int)

        # Parse delay setting
        self.parse_delay = app_settings.value("editor/parseDelay", 500, type=int)

        # Timer for delaying error highlights
        self.error_highlight_timer = QTimer(self)
        self.error_highlight_timer.setSingleShot(True)
        self.error_highlight_timer.timeout.connect(self.apply_delayed_error_highlights)

        # Cached errors for delayed highlighting
        self.pending_errors = []

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

        # Editor - using our enhanced text edit
        self.editor = EnhancedTextEdit()
        self.editor.setObjectName("codeEditor")  # For stylesheet targeting
        self.editor.setPlaceholderText(
            "// Enter your FTML here\n// Example:\n// name = \"My Document\"\n// version = 1.0")
        font = QFont("Courier New", 10)
        font.setFixedPitch(True)
        self.editor.setFont(font)
        logger.debug("Created EnhancedTextEdit")

        # Apply highlighter with theme support and error highlighting based on global setting
        self.highlighter = FTMLASTHighlighter(
            self.editor.document(),
            theme_manager,
            error_highlighting=self.error_highlighting_enabled,
            parse_delay=self.parse_delay
        )

        # Connect the editor with the highlighter
        self.editor.setHighlighter(self.highlighter)

        # Connect highlighter errors signal to update error display
        self.highlighter.errorsChanged.connect(self.update_error_display)

        # Connect text changed to track modifications
        self.editor.textChanged.connect(self.on_text_changed)

        logger.debug("Applied FTMLASTHighlighter with theme support and error highlighting="
                     f"{self.error_highlighting_enabled}")

        # Add editor to container
        editor_layout.addWidget(self.editor)

        # Status bar at the bottom
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(10, 5, 10, 5)

        # Status label
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")  # For stylesheet targeting
        status_layout.addWidget(self.status_label)

        # Error details button - initially hidden
        self.error_details_btn = QPushButton("Show Error Details")
        self.error_details_btn.setObjectName("errorDetailsButton")
        self.error_details_btn.clicked.connect(self.toggle_error_details)
        self.error_details_btn.setVisible(False)
        status_layout.addWidget(self.error_details_btn)

        # Settings button
        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(ThemedIcon.load("settings", self, theme_manager.get_active_theme() == theme_manager.DARK))
        self.settings_btn.setToolTip("Editor Settings")
        self.settings_btn.setObjectName("settingsButton")
        self.settings_btn.setFixedSize(QSize(24, 24))
        self.settings_btn.clicked.connect(self.show_settings_dialog)
        status_layout.addWidget(self.settings_btn)

        status_layout.addStretch()

        # Add containers to main layout
        main_layout.addWidget(editor_container, 1)  # Editor gets all available space
        main_layout.addWidget(status_container)

        # Error details panel (initially hidden)
        self.error_details_panel = QWidget()
        error_details_layout = QVBoxLayout(self.error_details_panel)
        error_details_layout.setContentsMargins(10, 5, 10, 5)

        # Error details text area
        self.error_details_text = QTextEdit()
        self.error_details_text.setReadOnly(True)
        self.error_details_text.setFont(font)
        self.error_details_text.setMaximumHeight(150)  # Limit height
        error_details_layout.addWidget(self.error_details_text)

        # Add error panel to main layout but hide it initially
        main_layout.addWidget(self.error_details_panel)
        self.error_details_panel.setVisible(False)

        # Initial status update
        self.update_status()

        # Set up context menu for editor
        self.setup_context_menu()

    def show_settings_dialog(self):
        """Show the editor settings dialog"""
        dialog = EditorSettingsDialog(self)

        if dialog.exec() == QDialog.Accepted:
            # Get settings from dialog
            settings = dialog.get_settings()

            # Apply settings
            self.autoparse_enabled = settings["autoparse_enabled"]
            self.error_highlighting_enabled = settings["error_highlight_enabled"]
            self.error_highlight_delay = settings["error_highlight_delay"]
            self.parse_delay = settings["parse_delay"]

            # Save settings
            app_settings = QSettings("FTMLStudio", "AppSettings")
            app_settings.setValue("editor/autoparseEnabled", self.autoparse_enabled)
            app_settings.setValue("editor/showErrorIndicators", self.error_highlighting_enabled)
            app_settings.setValue("editor/errorHighlightDelay", self.error_highlight_delay)
            app_settings.setValue("editor/parseDelay", self.parse_delay)

            # Update highlighter settings
            self.recreate_highlighter()

            # If error highlighting is enabled, apply any pending error highlights with new delay
            if self.error_highlighting_enabled and self.pending_errors:
                self.schedule_error_highlights(self.pending_errors)
            else:
                # Otherwise clear any error highlights
                self.clear_error_highlights()

            logger.debug(f"Applied settings: autoparse={self.autoparse_enabled}, "
                         f"error_highlight={self.error_highlighting_enabled}, "
                         f"error_delay={self.error_highlight_delay}ms, "
                         f"parse_delay={self.parse_delay}ms")

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

    @staticmethod
    def get_toolbar_style(is_dark):
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
                
                QPushButton[objectName="settingsButton"] {{
                    color: white;
                    background-color: transparent;
                    border: none;
                    border-radius: 4px;
                    padding: 2px;
                    margin: 1px;
                }}

                QPushButton[objectName="settingsButton"]:hover {{
                    background-color: #444444;
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
                
                QPushButton[objectName="settingsButton"] {{
                    color: #333333;
                    background-color: transparent;
                    border: none;
                    border-radius: 4px;
                    padding: 2px;
                    margin: 1px;
                }}

                QPushButton[objectName="settingsButton"]:hover {{
                    background-color: #e0e0e0;
                }}
            """

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

    def recreate_highlighter(self):
        """Recreate the highlighter to apply new theme colors and settings"""
        # Store cursor position
        cursor_pos = self.editor.textCursor().position()

        # Check current theme
        is_dark = theme_manager.get_active_theme() == theme_manager.DARK
        logger.debug(f"Recreating highlighter with theme: {'DARK' if is_dark else 'LIGHT'}")

        # Delete and recreate highlighter
        if hasattr(self, 'highlighter'):
            # Disconnect old signals if any
            if hasattr(self.highlighter, 'errorsChanged'):
                try:
                    self.highlighter.errorsChanged.disconnect(self.update_error_display)
                except Exception:
                    pass  # In case not connected

            del self.highlighter

        # Create new highlighter with current theme and settings
        self.highlighter = FTMLASTHighlighter(
            self.editor.document(),
            theme_manager,
            error_highlighting=self.error_highlighting_enabled,
            parse_delay=self.parse_delay
        )

        # Set autoparse setting
        if hasattr(self.highlighter, 'set_autoparse'):
            self.highlighter.set_autoparse(self.autoparse_enabled)

        # Connect editor with new highlighter
        self.editor.setHighlighter(self.highlighter)

        # Reconnect signals
        self.highlighter.errorsChanged.connect(self.update_error_display)

        # Restore cursor position
        cursor = self.editor.textCursor()
        cursor.setPosition(cursor_pos)
        self.editor.setTextCursor(cursor)

        # Update toolbar styling and icons for theme change
        self.update_toolbar_theme(is_dark)

        # Clear any error highlights
        self.clear_error_highlights()

        # Force update of the editor
        self.editor.update()

        logger.debug(f"Recreated highlighter with autoparse={self.autoparse_enabled}, "
                     f"error_highlighting={self.error_highlighting_enabled}, "
                     f"error_delay={self.error_highlight_delay}ms, "
                     f"parse_delay={self.parse_delay}ms")

    def update_toolbar_theme(self, is_dark):
        """Update toolbar styling and icons based on theme change"""
        # Update toolbar container styling
        if hasattr(self, 'toolbar_container'):
            self.toolbar_container.setStyleSheet(self.get_toolbar_style(is_dark))
            logger.debug(f"Updated toolbar styling for {'dark' if is_dark else 'light'} theme")

        # Update toolbar icons
        self.update_toolbar_icons(is_dark)

        # Update settings button icon
        if hasattr(self, 'settings_btn'):
            self.settings_btn.setIcon(ThemedIcon.load("settings", self, is_dark))

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

        # Track modifications
        if not self.is_modified:
            self.is_modified = True
            self.update_title()
            self.save_button.setEnabled(True)

        # Cancel any pending error highlights when text changes
        if self.error_highlight_timer.isActive():
            self.error_highlight_timer.stop()

    def update_error_display(self, errors):
        """Update the error display based on errors from the highlighter"""
        logger.debug(f"Updating error display with {len(errors)} errors")

        # Update error details panel based on errors
        if errors:
            # Show first error in the status bar
            errors[0].get('message', 'Error detected')
            self.status_label.setText("✗ Parsing Error")
            self.status_label.setStyleSheet("color: red;")

            # Show error details button if there are errors
            self.error_details_btn.setVisible(True)

            # Update error details text
            error_details = ""
            for i, error in enumerate(errors):
                line = error.get('line', 0)
                col = error.get('col', 0)
                message = error.get('message', 'Unknown error')
                error_details += f"Error {i+1}: Line {line}, Column {col} - {message}\n\n"

            self.error_details_text.setPlainText(error_details)

            # Apply error highlights if showing errors is enabled
            if self.error_highlighting_enabled:
                # Store errors for later highlighting with delay
                self.schedule_error_highlights(errors)

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
            else:
                # Clear highlights if error highlighting is disabled
                self.clear_error_highlights()
        else:
            # No errors - show success message and hide error details
            if hasattr(self.highlighter, 'ast') and self.highlighter.ast is not None:
                self.status_label.setText("✓ Valid FTML")
                self.status_label.setStyleSheet("color: green;")
            else:
                self.status_label.setText("Document parsed")
                self.status_label.setStyleSheet("color: gray;")

            # Hide error details button and panel
            self.error_details_btn.setVisible(False)
            self.error_details_panel.setVisible(False)

            # Clear any error highlights
            self.clear_error_highlights()

    def schedule_error_highlights(self, errors):
        """Schedule error highlights to appear after the configured delay"""
        # Store errors for delayed highlighting
        self.pending_errors = errors.copy()

        # Clear existing error highlights
        self.clear_error_highlights()

        # Only schedule highlights if error highlighting is enabled
        if not self.error_highlighting_enabled:
            logger.debug("Error highlighting disabled, not scheduling highlights")
            return

        # Cancel any existing timer
        if self.error_highlight_timer.isActive():
            self.error_highlight_timer.stop()

        # Start the timer for delayed highlighting if delay > 0
        if self.error_highlight_delay > 0:
            logger.debug(f"Scheduling error highlights with {self.error_highlight_delay}ms delay")
            self.error_highlight_timer.start(self.error_highlight_delay)
        else:
            # Apply immediately if delay is 0
            self.apply_delayed_error_highlights()

    def apply_delayed_error_highlights(self):
        """Apply error highlights after the delay timer expires"""
        logger.debug(f"Applying delayed error highlights for {len(self.pending_errors)} errors")

        # Double-check error highlighting is still enabled
        if not self.error_highlighting_enabled:
            logger.debug("Error highlighting disabled, not applying highlights")
            return

        # Apply the highlights from pending errors
        if self.pending_errors:
            self.apply_error_highlights()

    def toggle_error_details(self):
        """Toggle visibility of error details panel"""
        is_visible = self.error_details_panel.isVisible()
        self.error_details_panel.setVisible(not is_visible)

        # Update button text
        if not is_visible:
            self.error_details_btn.setText("Hide Error Details")
        else:
            self.error_details_btn.setText("Show Error Details")

    def update_error_highlighting(self, enabled):
        """Update the error highlighting based on the provided enabled state"""
        logger.debug(f"Updating error highlighting to: {enabled}")

        # Update highlighter settings
        if hasattr(self, 'highlighter'):
            self.highlighter.error_highlighting = enabled

            # Store the setting
            self.error_highlighting_enabled = enabled

            # Save the setting to settings
            app_settings = QSettings("FTMLStudio", "AppSettings")
            app_settings.setValue("editor/showErrorIndicators", enabled)

            # Update error display
            if enabled and hasattr(self.highlighter, 'errors'):
                self.update_error_display(self.highlighter.errors)
            else:
                self.clear_error_highlights()

            # Force rehighlight to apply/remove error indicators
            self.highlighter.rehighlight()

    def clear_error_highlights(self):
        """Clear all error highlights"""
        self.editor.setExtraSelections([])
        self.editor.error_positions = []

    def apply_error_highlights(self):
        """Apply all error highlights from the pending errors list"""
        # Check if error highlighting is enabled
        if not self.error_highlighting_enabled or not self.pending_errors:
            self.clear_error_highlights()
            return

        # Get errors from cached list
        errors = self.pending_errors

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
        """Parse the FTML and update the status display"""
        logger.debug("Parsing FTML")
        content = self.editor.toPlainText()
        if not content:
            self.status_label.setText("Empty document")
            self.status_label.setStyleSheet("color: gray;")
            self.error_details_panel.setVisible(False)
            self.error_details_btn.setVisible(False)
            return

        try:
            # Parse the FTML
            logger.debug("Parsing FTML for validation")
            ftml.load(content)
            logger.debug("FTML parsed successfully")

            # Set success status
            self.status_label.setText("✓ Valid FTML")
            self.status_label.setStyleSheet("color: green;")

            # Hide error details
            self.error_details_panel.setVisible(False)
            self.error_details_btn.setVisible(False)

        except FTMLParseError as e:
            error_message = str(e)
            logger.debug(f"FTML parse error in parse_ftml: {error_message}")

            # Set error status
            self.status_label.setText("✗ Parsing Error")
            self.status_label.setStyleSheet("color: red;")

            # Show error details
            self.error_details_btn.setVisible(True)
            self.error_details_text.setPlainText(f"Error: {error_message}")

        except Exception as e:
            logger.debug(f"Other error in parse_ftml: {str(e)}")

            # Set error status
            self.status_label.setText(f"✗ Error: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

            # Show error details
            self.error_details_btn.setVisible(True)
            self.error_details_text.setPlainText(f"Error: {str(e)}")


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


# Create a mock version of the FTMLASTHighlighter class for testing
# This is needed if you want to test the code without modifying the actual highlighter class
class MockFTMLASTHighlighter(FTMLASTHighlighter):
    def __init__(self, document, theme_manager, error_highlighting=True, parse_delay=500):
        super().__init__(document, theme_manager, error_highlighting, parse_delay)
        self.autoparse_enabled = True

    def set_autoparse(self, enabled):
        """Set whether autoparse is enabled"""
        self.autoparse_enabled = enabled
        logger.debug(f"Mock highlighter autoparse set to: {enabled}")

# Monkey patch the FTMLASTHighlighter class to support autoparse
if not hasattr(FTMLASTHighlighter, 'set_autoparse'):
    def set_autoparse(self, enabled):
        """Set whether autoparse is enabled"""
        self.autoparse_enabled = enabled
        logger.debug(f"Highlighter autoparse set to: {enabled}")

    FTMLASTHighlighter.set_autoparse = set_autoparse
    FTMLASTHighlighter.autoparse_enabled = True

# Allow standalone execution for testing
if __name__ == "__main__":
    # Set up proper debug logging
    current_level = os.environ.get('FTML_STUDIO_LOG_LEVEL', 'DEBUG')
    logger = setup_logger("ftml_studio.editor_window", current_level)
    logger.debug(f"Starting FTML Studio application with log level: {current_level}")

    # Also set up logging for the enhanced text edit
    enhanced_logger = setup_logger("enhanced_text_edit", current_level)

    # Create Qt application
    app = QApplication(sys.argv)

    # Apply initial theme
    theme_manager.apply_theme(app)

    # Create and show test window
    window = FTMLEditorTestWindow()
    window.show()

    sys.exit(app.exec())
