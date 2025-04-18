```
ftml-studio/
├── src/
│   └── ftml_studio/
│       ├── __init__.py
│       ├── __main__.py                 # CLI entry point
│       ├── converters/                 # Format converters
│       │   ├── __init__.py             # Converter registry
│       │   ├── base.py                 # Abstract converter
│       │   ├── json_converter.py
│       │   └── [other_converters].py
│       ├── ui/                         # UI components
│       │   ├── __init__.py
│       │   ├── base_window.py          # Common window functionality
│       │   ├── converter_window.py     # Standalone converter
│       │   ├── editor_window.py        # FTML editor with highlighting
│       │   ├── main_window.py          # Optional integrated UI
│       │   └── widgets/
│       │       ├── __init__.py
│       │       ├── ftml_editor.py      # Reusable FTML editor widget
│       │       └── format_selector.py  # Format dropdown widget
│       └── syntax/
│           ├── __init__.py
│           └── ftml_highlighter.py     # Syntax highlighting logic
├── tests/
│   ├── test_converters/
│   └── test_ui/
└── pyproject.toml
```