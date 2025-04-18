# src/ftml_studio/cli/__init__.py
import sys
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ftml_cli")

def main():
    """Main entry point for the FTML Studio CLI"""
    parser = argparse.ArgumentParser(description="FTML Studio - A modern editor for FTML markup language")

    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Open command - default action to open the main app
    open_parser = subparsers.add_parser("open", help="Open the FTML Studio application")
    open_parser.add_argument("file", nargs="?", help="Optional FTML file to open")

    # Editor command - open just the editor
    editor_parser = subparsers.add_parser("editor", help="Open only the FTML editor")
    editor_parser.add_argument("file", nargs="?", help="Optional FTML file to open")

    # Converter command - open just the converter
    converter_parser = subparsers.add_parser("converter", help="Open only the format converter")
    converter_parser.add_argument("file", nargs="?", help="Optional file to convert")

    # Parse arguments
    args = parser.parse_args()

    # Default to 'open' if no command specified
    if not args.command:
        args.command = "open"
        args.file = None

    # Import here to avoid circular imports
    try:
        from PySide6.QtWidgets import QApplication
        from src.ftml_studio.ui.themes import theme_manager
    except ImportError:
        logger.error("PySide6 is required but not installed. Please install it with: pip install PySide6")
        sys.exit(1)

    # Create application
    app = QApplication(sys.argv)
    theme_manager.apply_theme(app)

    # Launch appropriate window based on command
    if args.command == "open":
        from src.ftml_studio.ui.main_window import MainWindow
        window = MainWindow()

        # TODO: If args.file is provided, open it in the editor

    elif args.command == "editor":
        from src.ftml_studio.ui.elements.ftml_editor import FTMLASTDemo
        window = FTMLASTDemo()

        # TODO: If args.file is provided, open it in the editor

    elif args.command == "converter":
        from src.ftml_studio.ui.elements.converter import ConverterWindow
        window = ConverterWindow()

        # TODO: If args.file is provided, open it in the converter

    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())