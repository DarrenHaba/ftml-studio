# src/ftml_studio/converters/__init__.py
from src.ftml_studio.converters.json_converter import JSONConverter

# Registry of format converters
_CONVERTERS = {
    ('ftml', 'json'): JSONConverter(),
    ('json', 'ftml'): JSONConverter(reverse=True),
    # Add more converters as you implement them
}


def get_converter(source_format, target_format):
    """Get a converter for the specified formats"""
    key = (source_format, target_format)
    if key not in _CONVERTERS:
        raise ValueError(f"No converter available from {source_format} to {target_format}")
    return _CONVERTERS[key]

