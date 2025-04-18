# src/ftml_studio/ui/editor_window.py
import sys
import logging
from PySide6.QtWidgets import (QMainWindow, QSplitter, QTextEdit, QVBoxLayout, QHBoxLayout,
                               QPushButton, QWidget, QLabel, QFileDialog, QMessageBox,
                               QApplication, QMenu, QTabWidget, QCheckBox)
from PySide6.QtCore import QSettings, QTimer, Qt, Signal
from PySide6.QtGui import QFont, QTextCursor, QAction, QActionGroup

import ftml
from ftml.exceptions import FTMLParseError, FTMLValidationError

from src.ftml_studio.ui.base_window import BaseWindow
from src.ftml_studio.ui.themes import theme_manager

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("editor_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ftml_editor")

class FTMLEditor(QTextEdit):
    """Enhanced text editor for FTML content with error highlighting"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLineWrapMode(QTextEdit.NoWrap)
        font = QFont("Fira Code", 10)
        font.setFixedPitch(True)
        self.setFont(font)

        # Current error information
        self.error_line = -1
        self.error_col = -1
        self.error_length = 0

    def highlight_error(self, line, col, length=1):
        """Highlight the current error position"""
        self.error_line = line
        self.error_col = col
        self.error_length = length

        # Move cursor to error position
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        for _ in range(line - 1):
            cursor.movePosition(QTextCursor.NextBlock)
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, col - 1)

        # Select error text
        for _ in range(length):
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)

        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def clear_error_highlighting(self):
        """Clear error highlighting"""
        self.error_line = -1
        self.error_col = -1
        self.error_length = 0

class EditorWindow(BaseWindow):
    """Window for editing and validating FTML documents"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FTML Editor")
        self.resize(1200, 800)
        logger.debug("Initializing EditorWindow")

        # Create settings to store window state
        self.settings = QSettings("FTMLStudio", "EditorWindow")

        # Validation timer to prevent excessive validation attempts while typing
        self.validation_timer = QTimer(self)
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self.validate_ftml)

        # Restore window geometry if available
        self.restore_geometry()

    def setup_ui(self):
        logger.debug("Setting up EditorWindow UI")
        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Top toolbar with actions
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # File operations buttons
        self.load_ftml_btn = QPushButton("Load FTML")
        self.load_ftml_btn.clicked.connect(lambda: self.load_file("ftml"))
        self.load_schema_btn = QPushButton("Load Schema")
        self.load_schema_btn.clicked.connect(lambda: self.load_file("schema"))
        self.save_ftml_btn = QPushButton("Save FTML")
        self.save_ftml_btn.clicked.connect(lambda: self.save_file("ftml"))
        self.save_schema_btn = QPushButton("Save Schema")
        self.save_schema_btn.clicked.connect(lambda: self.save_file("schema"))

        # Auto-validate checkbox
        self.auto_validate_check = QCheckBox("Auto Validate")
        self.auto_validate_check.setChecked(True)
        self.auto_validate_check.stateChanged.connect(self.toggle_auto_validate)

        # Validate button
        self.validate_btn = QPushButton("Validate")
        self.validate_btn.setObjectName("validateButton")
        self.validate_btn.clicked.connect(self.validate_ftml)

        # Add to top layout
        top_layout.addWidget(self.load_ftml_btn)
        top_layout.addWidget(self.save_ftml_btn)
        top_layout.addWidget(self.load_schema_btn)
        top_layout.addWidget(self.save_schema_btn)
        top_layout.addStretch(1)
        top_layout.addWidget(self.auto_validate_check)
        top_layout.addWidget(self.validate_btn)

        # Main content splitter
        content_splitter = QSplitter(Qt.Horizontal)

        # Left side - FTML editor
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_label = QLabel("FTML Document")
        left_label.setStyleSheet("font-weight: bold;")
        self.ftml_editor = FTMLEditor()
        self.ftml_editor.textChanged.connect(self.on_ftml_changed)

        left_layout.addWidget(left_label)
        left_layout.addWidget(self.ftml_editor)

        # Right side - Schema editor and validation results
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_label = QLabel("FTML Schema")
        right_label.setStyleSheet("font-weight: bold;")
        self.schema_editor = QTextEdit()
        self.schema_editor.setLineWrapMode(QTextEdit.NoWrap)
        font = QFont("Fira Code", 10)
        font.setFixedPitch(True)
        self.schema_editor.setFont(font)
        self.schema_editor.textChanged.connect(self.on_schema_changed)

        # Validation results
        results_label = QLabel("Validation Results")
        results_label.setStyleSheet("font-weight: bold;")
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setMaximumHeight(150)

        right_layout.addWidget(right_label)
        right_layout.addWidget(self.schema_editor)
        right_layout.addWidget(results_label)
        right_layout.addWidget(self.results_display)

        # Add widgets to splitter
        content_splitter.addWidget(left_widget)
        content_splitter.addWidget(right_widget)
        content_splitter.setSizes([600, 600])  # Set initial sizes

        # Add everything to main layout
        main_layout.addWidget(top_panel)
        main_layout.addWidget(content_splitter, 1)

        # Create status bar
        self.statusBar().showMessage("Ready")

        # Create menu bar with theme selection
        self.create_menu_bar()

        # Apply syntax highlighting
        self.setup_syntax_highlighting()

        logger.debug("UI setup complete")

    def create_menu_bar(self):
        """Create the menu bar with theme options"""
        menu_bar = self.menuBar()

        # Create File menu
        file_menu = menu_bar.addMenu("File")

        # Add file actions
        new_action = QAction("New Document", self)
        new_action.triggered.connect(self.new_document)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        load_ftml_action = QAction("Load FTML", self)
        load_ftml_action.triggered.connect(lambda: self.load_file("ftml"))
        file_menu.addAction(load_ftml_action)

        load_schema_action = QAction("Load Schema", self)
        load_schema_action.triggered.connect(lambda: self.load_file("schema"))
        file_menu.addAction(load_schema_action)

        file_menu.addSeparator()

        save_ftml_action = QAction("Save FTML", self)
        save_ftml_action.triggered.connect(lambda: self.save_file("ftml"))
        file_menu.addAction(save_ftml_action)

        save_schema_action = QAction("Save Schema", self)
        save_schema_action.triggered.connect(lambda: self.save_file("schema"))
        file_menu.addAction(save_schema_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

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
        current_theme = theme_manager.current_theme
        if current_theme == "light":
            light_action.setChecked(True)
        elif current_theme == "dark":
            dark_action.setChecked(True)
        else:  # auto
            auto_action.setChecked(True)

    def change_theme(self, theme):
        """Change the application theme"""
        theme_manager.apply_theme(QApplication.instance(), theme)
        logger.debug(f"Changed theme to {theme}")
        # Update highlighters for new theme
        self.setup_syntax_highlighting()

    def setup_syntax_highlighting(self):
        """Set up syntax highlighting for FTML and Schema editors"""
        # Import highlighting classes here to avoid circular imports
        from src.ftml_studio.syntax.ast_highlighter import FTMLASTHighlighter
        from src.ftml_studio.syntax.schema_highlighter import SchemaHighlighter

        # Create and apply highlighters
        self.ftml_highlighter = FTMLASTHighlighter(self.ftml_editor.document(), theme_manager)
        self.schema_highlighter = SchemaHighlighter(self.schema_editor.document(), theme_manager)

    def new_document(self):
        """Create a new document"""
        # Ask to save if current document has changes
        # For now just clear both editors
        self.ftml_editor.clear()
        self.schema_editor.clear()
        self.results_display.clear()
        self.statusBar().showMessage("New document created")

    def toggle_auto_validate(self, state):
        """Toggle automatic validation when typing"""
        if state == Qt.Checked:
            logger.debug("Auto-validation enabled")
            # Validate current content
            self.validation_timer.start(1000)  # Validate after 1 second of inactivity
        else:
            logger.debug("Auto-validation disabled")
            self.validation_timer.stop()

    def on_ftml_changed(self):
        """Handle changes to FTML document"""
        if self.auto_validate_check.isChecked():
            # Restart validation timer
            self.validation_timer.start(1000)  # 1 second delay

    def on_schema_changed(self):
        """Handle changes to Schema document"""
        if self.auto_validate_check.isChecked():
            # Restart validation timer
            self.validation_timer.start(1000)  # 1 second delay

    def validate_ftml(self):
        """Validate FTML against the Schema"""
        ftml_content = self.ftml_editor.toPlainText()
        schema_content = self.schema_editor.toPlainText()

        if not ftml_content:
            self.results_display.setText("No FTML content to validate")
            self.statusBar().showMessage("No FTML content to validate")
            return

        self.ftml_editor.clear_error_highlighting()

        try:
            # First validate the FTML syntax
            if not schema_content:
                # Only validate FTML syntax if no schema is provided
                data = ftml.load(ftml_content)
                self.results_display.setStyleSheet("color: green;")
                self.results_display.setText("✓ FTML syntax is valid")
                self.statusBar().showMessage("FTML syntax validation successful")
            else:
                # Try to parse the schema first
                try:
                    from ftml.schema.schema_parser import SchemaParser
                    schema_parser = SchemaParser()
                    parsed_schema = schema_parser.parse(schema_content)

                    # Now validate the FTML against the schema
                    data = ftml.load(ftml_content, schema=parsed_schema)
                    self.results_display.setStyleSheet("color: green;")
                    self.results_display.setText("✓ FTML validates successfully against schema")
                    self.statusBar().showMessage("FTML schema validation successful")
                except ImportError:
                    # If SchemaParser is not available
                    logger.warning("Schema parser not available, falling back to direct schema string")
                    # Validate using the schema as a string directly
                    data = ftml.load(ftml_content, schema=schema_content)
                    self.results_display.setStyleSheet("color: green;")
                    self.results_display.setText("✓ FTML validates successfully against schema")
                    self.statusBar().showMessage("FTML schema validation successful")

        except FTMLParseError as e:
            # Handle parse error
            self.results_display.setStyleSheet("color: red;")
            error_message = f"❌ FTML Parse Error: {str(e)}"
            self.results_display.setText(error_message)
            self.statusBar().showMessage("FTML syntax error detected")

            # Highlight the error location if available
            if hasattr(e, "line") and hasattr(e, "col"):
                self.ftml_editor.highlight_error(e.line, e.col)

        except FTMLValidationError as e:
            # Handle validation error
            self.results_display.setStyleSheet("color: red;")
            error_message = f"❌ Schema Validation Error: {str(e)}"
            if hasattr(e, "errors") and e.errors:
                error_message += "\n\nDetails:"
                for err in e.errors:
                    error_message += f"\n- {err}"

            self.results_display.setText(error_message)
            self.statusBar().showMessage("FTML schema validation failed")

        except Exception as e:
            # Handle generic errors
            self.results_display.setStyleSheet("color: red;")
            self.results_display.setText(f"❌ Error: {str(e)}")
            self.statusBar().showMessage("Validation error")
            logger.error(f"Validation error: {str(e)}", exc_info=True)

    def load_file(self, file_type):
        """Load file content into the appropriate editor"""
        file_filter = ""
        if file_type == "ftml":
            file_filter = "FTML Files (*.ftml);;All Files (*)"
        elif file_type == "schema":
            file_filter = "FTML Schema Files (*.schema.ftml);;All Files (*)"

        file_path, _ = QFileDialog.getOpenFileName(
            self, f"Open {file_type.upper()} File", "", file_filter)

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if file_type == "ftml":
                    self.ftml_editor.setPlainText(content)
                    self.statusBar().showMessage(f"Loaded FTML file: {file_path}")
                elif file_type == "schema":
                    self.schema_editor.setPlainText(content)
                    self.statusBar().showMessage(f"Loaded Schema file: {file_path}")

                logger.info(f"Successfully loaded {file_type} file: {file_path}")

                # Validate after loading
                if self.auto_validate_check.isChecked():
                    self.validate_ftml()

            except Exception as e:
                logger.error(f"Error loading file: {str(e)}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def save_file(self, file_type):
        """Save editor content to a file"""
        content = ""
        file_filter = ""

        if file_type == "ftml":
            content = self.ftml_editor.toPlainText()
            file_filter = "FTML Files (*.ftml);;All Files (*)"
            default_ext = ".ftml"
        elif file_type == "schema":
            content = self.schema_editor.toPlainText()
            file_filter = "FTML Schema Files (*.schema.ftml);;All Files (*)"
            default_ext = ".schema.ftml"

        if not content:
            QMessageBox.warning(self, "Warning", f"No {file_type} content to save")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Save {file_type.upper()} File", "", file_filter)

        if file_path:
            # Add default extension if not specified
            if not file_path.endswith(default_ext):
                file_path += default_ext

            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                self.statusBar().showMessage(f"Saved {file_type} to: {file_path}")
                logger.info(f"Successfully saved {file_type} to: {file_path}")

            except Exception as e:
                logger.error(f"Error saving file: {str(e)}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

    def save_geometry(self):
        """Save window position and size"""
        self.settings.setValue("geometry", self.saveGeometry())

    def restore_geometry(self):
        """Restore window position and size"""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def closeEvent(self, event):
        """Handle window close event"""
        self.save_geometry()
        super().closeEvent(event)

# Allow standalone execution
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    # Apply theme
    theme_manager.apply_theme(app)

    window = EditorWindow()
    window.show()
    sys.exit(app.exec())