# src/ftml_studio/converters/xml_converter.py
import json
import logging
import ftml
import xml.etree.ElementTree as ET
from xml.dom import minidom
from .base import BaseConverter

# Configure logging
logger = logging.getLogger("xml_converter")

class XMLConverter(BaseConverter):
    """Handles conversion between FTML and XML"""

    def __init__(self, reverse=False):
        self.reverse = reverse  # If True, converts XML to FTML
        logger.debug(f"Created XMLConverter with reverse={reverse}")

    def convert(self, content):
        if self.reverse:
            # XML to FTML conversion
            logger.debug("Starting XML to FTML conversion")
            try:
                # Parse XML
                root = ET.fromstring(content)

                # Convert to Python dictionary
                data = self._xml_to_dict(root)
                logger.debug(f"Parsed XML data: {str(data)[:100]}...")

                # Convert dictionary to FTML
                result = self._dict_to_ftml(data)
                logger.debug(f"Conversion result: {result[:100]}...")
                return result
            except ET.ParseError as e:
                error_msg = f"XML parsing error: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            except Exception as e:
                error_msg = f"XML to FTML conversion failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise ValueError(error_msg)
        else:
            # FTML to XML conversion
            logger.debug("Starting FTML to XML conversion")
            try:
                # Use the official FTML parser to parse the content
                data = ftml.load(content)
                logger.debug(f"Parsed FTML data: {str(dict(data))[:100]}...")

                # Convert to XML
                xml_str = self._dict_to_xml("root", data)

                # Pretty print the XML with proper indentation
                parsed_xml = minidom.parseString(xml_str)
                result = parsed_xml.toprettyxml(indent="  ")

                # Remove the XML declaration if it exists
                if result.startswith('<?xml'):
                    result = result[result.find('?>')+2:].lstrip()

                logger.debug(f"Conversion result: {result[:100]}...")
                return result
            except ftml.FTMLParseError as e:
                error_msg = f"FTML parsing error: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            except Exception as e:
                error_msg = f"FTML to XML conversion failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise ValueError(error_msg)

    def _xml_to_dict(self, element):
        """
        Convert an XML element to a Python dictionary.
        Attributes become keys with @ prefix, child elements become nested dictionaries.
        Text content is stored with #text key.
        """
        result = {}

        # Process attributes
        for key, value in element.attrib.items():
            result[f"@{key}"] = value

        # Process child elements
        for child in element:
            child_dict = self._xml_to_dict(child)

            if child.tag in result:
                # If this tag already exists, convert to a list
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_dict)
            else:
                result[child.tag] = child_dict

        # Process text content
        if element.text and element.text.strip():
            text = element.text.strip()
            if result:  # If we already have attributes or children
                result["#text"] = text
            else:
                # If this is a leaf node with just text, return the text directly
                return text

        return result

    def _dict_to_xml(self, root_name, data):
        """
        Convert a Python dictionary to XML string.
        Keys with @ prefix become attributes, #text becomes text content.
        """
        root = ET.Element(root_name)

        if isinstance(data, dict):
            # Process each key-value pair
            attributes = {}
            children = {}
            text_content = None

            for key, value in data.items():
                if key.startswith('@'):
                    # Attribute
                    attributes[key[1:]] = str(value)
                elif key == '#text':
                    # Text content
                    text_content = str(value)
                else:
                    # Child element
                    children[key] = value

            # Set attributes
            for attr_name, attr_value in attributes.items():
                root.set(attr_name, attr_value)

            # Set text content
            if text_content is not None:
                root.text = text_content

            # Add child elements
            for child_name, child_value in children.items():
                if isinstance(child_value, list):
                    # Multiple child elements with the same tag
                    for item in child_value:
                        child_xml = self._dict_to_xml(child_name, item)
                        root.append(ET.fromstring(child_xml))
                else:
                    # Single child element
                    child_xml = self._dict_to_xml(child_name, child_value)
                    root.append(ET.fromstring(child_xml))
        else:
            # Simple value
            root.text = str(data)

        return ET.tostring(root, encoding='unicode')

    def _dict_to_ftml(self, data, indent=0):
        """Convert dictionary to FTML format with proper indentation."""
        return self._json_to_ftml(data, indent)

    def _json_to_ftml(self, data, indent=0):
        """Convert a dictionary to FTML format with proper indentation."""
        logger.debug(f"Converting to FTML, indent={indent}, type={type(data)}")

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
        """Format a dictionary as an FTML object."""
        logger.debug(f"Converting object to FTML, indent={indent}")

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
        """Format a list as an FTML list."""
        logger.debug(f"Converting list to FTML, indent={indent}, length={len(items)}")

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
            return source_format.lower() == "xml" and target_format.lower() == "ftml"
        else:
            return source_format.lower() == "ftml" and target_format.lower() == "xml"


class JSONToXMLConverter(BaseConverter):
    """Handles direct conversion between JSON and XML"""

    def convert(self, content):
        logger.debug("Starting JSON to XML conversion")
        try:
            # Parse JSON
            data = json.loads(content)
            logger.debug(f"Parsed JSON data: {str(data)[:100]}...")

            # Convert to XML
            converter = XMLConverter()
            xml_str = converter._dict_to_xml("root", data)

            # Pretty print the XML with proper indentation
            parsed_xml = minidom.parseString(xml_str)
            result = parsed_xml.toprettyxml(indent="  ")

            # Remove the XML declaration if it exists
            if result.startswith('<?xml'):
                result = result[result.find('?>')+2:].lstrip()

            logger.debug(f"Conversion result: {result[:100]}...")
            return result
        except json.JSONDecodeError as e:
            error_msg = f"JSON parsing error: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"JSON to XML conversion failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)

    def can_convert(self, source_format, target_format):
        """Check if this converter supports the specified formats"""
        return source_format.lower() == "json" and target_format.lower() == "xml"


class XMLToJSONConverter(BaseConverter):
    """Handles direct conversion between XML and JSON"""

    def convert(self, content):
        logger.debug("Starting XML to JSON conversion")
        try:
            # Parse XML
            root = ET.fromstring(content)

            # Convert to Python dictionary
            converter = XMLConverter()
            data = converter._xml_to_dict(root)
            logger.debug(f"Parsed XML data: {str(data)[:100]}...")

            # Convert to JSON
            result = json.dumps(data, indent=2, ensure_ascii=False)
            logger.debug(f"Conversion result: {result[:100]}...")
            return result
        except ET.ParseError as e:
            error_msg = f"XML parsing error: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"XML to JSON conversion failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)

    def can_convert(self, source_format, target_format):
        """Check if this converter supports the specified formats"""
        return source_format.lower() == "xml" and target_format.lower() == "json"
    