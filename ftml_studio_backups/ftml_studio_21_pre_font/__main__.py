# src/ftml_studio/__main__.py
"""
FTML Studio - Main entry point
Use CLI for launching: python -m ftml_studio [command]

For quick debugging, uncomment the desired log level below:
"""

import os
from src.ftml_studio.logger import setup_logger
from src.ftml_studio.cli import main

# Quick debug level setting - uncomment ONE of these lines:
# os.environ['FTML_STUDIO_LOG_LEVEL'] = 'DEBUG'  # Show all debug messages
# os.environ['FTML_STUDIO_LOG_LEVEL'] = 'INFO'     # Show informational messages and above
# os.environ['FTML_STUDIO_LOG_LEVEL'] = 'WARNING'  # Show only warnings and errors
# os.environ['FTML_STUDIO_LOG_LEVEL'] = 'ERROR'    # Show only errors

if __name__ == "__main__":
    # Get the current log level (from environment or default)
    current_level = os.environ.get('FTML_STUDIO_LOG_LEVEL', 'INFO')

    # Configure initial logger for startup messages
    logger = setup_logger('ftml_studio.startup')
    logger.debug(f"Starting FTML Studio application with log level: {current_level}")

    # Run the main CLI function
    main()
