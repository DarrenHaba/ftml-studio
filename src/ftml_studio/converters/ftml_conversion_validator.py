# src/ftml_studio/converters/ftml_parser.py
import logging
import ftml
from ftml.exceptions import FTMLParseError, FTMLError

logger = logging.getLogger("ftml_parser")


class FTMLConversionValidator:
    """Parser for validating FTML format"""

    def __init__(self):
        self.result = None

    def parse(self, ftml_content):
        """
        Parse FTML content and validate its structure

        Args:
            ftml_content (str): The FTML content to parse

        Returns:
            dict: The parsed FTML structure

        Raises:
            FTMLParseError: If the FTML content is invalid
        """
        if not ftml_content or not ftml_content.strip():
            raise FTMLParseError("Empty FTML content")

        try:
            # Use the FTML library's load function to parse and validate
            result = ftml.load(ftml_content, validate=True)

            # Additional validation - a plain string is not valid FTML
            if isinstance(ftml_content, str) and ftml_content.strip().startswith('"') and ftml_content.strip().endswith(
                    '"'):
                # Check if it's just a quoted string without a key
                if "=" not in ftml_content:
                    raise FTMLParseError("Plain string is not valid FTML. FTML requires key-value pairs.")

            self.result = result
            return result

        except FTMLParseError as e:
            # Re-raise FTML parsing errors
            logger.error(f"FTML parsing error: {str(e)}")
            raise

        except FTMLError as e:
            # Convert other FTML errors to parse errors
            logger.error(f"FTML error: {str(e)}")
            raise FTMLParseError(f"FTML validation error: {str(e)}")

        except Exception as e:
            # Catch any other exceptions
            logger.error(f"Unexpected error parsing FTML: {str(e)}")
            raise FTMLParseError(f"FTML parsing error: {str(e)}")
