# src/ftml_studio/ui/elements/sidebar.py
import os
import sys
import logging
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QFrame, QStyle, QApplication,
                               QMainWindow, QComboBox, QLabel, QGraphicsColorizeEffect)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, Signal
from PySide6.QtGui import QIcon, QPixmap, QColor

from src.ftml_studio.ui.themes import theme_manager
from src.ftml_studio.logger import setup_logger

# Configure logging
logger = setup_logger("ftml_studio.sidebar")


class ThemedIcon:
    """Utility class for theme-aware icons"""

    @staticmethod
    def load(icon_name, parent=None, is_dark_theme=False):
        """Load an icon from the appropriate theme folder or fallback to system icon"""
        # Select folder based on theme
        folder = "light" if is_dark_theme else "dark"

        # Path to the icon file in the theme-specific folder
        icon_path = os.path.join(os.path.dirname(__file__), f"../icons/{folder}/{icon_name}.png")

        # Try fallback path if main path doesn't exist
        if not os.path.exists(icon_path):
            fallback_path = os.path.join(os.path.dirname(__file__), f"../icons/{icon_name}.png")
            if os.path.exists(fallback_path):
                logger.debug(f"Using fallback icon at: {fallback_path}")
                return QIcon(fallback_path)

            # If neither path works, use a system icon
            logger.warning(f"Icon not found: {icon_name}, using system fallback")

            # Map icon names to appropriate system icons
            system_icon_map = {
                "menu": QStyle.SP_CommandLink,
                "menu_open": QStyle.SP_ArrowRight,
                "menu_close": QStyle.SP_ArrowLeft,
                "editor": QStyle.SP_FileIcon,
                "converter": QStyle.SP_FileLinkIcon,
                "settings": QStyle.SP_FileDialogDetailedView
            }

            # Get appropriate system icon or default to file icon
            icon_type = system_icon_map.get(icon_name, QStyle.SP_FileIcon)
            return QApplication.style().standardIcon(icon_type)

        # Return the themed icon if found
        return QIcon(icon_path)


class SidebarButton(QPushButton):
    """Custom sidebar button with icon and text"""

    def __init__(self, icon_name, text, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.parent_sidebar = parent  # Store reference to parent sidebar

        # Store icon name for later reference
        self.icon_name = icon_name

        # Store the hover states for menu button
        self.hover_icon_map = {
            "menu": {
                "hover": "menu_open" if not parent.expanded else "menu_close",
                "normal": "menu"
            }
        }

        # Track hover state
        self.is_hovered = False

        # Get current theme
        is_dark = theme_manager.get_active_theme() == theme_manager.DARK

        # Set icon with theme awareness
        self.setIcon(ThemedIcon.load(icon_name, self, is_dark))

        self.setIconSize(QSize(24, 24))
        self.setCheckable(True)
        self.setObjectName("sidebarButton")

        # Minimum size to ensure icon is visible in collapsed state
        self.setMinimumWidth(40)

        # Fixed height for uniform appearance
        self.setFixedHeight(40)

        # Install event filter for hover events if this is a menu button
        if icon_name == "menu":
            self.installEventFilter(self)
            self.setCheckable(False)  # Menu button is not checkable

        logger.debug(f"Created SidebarButton: {icon_name} - {text}")

    def update_theme(self, is_dark):
        """Update icon based on theme change"""
        if self.icon_name == "menu" and self.is_hovered:
            # If menu button and hovered, use appropriate hover icon
            hover_icon = "menu_close" if self.parent_sidebar.expanded else "menu_open"
            self.setIcon(ThemedIcon.load(hover_icon, self, is_dark))
        else:
            self.setIcon(ThemedIcon.load(self.icon_name, self, is_dark))

    def eventFilter(self, watched, event):
        """Event filter to handle hover events for menu button"""
        if self.icon_name == "menu":
            if event.type() == event.Type.Enter:
                self.is_hovered = True
                is_dark = theme_manager.get_active_theme() == theme_manager.DARK
                # Use the appropriate hover icon based on sidebar state
                hover_icon = "menu_close" if self.parent_sidebar.expanded else "menu_open"
                self.setIcon(ThemedIcon.load(hover_icon, self, is_dark))
                return True

            elif event.type() == event.Type.Leave:
                self.is_hovered = False
                is_dark = theme_manager.get_active_theme() == theme_manager.DARK
                normal_icon = self.hover_icon_map["menu"]["normal"]
                self.setIcon(ThemedIcon.load(normal_icon, self, is_dark))
                return True

        return super().eventFilter(watched, event)

    def update_hover_icon(self):
        """Update the hover icon if currently being hovered"""
        if self.icon_name == "menu" and self.is_hovered:
            is_dark = theme_manager.get_active_theme() == theme_manager.DARK
            hover_icon = "menu_close" if self.parent_sidebar.expanded else "menu_open"
            self.setIcon(ThemedIcon.load(hover_icon, self, is_dark))


class Sidebar(QWidget):
    """Custom sidebar widget with collapsible behavior"""

    # Define signals for the sidebar
    modeChanged = Signal(int)  # Signal to notify when a mode button is clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        # Start with collapsed sidebar
        self.expanded = False
        self.setObjectName("sidebar")

        # Fixed width when collapsed
        self.collapsed_width = 50

        # Calculate optimal expanded width
        self.expanded_width = self.calculate_optimal_width()

        # Set initial width to collapsed state
        self.setFixedWidth(self.collapsed_width)
        self.setMinimumWidth(self.collapsed_width)
        self.setMaximumWidth(self.collapsed_width)

        # Setup UI
        self.setup_ui()
        logger.debug(f"Sidebar initialized in {'expanded' if self.expanded else 'collapsed'} state")

    def calculate_optimal_width(self):
        """Calculate the optimal expanded width based on text content"""
        # Get font metrics to measure text width
        font_metrics = self.fontMetrics()

        # Measure the width of each text item
        texts = ["FTML Editor", "Format Converter", "Settings"]
        text_widths = [font_metrics.horizontalAdvance(text) for text in texts]

        # Find the longest text width
        max_text_width = max(text_widths) if text_widths else 0

        # Add width for icon (24px) + padding (10px left + 15px right) + buffer
        optimal_width = max_text_width + 24 + 10 + 15 + 5

        # Ensure minimum width of 150px and maximum of 220px
        optimal_width = max(150, min(220, optimal_width))

        return optimal_width

    def setup_ui(self):
        """Setup the sidebar UI components"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Menu button at top
        self.hamburger_btn = SidebarButton("menu", "", self)
        self.hamburger_btn.setObjectName("hamburgerButton")
        self.hamburger_btn.setToolTip("Toggle Sidebar")
        self.hamburger_btn.clicked.connect(self.toggle_expansion)
        self.hamburger_btn.setCheckable(False)  # Not checkable
        self.hamburger_btn.setFixedHeight(40)  # Make sure it has enough height
        self.hamburger_btn.setContentsMargins(0, 0, 0, 0)  # Remove any margins

        # Add hamburger button with left alignment
        layout.addWidget(self.hamburger_btn, 0, Qt.AlignLeft)

        # Add a small space
        layout.addSpacing(10)

        # FTML Editor button - initially with no text (collapsed)
        self.editor_btn = SidebarButton("editor", "", self)
        layout.addWidget(self.editor_btn)

        # Format Converter button - initially with no text (collapsed)
        self.converter_btn = SidebarButton("converter", "", self)
        layout.addWidget(self.converter_btn)

        # Add stretch to push settings to bottom
        layout.addStretch(1)

        # Add separator line
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # Settings button at bottom - initially with no text (collapsed)
        self.settings_btn = SidebarButton("settings", "", self)
        layout.addWidget(self.settings_btn)

        # Add a small bottom space
        layout.addSpacing(10)

        # Connect button signals
        self.editor_btn.clicked.connect(lambda: self.handle_mode_button(0))
        self.converter_btn.clicked.connect(lambda: self.handle_mode_button(1))
        self.settings_btn.clicked.connect(lambda: self.handle_mode_button(2))

        # Apply styling
        self.apply_styling()

        logger.debug("Sidebar UI components created")

    def handle_mode_button(self, mode_index):
        """Handle sidebar mode button clicks"""
        # Update button states
        self.editor_btn.setChecked(mode_index == 0)
        self.converter_btn.setChecked(mode_index == 1)
        self.settings_btn.setChecked(mode_index == 2)

        # Update hover state mapping
        self.hamburger_btn.update_hover_icon()

        # If menu button is currently being hovered, update its icon
        if self.hamburger_btn.is_hovered:
            is_dark = theme_manager.get_active_theme() == theme_manager.DARK
            hover_icon = "menu_close" if self.expanded else "menu_open"
            self.hamburger_btn.setIcon(ThemedIcon.load(hover_icon, self, is_dark))

        # Emit signal to notify MainWindow
        self.modeChanged.emit(mode_index)

        # Log the mode change for testing
        logger.debug(f"Mode changed to {mode_index}")

    def apply_styling(self):
        """Apply styling to sidebar components based on current theme"""
        is_dark = theme_manager.get_active_theme() == theme_manager.DARK
        accent_color = theme_manager.accent_color

        # Sidebar container styling
        # self.setStyleSheet(self.get_sidebar_style(is_dark))

        # Hamburger button styling
        self.hamburger_btn.setStyleSheet(self.get_hamburger_style(is_dark))

        # Regular buttons styling
        button_style = self.get_button_style(is_dark, self.expanded, accent_color)
        for btn in [self.editor_btn, self.converter_btn, self.settings_btn]:
            btn.setStyleSheet(button_style)

    # def get_sidebar_style(self, is_dark):
    #     """Get sidebar container style"""
    #     if is_dark:
    #         return """
    #             #sidebar {
    #                 background-color: #333333;
    #                 border-right: 1px solid #555555;
    #             }
    #             
    #             QFrame#separator {
    #                 background-color: #555555;
    #             }
    #         """
    #     else:
    #         return """
    #             #sidebar {
    #                 background-color: #e0e0e0;
    #                 border-right: 1px solid #cccccc;
    #             }
    #             
    #             QFrame#separator {
    #                 background-color: #cccccc;
    #             }
    #         """

    def get_hamburger_style(self, is_dark):
        """Get hamburger button style"""
        if is_dark:
            return """
                QPushButton#hamburgerButton {
                    text-align: left;
                    padding-left: 10px;
                    border: none;
                    border-radius: 0;
                    margin: 0;
                    color: white;
                    background-color: transparent;
                }
                
                QPushButton#hamburgerButton:hover {
                    background-color: #444444;
                }
            """
        else:
            return """
                QPushButton#hamburgerButton {
                    text-align: left;
                    padding-left: 10px;
                    border: none;
                    border-radius: 0;
                    margin: 0;
                    color: #333333;
                    background-color: transparent;
                }
                
                QPushButton#hamburgerButton:hover {
                    background-color: #d0d0d0;
                }
            """

    def get_button_style(self, is_dark, is_expanded, accent_color):
        """Get sidebar button style"""
        # Use theme-appropriate text colors for both normal and checked states
        checked_text_color = "white" if is_dark else "#333333"
    
        base_style = f"""
            QPushButton {{
                text-align: left;
                padding-left: 10px;
                padding-right: 0px;
                border: none;
                border-radius: 0;
                margin: 0;
            }}
            
            QPushButton:checked {{
                background-color: {accent_color};
                color: {checked_text_color};
            }}
            
            /* Ensure checked+hover state keeps accent color */
            QPushButton:checked:hover {{
                background-color: {accent_color};
            }}
        """
    
        if is_dark:
            return base_style + """
                QPushButton {
                    color: white;
                    background-color: transparent;
                }
                
                QPushButton:hover:!checked {
                    background-color: #444444;
                }
            """
        else:
            return base_style + """
                QPushButton {
                    color: #333333;
                    background-color: transparent;
                }
                
                QPushButton:hover:!checked {
                    background-color: #d0d0d0;
                }
                """

    def toggle_expansion(self):
        """Toggle between expanded and collapsed states"""
        logger.debug(f"Toggling sidebar: current state={self.expanded}")
        logger.debug(f"Toggling sidebar. Current expanded state: {self.expanded}")

        # Store current state before changing it
        was_expanded = self.expanded
        self.expanded = not was_expanded

        # If collapsing, remove text before animation
        if not self.expanded:
            logger.debug(f"Collapsing sidebar - removing button texts")
            for btn in [self.editor_btn, self.converter_btn, self.settings_btn]:
                btn.setText("")
                # Apply styling
                is_dark = theme_manager.get_active_theme() == theme_manager.DARK
                btn.setStyleSheet(self.get_button_style(is_dark, self.expanded, theme_manager.accent_color))

            # Force layout update
            self.layout().invalidate()
            self.layout().activate()
            QApplication.processEvents()

        # Calculate target width
        target_width = self.expanded_width if self.expanded else self.collapsed_width
        logger.debug(f"Animation target width: {target_width}")

        # Create animation
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Set maximum width
        self.setMaximumWidth(target_width)

        # Connect animation finished signal
        if self.expanded:
            logger.debug(f"Connecting add_button_texts to animation finished")
            self.animation.finished.connect(self.animation_finished)
        else:
            # For collapse animation, just update hover icon when animation finishes
            self.animation.finished.connect(self.update_hamburger_hover)

        # Start animation
        self.animation.start()

        logger.debug(f"Sidebar toggled to {'expanded' if self.expanded else 'collapsed'}")
        logger.debug(f"Sidebar toggle complete. New expanded state: {self.expanded}")

    def animation_finished(self):
        """Handle animation finished for expansion"""
        # Add button texts
        self.add_button_texts()

        # Update hamburger hover icon if it's still being hovered
        self.update_hamburger_hover()

        # Disconnect to avoid multiple connections
        try:
            self.animation.finished.disconnect(self.animation_finished)
        except:
            pass  # Signal might not be connected

    def update_hamburger_hover(self):
        """Update hamburger button hover icon based on current sidebar state"""
        # Update the hamburger button's hover icon if it's currently hovered
        self.hamburger_btn.update_hover_icon()

        # Disconnect any animation signal
        try:
            self.animation.finished.disconnect()
        except:
            pass  # Signal might not be connected

    def add_button_texts(self):
        """Add button texts after expansion animation completes"""
        # Add texts to buttons
        for btn in [self.editor_btn, self.converter_btn, self.settings_btn]:
            if btn.icon_name == "editor":
                btn.setText("FTML Editor")
            elif btn.icon_name == "converter":
                btn.setText("Format Converter")
            elif btn.icon_name == "settings":
                btn.setText("Settings")

            # Apply theme-aware styling
            is_dark = theme_manager.get_active_theme() == theme_manager.DARK
            btn.setStyleSheet(self.get_button_style(is_dark, self.expanded, theme_manager.accent_color))

        # If hamburger button is still being hovered, update its icon
        if self.hamburger_btn.is_hovered:
            is_dark = theme_manager.get_active_theme() == theme_manager.DARK
            hover_icon = "menu_close" if self.expanded else "menu_open"
            self.hamburger_btn.setIcon(ThemedIcon.load(hover_icon, self, is_dark))

        # Disconnect to avoid multiple connections
        try:
            self.animation.finished.disconnect(self.add_button_texts)
        except:
            pass  # Signal might not be connected

    def update_theme(self):
        """Update styling when theme changes"""
        is_dark = theme_manager.get_active_theme() == theme_manager.DARK
        logger.debug(f"Theme update triggered. Active theme is{'DARK' if is_dark else 'LIGHT'}")
        logger.debug(f"Sidebar expanded state: {self.expanded}")

        self.apply_styling()

        # Update button icons
        for btn in [self.editor_btn, self.converter_btn, self.settings_btn, self.hamburger_btn]:
            logger.debug(f"Updating button icon: {btn.icon_name if hasattr(btn, 'icon_name') else 'hamburger'}")
            if hasattr(btn, 'update_theme'):
                btn.update_theme(is_dark)

        logger.debug(f"Theme update completed")


# Test window for standalone execution
class SidebarTestWindow(QMainWindow):
    """Test window for standalone sidebar testing"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sidebar Component Test")
        self.resize(400, 600)

        # Main container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        main_layout = QHBoxLayout(self.central_widget)

        # Create sidebar
        self.sidebar = Sidebar()

        # Theme selector
        theme_container = QWidget()
        theme_layout = QVBoxLayout(theme_container)

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
        theme_layout.addStretch(1)  # Push everything to the top

        # Add components to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(theme_container, 1)  # Give theme container stretch

        # Connect sidebar signals to logging
        self.sidebar.modeChanged.connect(self.on_mode_changed)

    def on_mode_changed(self, mode_index):
        """Handle sidebar mode changes"""
        modes = ["Editor", "Converter", "Settings"]
        mode_name = modes[mode_index] if mode_index < len(modes) else f"Unknown ({mode_index})"
        self.statusBar().showMessage(f"Mode changed to: {mode_name}")

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

        # Update sidebar styling
        self.sidebar.update_theme()

        # Show status
        self.statusBar().showMessage(f"Theme changed to {new_theme}")


# Allow standalone execution for testing
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply initial theme
    theme_manager.apply_theme(app)

    # Create and show test window
    window = SidebarTestWindow()
    window.show()

    sys.exit(app.exec())
