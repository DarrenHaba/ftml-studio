# src/ftml_studio/cli/__init__.py
import sys
import argparse

from ftml_studio.logger import setup_logger, LOG_LEVELS


def main():
    """Main entry point for the FTML Studio CLI"""
    parser = argparse.ArgumentParser(description="FTML Studio - A modern editor for FTML markup language")

    # Add global options
    parser.add_argument("--log-level", choices=list(LOG_LEVELS.keys()),
                        help="Set logging level")

    # Parse arguments
    args = parser.parse_args()

    # Configure logging based on CLI args or environment variable
    logger = setup_logger('ftml_cli', args.log_level if hasattr(args, 'log_level') else None)
    logger.info("Starting FTML Studio")

    # Import here to avoid circular imports
    try:
        from PySide6.QtWidgets import QApplication
        from ftml_studio.ui.themes import theme_manager
        from ftml_studio.ui.main_window import MainWindow
    except ImportError:
        logger.error("PySide6 is required but not installed. Please install it with: pip install PySide6")
        sys.exit(1)

    # Create application
    app = QApplication(sys.argv)
    theme_manager.apply_theme(app)

    # Launch main window
    window = MainWindow()
    window.setWindowTitle("FTML Studio - v0.1.0a1")
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
