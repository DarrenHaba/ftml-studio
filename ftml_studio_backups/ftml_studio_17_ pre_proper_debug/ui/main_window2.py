# src/ftml_studio/ui/main_window.py
import sys
import logging
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout,
                               QWidget, QPushButton, QStackedWidget, QLabel,
                               QComboBox, QApplication, QFrame, QToolButton)
from PySide6.QtCore import Qt, QSettings, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QFont

# Import our window classes - now these are QWidgets, not QMainWindows
from src.ftml_studio.ui.elements.ftml_editor import FTMLEditorWidget
from src.ftml_studio.ui.elements.converter import ConverterWidget
from src.ftml_studio.ui.base_window import BaseWindow
from src.ftml_studio.ui.themes import theme_manager

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("main_window")

class SidebarButton(QPushButton):
    """Custom sidebar button with icon and text"""

    def __init__(self, icon_path, text, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(24, 24))
        self.setCheckable(True)
        self.setObjectName("sidebarButton")

        # Minimum size to ensure icon is visible in collapsed state
        self.setMinimumWidth(40)

        # Fixed height for uniform appearance
        self.setFixedHeight(40)

        # Left align text with icon
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 10px;
                border: none;
                border-radius: 0;
                margin: 0;
            }
            
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
            }
        """)

class Sidebar(QWidget):
    """Custom sidebar widget with collapsible behavior"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.expanded = True
        self.setObjectName("sidebar")

        # Fixed width when expanded and collapsed
        self.expanded_width = 200
        self.collapsed_width = 50
        self.setFixedWidth(self.expanded_width)

        # Handle styling
        self.setStyleSheet("""
            #sidebar {
                background-color: #333333;
                border-right: 1px solid #555555;
            }
            
            QToolButton {
                border: none;
                color: white;
                background-color: transparent;
            }
            
            QToolButton:hover {
                background-color: #444444;
            }
            
            #sidebarButton {
                color: white;
                background-color: transparent;
            }
            
            #sidebarButton:hover {
                background-color: #444444;
            }
            
            #sidebarButton:checked {
                background-color: #4CAF50;
                color: white;
            }
            
            QFrame#separator {
                background-color: #555555;
            }
        """)

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Setup the sidebar UI components"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Hamburger menu button at top
        self.hamburger_btn = QToolButton()
        self.hamburger_btn.setIcon(QIcon(":/icons/hamburger.png"))  # Replace with your icon path
        self.hamburger_btn.setIconSize(QSize(24, 24))
        self.hamburger_btn.setToolTip("Toggle Sidebar")
        self.hamburger_btn.clicked.connect(self.toggle_expansion)
        self.hamburger_btn.setFixedSize(QSize(50, 40))

        # Add hamburger button
        layout.addWidget(self.hamburger_btn, 0, Qt.AlignLeft)

        # Add a small space
        layout.addSpacing(10)

        # FTML Editor button
        self.editor_btn = SidebarButton(":/icons/editor.png", "FTML Editor")
        layout.addWidget(self.editor_btn)

        # Format Converter button
        self.converter_btn = SidebarButton(":/icons/converter.png", "Format Converter")
        layout.addWidget(self.converter_btn)

        # Add stretch to push settings to bottom
        layout.addStretch(1)

        # Add separator line
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # Settings button at bottom
        self.settings_btn = SidebarButton(":/icons/settings.png", "Settings")
        layout.addWidget(self.settings_btn)

        # Add a small bottom space
        layout.addSpacing(10)

    def toggle_expansion(self):
        """Toggle between expanded and collapsed states"""
        self.expanded = not self.expanded
        target_width = self.expanded_width if self.expanded else self.collapsed_width

        # Create animation for smooth transition
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

        # Update the maximum width as well
        self.setMaximumWidth(target_width)

        # Update button display - hide/show text
        for btn in [self.editor_btn, self.converter_btn, self.settings_btn]:
            btn.setText(btn.text() if self.expanded else "")
            # Center icon when collapsed, left-align when expanded
            if self.expanded:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding-left: 10px;
                        border: none;
                        border-radius: 0;
                        margin: 0;
                    }
                    
                    QPushButton:checked {
                        background-color: #4CAF50;
                        color: white;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: center;
                        padding-left: 0px;
                        border: none;
                        border-radius: 0;
                        margin: 0;
                    }
                    
                    QPushButton:checked {
                        background-color: #4CAF50;
                        color: white;
                    }
                """)

class MainWindow(BaseWindow):
    """Main application window for FTML Studio"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FTML Studio")
        self.resize(1200, 800)
        self.settings = QSettings("FTMLStudio", "MainWindow")

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

        # Create the sidebar
        self.sidebar = Sidebar(self)
        self.main_layout.addWidget(self.sidebar)

        # Connect sidebar buttons to switch views
        self.sidebar.editor_btn.setChecked(True)  # Default to editor view
        self.sidebar.editor_btn.clicked.connect(lambda: self.switch_mode(0))
        self.sidebar.converter_btn.clicked.connect(lambda: self.switch_mode(1))
        self.sidebar.settings_btn.clicked.connect(self.show_settings)

        # Main content area (everything except sidebar)
        self.content_area = QWidget()
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Add content area to main layout
        self.main_layout.addWidget(self.content_area, 1)  # Stretch factor 1

        # Content area (main content)
        self.content_widget = QStackedWidget()
        content_layout.addWidget(self.content_widget)

        # Create editor widget
        self.editor_widget = FTMLEditorWidget()
        self.content_widget.addWidget(self.editor_widget)

        # Create converter widget
        self.converter_widget = ConverterWidget()
        self.content_widget.addWidget(self.converter_widget)

        # Create settings widget (initially not added to stack)
        self.setup_settings_panel()

        # Create status bar for application-wide messages
        self.statusBar().showMessage("Ready")

        logger.debug("MainWindow UI setup complete")

    def setup_settings_panel(self):
        """Create the settings panel widget"""
        # Create settings panel container
        self.settings_panel = QWidget()
        self.settings_panel.setObjectName("settingsPanel")

        # Settings panel layout
        settings_layout = QVBoxLayout(self.settings_panel)
        settings_layout.setContentsMargins(20, 20, 20, 20)
        settings_layout.setSpacing(15)

        # Settings header
        settings_header = QLabel("Settings")
        settings_header.setObjectName("settingsHeader")
        settings_header.setFont(QFont("Arial", 14, QFont.Bold))
        settings_header.setAlignment(Qt.AlignCenter)
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

        # Back button
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.hide_settings)
        settings_layout.addWidget(back_btn, 0, Qt.AlignRight)

        # Stretch to push content to the top
        settings_layout.addStretch(1)

        # Add to content widget
        self.content_widget.addWidget(self.settings_panel)

    def switch_mode(self, index):
        """Switch between editor and converter modes"""
        logger.debug(f"Switching to mode {index}")

        # Update sidebar buttons
        self.sidebar.editor_btn.setChecked(index == 0)
        self.sidebar.converter_btn.setChecked(index == 1)
        self.sidebar.settings_btn.setChecked(False)  # Uncheck settings

        # Switch the stacked widget
        self.content_widget.setCurrentIndex(index)

        # Set focus to the current widget
        if index == 0:
            self.editor_widget.setFocus()
        else:
            self.converter_widget.setFocus()

        # Process events to ensure focus changes are applied
        QApplication.processEvents()

    def show_settings(self):
        """Show the settings panel"""
        # Uncheck other buttons, keep settings checked
        self.sidebar.editor_btn.setChecked(False)
        self.sidebar.converter_btn.setChecked(False)
        self.sidebar.settings_btn.setChecked(True)

        # Show settings panel
        self.content_widget.setCurrentWidget(self.settings_panel)

    def hide_settings(self):
        """Hide settings and return to previous view"""
        # Determine which view to go back to (default to editor)
        previous_index = 0  # Default to editor

        # Go back to previous view
        self.switch_mode(previous_index)

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
        current_index = self.content_widget.currentIndex()
        if current_index < 2:  # Only save if it's editor or converter, not settings
            self.settings.setValue("mode", current_index)

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

    window = MainWindow()
    window.show()
    sys.exit(app.exec())