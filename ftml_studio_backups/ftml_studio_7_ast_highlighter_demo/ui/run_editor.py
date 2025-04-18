#!/usr/bin/env python
"""
FTML Studio - Editor Launcher

This script launches the FTML Editor component of FTML Studio.
"""

import sys
import os
import logging
from PySide6.QtWidgets import QApplication

# Set up the logging level
logging.basicConfig(level=logging.INFO)

# Add the parent directory to the path so we can import the src module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    """Launch the FTML Editor application"""
    from src.ftml_studio.ui.elements.ftml_editor import EditorWindow
    from src.ftml_studio.ui.themes import theme_manager

    app = QApplication(sys.argv)

    # Apply theme
    theme_manager.apply_theme(app)

    # Create and show editor window
    window = EditorWindow()
    window.show()

    # Add example content if specified
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        window.ftml_editor.setPlainText("""//! Sample FTML Document
// Basic key-value pairs
name = "My Application"
version = "1.0"

// Object example
server = {
    host = "localhost",
    port = 8080,
    debug = true
}

// List example
features = [
    "authentication",
    "logging",
    "caching"
]
""")

        window.schema_editor.setPlainText("""//! Sample FTML Schema
// Basic scalar types
name: str<min_length=1>
version: str

// Object with constraints
server: {
    host: str,
    port: int<min=1024, max=65535>,
    debug: bool
}

// List with constraints
features: [str]<min=1>
""")

        # Validate the demo content
        window.validate_ftml()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())