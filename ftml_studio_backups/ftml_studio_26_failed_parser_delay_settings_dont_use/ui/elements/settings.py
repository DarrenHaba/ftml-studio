# src/ftml_studio/ui/elements/settings.py
import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QComboBox, QApplication, QFrame,
                               QTabWidget, QColorDialog, QMessageBox,
                               QGridLayout, QGroupBox, QCheckBox, QMainWindow,
                               QSlider)
from PySide6.QtCore import Qt, QSettings, Signal
from PySide6.QtGui import QColor, QFont

from src.ftml_studio.ui.themes import theme_manager
from src.ftml_studio.logger import setup_logger

# Configure logging
logger = setup_logger("ftml_studio.settings_window")

class SettingsPanel(QWidget):
    """Settings panel for FTML Studio"""

    # Define signals
    settingsChanged = Signal()  # Signal to notify when settings are changed
    errorIndicatorSettingChanged = Signal(bool)  # Signal specifically for error indicator setting changes
    parseSettingChanged = Signal()  # Signal specifically for parse setting changes

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
        self.setAlignment(Qt.AlignCenter)

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

    def create_editor_tab(self):
        """Create the editor settings tab"""
        editor_widget = QWidget()
        layout = QVBoxLayout(editor_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Auto-parsing group
        auto_parse_group = QGroupBox("FTML Parsing")
        auto_parse_layout = QVBoxLayout(auto_parse_group)

        # Auto-parse checkbox
        self.auto_parse_checkbox = QCheckBox("Automatically parse FTML for errors")
        auto_parse = self.settings.value("editor/autoParseEnabled", True, type=bool)
        self.auto_parse_checkbox.setChecked(auto_parse)
        self.auto_parse_checkbox.stateChanged.connect(self.save_auto_parse_setting)

        # Parse delay slider and label
        parse_delay_layout = QHBoxLayout()
        parse_delay_label = QLabel("Parse delay:")
        self.parse_delay_value_label = QLabel("1.0 seconds")  # will be updated by slider
        self.parse_delay_slider = QSlider(Qt.Horizontal)
        self.parse_delay_slider.setMinimum(1)  # 1 second
        self.parse_delay_slider.setMaximum(30)  # 30 seconds
        self.parse_delay_slider.setTickPosition(QSlider.TicksBelow)
        self.parse_delay_slider.setTickInterval(5)  # Tick every 5 seconds

        # Get current parse delay setting (default 0.5s converted to whole seconds)
        parse_delay_seconds = int(self.settings.value("editor/parseDelay", 500, type=int) / 1000)
        # Ensure it's within our new range
        parse_delay_seconds = max(1, min(30, parse_delay_seconds))
        self.parse_delay_slider.setValue(parse_delay_seconds)
        self.parse_delay_slider.valueChanged.connect(self.save_parse_delay)

        # Update label
        self.update_parse_delay_label(parse_delay_seconds)

        parse_delay_layout.addWidget(parse_delay_label)
        parse_delay_layout.addWidget(self.parse_delay_slider)
        parse_delay_layout.addWidget(self.parse_delay_value_label)

        auto_parse_layout.addWidget(self.auto_parse_checkbox)
        auto_parse_layout.addLayout(parse_delay_layout)

        # Description label
        auto_parse_description = QLabel(
            "When enabled, FTML code will be periodically checked for syntax errors. "
            "Disabling may improve performance with large files."
        )
        auto_parse_description.setWordWrap(True)
        auto_parse_description.setStyleSheet("color: #666; font-size: 10px;")
        auto_parse_layout.addWidget(auto_parse_description)

        layout.addWidget(auto_parse_group)

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

        # Update UI state based on auto-parse setting
        self.update_parsing_ui_state(auto_parse)

        # Add stretch to push content to the top
        layout.addStretch(1)

        return editor_widget

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

    def save_auto_parse_setting(self, state):
        """Save auto-parse setting"""
        enabled = bool(state)
        self.settings.setValue("editor/autoParseEnabled", enabled)

        # Update UI state
        self.update_parsing_ui_state(enabled)

        # Emit signal that settings changed
        self.settingsChanged.emit()

        # Emit specific signal for parse settings change
        self.parseSettingChanged.emit()

        logger.debug(f"Auto-parse setting set to {enabled}")

    def save_parse_delay(self, value):
        """Save parse delay setting"""
        # Convert slider value (seconds) to milliseconds for internal use
        delay_ms = value * 1000
        self.settings.setValue("editor/parseDelay", delay_ms)

        # Update the label
        self.update_parse_delay_label(value)

        # Emit signal that settings changed
        self.settingsChanged.emit()

        # Emit specific signal for parse settings change
        self.parseSettingChanged.emit()

        logger.debug(f"Parse delay set to {value} seconds ({delay_ms}ms)")

    def update_parse_delay_label(self, value):
        """Update the parse delay value label"""
        self.parse_delay_value_label.setText(f"{value}.0 seconds")

    def update_parsing_ui_state(self, enabled):
        """Update UI state based on auto-parse setting"""
        # Enable/disable parse delay controls
        self.parse_delay_slider.setEnabled(enabled)
        self.parse_delay_value_label.setEnabled(enabled)

        # If auto-parse is disabled, disable error highlighting too
        if not enabled:
            self.show_errors_checkbox.setChecked(False)
            self.show_errors_checkbox.setEnabled(False)
        else:
            self.show_errors_checkbox.setEnabled(True)

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
        # Store the current settings before clearing
        old_error_indicator_setting = self.settings.value("editor/showErrorIndicators", True, type=bool)
        old_auto_parse_setting = self.settings.value("editor/autoParseEnabled", True, type=bool)
        old_parse_delay_setting = self.settings.value("editor/parseDelay", 500, type=int)

        # Clear all settings
        self.settings.clear()

        # Reset theme to default (AUTO)
        theme_manager.set_theme(theme_manager.AUTO)
        self.theme_combo.setCurrentIndex(2)  # Auto

        # Reset accent colors
        theme_manager.reset_colors()
        self.update_color_buttons()

        # Reset editor settings
        self.auto_parse_checkbox.setChecked(True)
        self.parse_delay_slider.setValue(1)  # 1 second default
        self.show_errors_checkbox.setChecked(True)
        self.update_parsing_ui_state(True)

        # Apply theme changes
        app = QApplication.instance()
        theme_manager.apply_theme(app)

        # Emit signal that settings changed
        self.settingsChanged.emit()

        # Emit specific signals if settings changed
        if old_error_indicator_setting != True:
            self.errorIndicatorSettingChanged.emit(True)

        if old_auto_parse_setting != True or old_parse_delay_setting != 500:
            self.parseSettingChanged.emit()

        logger.debug("All settings reset to defaults")

    def go_back(self):
        """Go back to previous screen - to be implemented by parent"""
        pass

    def setAlignment(self, alignment):
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
        # If auto-parse is disabled, error indicators should also be disabled
        auto_parse = self.settings.value("editor/autoParseEnabled", True, type=bool)
        if not auto_parse:
            return False
        return self.settings.value("editor/showErrorIndicators", True, type=bool)

    def get_auto_parse_setting(self):
        """Utility method to get the current auto-parse setting"""
        return self.settings.value("editor/autoParseEnabled", True, type=bool)

    def get_parse_delay_setting(self):
        """Utility method to get the current parse delay setting in milliseconds"""
        return self.settings.value("editor/parseDelay", 500, type=int)


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
    app = QApplication(sys.argv)

    # Apply initial theme
    theme_manager.apply_theme(app)

    # Create and show test window
    window = SettingsTestWindow()
    window.show()

    sys.exit(app.exec())