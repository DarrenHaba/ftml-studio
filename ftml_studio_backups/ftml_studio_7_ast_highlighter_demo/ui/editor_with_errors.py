# src/ftml_studio/ui/editor_with_errors.py
"""
Enhanced FTML editor with error indicators and tooltips
"""
import sys
from PySide6.QtWidgets import (
    QTextEdit, QToolTip, QApplication, QMainWindow, QVBoxLayout,
    QHBoxLayout, QPushButton, QWidget, QLabel, QSplitter
)
from PySide6.QtCore import Qt, QPoint, QRect, QEvent
from PySide6.QtGui import (
    QTextCursor, QTextCharFormat, QColor, QPen, QPainter,
    QTextFormat, QFont, QTextOption, QBrush
)

import ftml
from ftml.exceptions import FTMLParseError

class ErrorInfo:
    """Information about a single error"""
    def __init__(self, line, col, message, length=1):
        self.line = line
        self.col = col
        self.message = message
        self.length = length
        self.cursor_position = -1  # Will be set when finding the error position

    def __repr__(self):
        return f"Error(line={self.line}, col={self.col}, msg='{self.message}')"

class FTMLEditorWithErrors(QTextEdit):
    """Enhanced text editor with error indicators for FTML"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)  # Enable mouse tracking for tooltips
        self.errors = []  # List of ErrorInfo objects
        self.error_format = QTextCharFormat()
        self.error_format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
        self.error_format.setUnderlineColor(QColor("red"))

        # For drawing error indicators
        self.error_positions = []  # List of cursor positions with errors

        # Set editor options
        self.setAcceptRichText(False)
        font = QFont("Courier New", 10)
        font.setFixedPitch(True)
        self.setFont(font)

        # Set word wrap mode
        self.setWordWrapMode(QTextOption.NoWrap)

    def clear_errors(self):
        """Clear all error indicators"""
        self.errors = []
        self.error_positions = []
        self.update_error_indicators()

    def add_error(self, line, col, message, length=1):
        """Add an error indicator at the specified location"""
        error = ErrorInfo(line, col, message, length)
        self.errors.append(error)
        self.find_error_cursor_position(error)
        self.update_error_indicators()
        self.update()

    def find_error_cursor_position(self, error):
        """Convert line/col to absolute cursor position"""
        try:
            cursor = QTextCursor(self.document())
            cursor.movePosition(QTextCursor.Start)

            # Move to the line
            for _ in range(error.line - 1):
                if not cursor.movePosition(QTextCursor.NextBlock):
                    break

            # Move to the column
            line_start_pos = cursor.position()
            cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, max(0, error.col - 1))

            # Store the absolute position
            error.cursor_position = cursor.position()

            # Remember this position for painting the indicator
            self.error_positions.append(error.cursor_position)

        except Exception as e:
            print(f"Error finding cursor position: {e}")

    def update_error_indicators(self):
        """Update the visual indicators for all errors"""
        extraSelections = []

        for error in self.errors:
            if error.cursor_position >= 0:
                selection = QTextEdit.ExtraSelection()
                selection.format = self.error_format
                selection.cursor = QTextCursor(self.document())
                selection.cursor.setPosition(error.cursor_position)
                selection.cursor.movePosition(
                    QTextCursor.Right,
                    QTextCursor.KeepAnchor,
                    error.length
                )
                extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    def mouseMoveEvent(self, event):
        """Show tooltip when hovering over an error"""
        super().mouseMoveEvent(event)

        cursor = self.cursorForPosition(event.pos())
        cursor_pos = cursor.position()

        # Check if we're hovering over an error
        for error in self.errors:
            if error.cursor_position <= cursor_pos < error.cursor_position + error.length:
                # Show tooltip with error message
                tooltip_text = f"Error: {error.message}"
                QToolTip.showText(event.globalPos(), tooltip_text, self)
                return

        # Hide tooltip if not over an error
        if QToolTip.isVisible():
            QToolTip.hideText()

    def paintEvent(self, event):
        """Custom paint event to draw error indicators"""
        super().paintEvent(event)

        # Draw red error indicators
        painter = QPainter(self.viewport())
        painter.setPen(QPen(QColor("red"), 2))

        # Draw a small red dot for each error
        for cursor_pos in self.error_positions:
            cursor = QTextCursor(self.document())
            cursor.setPosition(cursor_pos)
            rect = self.cursorRect(cursor)

            # Draw a red horizontal line under the error position
            painter.drawLine(
                rect.left(),
                rect.bottom(),
                rect.right(),
                rect.bottom()
            )


# Demo application to test the enhanced editor
class ErrorIndicatorDemo(QMainWindow):
    """Demo window to show error indicators"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FTML Error Indicator Demo")
        self.resize(800, 600)

        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header
        header_label = QLabel("FTML Editor with Error Indicators")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(header_label)

        # Split view
        splitter = QSplitter(Qt.Vertical)

        # Editor
        self.editor = FTMLEditorWithErrors()
        self.editor.setPlaceholderText("Enter FTML here...")

        # Sample content with errors
        self.editor.setPlainText("""// A simple FTML document with errors
key = "value"
key = "duplicate key error"

invalid_syntax = 123 this will cause an error

list = [
    "item1",
    "item2",
    "missing closing bracket
]
""")

        # Control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)

        # Buttons
        parse_btn = QPushButton("Parse FTML")
        parse_btn.clicked.connect(self.parse_ftml)

        clear_btn = QPushButton("Clear Errors")
        clear_btn.clicked.connect(self.editor.clear_errors)

        add_error_btn = QPushButton("Add Sample Error")
        add_error_btn.clicked.connect(self.add_sample_error)

        # Status label
        self.status_label = QLabel("Ready")

        # Add to layout
        control_layout.addWidget(parse_btn)
        control_layout.addWidget(clear_btn)
        control_layout.addWidget(add_error_btn)
        control_layout.addWidget(self.status_label)
        control_layout.addStretch()

        # Error display
        self.error_display = QTextEdit()
        self.error_display.setReadOnly(True)
        self.error_display.setMaximumHeight(150)

        # Add widgets to layout
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.addWidget(self.editor)
        editor_layout.addWidget(control_panel)

        splitter.addWidget(editor_container)
        splitter.addWidget(self.error_display)
        splitter.setSizes([400, 100])

        main_layout.addWidget(splitter)

    def parse_ftml(self):
        """Parse the FTML and show error indicators"""
        content = self.editor.toPlainText()
        self.editor.clear_errors()
        self.error_display.clear()

        try:
            # Parse the FTML
            ftml.load(content)
            self.status_label.setText("✓ Valid FTML")
            self.status_label.setStyleSheet("color: green;")
            self.error_display.setText("No errors found.")

        except FTMLParseError as e:
            # Handle parse error
            self.status_label.setText("✗ Parse error")
            self.status_label.setStyleSheet("color: red;")

            # Display the error
            self.error_display.setText(f"Error parsing FTML:\n{str(e)}")

            # Add error indicator
            if hasattr(e, "line") and hasattr(e, "col"):
                self.editor.add_error(e.line, e.col, str(e))

                # Move cursor to error position
                cursor = QTextCursor(self.editor.document())
                cursor.movePosition(QTextCursor.Start)
                for _ in range(e.line - 1):
                    cursor.movePosition(QTextCursor.NextBlock)
                cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, e.col - 1)
                self.editor.setTextCursor(cursor)
                self.editor.ensureCursorVisible()

        except Exception as e:
            self.status_label.setText(f"✗ Error: {type(e).__name__}")
            self.status_label.setStyleSheet("color: red;")
            self.error_display.setText(f"Unexpected error:\n{str(e)}")

    def add_sample_error(self):
        """Add a sample error for testing"""
        # Get cursor position
        cursor = self.editor.textCursor()
        block_number = cursor.blockNumber() + 1  # Line number (1-based)
        col_number = cursor.columnNumber() + 1   # Column number (1-based)

        # Add error at cursor position
        self.editor.add_error(
            block_number,
            col_number,
            f"Sample error at line {block_number}, column {col_number}"
        )

        # Update status
        self.status_label.setText(f"Added sample error at line {block_number}, column {col_number}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ErrorIndicatorDemo()
    window.show()
    sys.exit(app.exec())