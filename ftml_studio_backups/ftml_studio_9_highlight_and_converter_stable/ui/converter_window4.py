# src/ftml_studio/ui/converter_window.py
import sys
import logging
from PySide6.QtWidgets import (QMainWindow, QSplitter, QTextEdit, QComboBox,
                               QPushButton, QVBoxLayout, QWidget,
                               QHBoxLayout, QLabel, QFileDialog,
                               QMessageBox, QApplication, QMenu)
from PySide6.QtGui import QFont, Qt, QActionGroup, QAction
from PySide6.QtCore import QSettings
import ftml
from ftml.exceptions import FTMLParseError

from src.ftml_studio.converters.ftml_conversion_validator import FTMLConversionValidator


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("converter_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ftml_converter")

# Import converter and theme manager
from src.ftml_studio.converters.json_converter import JSONConverter
from src.ftml_studio.ui.themes import theme_manager

# Create a simple FormatSelector widget
class FormatSelector(QWidget):
    """Format selector with label"""

    def __init__(self, label_text, formats, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label_text)
        self.combo = QComboBox()

        for fmt in formats:
            self.combo.addItem(fmt)

        layout.addWidget(self.label)
        layout.addWidget(self.combo)

    def get_selected_format(self):
        """Get the currently selected format"""
        return self.combo.currentText()

    def set_selected_format(self, format):
        """Set the selected format"""
        index = self.combo.findText(format)
        if index >= 0:
            self.combo.setCurrentIndex(index)

# Get converter for the specified formats
def get_converter(source_fmt, target_fmt):
    """Return the appropriate converter based on source and target formats"""
    logger.debug(f"Getting converter for {source_fmt} to {target_fmt}")

    # FTML conversions
    if source_fmt.lower() == "json" and target_fmt.lower() == "ftml":
        logger.debug("Creating JSON to FTML converter")
        return JSONConverter(reverse=True)
    elif source_fmt.lower() == "ftml" and target_fmt.lower() == "json":
        logger.debug("Creating FTML to JSON converter")
        return JSONConverter(reverse=False)
    elif source_fmt.lower() == "yaml" and target_fmt.lower() == "ftml":
        logger.debug("Creating YAML to FTML converter")
        from src.ftml_studio.converters.yaml_converter import YAMLConverter
        return YAMLConverter(reverse=True)
    elif source_fmt.lower() == "ftml" and target_fmt.lower() == "yaml":
        logger.debug("Creating FTML to YAML converter")
        from src.ftml_studio.converters.yaml_converter import YAMLConverter
        return YAMLConverter(reverse=False)
    elif source_fmt.lower() == "toml" and target_fmt.lower() == "ftml":
        logger.debug("Creating TOML to FTML converter")
        from src.ftml_studio.converters.toml_converter import TOMLConverter
        return TOMLConverter(reverse=True)
    elif source_fmt.lower() == "ftml" and target_fmt.lower() == "toml":
        logger.debug("Creating FTML to TOML converter")
        from src.ftml_studio.converters.toml_converter import TOMLConverter
        return TOMLConverter(reverse=False)
    elif source_fmt.lower() == "xml" and target_fmt.lower() == "ftml":
        logger.debug("Creating XML to FTML converter")
        from src.ftml_studio.converters.xml_converter import XMLConverter
        return XMLConverter(reverse=True)
    elif source_fmt.lower() == "ftml" and target_fmt.lower() == "xml":
        logger.debug("Creating FTML to XML converter")
        from src.ftml_studio.converters.xml_converter import XMLConverter
        return XMLConverter(reverse=False)

    # Direct format conversions
    elif source_fmt.lower() == "json" and target_fmt.lower() == "yaml":
        logger.debug("Creating JSON to YAML converter")
        from src.ftml_studio.converters.yaml_converter import JSONToYAMLConverter
        return JSONToYAMLConverter()
    elif source_fmt.lower() == "yaml" and target_fmt.lower() == "json":
        logger.debug("Creating YAML to JSON converter")
        from src.ftml_studio.converters.yaml_converter import YAMLToJSONConverter
        return YAMLToJSONConverter()
    elif source_fmt.lower() == "json" and target_fmt.lower() == "toml":
        logger.debug("Creating JSON to TOML converter")
        from src.ftml_studio.converters.toml_converter import JSONToTOMLConverter
        return JSONToTOMLConverter()
    elif source_fmt.lower() == "toml" and target_fmt.lower() == "json":
        logger.debug("Creating TOML to JSON converter")
        from src.ftml_studio.converters.toml_converter import TOMLToJSONConverter
        return TOMLToJSONConverter()
    elif source_fmt.lower() == "json" and target_fmt.lower() == "xml":
        logger.debug("Creating JSON to XML converter")
        from src.ftml_studio.converters.xml_converter import JSONToXMLConverter
        return JSONToXMLConverter()
    elif source_fmt.lower() == "xml" and target_fmt.lower() == "json":
        logger.debug("Creating XML to JSON converter")
        from src.ftml_studio.converters.xml_converter import XMLToJSONConverter
        return XMLToJSONConverter()
    else:
        logger.warning(f"Unsupported conversion: {source_fmt} to {target_fmt}")
        raise ValueError(f"Conversion from {source_fmt} to {target_fmt} is not supported")

class ConverterWindow(QMainWindow):
    """Window for converting between FTML and other formats"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FTML Converter")
        self.resize(800, 600)
        logger.debug("Initializing ConverterWindow")

        # Create settings to store window state
        self.settings = QSettings("FTMLStudio", "ConverterWindow")

        # Set up the UI
        self.setup_ui()

        # Restore window geometry if available
        self.restore_geometry()

    def setup_ui(self):
        logger.debug("Setting up ConverterWindow UI")
        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Top controls panel
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(15)

        # Format selections
        supported_formats = ["ftml", "json", "yaml", "toml", "xml"]
        self.source_format = FormatSelector("Source Format:", supported_formats)
        self.target_format = FormatSelector("Target Format:", supported_formats)

        # Set default formats
        self.source_format.set_selected_format("json")
        self.target_format.set_selected_format("ftml")

        # Load/Save buttons
        self.load_btn = QPushButton("Load File")
        self.load_btn.clicked.connect(self.load_file)
        self.save_btn = QPushButton("Save Result")
        self.save_btn.clicked.connect(self.save_result)

        # Add to top panel
        top_layout.addWidget(self.source_format)
        top_layout.addWidget(self.load_btn)
        top_layout.addWidget(self.target_format)
        top_layout.addWidget(self.save_btn)

        # Conversion status area
        self.conversion_info = QLabel("Ready to convert")
        self.conversion_info.setObjectName("conversionInfo")  # For targeted styling
        self.conversion_info.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Convert button - full width
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.setObjectName("convertButton")  # For targeted styling
        self.convert_btn.clicked.connect(self.convert)

        # Text areas
        splitter = QSplitter()
        self.source_text = QTextEdit()
        self.target_text = QTextEdit()
    
        # Set monospace font
        font = QFont("Fira Code", 10)  # Or "Courier New" if Fira Code isn't available
        font.setFixedPitch(True)
        self.source_text.setFont(font)
        self.target_text.setFont(font)
    
        # Apply syntax highlighting based on selected formats
        self.update_syntax_highlighting()
    
        # Connect format selection changes to update highlighting
        self.source_format.combo.currentIndexChanged.connect(self.update_syntax_highlighting)
        self.target_format.combo.currentIndexChanged.connect(self.update_syntax_highlighting)

        splitter.addWidget(self.source_text)
        splitter.addWidget(self.target_text)
        splitter.setSizes([400, 400])

        # Create status bar
        self.statusBar().showMessage("Ready")

        # Create menu bar with theme selection
        self.create_menu_bar()

        # Layout assembly
        layout.addWidget(top_panel)
        layout.addWidget(splitter, 1)
        layout.addWidget(self.convert_btn)
        # layout.addWidget(self.conversion_info)

        logger.debug("UI setup complete")



    def validate_ftml(self, ftml_content):
        """
        Validates if the given content is valid FTML
        Returns (is_valid, error_message)
        """
        logger.debug("Validating FTML content")
        if not ftml_content.strip():
            return False, "Empty FTML content"
    
        try:
            # Try to parse the FTML using our parser
            parser = FTMLConversionValidator()
            parser.parse(ftml_content)
            return True, "FTML validation successful"
        except FTMLParseError as e:
            logger.error(f"FTML validation error: {str(e)}", exc_info=True)
            return False, f"Invalid FTML: {str(e)}"
        except Exception as e:
            logger.error(f"FTML validation error: {str(e)}", exc_info=True)
            return False, f"Invalid FTML: {str(e)}"


    def update_syntax_highlighting(self):
        """Update syntax highlighting based on selected formats"""
        # Import highlighters on-demand
        from src.ftml_studio.syntax import (
            JSONHighlighter, YAMLHighlighter,
            TOMLHighlighter, XMLHighlighter, FTMLASTHighlighter
        )
    
        # Source highlighting - first clear any existing highlighter by setting document to None
        if hasattr(self, 'source_highlighter'):
            self.source_highlighter.setDocument(None)
    
        # Create new highlighter based on source format
        source_format = self.source_format.get_selected_format().lower()
        if source_format == "ftml":
            self.source_highlighter = FTMLASTHighlighter(self.source_text.document(), theme_manager)
        elif source_format == "json":
            self.source_highlighter = JSONHighlighter(self.source_text.document(), theme_manager)
        elif source_format == "yaml":
            self.source_highlighter = YAMLHighlighter(self.source_text.document(), theme_manager)
        elif source_format == "toml":
            self.source_highlighter = TOMLHighlighter(self.source_text.document(), theme_manager)
        elif source_format == "xml":
            self.source_highlighter = XMLHighlighter(self.source_text.document(), theme_manager)
    
        # Target highlighting - first clear any existing highlighter by setting document to None
        if hasattr(self, 'target_highlighter'):
            self.target_highlighter.setDocument(None)
    
        # Create new highlighter based on target format
        target_format = self.target_format.get_selected_format().lower()
        if target_format == "ftml":
            self.target_highlighter = FTMLASTHighlighter(self.target_text.document(), theme_manager)
        elif target_format == "json":
            self.target_highlighter = JSONHighlighter(self.target_text.document(), theme_manager)
        elif target_format == "yaml":
            self.target_highlighter = YAMLHighlighter(self.target_text.document(), theme_manager)
        elif target_format == "toml":
            self.target_highlighter = TOMLHighlighter(self.target_text.document(), theme_manager)
        elif target_format == "xml":
            self.target_highlighter = XMLHighlighter(self.target_text.document(), theme_manager)
        
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
        self.light_action = QAction("Light", self, checkable=True)
        self.dark_action = QAction("Dark", self, checkable=True)
        self.auto_action = QAction("Auto (System)", self, checkable=True)
    
        # Add actions to group and menu
        theme_group.addAction(self.light_action)
        theme_group.addAction(self.dark_action)
        theme_group.addAction(self.auto_action)
    
        theme_menu.addAction(self.light_action)
        theme_menu.addAction(self.dark_action)
        theme_menu.addAction(self.auto_action)
    
        # Connect actions to theme change
        self.light_action.triggered.connect(lambda: self.change_theme(theme_manager.LIGHT))
        self.dark_action.triggered.connect(lambda: self.change_theme(theme_manager.DARK))
        self.auto_action.triggered.connect(lambda: self.change_theme(theme_manager.AUTO))
    
        # Update theme menu to match current theme
        self.update_theme_menu()

    def update_theme_menu(self):
        """Update theme menu to reflect current theme"""
        current_theme = theme_manager.current_theme
    
        self.light_action.setChecked(current_theme == theme_manager.LIGHT)
        self.dark_action.setChecked(current_theme == theme_manager.DARK)
        self.auto_action.setChecked(current_theme == theme_manager.AUTO)
    
    def change_theme(self, theme):
        """Change the application theme"""
        # Set theme in global theme manager
        theme_manager.set_theme(theme)
    
        # Apply the theme
        app = QApplication.instance()
        theme_manager.apply_theme(app)
    
        # Update highlighting for new theme
        self.recreate_highlighters()
    
        logger.debug(f"Changed theme to {theme}")

    def recreate_highlighters(self):
        """Recreate the highlighters to apply new theme colors"""
        # Store current content
        source_content = self.source_text.toPlainText()
        target_content = self.target_text.toPlainText()
    
        # Re-apply syntax highlighting based on selected formats
        self.update_syntax_highlighting()
    
        # Restore content
        self.source_text.setPlainText(source_content)
        self.target_text.setPlainText(target_content)
    
    def save_geometry(self):
        """Save window position and size"""
        self.settings.setValue("geometry", self.saveGeometry())

    def restore_geometry(self):
        """Restore window position and size"""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def convert(self):
        """Convert from source format to target format"""
        source_fmt = self.source_format.get_selected_format()
        target_fmt = self.target_format.get_selected_format()
        source_content = self.source_text.toPlainText()
    
        self.conversion_info.setText(f"Converting from {source_fmt} to {target_fmt}...")
        self.statusBar().showMessage(f"Converting from {source_fmt} to {target_fmt}...")
    
        if not source_content:
            self.conversion_info.setText("⚠️ No content to convert")
            self.statusBar().showMessage("Warning: No content to convert")
            QMessageBox.warning(self, "Warning", "No content to convert")
            return
    
        try:
            converter = get_converter(source_fmt, target_fmt)
            result = converter.convert(source_content)
    
            # Temporarily remove highlighter to avoid parsing errors during text change
            if hasattr(self, 'target_highlighter'):
                self.target_highlighter.setDocument(None)
    
            # Set the text content
            self.target_text.setPlainText(result)
    
            # Reapply highlighting with correct format
            self.update_syntax_highlighting()
    
            # If target is FTML, validate it
            if target_fmt.lower() == "ftml":
                is_valid, error_msg = self.validate_ftml(result)
                if not is_valid:
                    self.conversion_info.setText(f"❌ Conversion failed: {error_msg}")
                    self.statusBar().showMessage(f"Conversion failed: Invalid FTML")
                    logger.warning(f"FTML validation failed: {error_msg}")
                    QMessageBox.warning(self, "Validation Error",
                                        f"The conversion completed but produced invalid FTML:\n\n{error_msg}")
                    return
    
            success_msg = f"✅ Successfully converted from {source_fmt} to {target_fmt}"
            self.conversion_info.setText(success_msg)
            self.statusBar().showMessage(success_msg)
            logger.info(f"Conversion from {source_fmt} to {target_fmt} successful")
    
        except Exception as e:
            error_msg = f"❌ Conversion failed: {str(e)}"
            self.conversion_info.setText(error_msg)
            self.statusBar().showMessage(error_msg)
            self.target_text.setPlainText(f"Error: {str(e)}")
            logger.error(f"Conversion error: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Conversion Error", str(e))

    def load_file(self):
        """Load content from a file"""
        source_fmt = self.source_format.get_selected_format()
        file_filter = f"{source_fmt.upper()} Files (*.{source_fmt});;All Files (*)"

        logger.debug(f"Opening file dialog for {source_fmt} files")
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"Open {source_fmt.upper()} File", "", file_filter)

        if file_path:
            logger.debug(f"Loading file: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.source_text.setPlainText(content)
                self.statusBar().showMessage(f"Loaded file: {file_path}")
                logger.info(f"Successfully loaded file: {file_path}")
            except Exception as e:
                logger.error(f"Error loading file: {str(e)}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def save_result(self):
        """Save conversion result to a file"""
        target_fmt = self.target_format.get_selected_format()
        result_content = self.target_text.toPlainText()

        if not result_content:
            logger.warning("No content to save")
            QMessageBox.warning(self, "Warning", "No content to save")
            return

        file_filter = f"{target_fmt.upper()} Files (*.{target_fmt});;All Files (*)"

        logger.debug(f"Opening save dialog for {target_fmt} files")
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Save {target_fmt.upper()} File", "", file_filter)

        if file_path:
            logger.debug(f"Saving to file: {file_path}")
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(result_content)
                self.statusBar().showMessage(f"Saved to file: {file_path}")
                logger.info(f"Successfully saved to file: {file_path}")
                QMessageBox.information(self, "Success", f"File saved successfully")
            except Exception as e:
                logger.error(f"Error saving file: {str(e)}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

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

    window = ConverterWindow()
    window.show()
    sys.exit(app.exec())