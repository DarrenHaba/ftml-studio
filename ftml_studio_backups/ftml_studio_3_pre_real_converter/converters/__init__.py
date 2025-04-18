# src/ftml_studio/converters/__init__.py
from .json_converter import JSONConverter

# Registry of format converters
_CONVERTERS = {
    ('ftml', 'json'): JSONConverter(),
    ('json', 'ftml'): JSONConverter(reverse=True),
    # Add more converters as you implement them
}

def get_converter(source_format, target_format):
    """Get a converter for the specified formats"""
    key = (source_format.lower(), target_format.lower())
    if key not in _CONVERTERS:
        raise ValueError(f"No converter available from {source_format} to {target_format}")
    return _CONVERTERS[key]

def get_supported_formats():
    """Get list of supported formats for conversion"""
    formats = set()
    for source, target in _CONVERTERS.keys():
        formats.add(source)
        formats.add(target)
    return sorted(list(formats))

def register_converter(source_format, target_format, converter):
    """Register a new converter"""
    key = (source_format.lower(), target_format.lower())
    _CONVERTERS[key] = converter