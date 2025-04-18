# src/ftml_studio/ui/ftml_ast_demo.py
import sys
import logging
from PySide6.QtWidgets import (QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout,
                               QPushButton, QWidget, QLabel, QApplication, QSplitter)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QFont

import ftml
from ftml.exceptions import FTMLParseError

from src.ftml_studio.syntax import FTMLASTHighlighter

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("ftml_ast_demo")

# Import highlighter
sys.path.insert(0, '..')  # Make sure we can import from parent dir
# from syntax.ast_highlighter import FTMLASTHighlighter

class FTMLASTDemo(QMainWindow):
    """Simple demo window for the FTML AST Highlighter"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FTML AST Highlighter Demo")
        self.resize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header
        header_label = QLabel("FTML AST Highlighter Demo")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(header_label)

        # Description
        desc_label = QLabel("Edit FTML content below to see syntax highlighting based on the AST.")
        main_layout.addWidget(desc_label)

        # Create a splitter for the editor and output
        splitter = QSplitter(Qt.Vertical)

        # Editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Enter FTML here...")
        font = QFont("Courier New", 10)
        font.setFixedPitch(True)
        self.editor.setFont(font)

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

        # Apply highlighter
        self.highlighter = FTMLASTHighlighter(self.editor.document(), None)

        # Parse status
        self.status_label = QLabel()
        self.update_status()

        # Parse button
        parse_btn = QPushButton("Parse FTML")
        parse_btn.clicked.connect(self.parse_ftml)

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
        self.editor.textChanged.connect(self.update_status)

    def update_status(self):
        """Update the parse status"""
        content = self.editor.toPlainText()
    
        # Clear any previous error highlighting when content changes
        self.editor.setExtraSelections([])
    
        if not content:
            self.status_label.setText("Empty document")
            self.status_label.setStyleSheet("color: gray;")
            return
    
        try:
            # Try to parse
            data = ftml.load(content)
            self.status_label.setText("✓ Valid FTML")
            self.status_label.setStyleSheet("color: green;")
        except FTMLParseError as e:
            self.status_label.setText(f"✗ Parse error: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
    
            # Highlight the error location
            if hasattr(e, "line") and hasattr(e, "col"):
                self.highlight_error_position(e.line, e.col, str(e))
        except Exception as e:
            self.status_label.setText(f"✗ Error: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

    def parse_ftml(self):
        """Parse the FTML and show the result"""
        content = self.editor.toPlainText()
        if not content:
            self.output.setPlainText("No content to parse")
            return
    
        # Clear any previous error highlighting
        self.editor.setExtraSelections([])
    
        try:
            # Parse the FTML
            data = ftml.load(content)
    
            # Format and display the output
            import json
            formatted = json.dumps(data, indent=2)
            self.output.setPlainText(formatted)
    
        except FTMLParseError as e:
            self.output.setPlainText(f"Error parsing FTML:\n{str(e)}")
    
            # Highlight the error location
            if hasattr(e, "line") and hasattr(e, "col"):
                self.highlight_error_position(e.line, e.col, str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FTMLASTDemo()
    window.show()
    sys.exit(app.exec())