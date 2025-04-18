# src/ftml_studio/converters/json_converter.py
import json
import ftml
# from .base import BaseConverter

class JSONConverter(BaseConverter):
    """Handles conversion between FTML and JSON"""

    def __init__(self, reverse=False):
        self.reverse = reverse  # If True, converts JSON to FTML

    def convert(self, content):
        if self.reverse:
            # JSON to FTML
            try:
                data = json.loads(content)
                return ftml.dump(data)
            except Exception as e:
                raise ValueError(f"JSON to FTML conversion failed: {str(e)}")
        else:
            # FTML to JSON
            try:
                data = ftml.load(content)
                return json.dumps(data, indent=2)
            except Exception as e:
                raise ValueError(f"FTML to JSON conversion failed: {str(e)}")