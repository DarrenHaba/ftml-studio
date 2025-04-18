# launch_editor.py
import sys
from PySide6.QtWidgets import QApplication
from src.ftml_studio.ui.elements.ftml_editor import EditorWindow
from src.ftml_studio.ui.themes import theme_manager

def main():
    """Launch the FTML Studio Editor"""
    app = QApplication(sys.argv)

    # Apply theme
    theme_manager.apply_theme(app)

    # Create and show editor window
    window = EditorWindow()
    window.show()

    # Load example content if needed
    if len(sys.argv) > 1:
        if sys.argv[1] == '--demo':
            # Load demo content
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