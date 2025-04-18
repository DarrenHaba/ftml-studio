# src/ftml_studio/syntax/__init__.py
from .base_highlighter import BaseHighlighter
from .ftml_highlighter import FTMLHighlighter
from .json_highlighter import JSONHighlighter
from .yaml_highlighter import YAMLHighlighter
from .toml_highlighter import TOMLHighlighter
from .xml_highlighter import XMLHighlighter
from .ast_highlighter import FTMLASTHighlighter
from .schema_highlighter import SchemaHighlighter

__all__ = [
    'BaseHighlighter',
    'FTMLHighlighter',
    'JSONHighlighter',
    'YAMLHighlighter',
    'TOMLHighlighter',
    'XMLHighlighter',
    'FTMLASTHighlighter',
    'SchemaHighlighter',
]
