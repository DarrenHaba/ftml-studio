# src/ftml_studio/ui/main_window.py
import sys
import logging
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout,
                               QWidget, QPushButton, QLabel,
                               QComboBox, QApplication, QFrame)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QFont

# Import our window classes - now these are QWidgets, not QMainWindows
from src.ftml_studio.ui.elements.ftml_editor import FTMLASTDemo
from src.ftml_studio.ui.elements.converter import ConverterWindow
from src.ftml_studio.ui.base_window import BaseWindow
from src.ftml_studio.ui.themes import theme_manager

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("main_window")

class MainWindow(BaseWindow):
    """Main application window for FTML Studio"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FTML Studio")
        self.resize(1200, 800)
        self.settings = QSettings("FTMLStudio", "MainWindow")

        # Initialize state variables
        self.sidebar_visible = False

        # Restore window geometry if available
        self.restore_window_state()

    def setup_ui(self):
        """Set up the UI components"""
        logger.debug("Setting up MainWindow UI")

        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Main content area
        self.content_area = QWidget()
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Create header with tabs and settings button
        self.create_header()

        # Content area (main content)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)

        # Add containers for different views
        self.editor_container = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_container)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)

        # Create editor widget - now it's a QWidget, not a QMainWindow
        self.editor_widget = FTMLASTDemo()
        self.editor_layout.addWidget(self.editor_widget)

        # Container for converter
        self.converter_container = QWidget()
        self.converter_container.hide()  # Start with it hidden
        self.converter_layout = QVBoxLayout(self.converter_container)
        self.converter_layout.setContentsMargins(0, 0, 0, 0)

        # Add containers to main content layout
        self.content_layout.addWidget(self.editor_container)
        self.content_layout.addWidget(self.converter_container)

        # Add content widget to content area
        content_layout.addWidget(self.content_widget)

        # Add content area to main layout
        self.main_layout.addWidget(self.content_area, 1)  # Stretch factor 1

        # Create settings panel (initially hidden)
        self.create_settings_panel()

        # Initial state - hide settings
        self.settings_panel.hide()

        # Create converter widget immediately (no need to lazy load)
        self.converter_widget = ConverterWindow()
        self.converter_layout.addWidget(self.converter_widget)

        # Create status bar for application-wide messages
        # self.statusBar().showMessage("Ready")

        logger.debug("MainWindow UI setup complete")

    def create_header(self):
        """Create the header with tabs and settings button"""
        # Create header widget at the top
        header_widget = QWidget()
        header_widget.setObjectName("header")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)
        header_layout.setSpacing(5)

        # Create buttons for different modes
        self.editor_btn = QPushButton("FTML Editor")
        self.editor_btn.setCheckable(True)
        self.editor_btn.setChecked(True)
        self.editor_btn.setObjectName("headerTab")
        self.editor_btn.clicked.connect(lambda: self.switch_mode(0))

        self.converter_btn = QPushButton("Format Converter")
        self.converter_btn.setCheckable(True)
        self.converter_btn.setObjectName("headerTab")
        self.converter_btn.clicked.connect(lambda: self.switch_mode(1))

        # Add buttons to header
        header_layout.addWidget(self.editor_btn)
        header_layout.addWidget(self.converter_btn)
        header_layout.addStretch(1)  # Push buttons to the left, settings to the right

        # Add settings button to the right
        self.settings_btn = QPushButton("⚙")  # Unicode gear symbol
        self.settings_btn.setObjectName("settingsButton")
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.clicked.connect(self.toggle_settings_panel)
        header_layout.addWidget(self.settings_btn)

        # Add header to content area
        self.content_area.layout().addWidget(header_widget)

    def create_settings_panel(self):
        """Create the settings panel that slides in from the right"""
        # Create settings panel container
        self.settings_panel = QWidget()
        self.settings_panel.setFixedWidth(250)  # Width of settings panel
        self.settings_panel.setObjectName("settingsPanel")  # For styling

        # Settings panel layout
        settings_layout = QVBoxLayout(self.settings_panel)
        settings_layout.setContentsMargins(15, 20, 15, 20)
        settings_layout.setSpacing(15)

        # Header with close button
        header_layout = QHBoxLayout()

        # Close button (X) on the left
        close_btn = QPushButton("✕")  # Unicode X symbol
        close_btn.setObjectName("closeButton")
        close_btn.setFixedSize(24, 24)
        close_btn.setToolTip("Close settings panel")
        close_btn.clicked.connect(self.toggle_settings_panel)
        header_layout.addWidget(close_btn)

        # Settings header
        settings_header = QLabel("Settings")
        settings_header.setObjectName("settingsHeader")
        settings_header.setFont(QFont("Arial", 14, QFont.Bold))
        settings_header.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(settings_header)

        # Empty widget to balance the layout
        spacer = QWidget()
        spacer.setFixedSize(24, 24)
        header_layout.addWidget(spacer)

        settings_layout.addLayout(header_layout)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        settings_layout.addWidget(separator)

        # Theme selection
        theme_label = QLabel("Theme:")
        theme_label.setObjectName("settingsLabel")

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Light")
        self.theme_combo.addItem("Dark")
        self.theme_combo.addItem("Auto (System)")

        # Set current theme in combo box
        current_theme = theme_manager.current_theme
        if current_theme == theme_manager.LIGHT:
            self.theme_combo.setCurrentIndex(0)
        elif current_theme == theme_manager.DARK:
            self.theme_combo.setCurrentIndex(1)
        else:  # AUTO
            self.theme_combo.setCurrentIndex(2)

        # Connect theme change
        self.theme_combo.currentIndexChanged.connect(self.change_theme)

        # Add to layout
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        settings_layout.addLayout(theme_layout)

        # Add more settings here as needed

        # Stretch to push content to the top
        settings_layout.addStretch(1)

        # Add settings panel to main layout
        self.main_layout.addWidget(self.settings_panel)

    def switch_mode(self, index):
        """Switch between editor and converter modes"""
        logger.debug(f"Switching to mode {index}")

        # Update buttons
        self.editor_btn.setChecked(index == 0)
        self.converter_btn.setChecked(index == 1)

        if index == 0:
            # Switch to editor
            self.converter_container.hide()
            self.editor_container.show()
            self.editor_widget.setFocus()

        else:
            # Switch to converter
            self.editor_container.hide()
            self.converter_container.show()
            self.converter_widget.setFocus()

        # Process events to ensure focus changes are applied
        QApplication.processEvents()

    def toggle_settings_panel(self):
        """Toggle the visibility of the settings panel"""
        self.sidebar_visible = not self.sidebar_visible
        logger.debug(f"Toggling settings panel: {self.sidebar_visible}")

        if self.sidebar_visible:
            self.settings_panel.show()
        else:
            self.settings_panel.hide()

    def change_theme(self, index):
        """Change the application theme based on combo box selection"""
        if index == 0:
            new_theme = theme_manager.LIGHT
        elif index == 1:
            new_theme = theme_manager.DARK
        else:
            new_theme = theme_manager.AUTO

        logger.debug(f"Changing theme to {new_theme}")

        # Set theme in global theme manager
        theme_manager.set_theme(new_theme)

        # Apply the theme
        app = QApplication.instance()
        theme_manager.apply_theme(app)

        # Update the editor widget
        if hasattr(self.editor_widget, 'recreate_highlighter'):
            self.editor_widget.recreate_highlighter()

        # Update converter
        if hasattr(self.converter_widget, 'recreate_highlighters'):
            self.converter_widget.recreate_highlighters()

    def save_window_state(self):
        """Save window position, size and state"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

        # Save current mode (editor or converter)
        current_mode = 1 if self.converter_container.isVisible() else 0
        self.settings.setValue("mode", current_mode)

    def restore_window_state(self):
        """Restore window position, size and state"""
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))

        if self.settings.contains("windowState"):
            self.restoreState(self.settings.value("windowState"))

        # Restore last mode if available
        if self.settings.contains("mode"):
            mode = int(self.settings.value("mode", 0))
            # Apply mode after UI is set up
            QApplication.instance().processEvents()
            self.switch_mode(mode)

    def closeEvent(self, event):
        """Handle window close event"""
        self.save_window_state()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply theme from global theme manager
    theme_manager.apply_theme(app)

    # Add stylesheet for custom widgets
    app.setStyleSheet("""
        #header {
            background-color: #f0f0f0;
            border-bottom: 1px solid #d0d0d0;
        }
        
        #headerTab {
            font-size: 14px;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 4px;
        }
        
        #headerTab:checked {
            background-color: #e0e0e0;
        }
        
        #settingsButton {
            font-size: 16px;
            border-radius: 15px;
            background-color: #e0e0e0;
        }
        
        #settingsButton:hover {
            background-color: #d0d0d0;
        }
        
        #settingsPanel {
            background-color: #f8f8f8;
            border-left: 1px solid #d0d0d0;
        }
        
        #settingsHeader {
            color: #333;
        }
        
        #settingsLabel {
            font-weight: bold;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())