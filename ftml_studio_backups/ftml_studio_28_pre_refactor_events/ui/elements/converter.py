# src/ftml_studio/ui/elements/converter.py
import logging
import os
import sys
from PySide6.QtWidgets import (QWidget, QSplitter, QTextEdit, QComboBox,
                               QPushButton, QVBoxLayout,
                               QHBoxLayout, QLabel, QFileDialog,
                               QMessageBox, QApplication)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QSettings
from ftml.exceptions import FTMLParseError

from src.ftml_studio.logger import setup_logger, LOG_LEVELS
from src.ftml_studio.converters.ftml_conversion_validator import FTMLConversionValidator
from src.ftml_studio.converters.json_converter import JSONConverter
from src.ftml_studio.ui.themes import theme_manager

# Configure logging
logger = setup_logger("ftml_studio.converter")


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
    elif source_fmt.lower() == "yaml" and target_fmt.lower() == "toml":
        logger.debug("Creating YAML to TOML converter")
        from src.ftml_studio.converters.yaml_converter import YAMLToTOMLConverter
        return YAMLToTOMLConverter()
    elif source_fmt.lower() == "yaml" and target_fmt.lower() == "xml":
        logger.debug("Creating YAML to XML converter")
        from src.ftml_studio.converters.yaml_converter import YAMLToXMLConverter
        return YAMLToXMLConverter()
    elif source_fmt.lower() == "toml" and target_fmt.lower() == "yaml":
        logger.debug("Creating TOML to YAML converter")
        from src.ftml_studio.converters.toml_converter import TOMLToYAMLConverter
        return TOMLToYAMLConverter()
    elif source_fmt.lower() == "toml" and target_fmt.lower() == "xml":
        logger.debug("Creating TOML to XML converter")
        from src.ftml_studio.converters.toml_converter import TOMLToXMLConverter
        return TOMLToXMLConverter()
    elif source_fmt.lower() == "xml" and target_fmt.lower() == "yaml":
        logger.debug("Creating XML to YAML converter")
        from src.ftml_studio.converters.xml_converter import XMLToYAMLConverter
        return XMLToYAMLConverter()
    elif source_fmt.lower() == "xml" and target_fmt.lower() == "toml":
        logger.debug("Creating XML to TOML converter")
        from src.ftml_studio.converters.xml_converter import XMLToTOMLConverter
        return XMLToTOMLConverter()
    else:
        logger.warning(f"Unsupported conversion: {source_fmt} to {target_fmt}")
        raise ValueError(f"Conversion from {source_fmt} to {target_fmt} is not supported")


class ConverterWidget(QWidget):
    """Widget for converting between FTML and other formats"""

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("Initializing ConverterWidget")

        # Create settings to store widget state
        self.settings = QSettings("FTMLStudio", "ConverterWidget")

        # Get the global error indicators setting
        app_settings = QSettings("FTMLStudio", "AppSettings")
        self.error_highlighting_enabled = app_settings.value("editor/showErrorIndicators", True, type=bool)
        logger.debug(f"Initializing with error highlighting: {self.error_highlighting_enabled}")

        # Set up the UI
        self.setup_ui()

        # Restore splitter state if available
        self.restore_state()

    def setup_ui(self):
        logger.debug("Setting up ConverterWidget UI")
        # Main layout (directly applied to this widget)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create the main splitter
        self.splitter = QSplitter()

        # Create left and right containers for the splitter
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Set minimum widths to prevent complete collapse
        left_container.setMinimumWidth(200)
        right_container.setMinimumWidth(200)

        # Format selections
        supported_formats = ["ftml", "json", "yaml", "toml", "xml"]

        # Left controls (source format and load)
        left_controls = QWidget()
        left_controls_layout = QHBoxLayout(left_controls)
        left_controls_layout.setContentsMargins(0, 0, 0, 0)

        self.source_format = FormatSelector("Source Format:", supported_formats)
        self.source_format.set_selected_format("json")

        self.load_btn = QPushButton("Load File")
        self.load_btn.clicked.connect(self.load_file)

        left_controls_layout.addWidget(self.source_format)
        left_controls_layout.addWidget(self.load_btn)
        left_controls_layout.addStretch(1)  # This pushes controls to the left

        # Right controls (target format and save)
        right_controls = QWidget()
        right_controls_layout = QHBoxLayout(right_controls)
        right_controls_layout.setContentsMargins(0, 0, 0, 0)

        self.target_format = FormatSelector("Target Format:", supported_formats)
        self.target_format.set_selected_format("ftml")

        self.save_btn = QPushButton("Save Result")
        self.save_btn.clicked.connect(self.save_result)

        right_controls_layout.addWidget(self.target_format)
        right_controls_layout.addWidget(self.save_btn)
        right_controls_layout.addStretch(1)  # This pushes controls to the left

        # Text areas
        self.source_text = QTextEdit()
        self.target_text = QTextEdit()

        # Set monospace font
        font = QFont("Fira Code", 10)  # Or "Courier New" if Fira Code isn't available
        font.setFixedPitch(True)
        self.source_text.setFont(font)
        self.target_text.setFont(font)

        # Assemble the left container
        left_layout.addWidget(left_controls)
        left_layout.addWidget(self.source_text, 1)  # 1 gives it stretch priority

        # Assemble the right container
        right_layout.addWidget(right_controls)
        right_layout.addWidget(self.target_text, 1)  # 1 gives it stretch priority

        # Add containers to splitter
        self.splitter.addWidget(left_container)
        self.splitter.addWidget(right_container)
        self.splitter.setSizes([400, 400])  # Equal initial sizes

        # Create convert button in center area
        convert_container = QWidget()
        convert_layout = QHBoxLayout(convert_container)
        convert_layout.setContentsMargins(0, 0, 0, 0)

        self.convert_btn = QPushButton(" Convert → ")
        self.convert_btn.setObjectName("convertButton")  # Important for CSS styling
        self.convert_btn.clicked.connect(self.convert)

        # Create a centered button with arrow icon
        self.convert_btn = QPushButton(" Convert → ")
        self.convert_btn.setObjectName("convertButton")
        self.convert_btn.clicked.connect(self.convert)

        convert_layout.addWidget(self.convert_btn)

        # Create status label (replacement for statusBar)
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")

        # Add the splitter, convert button, and status label to the main layout
        main_layout.addWidget(self.splitter, 1)
        main_layout.addWidget(convert_container, 0, Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        # Apply syntax highlighting based on selected formats
        self.update_syntax_highlighting()

        # Connect format selection changes to update highlighting
        self.source_format.combo.currentIndexChanged.connect(self.update_syntax_highlighting)
        self.target_format.combo.currentIndexChanged.connect(self.update_syntax_highlighting)

        logger.debug("UI setup complete")

    def update_error_highlighting_setting(self, enabled):
        """Update the error highlighting setting for all FTML highlighters"""
        logger.debug(f"Updating error highlighting setting to: {enabled}")
        self.error_highlighting_enabled = enabled

        # Recreate highlighters to apply the setting
        self.update_syntax_highlighting()

    @staticmethod
    def validate_ftml(ftml_content):
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
        # Get the current global error indicators setting
        app_settings = QSettings("FTMLStudio", "AppSettings")
        self.error_highlighting_enabled = app_settings.value("editor/showErrorIndicators", True, type=bool)

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
            self.source_highlighter = FTMLASTHighlighter(
                self.source_text.document(),
                theme_manager,
                error_highlighting=self.error_highlighting_enabled  # Apply global setting
            )
            logger.debug(
                f"Created FTML highlighter for source with error highlighting={self.error_highlighting_enabled}")
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
            self.target_highlighter = FTMLASTHighlighter(
                self.target_text.document(),
                theme_manager,
                error_highlighting=self.error_highlighting_enabled  # Apply global setting
            )
            logger.debug(
                f"Created FTML highlighter for target with error highlighting={self.error_highlighting_enabled}")
        elif target_format == "json":
            self.target_highlighter = JSONHighlighter(self.target_text.document(), theme_manager)
        elif target_format == "yaml":
            self.target_highlighter = YAMLHighlighter(self.target_text.document(), theme_manager)
        elif target_format == "toml":
            self.target_highlighter = TOMLHighlighter(self.target_text.document(), theme_manager)
        elif target_format == "xml":
            self.target_highlighter = XMLHighlighter(self.target_text.document(), theme_manager)

    def recreate_highlighters(self):
        """Recreate the highlighters to apply new theme colors"""
        # Store current content
        source_content = self.source_text.toPlainText()
        target_content = self.target_text.toPlainText()

        # Get the current global error indicators setting
        app_settings = QSettings("FTMLStudio", "AppSettings")
        self.error_highlighting_enabled = app_settings.value("editor/showErrorIndicators", True, type=bool)
        logger.debug(f"Recreating highlighters with error highlighting={self.error_highlighting_enabled}")

        # Re-apply syntax highlighting based on selected formats
        self.update_syntax_highlighting()

        # Restore content
        self.source_text.setPlainText(source_content)
        self.target_text.setPlainText(target_content)

    def save_state(self):
        """Save splitter state"""
        self.settings.setValue("splitterState", self.splitter.saveState())

    def restore_state(self):
        """Restore splitter state"""
        splitter_state = self.settings.value("splitterState")
        if splitter_state:
            self.splitter.restoreState(splitter_state)

    def convert(self):
        """Convert from source format to target format"""
        source_fmt = self.source_format.get_selected_format()
        target_fmt = self.target_format.get_selected_format()
        source_content = self.source_text.toPlainText()

        # Update status label
        self.status_label.setText(f"Converting from {source_fmt} to {target_fmt}...")

        if not source_content:
            self.status_label.setText("⚠️ Warning: No content to convert")
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
                    self.status_label.setText("❌ Conversion failed: Invalid FTML")
                    logger.warning(f"FTML validation failed: {error_msg}")
                    QMessageBox.warning(self, "Validation Error",
                                        f"The conversion completed but produced invalid FTML:\n\n{error_msg}")
                    return

            success_msg = f"✅ Successfully converted from {source_fmt} to {target_fmt}"
            self.status_label.setText(success_msg)
            logger.info(f"Conversion from {source_fmt} to {target_fmt} successful")

        except Exception as e:
            error_msg = f"❌ Conversion failed: {str(e)}"
            self.status_label.setText(error_msg)
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
                self.status_label.setText(f"Loaded file: {file_path}")
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
                self.status_label.setText(f"Saved to file: {file_path}")
                logger.info(f"Successfully saved to file: {file_path}")
                QMessageBox.information(self, "Success", "File saved successfully")
            except Exception as e:
                logger.error(f"Error saving file: {str(e)}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")


# Allow standalone execution
if __name__ == "__main__":
    from PySide6.QtWidgets import QMainWindow

    current_level = os.environ.get('FTML_STUDIO_LOG_LEVEL', 'DEBUG')
    logger.setLevel(LOG_LEVELS.get(current_level, logging.DEBUG))
    logger.debug(f"Starting FTML Studio application with log level: {current_level}")

    app = QApplication(sys.argv)

    # Apply theme
    theme_manager.apply_theme(app)

    # Create main window and add converter widget
    main_window = QMainWindow()
    main_window.setWindowTitle("FTML Converter")
    main_window.resize(800, 600)

    converter = ConverterWidget()
    main_window.setCentralWidget(converter)

    main_window.show()
    sys.exit(app.exec())
