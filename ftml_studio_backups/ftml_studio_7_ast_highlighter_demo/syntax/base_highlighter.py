# src/ftml_studio/syntax/base_highlighter.py
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import QRegularExpression, Qt


class BaseHighlighter(QSyntaxHighlighter):
    """Base syntax highlighter with theme support"""

    def __init__(self, document, theme_manager=None):
        super().__init__(document)
        self.theme_manager = theme_manager
        self.highlighting_rules = []
        self.initialize_formats()

    def initialize_formats(self):
        """Initialize text formats - override in subclasses"""
        # Define common formats based on current theme
        self.formats = {}

        # Default format definitions (can be overridden by specific highlighters)
        self._create_format("key", foreground="#0066cc", bold=True)
        self._create_format("string", foreground="#008800")
        self._create_format("number", foreground="#aa6600")
        self._create_format("boolean", foreground="#0000ff", bold=True)
        self._create_format("null", foreground="#880088", bold=True)
        self._create_format("comment", foreground="#808080", italic=True)
        self._create_format("symbol", foreground="#666666")
        self._create_format("error", foreground="#ff0000", underline=True)

    def _create_format(self, name, foreground=None, background=None,
                       bold=False, italic=False, underline=False):
        """Create a text format with the specified attributes"""
        fmt = QTextCharFormat()

        # Apply color based on theme if theme manager is available
        if self.theme_manager and foreground:
            # Try to get color from theme, otherwise use the provided color
            # This is where theme integration happens
            theme = self.theme_manager.current_theme
            if theme == "auto":
                # Resolve auto theme
                theme = "dark" if self.theme_manager._is_system_dark_theme() else "light"

            # You could define syntax colors in the theme manager
            # For now, use hardcoded colors based on theme
            if theme == "dark":
                color_map = {
                    "#0066cc": "#6699ff",  # key - lighter blue in dark mode
                    "#008800": "#88cc88",  # string - lighter green in dark mode
                    "#aa6600": "#ffaa44",  # number - brighter orange in dark mode
                    "#0000ff": "#8888ff",  # boolean - lighter blue in dark mode
                    "#880088": "#ff88ff",  # null - brighter purple in dark mode
                    "#808080": "#a0a0a0",  # comment - lighter gray in dark mode
                    "#666666": "#aaaaaa",  # symbol - lighter gray in dark mode
                    "#ff0000": "#ff6666",  # error - lighter red in dark mode
                }
                foreground = color_map.get(foreground, foreground)

        if foreground:
            fmt.setForeground(QColor(foreground))
        if background:
            fmt.setBackground(QColor(background))
        if bold:
            fmt.setFontWeight(QFont.Bold)
        if italic:
            fmt.setFontItalic(True)
        if underline:
            fmt.setFontUnderline(True)

        self.formats[name] = fmt
        return fmt

    def add_rule(self, pattern, format_name):
        """Add a highlighting rule with the specified pattern and format"""
        self.highlighting_rules.append((
            QRegularExpression(pattern),
            self.formats[format_name]
        ))

    def highlightBlock(self, text):
        """Apply highlighting rules to the given block of text"""
        # Apply each highlighting rule
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)