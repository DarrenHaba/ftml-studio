# src/ftml_studio/ui/converter_window.py
import sys
import logging
from PySide6.QtWidgets import (QMainWindow, QSplitter, QTextEdit, QComboBox,
                               QPushButton, QVBoxLayout, QWidget,
                               QHBoxLayout, QLabel, QFileDialog,
                               QMessageBox, QApplication)
from PySide6.QtGui import QFont

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

# Import the actual converter
from src.ftml_studio.converters.json_converter import JSONConverter

# Create a simple FormatSelector right in this file to avoid import issues
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

# Connect to the actual converter
def get_converter(source_fmt, target_fmt):
    """Return the appropriate converter based on source and target formats"""
    logger.debug(f"Getting converter for {source_fmt} to {target_fmt}")

    if source_fmt.lower() == "json" and target_fmt.lower() == "ftml":
        logger.debug("Creating JSON to FTML converter")
        return JSONConverter(reverse=True)
    elif source_fmt.lower() == "ftml" and target_fmt.lower() == "json":
        logger.debug("Creating FTML to JSON converter")
        return JSONConverter(reverse=False)
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
        self.setup_ui()

    def setup_ui(self):
        logger.debug("Setting up ConverterWindow UI")
        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Top controls panel
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Format selections
        supported_formats = ["ftml", "json"]
        self.source_format = FormatSelector("Source Format:", supported_formats)
        self.target_format = FormatSelector("Target Format:", supported_formats)

        # Set default formats for common conversion
        self.source_format.set_selected_format("json")
        self.target_format.set_selected_format("ftml")

        # Load button
        self.load_btn = QPushButton("Load File")
        self.load_btn.clicked.connect(self.load_file)

        # Save button
        self.save_btn = QPushButton("Save Result")
        self.save_btn.clicked.connect(self.save_result)

        # Add to top panel
        top_layout.addWidget(self.source_format)
        top_layout.addWidget(self.load_btn)
        top_layout.addWidget(self.target_format)
        top_layout.addWidget(self.save_btn)

        # Text areas
        splitter = QSplitter()
        self.source_text = QTextEdit()
        self.target_text = QTextEdit()

        # Set monospace font
        font = QFont("Courier New", 10)
        font.setFixedPitch(True)
        self.source_text.setFont(font)
        self.target_text.setFont(font)

        splitter.addWidget(self.source_text)
        splitter.addWidget(self.target_text)
        splitter.setSizes([400, 400])  # Equal size

        # Conversion info label
        self.conversion_info = QLabel("Ready to convert")
        self.conversion_info.setStyleSheet("""
            QLabel {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                padding: 5px;
                font-weight: bold;
            }
        """)

        # Convert button
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.clicked.connect(self.convert)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        # Status bar at the bottom
        self.status_area = QLabel("Ready")
        self.status_area.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border-top: 1px solid #ccc;
                padding: 5px;
                font-style: italic;
            }
        """)

        # Layout assembly
        layout.addWidget(top_panel)
        layout.addWidget(splitter, 1)  # Give splitter most of the space
        layout.addWidget(self.conversion_info)  # Add conversion info above the button
        layout.addWidget(self.convert_btn)
        layout.addWidget(self.status_area)  # Add status area at the bottom

        logger.debug("UI setup complete")

    def convert(self):
        """Convert from source format to target format"""
        source_fmt = self.source_format.get_selected_format()
        target_fmt = self.target_format.get_selected_format()
        source_content = self.source_text.toPlainText()

        logger.debug(f"Converting from {source_fmt} to {target_fmt}")
        logger.debug(f"Source content: {source_content[:100]}...")

        if not source_content:
            logger.warning("No content to convert")
            QMessageBox.warning(self, "Warning", "No content to convert")
            return

        try:
            # Update conversion info
            self.conversion_info.setText(f"Converting from {source_fmt} to {target_fmt}...")

            # Get the proper converter
            converter = get_converter(source_fmt, target_fmt)

            # Perform the conversion
            logger.debug("Starting conversion")
            result = converter.convert(source_content)
            logger.debug(f"Conversion result: {result[:100]}...")

            # Update the target text without prefixing
            self.target_text.setPlainText(result)

            # Update status
            self.conversion_info.setText(f"Converted from {source_fmt} to {target_fmt}")
            self.status_area.setText(f"Conversion successful")
            logger.info(f"Conversion from {source_fmt} to {target_fmt} successful")

        except Exception as e:
            logger.error(f"Conversion error: {str(e)}", exc_info=True)
            self.target_text.setPlainText(f"Error: {str(e)}")
            self.conversion_info.setText(f"Conversion failed")
            self.status_area.setText(f"Conversion error: {str(e)}")
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
                self.status_area.setText(f"Loaded file: {file_path}")
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
                self.status_area.setText(f"Saved to file: {file_path}")
                logger.info(f"Successfully saved to file: {file_path}")
                QMessageBox.information(self, "Success", f"File saved successfully")
            except Exception as e:
                logger.error(f"Error saving file: {str(e)}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

# Allow standalone execution
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)  # Create QApplication FIRST
    window = ConverterWindow()
    window.show()
    sys.exit(app.exec())  # Start the event loop