# src/ftml_studio/__main__.py
import sys
from PySide6.QtWidgets import QApplication

def main():
    import argparse

    parser = argparse.ArgumentParser(description="FTML Studio")
    parser.add_argument('--test', action='store_true', help='Open test window')
    parser.add_argument('--converter', action='store_true', help='Open converter window')
    parser.add_argument('--editor', action='store_true', help='Open editor window')
    parser.add_argument('--file', type=str, help='File to open')

    args = parser.parse_args()

    # Initialize application first
    app = QApplication(sys.argv)

    # Determine which window to open
    if args.test:
        from src.ftml_studio.ui.window_foo import WindowFoo
        window = WindowFoo()
    elif args.converter:
        from src.ftml_studio.ui.elements.converter import ConverterWindow
        window = ConverterWindow()
    elif args.editor:
        from src.ftml_studio.ui.elements.ftml_editor import EditorWindow
        window = EditorWindow()
        if args.file:
            try:
                with open(args.file, 'r') as f:
                    window.load_content(f.read())
            except Exception as e:
                print(f"Error opening file: {e}", file=sys.stderr)
    else:
        # Default to main window
        from src.ftml_studio.ui.main_window import MainWindow
        window = MainWindow()

    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())