# src/ftml_studio/syntax/ftml_highlighter.py
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PySide6.QtCore import QRegularExpression


class FTMLHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for FTML documents"""

    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        # Keys (before =)
        key_format = QTextCharFormat()
        key_format.setForeground(QColor("#0000FF"))  # Blue
        self.highlighting_rules.append((
            QRegularExpression(r"^[A-Za-z_][A-Za-z0-9_]*(?=\s*=)"),
            key_format
        ))

        # Strings in quotes
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#008000"))  # Green
        self.highlighting_rules.append((
            QRegularExpression(r'"(?:\\.|[^"\\])*"'),
            string_format
        ))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))  # Gray
        self.highlighting_rules.append((
            QRegularExpression(r'//.*$'),
            comment_format
        ))

        # Add more rules as needed for numbers, booleans, etc.

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)
