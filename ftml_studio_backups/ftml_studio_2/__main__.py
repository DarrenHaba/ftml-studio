# src/ftml_studio/__main__.py
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description="FTML Studio")
    parser.add_argument('--converter', action='store_true', help='Open converter window')
    parser.add_argument('--editor', action='store_true', help='Open editor window')
    parser.add_argument('--file', type=str, help='File to open')

    args = parser.parse_args()

    # Determine which window to open
    if args.converter:
        from .ui.converter_window import ConverterWindow
        window = ConverterWindow()
    elif args.editor:
        from .ui.editor_window import EditorWindow
        window = EditorWindow()
        if args.file:
            try:
                with open(args.file, 'r') as f:
                    window.load_content(f.read())
            except Exception as e:
                print(f"Error opening file: {e}", file=sys.stderr)
    else:
        # Default to main window or show help
        from .ui.main_window import MainWindow
        window = MainWindow()

    return window.run()


if __name__ == "__main__":
    sys.exit(main())