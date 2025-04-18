# src/ftml_studio/ui/editor_window.py
from PySide6.QtWidgets import (QVBoxLayout, QWidget,
                               QFileDialog, QMessageBox, QToolBar,
                               QStatusBar)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QAction

from src.ftml_studio.syntax.ftml_highlighter import FTMLHighlighter
from src.ftml_studio.ui.base_window import BaseWindow
from src.ftml_studio.ui.widgets.ftml_editor import FTMLEditor


class EditorWindow(BaseWindow):
    """Window for editing FTML with syntax highlighting"""

    def setup_ui(self):
        self.setWindowTitle("FTML Editor")
        self.resize(800, 600)

        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Create editor widget
        self.editor = FTMLEditor(self)
        layout.addWidget(self.editor)

        # Set up highlighter
        self.highlighter = FTMLHighlighter(self.editor.document())

        # Setup menu and toolbar
        self._setup_menu()
        self._setup_toolbar()

        # Status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Track file path
        self.current_file_path = None

    def _setup_menu(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        # New action
        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)

        # Open action
        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        # Save action
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)

        # Save As action
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")

        # Undo action
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        # Redo action
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        # Cut action
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)

        # Copy action
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)

        # Paste action
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)

    def _setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # New file action
        new_action = QAction("New", self)
        new_action.triggered.connect(self._new_file)
        toolbar.addAction(new_action)

        # Open action
        open_action = QAction("Open", self)
        open_action.triggered.connect(self._open_file)
        toolbar.addAction(open_action)

        # Save action
        save_action = QAction("Save", self)
        save_action.triggered.connect(self._save_file)
        toolbar.addAction(save_action)

    def _new_file(self):
        if self.editor.document().isModified():
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "Do you want to save your changes before creating a new file?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                if not self._save_file():
                    return  # Cancel new file if save was cancelled
            elif reply == QMessageBox.Cancel:
                return  # Cancel new file

        self.editor.clear()
        self.current_file_path = None
        self.setWindowTitle("FTML Editor - Untitled")
        self.status_bar.showMessage("New file created")

    def _open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open FTML File", "", "FTML Files (*.ftml);;All Files (*)")

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.load_content(content)
                self.current_file_path = file_path
                self.setWindowTitle(f"FTML Editor - {file_path}")
                self.status_bar.showMessage(f"Opened {file_path}")
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
                return False
        return False

    def _save_file(self):
        if self.current_file_path:
            return self._save_to_path(self.current_file_path)
        else:
            return self._save_file_as()

    def _save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save FTML File", "", "FTML Files (*.ftml);;All Files (*)")

        if file_path:
            return self._save_to_path(file_path)
        return False

    def _save_to_path(self, path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.current_file_path = path
            self.setWindowTitle(f"FTML Editor - {path}")
            self.editor.document().setModified(False)
            self.status_bar.showMessage(f"Saved to {path}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
            return False

    def load_content(self, content):
        """Load content into the editor"""
        self.editor.setPlainText(content)
        self.editor.document().setModified(False)

# Allow standalone execution
if __name__ == "__main__":
    window = EditorWindow()
    window.run()