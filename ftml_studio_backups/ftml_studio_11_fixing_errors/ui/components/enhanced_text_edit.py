# src/ftml_studio/ui/components/enhanced_text_edit.py

import logging
from PySide6.QtWidgets import QTextEdit, QToolTip
from PySide6.QtGui import QTextCursor, QTextCharFormat, QColor

logger = logging.getLogger("enhanced_text_edit")

class EnhancedTextEdit(QTextEdit):
    """Enhanced QTextEdit with improved tooltip support for error indicators"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        # Store multiple errors instead of just one
        self.error_positions = []  # List of {position, message} dictionaries
        self.error_selections = []

        # Reference to the highlighter
        self.highlighter = None

    def setHighlighter(self, highlighter):
        """Set the syntax highlighter and connect error signals if applicable"""
        self.highlighter = highlighter

        # If the highlighter has errors, we should update our error positions
        if hasattr(self.highlighter, 'errors'):
            # Connect to error changes when the highlighter updates
            if hasattr(self.highlighter, 'errorsChanged'):
                self.highlighter.errorsChanged.connect(self.updateErrorPositions)

    def updateErrorPositions(self, errors=None):
        """Update error positions from highlighter or direct input"""
        if errors is not None:
            self.error_positions = errors
        elif self.highlighter and hasattr(self.highlighter, 'errors'):
            # Convert highlighter errors to positions for tooltips
            self._convertHighlighterErrors()

        # Force update to ensure tooltips work right away
        self.update()

    def _convertHighlighterErrors(self):
        """Convert errors from highlighter format to position format for tooltips"""
        self.error_positions = []

        if not hasattr(self.highlighter, 'errors'):
            return

        for error in self.highlighter.errors:
            # Skip errors without position info
            if 'line' not in error or 'col' not in error:
                continue

            line = error.get('line', 0)
            col = error.get('col', 0)
            message = error.get('message', '')

            # Create a cursor at the error position
            cursor = QTextCursor(self.document())
            cursor.movePosition(QTextCursor.Start)

            # Move to the correct line
            for i in range(line - 1):
                if not cursor.movePosition(QTextCursor.NextBlock):
                    logger.warning(f"Could not move to line {line}, stopped at line {i+1}")
                    break

            # Move to the column
            if col > 1:
                for i in range(col - 1):
                    if not cursor.movePosition(QTextCursor.Right):
                        logger.warning(f"Could not move to column {col}, stopped at column {i+1}")
                        break

            # Store position info for tooltips
            self.error_positions.append({
                'position': cursor.position(),
                'message': message
            })

    def mouseMoveEvent(self, event):
        """Handle mouse movement to show tooltips over error positions"""
        super().mouseMoveEvent(event)

        if not self.error_positions:
            return

        cursor = self.cursorForPosition(event.pos())
        pos = cursor.position()

        # Check if cursor is near any error position
        for error in self.error_positions:
            error_pos = error.get('position', -1)
            error_msg = error.get('message', '')

            # Check if cursor is near the error position (with a small range to make selection easier)
            if error_pos >= 0 and abs(error_pos - pos) < 5:  # Using abs for a range around the error
                QToolTip.showText(event.globalPos(), error_msg)
                return

        # Hide tooltip if not over an error
        QToolTip.hideText()

    def setExtraSelections(self, selections):
        """Override to log extra selections being applied"""
        logger.debug(f"Setting {len(selections)} extra selections")
        self.error_selections = selections
        super().setExtraSelections(selections)
