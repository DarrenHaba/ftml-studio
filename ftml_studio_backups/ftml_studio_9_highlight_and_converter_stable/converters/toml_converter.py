# src/ftml_studio/converters/toml_converter.py
import toml
import json
import logging
import ftml
from .base import BaseConverter

# Configure logging
logger = logging.getLogger("toml_converter")

class TOMLConverter(BaseConverter):
    """Handles conversion between FTML and TOML"""

    def __init__(self, reverse=False):
        self.reverse = reverse  # If True, converts TOML to FTML
        logger.debug(f"Created TOMLConverter with reverse={reverse}")

    def convert(self, content):
        if self.reverse:
            # TOML to FTML conversion
            logger.debug("Starting TOML to FTML conversion")
            try:
                data = toml.loads(content)
                logger.debug(f"Parsed TOML data: {str(data)[:100]}...")
                result = self._toml_to_ftml(data)
                logger.debug(f"Conversion result: {result[:100]}...")
                return result
            except toml.TomlDecodeError as e:
                error_msg = f"TOML parsing error: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            except Exception as e:
                error_msg = f"TOML to FTML conversion failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise ValueError(error_msg)
        else:
            # FTML to TOML conversion
            logger.debug("Starting FTML to TOML conversion")
            try:
                # Use the official FTML parser to parse the content
                data = ftml.load(content)
                logger.debug(f"Parsed FTML data: {str(data)[:100]}...")

                # Convert to TOML
                result = toml.dumps(dict(data))
                logger.debug(f"Conversion result: {result[:100]}...")
                return result
            except ftml.FTMLParseError as e:
                error_msg = f"FTML parsing error: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            except Exception as e:
                error_msg = f"FTML to TOML conversion failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise ValueError(error_msg)

    def _toml_to_ftml(self, data, indent=0):
        """Convert TOML object to FTML format with proper indentation."""
        # Reuse the JSON to FTML conversion logic since the data structure is the same
        # after parsing TOML
        logger.debug(f"Converting TOML to FTML, indent={indent}, type={type(data)}")

        if not isinstance(data, dict):
            return self._format_scalar_value(data)

        if not data:  # Empty object
            return "{}"

        lines = []
        spaces = " " * indent

        for key, value in data.items():
            if isinstance(value, dict):
                formatted_value = self._toml_to_ftml_object(value, indent + 4)
                lines.append(f"{spaces}{key} = {formatted_value}")
            elif isinstance(value, list):
                formatted_value = self._toml_to_ftml_list(value, indent + 4)
                lines.append(f"{spaces}{key} = {formatted_value}")
            else:
                formatted_value = self._format_scalar_value(value)
                lines.append(f"{spaces}{key} = {formatted_value}")

        return "\n".join(lines)

    def _toml_to_ftml_object(self, obj, indent=0):
        """Format a TOML object as an FTML object."""
        logger.debug(f"Converting TOML object to FTML, indent={indent}")

        if not obj:  # Empty object
            return "{}"

        lines = ["{"]
        spaces = " " * indent

        for key, value in obj.items():
            if isinstance(value, dict):
                formatted_value = self._toml_to_ftml_object(value, indent + 4)
                lines.append(f"{spaces}{key} = {formatted_value},")
            elif isinstance(value, list):
                formatted_value = self._toml_to_ftml_list(value, indent + 4)
                lines.append(f"{spaces}{key} = {formatted_value},")
            else:
                formatted_value = self._format_scalar_value(value)
                lines.append(f"{spaces}{key} = {formatted_value},")

        # Remove trailing comma from the last item if there is one
        if lines[-1].endswith(","):
            lines[-1] = lines[-1][:-1]

        lines.append(" " * (indent - 4) + "}")
        return "\n".join(lines)

    def _toml_to_ftml_list(self, items, indent=0):
        """Format a TOML array as an FTML list."""
        logger.debug(f"Converting TOML array to FTML, indent={indent}, length={len(items)}")

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
                formatted_item = self._toml_to_ftml_object(item, indent + 4)
                lines.append(f"{spaces}{formatted_item},")
            elif isinstance(item, list):
                formatted_item = self._toml_to_ftml_list(item, indent + 4)
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
            return source_format.lower() == "toml" and target_format.lower() == "ftml"
        else:
            return source_format.lower() == "ftml" and target_format.lower() == "toml"


class JSONToTOMLConverter(BaseConverter):
    """Handles direct conversion between JSON and TOML"""

    def convert(self, content):
        logger.debug("Starting JSON to TOML conversion")
        try:
            # Parse JSON
            data = json.loads(content)
            logger.debug(f"Parsed JSON data: {str(data)[:100]}...")

            # Convert to TOML
            result = toml.dumps(data)
            logger.debug(f"Conversion result: {result[:100]}...")
            return result
        except json.JSONDecodeError as e:
            error_msg = f"JSON parsing error: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"JSON to TOML conversion failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)

    def can_convert(self, source_format, target_format):
        """Check if this converter supports the specified formats"""
        return source_format.lower() == "json" and target_format.lower() == "toml"


class TOMLToJSONConverter(BaseConverter):
    """Handles direct conversion between TOML and JSON"""

    def convert(self, content):
        logger.debug("Starting TOML to JSON conversion")
        try:
            # Parse TOML
            data = toml.loads(content)
            logger.debug(f"Parsed TOML data: {str(data)[:100]}...")

            # Convert to JSON
            result = json.dumps(data, indent=2, ensure_ascii=False)
            logger.debug(f"Conversion result: {result[:100]}...")
            return result
        except toml.TomlDecodeError as e:
            error_msg = f"TOML parsing error: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"TOML to JSON conversion failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)

    def can_convert(self, source_format, target_format):
        """Check if this converter supports the specified formats"""
        return source_format.lower() == "toml" and target_format.lower() == "json"