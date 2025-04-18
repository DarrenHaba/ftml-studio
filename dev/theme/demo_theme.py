import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QComboBox, QStyle)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize

from src.ftml_studio.ui.themes import theme_manager

class SimpleToolbar(QMainWindow):
    """A minimal test window for toolbar styling and icon loading"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Toolbar Styling Test")
        self.resize(600, 300)

        # Main container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        main_layout = QVBoxLayout(self.central_widget)

        # Theme selector
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
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
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch(1)

        main_layout.addLayout(theme_layout)

        # Create toolbar container
        self.create_toolbar(main_layout)

        # Add a placeholder
        label = QLabel("Toolbar styling test")
        label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(label, 1)

    def create_toolbar(self, parent_layout):
        """Create a horizontal toolbar with a settings button"""
        # Create toolbar container
        toolbar_container = QWidget()
        toolbar_container.setObjectName("toolbarContainer")

        # Toolbar layout
        toolbar_layout = QHBoxLayout(toolbar_container)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        toolbar_layout.setSpacing(10)

        # Current theme
        is_dark = theme_manager.get_active_theme() == theme_manager.DARK

        # Create settings button - first try local icon, then fallback
        self.settings_button = QPushButton()

        # Try to load local icon first
        local_icon_path = os.path.join(os.path.dirname(__file__), "settings.png")
        if os.path.exists(local_icon_path):
            print(f"Loading local icon: {local_icon_path}")
            self.settings_button.setIcon(QIcon(local_icon_path))
        else:
            # Fallback to system icon
            print(f"Local icon not found, using system icon")
            self.settings_button.setIcon(QApplication.style().standardIcon(QStyle.SP_FileDialogDetailedView))

        self.settings_button.setObjectName("toolbarButton")
        self.settings_button.setFixedSize(QSize(32, 32))
        self.settings_button.setToolTip("Settings")

        # Add button to toolbar
        toolbar_layout.addWidget(self.settings_button)
        toolbar_layout.addStretch(1)

        # Apply styling
        toolbar_container.setStyleSheet(self.get_toolbar_style(is_dark))

        # Add toolbar to parent layout
        parent_layout.addWidget(toolbar_container)

        # Store reference to container for theme updates
        self.toolbar_container = toolbar_container

    def get_toolbar_style(self, is_dark):
        """Get theme-aware toolbar style"""
        accent_color = theme_manager.accent_color

        # Theme-specific styling
        if is_dark:
            return f"""
                #toolbarContainer {{
                    background-color: #333333;
                    border-bottom: 1px solid #444444;
                }}
                
                QPushButton[objectName="toolbarButton"] {{
                    color: white;
                    background-color: transparent;
                    border: none;
                    border-radius: 4px;
                    padding: 4px;
                    margin: 2px;
                }}
                
                QPushButton[objectName="toolbarButton"]:hover {{
                    background-color: #444444;
                }}
                
                QPushButton[objectName="toolbarButton"]:pressed {{
                    background-color: {accent_color};
                }}
                
                QPushButton[objectName="toolbarButton"]:disabled {{
                    opacity: 0.5;
                }}
            """
        else:
            return f"""
                #toolbarContainer {{
                    background-color: #f0f0f0;
                    border-bottom: 1px solid #e0e0e0;
                }}
                
                QPushButton[objectName="toolbarButton"] {{
                    color: #333333;
                    background-color: transparent;
                    border: none;
                    border-radius: 4px;
                    padding: 4px;
                    margin: 2px;
                }}
                
                QPushButton[objectName="toolbarButton"]:hover {{
                    background-color: #e0e0e0;
                }}
                
                QPushButton[objectName="toolbarButton"]:pressed {{
                    background-color: {accent_color};
                }}
                
                QPushButton[objectName="toolbarButton"]:disabled {{
                    opacity: 0.5;
                }}
            """

    def change_theme(self, index):
        """Change theme based on combo selection"""
        if index == 0:
            new_theme = theme_manager.LIGHT
        elif index == 1:
            new_theme = theme_manager.DARK
        else:
            new_theme = theme_manager.AUTO

        # Set theme
        theme_manager.set_theme(new_theme)

        # Apply to application
        app = QApplication.instance()
        theme_manager.apply_theme(app)

        # Update toolbar styling
        is_dark = theme_manager.get_active_theme() == theme_manager.DARK
        self.toolbar_container.setStyleSheet(self.get_toolbar_style(is_dark))

        # Show status
        self.statusBar().showMessage(f"Theme changed to {new_theme}")

# Option for Global Styling in Theme Manager
# Add this method to theme_manager.py
def get_global_toolbar_style(self, is_dark=None):
    """Get global toolbar styling for consistency"""
    # Determine theme if not specified
    if is_dark is None:
        is_dark = self.get_active_theme() == self.DARK

    accent_color = self.accent_color

    if is_dark:
        return f"""
            #toolbarContainer {{
                background-color: #333333;
                border-bottom: 1px solid #444444;
            }}
            
            QPushButton[objectName="toolbarButton"] {{
                color: white;
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
                margin: 2px;
            }}
            
            QPushButton[objectName="toolbarButton"]:hover {{
                background-color: #444444;
            }}
            
            QPushButton[objectName="toolbarButton"]:pressed {{
                background-color: {accent_color};
            }}
            
            QPushButton[objectName="toolbarButton"]:disabled {{
                opacity: 0.5;
            }}
        """
    else:
        return f"""
            #toolbarContainer {{
                background-color: #f0f0f0;
                border-bottom: 1px solid #e0e0e0;
            }}
            
            QPushButton[objectName="toolbarButton"] {{
                color: #333333;
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
                margin: 2px;
            }}
            
            QPushButton[objectName="toolbarButton"]:hover {{
                background-color: #e0e0e0;
            }}
            
            QPushButton[objectName="toolbarButton"]:pressed {{
                background-color: {accent_color};
            }}
            
            QPushButton[objectName="toolbarButton"]:disabled {{
                opacity: 0.5;
            }}
        """

# How you would use the global styling:
# toolbar_container.setStyleSheet(theme_manager.get_global_toolbar_style())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply initial theme
    theme_manager.apply_theme(app)

    # Create and show window
    window = SimpleToolbar()
    window.show()

    sys.exit(app.exec())