# src/ftml_studio/syntax/yaml_highlighter.py
from PySide6.QtCore import QRegularExpression
from .base_highlighter import BaseHighlighter

class YAMLHighlighter(BaseHighlighter):
    """Syntax highlighter for YAML documents"""

    def __init__(self, document, theme_manager=None):
        super().__init__(document, theme_manager)
        self.initialize_formats()

    def initialize_formats(self):
        """Initialize text formats with custom colors"""
        super().initialize_formats()
    
        # YAML-specific formatting adjustments using theme colors
        if self.theme_manager:
            self._create_format("key", foreground=self.theme_manager.get_syntax_color("keyword"), bold=True)
            self._create_format("list_item", foreground=self.theme_manager.get_syntax_color("string"))  # Use string color for list items
            self._create_format("dash", foreground=self.theme_manager.get_syntax_color("symbol"))  # Use symbol color for dash markers
        else:
            # Fallback colors if no theme manager
            self._create_format("key", foreground="#0077aa", bold=True)
            self._create_format("list_item", foreground="#008800")
            self._create_format("dash", foreground="#666666")

    def highlightBlock(self, text):
        """Custom YAML highlighting logic with better multi-word support"""
        # Clear previous formatting
        self.setCurrentBlockState(0)

        # Track which parts of the text have been highlighted to avoid conflicts
        highlighted = [False] * len(text)

        # Apply highlighting in specific order
        self._highlight_comments(text, highlighted)
        self._highlight_keys(text, highlighted)
        self._highlight_list_markers(text, highlighted)
        self._highlight_inline_lists(text, highlighted)
        self._highlight_values(text, highlighted)  # Values last to catch everything else

    def _is_highlighted(self, start, length, highlighted):
        """Check if any part of the range is already highlighted"""
        for i in range(start, min(start + length, len(highlighted))):
            if highlighted[i]:
                return True
        return False

    def _mark_highlighted(self, start, length, highlighted):
        """Mark a range as highlighted"""
        for i in range(start, min(start + length, len(highlighted))):
            highlighted[i] = True

    def _highlight_comments(self, text, highlighted):
        """Highlight comment lines"""
        pattern = QRegularExpression(r'#.*$')
        match_iterator = pattern.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            start = match.capturedStart()
            length = match.capturedLength()

            if not self._is_highlighted(start, length, highlighted):
                self.setFormat(start, length, self.formats["comment"])
                self._mark_highlighted(start, length, highlighted)

    def _highlight_keys(self, text, highlighted):
        """Highlight all keys including those in list contexts"""
        # Normal keys (with colon)
        key_pattern = QRegularExpression(r'^\s*([A-Za-z0-9_-]+)(?=\s*:)')
        match_iterator = key_pattern.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            start = match.capturedStart(1)
            length = match.capturedLength(1)

            if not self._is_highlighted(start, length, highlighted):
                self.setFormat(start, length, self.formats["key"])
                self._mark_highlighted(start, length, highlighted)

        # Keys in indented lines
        indented_key_pattern = QRegularExpression(r'^\s+([A-Za-z0-9_-]+)(?=\s*:)')
        match_iterator = indented_key_pattern.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            start = match.capturedStart(1)
            length = match.capturedLength(1)

            if not self._is_highlighted(start, length, highlighted):
                self.setFormat(start, length, self.formats["key"])
                self._mark_highlighted(start, length, highlighted)

        # Keys after list item dashes
        list_key_pattern = QRegularExpression(r'^\s*-\s+([A-Za-z0-9_-]+)(?=\s*:)')
        match_iterator = list_key_pattern.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            start = match.capturedStart(1)
            length = match.capturedLength(1)

            if not self._is_highlighted(start, length, highlighted):
                self.setFormat(start, length, self.formats["key"])
                self._mark_highlighted(start, length, highlighted)

    def _highlight_list_markers(self, text, highlighted):
        """Highlight list item markers and their values"""
        # List item dashes
        dash_pattern = QRegularExpression(r'(^\s*-)(\s+)([^:\n#]+)(?=\s*$|\s+#)')
        match_iterator = dash_pattern.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()

            # Highlight dash
            dash_start = match.capturedStart(1)
            dash_length = match.capturedLength(1)
            if not self._is_highlighted(dash_start, dash_length, highlighted):
                self.setFormat(dash_start, dash_length, self.formats["dash"])
                self._mark_highlighted(dash_start, dash_length, highlighted)

            # Highlight the actual value (all text after the dash and whitespace)
            value_start = match.capturedStart(3)
            value_length = match.capturedLength(3)
            if not self._is_highlighted(value_start, value_length, highlighted):
                self.setFormat(value_start, value_length, self.formats["list_item"])
                self._mark_highlighted(value_start, value_length, highlighted)

    def _highlight_inline_lists(self, text, highlighted):
        """Handle inline lists like [item1, item2, item3]"""
        # Find anything that looks like an inline list
        list_pattern = QRegularExpression(r'\[([^\]]*)\]')
        match_iterator = list_pattern.globalMatch(text)

        while match_iterator.hasNext():
            list_match = match_iterator.next()
            list_content = list_match.captured(1)
            list_start = list_match.capturedStart()
            list_length = list_match.capturedLength()

            # Highlight brackets
            if not self._is_highlighted(list_start, 1, highlighted):
                self.setFormat(list_start, 1, self.formats["symbol"])  # Opening bracket
                self._mark_highlighted(list_start, 1, highlighted)

            if not self._is_highlighted(list_start + list_length - 1, 1, highlighted):
                self.setFormat(list_start + list_length - 1, 1, self.formats["symbol"])  # Closing bracket
                self._mark_highlighted(list_start + list_length - 1, 1, highlighted)

            # Highlight individual items
            item_pattern = QRegularExpression(r'([^,]+)(?:,|$)')
            item_start = 0

            item_match_iterator = item_pattern.globalMatch(list_content)
            while item_match_iterator.hasNext():
                item_match = item_match_iterator.next()
                item_text = item_match.captured(1).strip()  # Using strip() instead of trimmed()

                # Find actual start and end in the original text
                raw_content = list_content[item_start:]
                raw_captured = item_match.captured(1)
                # Find position of the trimmed text within the raw captured text
                trim_start = raw_captured.find(item_text)
                actual_start = list_start + 1 + item_start + trim_start
                actual_length = len(item_text)

                if not self._is_highlighted(actual_start, actual_length, highlighted):
                    self.setFormat(actual_start, actual_length, self.formats["string"])
                    self._mark_highlighted(actual_start, actual_length, highlighted)

                # Find comma after this item
                comma_index = raw_content.find(',', len(raw_captured))
                if comma_index != -1:
                    actual_comma_pos = list_start + 1 + item_start + comma_index
                    if not self._is_highlighted(actual_comma_pos, 1, highlighted):
                        self.setFormat(actual_comma_pos, 1, self.formats["symbol"])
                        self._mark_highlighted(actual_comma_pos, 1, highlighted)

                item_start += item_match.capturedLength()

    def _highlight_values(self, text, highlighted):
        """Highlight scalar values after keys"""
        # This pattern catches all text after a colon until end of line or a comment
        value_pattern = QRegularExpression(r':\s+([^:#\[\]{}][^#\n]*?)(?=$|\s+#)')
        match_iterator = value_pattern.globalMatch(text)

        while match_iterator.hasNext():
            match = match_iterator.next()
            value_text = match.captured(1).strip()  # Using strip() instead of trimmed()

            # Skip if empty
            if not value_text:
                continue

            start = match.capturedStart(1)
            length = match.capturedLength(1)

            # Skip if already highlighted
            if self._is_highlighted(start, length, highlighted):
                continue

            # Determine format based on content
            format = self.formats["string"]  # Default format

            # Check for boolean values
            if value_text.lower() in ["true", "false", "yes", "no", "on", "off"]:
                format = self.formats["boolean"]
            # Check for null values
            elif value_text.lower() in ["null", "~", "none"]:
                format = self.formats["null"]
            # Check for numbers
            elif QRegularExpression(r'^-?\d+(\.\d+)?$').match(value_text).hasMatch():
                format = self.formats["number"]

            self.setFormat(start, length, format)
            self._mark_highlighted(start, length, highlighted)

        # Handle quoted strings specifically
        quoted_pattern = QRegularExpression(r':\s+(["\'])(.*?)\1')
        match_iterator = quoted_pattern.globalMatch(text)

        while match_iterator.hasNext():
            match = match_iterator.next()
            # Find the actual start of the quoted text
            full_match = match.captured(0)
            quote_char = match.captured(1)
            quote_start = full_match.find(quote_char)

            start = match.capturedStart(0) + quote_start
            length = len(match.captured(1)) + len(match.captured(2)) + len(match.captured(1))

            if not self._is_highlighted(start, length, highlighted):
                self.setFormat(start, length, self.formats["string"])
                self._mark_highlighted(start, length, highlighted)