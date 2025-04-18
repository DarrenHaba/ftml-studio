# src/ftml_studio/ui/main_window.py
import sys
import logging
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout,
                               QWidget, QPushButton, QStackedWidget, QLabel,
                               QComboBox, QApplication, QFrame)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QFont

# Import our window classes
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

        # Content area (main content)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)

        # Stacked widget for main content (editor/converter)
        self.main_stack = QStackedWidget()

        # Create the editor widget
        self.editor_widget = FTMLASTDemo()
        self.editor_widget.setWindowFlags(Qt.Widget)  # Change window behavior to embedded widget

        # Create the converter widget
        self.converter_widget = ConverterWindow()
        self.converter_widget.setWindowFlags(Qt.Widget)  # Change window behavior to embedded widget

        # Add widgets to the stack
        self.main_stack.addWidget(self.editor_widget)
        self.main_stack.addWidget(self.converter_widget)

        # Add toolbar for navigation
        self.create_toolbar()

        # Add main content stack to the layout
        self.content_layout.addWidget(self.main_stack)

        # Add content widget to main layout
        self.main_layout.addWidget(self.content_widget, 1)  # Stretch factor 1

        # Create right sidebar with icons
        self.create_sidebar()

        # Create settings panel (initially hidden)
        self.create_settings_panel()

        # Initial state - hide settings
        self.settings_panel.hide()

        logger.debug("MainWindow UI setup complete")

    def create_toolbar(self):
        """Create the toolbar for navigating between modes"""
        # Create toolbar widget at the top
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)

        # Create buttons for different modes
        self.editor_btn = QPushButton("FTML Editor")
        self.editor_btn.setCheckable(True)
        self.editor_btn.setChecked(True)
        self.editor_btn.clicked.connect(lambda: self.switch_mode(0))

        self.converter_btn = QPushButton("Format Converter")
        self.converter_btn.setCheckable(True)
        self.converter_btn.clicked.connect(lambda: self.switch_mode(1))

        # Add buttons to toolbar
        toolbar_layout.addWidget(self.editor_btn)
        toolbar_layout.addWidget(self.converter_btn)
        toolbar_layout.addStretch(1)  # Push buttons to the left

        # Add toolbar to content layout
        self.content_layout.addWidget(toolbar_widget)

    def create_sidebar(self):
        """Create the sidebar with icon buttons"""
        # Create sidebar container
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(40)  # Fixed width for icons
        self.sidebar.setObjectName("sidebar")  # For styling

        # Sidebar layout
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(5, 10, 5, 10)
        sidebar_layout.setSpacing(15)

        # Create settings button (gear icon)
        self.settings_btn = QPushButton("⚙")  # Unicode gear symbol
        self.settings_btn.setObjectName("sidebarButton")
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.clicked.connect(self.toggle_settings_panel)

        # Add buttons to sidebar
        sidebar_layout.addWidget(self.settings_btn)
        sidebar_layout.addStretch(1)  # Push buttons to the top

        # Add sidebar to main layout
        self.main_layout.addWidget(self.sidebar)

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

        # Settings header
        settings_header = QLabel("Settings")
        settings_header.setObjectName("settingsHeader")
        settings_header.setFont(QFont("Arial", 14, QFont.Bold))
        settings_layout.addWidget(settings_header)

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

        # Switch the stacked widget
        self.main_stack.setCurrentIndex(index)

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

        # Update the editor and converter widgets
        if hasattr(self.editor_widget, 'recreate_highlighter'):
            self.editor_widget.recreate_highlighter()

        if hasattr(self.converter_widget, 'recreate_highlighters'):
            self.converter_widget.recreate_highlighters()

    def save_window_state(self):
        """Save window position, size and state"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("mode", self.main_stack.currentIndex())

    def restore_window_state(self):
        """Restore window position, size and state"""
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))

        if self.settings.contains("windowState"):
            self.restoreState(self.settings.value("windowState"))

        # Restore last mode if available
        if self.settings.contains("mode"):
            mode = int(self.settings.value("mode", 0))
            # We'll apply this after UI is set up
            QApplication.instance().processEvents()
            self.main_stack.setCurrentIndex(mode)

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
        #sidebar {
            background-color: #f0f0f0;
            border-right: 1px solid #d0d0d0;
        }
        
        #sidebarButton {
            font-size: 16px;
            border-radius: 15px;
            background-color: #e0e0e0;
        }
        
        #sidebarButton:hover {
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