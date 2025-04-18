# src/ftml_studio/syntax/__init__.py
from .ftml_highlighter import FTMLHighlighter
from .json_highlighter import JSONHighlighter
from .yaml_highlighter import YAMLHighlighter
from .toml_highlighter import TOMLHighlighter
from .xml_highlighter import XMLHighlighter

__all__ = ['FTMLHighlighter', 'JSONHighlighter', 
           'YAMLHighlighter', 'TOMLHighlighter', 'XMLHighlighter']
