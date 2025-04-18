# src/ftml_studio/logger.py
"""
Logging configuration for FTML Studio
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Logging levels dictionary for easy reference
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# Default level
DEFAULT_LEVEL = "INFO"


def get_logs_dir():
    """
    Determine the logs directory based on whether the package is installed
    or running from source.
    """
    # When running as an installed package
    if getattr(sys, 'frozen', False):
        # For PyInstaller
        app_dir = os.path.dirname(sys.executable)
        logs_dir = os.path.join(app_dir, 'logs')
    elif __package__:
        # When installed with pip
        home_dir = str(Path.home())
        logs_dir = os.path.join(home_dir, '.ftml_studio', 'logs')
    else:
        # When running from source
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logs_dir = os.path.join(app_dir, 'logs')

    # Ensure log directory exists
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir


def setup_logger(name=None, level=None):
    """
    Set up and configure a logger with the specified name and level.

    Args:
        name: Logger name (default is root logger)
        level: Logging level (default from environment or DEFAULT_LEVEL)

    Returns:
        Configured logger instance
    """
    # Get level from environment variable, parameter, or default
    log_level = level or os.environ.get('FTML_STUDIO_LOG_LEVEL', DEFAULT_LEVEL)

    # Convert string to logging level
    if isinstance(log_level, str):
        log_level = LOG_LEVELS.get(log_level.upper(), LOG_LEVELS[DEFAULT_LEVEL])

    # Get or create logger
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(log_level)

        # Create logs directory if needed
        logs_dir = get_logs_dir()

        # Common format for all handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # File handler with rotation (max 5MB, keep 3 backups)
        log_file = os.path.join(logs_dir, f"{name or 'ftml_studio'}.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Prevent propagation to root logger to avoid duplicate logs
        logger.propagate = False

    return logger


# Create and configure the default logger
default_logger = setup_logger('ftml_studio')
