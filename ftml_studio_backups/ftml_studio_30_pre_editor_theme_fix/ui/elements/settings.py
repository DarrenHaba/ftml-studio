# src/ftml_studio/ui/elements/settings.py
import logging
import os
import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QComboBox, QApplication, QFrame,
                               QTabWidget, QColorDialog, QMessageBox,
                               QGridLayout, QGroupBox, QCheckBox, QMainWindow)
from PySide6.QtCore import Qt, QSettings, Signal
from PySide6.QtGui import QColor, QFont

from src.ftml_studio.ui.themes import theme_manager
from src.ftml_studio.logger import setup_logger, LOG_LEVELS

# Configure logging
logger = setup_logger("ftml_studio.settings_window")


class SettingsPanel(QWidget):
    """Settings panel for FTML Studio"""

    # Define signals
    settingsChanged = Signal()  # Signal to notify when settings are changed
    errorIndicatorSettingChanged = Signal(bool)  # Signal specifically for error indicator setting changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("FTMLStudio", "AppSettings")
        self.setup_ui()
        logger.debug("Settings panel initialized")

    def setup_ui(self):
        """Set up the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Settings header
        settings_header = QLabel("Settings")
        settings_header.setObjectName("settingsHeader")
        settings_header.setFont(QFont("Arial", 14, QFont.Bold))
        settings_header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(settings_header)

        # Reset button in top-right corner
        reset_btn = QPushButton("Reset All Settings")
        reset_btn.setObjectName("resetButton")
        reset_btn.clicked.connect(self.confirm_reset_settings)

        # Add reset button in top-right of header area
        header_layout = QHBoxLayout()
        header_layout.addWidget(settings_header, 1)  # Stretch to push reset button right
        header_layout.addWidget(reset_btn)
        main_layout.addLayout(header_layout)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # Create tabs for different setting categories
        self.tabs = QTabWidget()
        self.tabs.setObjectName("settingsTabs")

        # Add appearance tab
        self.appearance_tab = self.create_appearance_tab()
        self.tabs.addTab(self.appearance_tab, "Appearance")

        # Add editor tab
        self.editor_tab = self.create_editor_tab()
        self.tabs.addTab(self.editor_tab, "Editor")

        # Add tabs to main layout
        main_layout.addWidget(self.tabs)

        # Add back button if needed when used in main window
        if not isinstance(self.parent(), QMainWindow):  # Only add if not top-level window
            back_btn = QPushButton("Back")
            back_btn.clicked.connect(self.go_back)
            main_layout.addWidget(back_btn, 0, Qt.AlignRight)

        # Limit width of the settings panel
        self.setMaximumWidth(600)

        # Center the panel
        self.set_alignment(Qt.AlignCenter)

    def create_appearance_tab(self):
        """Create the appearance settings tab with separate accent colors for each theme"""
        appearance_widget = QWidget()
        layout = QVBoxLayout(appearance_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Theme group
        theme_group = QGroupBox("Theme")
        theme_layout = QGridLayout(theme_group)

        # Theme selection
        theme_label = QLabel("Application Theme:")
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
        theme_layout.addWidget(theme_label, 0, 0)
        theme_layout.addWidget(self.theme_combo, 0, 1)

        # Light theme accent color selection
        light_accent_label = QLabel("Light Theme Accent:")
        self.light_accent_btn = QPushButton()
        self.light_accent_btn.setFixedSize(30, 30)
        self.light_accent_btn.setToolTip("Select light theme accent color")
        self.light_accent_btn.clicked.connect(self.select_light_accent_color)

        # Dark theme accent color selection
        dark_accent_label = QLabel("Dark Theme Accent:")
        self.dark_accent_btn = QPushButton()
        self.dark_accent_btn.setFixedSize(30, 30)
        self.dark_accent_btn.setToolTip("Select dark theme accent color")
        self.dark_accent_btn.clicked.connect(self.select_dark_accent_color)

        # Set button colors to current accent colors
        self.update_color_buttons()

        # Add to layout
        theme_layout.addWidget(light_accent_label, 1, 0)
        theme_layout.addWidget(self.light_accent_btn, 1, 1)
        theme_layout.addWidget(dark_accent_label, 2, 0)
        theme_layout.addWidget(self.dark_accent_btn, 2, 1)

        layout.addWidget(theme_group)

        # Add stretch to push content to the top
        layout.addStretch(1)

        return appearance_widget

    def select_light_accent_color(self):
        """Open color dialog to select light theme accent color"""
        current_color = QColor(theme_manager.light_accent_color)
        color = QColorDialog.getColor(current_color, self, "Select Light Theme Accent Color")

        if color.isValid():
            # Set the new light theme accent color
            theme_manager.light_accent_color = color.name()

            # Update button appearance
            self.update_color_buttons()

            # Apply theme to update UI with new accent color
            app = QApplication.instance()
            theme_manager.apply_theme(app)

            # Emit signal that settings changed
            self.settingsChanged.emit()

            logger.debug(f"Light theme accent color changed to {color.name()}")

    def update_color_buttons(self):
        """Update color buttons appearance based on current accent colors"""
        # Set light accent button color
        light_accent_color = QColor(theme_manager.light_accent_color)
        self.light_accent_btn.setStyleSheet(
            f"QPushButton {{ background-color: {light_accent_color.name()}; border: 1px solid #999; }}"
            f"QPushButton:hover {{ border: 1px solid #333; }}"
        )

        # Set dark accent button color
        dark_accent_color = QColor(theme_manager.dark_accent_color)
        self.dark_accent_btn.setStyleSheet(
            f"QPushButton {{ background-color: {dark_accent_color.name()}; border: 1px solid #999; }}"
            f"QPushButton:hover {{ border: 1px solid #333; }}"
        )

    def select_dark_accent_color(self):
        """Open color dialog to select dark theme accent color"""
        current_color = QColor(theme_manager.dark_accent_color)
        color = QColorDialog.getColor(current_color, self, "Select Dark Theme Accent Color")

        if color.isValid():
            # Set the new dark theme accent color
            theme_manager.dark_accent_color = color.name()

            # Update button appearance
            self.update_color_buttons()

            # Apply theme to update UI with new accent color
            app = QApplication.instance()
            theme_manager.apply_theme(app)

            # Emit signal that settings changed
            self.settingsChanged.emit()

            logger.debug(f"Dark theme accent color changed to {color.name()}")

    def create_editor_tab(self):
        """Create the editor settings tab"""
        editor_widget = QWidget()
        layout = QVBoxLayout(editor_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Error highlighting group
        error_group = QGroupBox("Error Highlighting")
        error_layout = QVBoxLayout(error_group)

        # Show error indicators checkbox
        self.show_errors_checkbox = QCheckBox("Show error indicators in all FTML editors")

        # Load the setting
        show_errors = self.settings.value("editor/showErrorIndicators", True, type=bool)
        self.show_errors_checkbox.setChecked(show_errors)

        # Connect to save setting
        self.show_errors_checkbox.stateChanged.connect(self.save_error_indicators)

        # Add description label to explain the feature
        error_description = QLabel(
            "When enabled, syntax errors in FTML code will be highlighted with a red underline. "
            "In the FTML Editor, hover over the highlighted text to see the error message."
        )
        error_description.setWordWrap(True)
        error_description.setStyleSheet("color: #666; font-size: 10px;")

        error_layout.addWidget(self.show_errors_checkbox)
        error_layout.addWidget(error_description)
        layout.addWidget(error_group)

        # Add stretch to push content to the top
        layout.addStretch(1)

        return editor_widget

    def update_color_button(self):
        """Update color button appearance based on current accent color"""
        accent_color = QColor(theme_manager.accent_color)

        # Set button background color using stylesheet
        self.accent_color_btn.setStyleSheet(
            f"QPushButton {{ background-color: {accent_color.name()}; border: 1px solid #999; }}"
            f"QPushButton:hover {{ border: 1px solid #333; }}"
        )

    def select_accent_color(self):
        """Open color dialog to select accent color"""
        current_color = QColor(theme_manager.accent_color)
        color = QColorDialog.getColor(current_color, self, "Select Accent Color")

        if color.isValid():
            # Set the new accent color
            theme_manager.accent_color = color.name()

            # Update button appearance
            self.update_color_button()

            # Save the setting
            self.settings.setValue("appearance/accentColor", color.name())

            # Apply theme to update UI with new accent color
            app = QApplication.instance()
            theme_manager.apply_theme(app)

            # Emit signal that settings changed
            self.settingsChanged.emit()

            logger.debug(f"Accent color changed to {color.name()}")

    def change_theme(self, index):
        """Change the application theme based on combo box selection"""
        try:
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

            # Emit signal that settings changed
            self.settingsChanged.emit()

            logger.debug("Theme change complete")

        except Exception as e:
            logger.error(f"Error changing theme: {str(e)}", exc_info=True)

    def save_error_indicators(self, state):
        """Save error indicators setting"""
        # Convert state to bool
        enabled = bool(state)

        # Save the setting
        self.settings.setValue("editor/showErrorIndicators", enabled)

        # Emit signal that settings changed
        self.settingsChanged.emit()

        # Emit specific signal for error indicators change
        self.errorIndicatorSettingChanged.emit(enabled)

        logger.debug(f"Global show error indicators set to {enabled}")

    def confirm_reset_settings(self):
        """Show confirmation dialog before resetting settings"""
        confirm = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to default values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            self.reset_settings()

    def reset_settings(self):
        """Reset all settings to default values"""
        # Store the current error indicator setting before clearing
        old_error_indicator_setting = self.settings.value("editor/showErrorIndicators", True, type=bool)

        # Clear all settings
        self.settings.clear()

        # Reset theme to default (AUTO)
        theme_manager.set_theme(theme_manager.AUTO)
        self.theme_combo.setCurrentIndex(2)  # Auto

        # Reset accent colors
        theme_manager.reset_colors()
        self.update_color_buttons()

        # Reset editor settings
        self.show_errors_checkbox.setChecked(True)

        # Apply theme changes
        app = QApplication.instance()
        theme_manager.apply_theme(app)

        # Emit signal that settings changed
        self.settingsChanged.emit()

        # Emit error indicator specific signal if it changed
        if not old_error_indicator_setting:  # Default is True
            self.errorIndicatorSettingChanged.emit(True)

        logger.debug("All settings reset to defaults")

    def go_back(self):
        """Go back to previous screen - to be implemented by parent"""
        pass

    def set_alignment(self, alignment):
        """Custom method to help center the panel"""
        if self.parent() and not isinstance(self.parent(), QMainWindow):
            # Add spacer items to center the panel
            parent_layout = self.parent().layout()
            if parent_layout and isinstance(parent_layout, QHBoxLayout):
                # Clear existing layout
                while parent_layout.count():
                    item = parent_layout.takeAt(0)
                    if item.widget():
                        item.widget().setParent(None)

                # Add spacers around the panel
                parent_layout.addStretch(1)
                parent_layout.addWidget(self)
                parent_layout.addStretch(1)

    def get_error_indicators_setting(self):
        """Utility method to get the current error indicators setting"""
        return self.settings.value("editor/showErrorIndicators", True, type=bool)


class SettingsTestWindow(QMainWindow):
    """Test window for standalone settings testing"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings Test Window")
        self.resize(800, 600)

        # Main container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        main_layout = QHBoxLayout(self.central_widget)

        # Create settings panel
        self.settings_panel = SettingsPanel(self)

        # Connect settings changed signal
        self.settings_panel.settingsChanged.connect(self.on_settings_changed)

        # Add panel to layout
        main_layout.addWidget(self.settings_panel)

    def on_settings_changed(self):
        """Handle settings changed event"""
        self.statusBar().showMessage("Settings changed", 3000)


# Allow standalone execution for testing
if __name__ == "__main__":
    current_level = os.environ.get('FTML_STUDIO_LOG_LEVEL', 'DEBUG')
    logger.setLevel(LOG_LEVELS.get(current_level, logging.DEBUG))
    logger.debug(f"Starting FTML Studio application with log level: {current_level}")

    app = QApplication(sys.argv)

    # Apply initial theme
    theme_manager.apply_theme(app)

    # Create and show test window
    window = SettingsTestWindow()
    window.show()

    sys.exit(app.exec())
