# src/ftml_studio/ui/main_window.py
import sys
import os
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout,
                               QWidget, QStackedWidget, QApplication)
from PySide6.QtCore import QSettings

from src.ftml_studio.ui.elements.ftml_editor import FTMLEditorWidget
from src.ftml_studio.ui.elements.converter import ConverterWidget
from src.ftml_studio.ui.elements.settings import SettingsPanel  # Import new SettingsPanel
from src.ftml_studio.ui.base_window import BaseWindow
from src.ftml_studio.ui.elements.sidebar import Sidebar  # Import the standalone sidebar
from src.ftml_studio.ui.themes import theme_manager
from src.ftml_studio.logger import setup_logger

# Configure logging
logger = setup_logger("ftml_studio.main_window")

class MainWindow(BaseWindow):
    """Main application window for FTML Studio"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FTML Studio")
        self.resize(1200, 800)
        self.settings = QSettings("FTMLStudio", "MainWindow")

        logger.debug("Initializing MainWindow")

        # Ensure icons directory exists
        icons_dir = os.path.join(os.path.dirname(__file__), "icons")
        if not os.path.exists(icons_dir):
            try:
                os.makedirs(icons_dir)
                logger.debug(f"Created icons directory: {icons_dir}")
            except Exception as e:
                logger.warning(f"Failed to create icons directory: {e}")

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

        # Create the sidebar using the new standalone component
        self.sidebar = Sidebar(self)
        self.main_layout.addWidget(self.sidebar)

        # Connect sidebar mode change signal
        self.sidebar.modeChanged.connect(self.handle_mode_change)

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

        # Create settings widget (replacing the old implementation)
        self.setup_settings_panel()

        # Create status bar for application-wide messages
        self.statusBar().showMessage("Ready")

        # Set initial mode
        self.handle_mode_change(0)  # Default to editor view

        # Apply global error indicators setting to all components
        self.apply_error_indicators_setting()

        logger.debug("MainWindow UI setup complete")

    def setup_settings_panel(self):
        """Create the settings panel using the new SettingsPanel class"""
        # Create settings panel from the new implementation
        self.settings_panel = SettingsPanel(self)

        # Override the go_back method to hide settings
        self.settings_panel.go_back = self.hide_settings

        # Connect settings changed signal
        self.settings_panel.settingsChanged.connect(self.update_theme_components)

        # Connect the specific error indicators setting change signal
        self.settings_panel.errorIndicatorSettingChanged.connect(self.on_error_indicators_changed)

        # Add to content widget
        self.content_widget.addWidget(self.settings_panel)

    def handle_mode_change(self, mode_index):
        """Handle sidebar mode changes"""
        logger.debug(f"Handling mode change to {mode_index}")

        if mode_index == 2:  # Settings
            self.show_settings()
        else:  # Editor (0) or Converter (1)
            self.switch_mode(mode_index)

    def switch_mode(self, index):
        """Switch between editor and converter modes"""
        logger.debug(f"Switching to mode {index}")

        # Update status for debugging
        mode_name = "FTML Editor" if index == 0 else "Format Converter" if index == 1 else "Unknown"
        logger.debug(f"Activating {mode_name} mode")

        # Switch the stacked widget
        if index < self.content_widget.count():
            self.content_widget.setCurrentIndex(index)
            logger.debug(f"Content widget switched to index {index}")
        else:
            logger.error(f"Invalid content widget index: {index}")

        # Set focus to the current widget
        if index == 0:
            self.editor_widget.setFocus()
            logger.debug("Focus set to editor widget")
        else:
            self.converter_widget.setFocus()
            logger.debug("Focus set to converter widget")

        # Process events to ensure focus changes are applied
        QApplication.processEvents()

        # Update status bar
        self.statusBar().showMessage(f"Switched to {mode_name}")

    def show_settings(self):
        """Show the settings panel"""
        logger.debug("Showing settings panel")

        # Store the current mode for when we return
        self.previous_mode = self.content_widget.currentIndex()
        logger.debug(f"Storing previous mode: {self.previous_mode}")

        # Show settings panel
        self.content_widget.setCurrentWidget(self.settings_panel)
        self.statusBar().showMessage("Settings")

    def hide_settings(self):
        """Hide settings and return to previous view"""
        logger.debug("Hiding settings panel")

        # Determine which view to go back to (default to editor)
        previous_index = getattr(self, 'previous_mode', 0)  # Default to editor
        logger.debug(f"Returning to previous mode: {previous_index}")

        # Go back to previous view
        self.switch_mode(previous_index)

        # Also update the sidebar button state
        self.sidebar.handle_mode_button(previous_index)

    def update_theme_components(self):
        """Update theme-dependent components after settings changes"""
        logger.debug("Updating theme components after settings change")

        # Update sidebar
        self.sidebar.update_theme()

        # Update the editor widget
        if hasattr(self.editor_widget, 'recreate_highlighter'):
            logger.debug("Recreating editor highlighter for new theme")
            self.editor_widget.recreate_highlighter()

        # Update converter
        if hasattr(self.converter_widget, 'recreate_highlighters'):
            logger.debug("Recreating converter highlighters for new theme")
            self.converter_widget.recreate_highlighters()

        # Show status message
        self.statusBar().showMessage("Settings updated", 3000)

    def on_error_indicators_changed(self, enabled):
        """Handle changes to the error indicators setting"""
        logger.debug(f"Error indicators setting changed to: {enabled}")

        # Apply the setting to all FTML editors
        self.apply_error_indicators_setting()

        # Show status message
        self.statusBar().showMessage(f"Error indicators {'enabled' if enabled else 'disabled'}", 3000)

    def apply_error_indicators_setting(self):
        """Apply the global error indicators setting to all editor components"""
        # Get the current setting from settings panel
        if hasattr(self, 'settings_panel'):
            enabled = self.settings_panel.get_error_indicators_setting()
            logger.debug(f"Applying error indicators setting: {enabled}")

            # Apply to editor widget
            if hasattr(self, 'editor_widget'):
                if hasattr(self.editor_widget, 'highlighter'):
                    self.editor_widget.highlighter.error_highlighting = enabled
                    self.editor_widget.highlighter.rehighlight()
                    logger.debug(f"Applied error highlighting setting to editor: {enabled}")

                # If editor has a checkbox, update it to match the global setting
                if hasattr(self.editor_widget, 'show_errors_checkbox'):
                    self.editor_widget.show_errors_checkbox.setChecked(enabled)
                    logger.debug(f"Updated editor's checkbox to: {enabled}")

            # Apply to converter widget - for any FTML highlighters it contains
            if hasattr(self, 'converter_widget'):
                # Update any FTML highlighters in the converter
                if hasattr(self.converter_widget, 'source_highlighter') and hasattr(self.converter_widget.source_highlighter, '__class__'):
                    if self.converter_widget.source_highlighter.__class__.__name__ == 'FTMLASTHighlighter':
                        self.converter_widget.source_highlighter.error_highlighting = enabled
                        self.converter_widget.source_highlighter.rehighlight()
                        logger.debug(f"Applied error highlighting to converter source editor: {enabled}")

                if hasattr(self.converter_widget, 'target_highlighter') and hasattr(self.converter_widget.target_highlighter, '__class__'):
                    if self.converter_widget.target_highlighter.__class__.__name__ == 'FTMLASTHighlighter':
                        self.converter_widget.target_highlighter.error_highlighting = enabled
                        self.converter_widget.target_highlighter.rehighlight()
                        logger.debug(f"Applied error highlighting to converter target editor: {enabled}")

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

            # Also update the sidebar button state
            # Note: This needs to happen after the sidebar is created in setup_ui
            QApplication.instance().processEvents()
            if hasattr(self, 'sidebar'):
                self.sidebar.handle_mode_button(mode)

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