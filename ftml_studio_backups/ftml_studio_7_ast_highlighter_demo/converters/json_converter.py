# src/ftml_studio/converters/json_converter.py
import json
import logging
import ftml
from .base import BaseConverter

# Configure logging
logger = logging.getLogger("json_converter")

class JSONConverter(BaseConverter):
    """Handles conversion between FTML and JSON"""

    def __init__(self, reverse=False):
        self.reverse = reverse  # If True, converts JSON to FTML
        logger.debug(f"Created JSONConverter with reverse={reverse}")

    def convert(self, content):
        if self.reverse:
            # JSON to FTML conversion
            logger.debug("Starting JSON to FTML conversion")
            try:
                data = json.loads(content)
                logger.debug(f"Parsed JSON data: {str(data)[:100]}...")
                result = self._json_to_ftml(data)
                logger.debug(f"Conversion result: {result[:100]}...")
                return result
            except json.JSONDecodeError as e:
                line_no = e.lineno
                col_no = e.colno
                error_msg = f"JSON parsing error at line {line_no}, column {col_no}: {e.msg}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            except Exception as e:
                error_msg = f"JSON to FTML conversion failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise ValueError(error_msg)
        else:
            # FTML to JSON conversion
            logger.debug("Starting FTML to JSON conversion")
            try:
                # Use the official FTML parser to parse the content
                data = ftml.load(content)
                logger.debug(f"Parsed FTML data: {str(data)[:100]}...")

                # Convert to JSON (ignoring any special FTML properties like _ast_node)
                result = json.dumps(data, indent=2, ensure_ascii=False)
                logger.debug(f"Conversion result: {result[:100]}...")
                return result
            except ftml.FTMLParseError as e:
                error_msg = f"FTML parsing error: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            except Exception as e:
                error_msg = f"FTML to JSON conversion failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise ValueError(error_msg)

    def _json_to_ftml(self, data, indent=0):
        """Convert JSON object to FTML format with proper indentation."""
        logger.debug(f"Converting JSON to FTML, indent={indent}, type={type(data)}")

        if not isinstance(data, dict):
            return self._format_scalar_value(data)

        if not data:  # Empty object
            return "{}"

        lines = []
        spaces = " " * indent

        for key, value in data.items():
            if isinstance(value, dict):
                formatted_value = self._json_to_ftml_object(value, indent + 4)
                lines.append(f"{spaces}{key} = {formatted_value}")
            elif isinstance(value, list):
                formatted_value = self._json_to_ftml_list(value, indent + 4)
                lines.append(f"{spaces}{key} = {formatted_value}")
            else:
                formatted_value = self._format_scalar_value(value)
                lines.append(f"{spaces}{key} = {formatted_value}")

        return "\n".join(lines)

    def _json_to_ftml_object(self, obj, indent=0):
        """Format a JSON object as an FTML object."""
        logger.debug(f"Converting JSON object to FTML, indent={indent}")

        if not obj:  # Empty object
            return "{}"

        lines = ["{"]
        spaces = " " * indent

        for key, value in obj.items():
            if isinstance(value, dict):
                formatted_value = self._json_to_ftml_object(value, indent + 4)
                lines.append(f"{spaces}{key} = {formatted_value},")
            elif isinstance(value, list):
                formatted_value = self._json_to_ftml_list(value, indent + 4)
                lines.append(f"{spaces}{key} = {formatted_value},")
            else:
                formatted_value = self._format_scalar_value(value)
                lines.append(f"{spaces}{key} = {formatted_value},")

        # Remove trailing comma from the last item if there is one
        if lines[-1].endswith(","):
            lines[-1] = lines[-1][:-1]

        lines.append(" " * (indent - 4) + "}")
        return "\n".join(lines)

    def _json_to_ftml_list(self, items, indent=0):
        """Format a JSON array as an FTML list."""
        logger.debug(f"Converting JSON array to FTML, indent={indent}, length={len(items)}")

        if not items:  # Empty list
            return "[]"

        if len(items) == 1 or all(not isinstance(item, (dict, list)) for item in items):
            # Short format for simple lists
            formatted_items = [self._format_scalar_value(item) for item in items]
            return f"[{', '.join(formatted_items)}]"

        # Multi-line format for complex lists
        lines = ["["]
        spaces = " " * indent

        for item in items:
            if isinstance(item, dict):
                formatted_item = self._json_to_ftml_object(item, indent + 4)
                lines.append(f"{spaces}{formatted_item},")
            elif isinstance(item, list):
                formatted_item = self._json_to_ftml_list(item, indent + 4)
                lines.append(f"{spaces}{formatted_item},")
            else:
                formatted_item = self._format_scalar_value(item)
                lines.append(f"{spaces}{formatted_item},")

        # Remove trailing comma from the last item if there is one
        if lines[-1].endswith(","):
            lines[-1] = lines[-1][:-1]

        lines.append(" " * (indent - 4) + "]")
        return "\n".join(lines)

    def _format_scalar_value(self, value):
        """Format a scalar value for FTML with proper escaping."""
        logger.debug(f"Formatting scalar value: {value} (type: {type(value)})")

        if isinstance(value, str):
            # Escape backslashes first to avoid double-escaping
            escaped = value.replace('\\', '\\\\')
            # Then escape other special characters
            escaped = escaped.replace('"', '\\"')
            # Handle newlines as literal \n in the output string
            escaped = escaped.replace('\n', '\\n').replace('\r', '\\r')
            return f'"{escaped}"'
        elif isinstance(value, bool):
            return str(value).lower()
        elif value is None:
            return "null"
        else:
            # For numbers, just convert to string
            return str(value)

    def can_convert(self, source_format, target_format):
        """Check if this converter supports the specified formats"""
        if self.reverse:
            return source_format.lower() == "json" and target_format.lower() == "ftml"
        else:
            return source_format.lower() == "ftml" and target_format.lower() == "json"