# src/ftml_studio/__main__.py
"""
FTML Studio - A modern editor for FTML markup language

This is the main entry point when running the package directly:
python -m ftml_studio
"""

import sys
from src.ftml_studio.cli import main

if __name__ == "__main__":
    sys.exit(main())