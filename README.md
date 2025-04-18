# FTML Studio

**A modern GUI tool for working with FTML markup language**

> ⚠️ **ALPHA SOFTWARE**: FTML Studio is currently in alpha. Both the editor and the FTML language itself are under active development. Please expect bugs and syntax changes as we refine the language.

## What is FTML Studio?

FTML Studio provides a visual environment for working with FTML markup language. It was created to help developers learn, use, and contribute to the evolution of FTML syntax through intuitive editing tools and real-time feedback.

## Installation

```bash
pip install ftml-studio
```

FTML Studio requires Python 3.9+ and the [ftml](https://pypi.org/project/ftml/) package will be installed automatically as a dependency.

## Usage

Launch FTML Studio by running:

```bash
ftml-studio
```

## Features

### FTML Editor

![FTML Editor](https://github.com/DarrenHaba/ftml-studio/blob/master/images/ftml-studio-editor.png)

- **Syntax Highlighting**: Makes your FTML code more readable and easier to understand
- **Live Error Detection**: Identifies syntax errors as you type with inline highlighting
- **File Management**: Open, edit, and save FTML files with simple controls
- **Dark/Light Themes**: Comfortable editing in any lighting condition 😎

### Format Converter

![Format Converter](https://github.com/DarrenHaba/ftml-studio/blob/master/images/ftml-studio-converter.png)

Convert between multiple markup formats:
- FTML
- JSON
- YAML
- TOML
- XML

The converter allows you to transform content between any of these formats, making it easier to adopt FTML or integrate it with existing systems.

## Why FTML Studio?

Learning a new markup syntax can be challenging, but with visual feedback and proper tooling, it becomes much more intuitive. FTML Studio provides the environment needed to quickly understand, experiment with, and master FTML syntax without the frustration of invisible errors or formatting issues.

## Contributing

Found a bug? Have a feature request? Want to contribute code? We'd love your help making FTML Studio better! Check out our [GitHub repository](https://github.com/DarrenHaba/ftml-studio/issues) to get started.


## Road Map
The main feature we are missing is the ability to validate data from a schema. Once this feature is implemented we will have
- Real time data safety
- Real time constraint validation

## License

This project is licensed under the GNU Lesser General Public License v3.0 (LGPL-3.0).

## Third-party dependencies

This project uses:
- Google Material Icons (https://fonts.google.com/icons) under the Apache License 2.0
- PySide6 (Qt for Python) under the LGPL 3.0 license
