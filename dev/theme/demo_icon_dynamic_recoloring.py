import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QFrame, QCheckBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, QLinearGradient

# Import theme manager - adjust path as needed
from src.ftml_studio.ui.themes.theme_manager import ThemeManager

# Create theme manager instance
theme_manager = ThemeManager()

class IconTintingMethods:
    """Contains different methods for tinting icons"""

    @staticmethod
    def use_colorize_effect(pixmap, color):
        """Tint using QGraphicsColorizeEffect (current method)"""
        if pixmap.isNull():
            return pixmap

        from PySide6.QtWidgets import QGraphicsColorizeEffect, QGraphicsScene, QGraphicsPixmapItem
        from PySide6.QtCore import QRectF

        # Create a colorize effect
        colorize_effect = QGraphicsColorizeEffect()
        colorize_effect.setColor(color)
        colorize_effect.setStrength(1.0)

        # Create a scene to apply the effect
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(pixmap)
        item.setGraphicsEffect(colorize_effect)
        scene.addItem(item)

        # Render the scene to a new pixmap
        result = QPixmap(pixmap.size())
        result.fill(Qt.transparent)

        painter = QPainter(result)
        scene.render(painter, QRectF(), QRectF(0, 0, pixmap.width(), pixmap.height()))
        painter.end()

        return result

    @staticmethod
    def use_source_in(pixmap, color):
        """Tint using QPainter with SourceIn composition mode (recommended)"""
        if pixmap.isNull():
            return pixmap

        result = QPixmap(pixmap.size())
        result.fill(Qt.transparent)  # Start with transparent background

        painter = QPainter(result)
        # Draw the original pixmap
        painter.drawPixmap(0, 0, pixmap)
        # Replace colors while preserving alpha
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(result.rect(), color)
        painter.end()

        return result

    @staticmethod
    def use_pixel_manipulation(pixmap, color):
        """Direct pixel-by-pixel manipulation"""
        if pixmap.isNull():
            return pixmap

        image = pixmap.toImage()
        for y in range(image.height()):
            for x in range(image.width()):
                pixel = image.pixel(x, y)
                if pixel != 0:  # Not fully transparent
                    # Replace with target color while preserving alpha
                    alpha = (pixel >> 24) & 0xff
                    new_pixel = (alpha << 24) | (color.red() << 16) | (color.green() << 8) | color.blue()
                    image.setPixel(x, y, new_pixel)
        return QPixmap.fromImage(image)


class IconButton(QPushButton):
    """Button with a customizable icon"""

    def __init__(self, icon_path, tint_method=None, tint_color=None, parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.tint_method = tint_method
        self.tint_color = tint_color

        self.setIconSize(QSize(24, 24))
        self.setFixedSize(QSize(40, 40))
        self.setStyleSheet("background-color: transparent; border: none;")

        self.update_icon()

    def update_icon(self):
        """Update the icon based on current settings"""
        if not os.path.exists(self.icon_path):
            return

        pixmap = QPixmap(self.icon_path)

        # Apply tinting if specified
        if self.tint_method and self.tint_color:
            pixmap = self.tint_method(pixmap, self.tint_color)

        self.setIcon(QIcon(pixmap))


class TransparencyTestWindow(QMainWindow):
    """Test window showing icons with different backgrounds to check transparency"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Icon Transparency Test")
        self.resize(800, 500)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Theme selector
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([theme_manager.LIGHT, theme_manager.DARK, theme_manager.AUTO])
        self.theme_combo.setCurrentText(theme_manager.current_theme)
        self.theme_combo.currentTextChanged.connect(self.change_theme)

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()

        main_layout.addLayout(theme_layout)

        # Icon path
        icon_path = os.path.join(os.path.dirname(__file__), "settings.png")
        if not os.path.exists(icon_path):
            error_label = QLabel(f"Icon not found: {icon_path}")
            main_layout.addWidget(error_label)
            return

        # Show original icon
        original_layout = QHBoxLayout()
        original_layout.addWidget(QLabel("Original Icon:"))
        original_icon = QLabel()
        original_icon.setPixmap(QPixmap(icon_path).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        original_layout.addWidget(original_icon)
        original_layout.addStretch()
        main_layout.addLayout(original_layout)

        # Create background options
        self.show_checkerboard = QCheckBox("Show Checkerboard (to visualize transparency)")
        self.show_checkerboard.setChecked(True)
        self.show_checkerboard.stateChanged.connect(self.update_backgrounds)
        main_layout.addWidget(self.show_checkerboard)

        # Create gradient background
        self.gradient_frame = QFrame()
        self.gradient_frame.setMinimumHeight(150)
        self.gradient_frame.setFrameShape(QFrame.StyledPanel)
        self.gradient_frame.setStyleSheet("")  # Will be set in update_backgrounds

        # Label
        gradient_label = QLabel("Icons on Gradient Background (to check for any non-transparent areas)")
        main_layout.addWidget(gradient_label)
        main_layout.addWidget(self.gradient_frame)

        # Add buttons on gradient background
        gradient_layout = QHBoxLayout(self.gradient_frame)

        # Dark theme color
        dark_color = QColor(40, 40, 40)

        # Original white icon
        self.original_btn = IconButton(icon_path)
        gradient_layout.addWidget(self.original_btn)

        # Current method (QGraphicsColorizeEffect)
        self.current_method_btn = IconButton(
            icon_path,
            IconTintingMethods.use_colorize_effect,
            dark_color
        )
        gradient_layout.addWidget(self.current_method_btn)

        # Recommended method (SourceIn)
        self.sourcein_method_btn = IconButton(
            icon_path,
            IconTintingMethods.use_source_in,
            dark_color
        )
        gradient_layout.addWidget(self.sourcein_method_btn)

        # Pixel method
        self.pixel_method_btn = IconButton(
            icon_path,
            IconTintingMethods.use_pixel_manipulation,
            dark_color
        )
        gradient_layout.addWidget(self.pixel_method_btn)

        gradient_layout.addStretch(1)

        # Add labels under the gradient
        labels_layout = QHBoxLayout()
        labels_layout.addWidget(QLabel("Original"))
        labels_layout.addWidget(QLabel("Current Method"))
        labels_layout.addWidget(QLabel("SourceIn Method"))
        labels_layout.addWidget(QLabel("Pixel Method"))
        labels_layout.addStretch(1)
        main_layout.addLayout(labels_layout)

        # Solid background for additional testing
        solid_frame = QFrame()
        solid_frame.setMinimumHeight(150)
        solid_frame.setFrameShape(QFrame.StyledPanel)

        # Will be updated in change_theme
        self.update_solid_background(solid_frame)

        # Label
        solid_label = QLabel("Icons on Solid Background")
        main_layout.addWidget(solid_label)
        main_layout.addWidget(solid_frame)

        # Add buttons on solid background
        solid_layout = QHBoxLayout(solid_frame)

        # Original white icon
        solid_layout.addWidget(IconButton(icon_path))

        # Current method (QGraphicsColorizeEffect)
        solid_layout.addWidget(IconButton(
            icon_path,
            IconTintingMethods.use_colorize_effect,
            dark_color
        ))

        # Recommended method (SourceIn)
        solid_layout.addWidget(IconButton(
            icon_path,
            IconTintingMethods.use_source_in,
            dark_color
        ))

        # Pixel method
        solid_layout.addWidget(IconButton(
            icon_path,
            IconTintingMethods.use_pixel_manipulation,
            dark_color
        ))

        solid_layout.addStretch(1)

        # Instructions
        instructions = QLabel(
            "This test shows icons with different tinting methods on different backgrounds.\n"
            "- The checkerboard pattern helps visualize transparency - any non-transparent parts will cover the pattern\n"
            "- The gradient background shows if there are any artifacts or color bleeding\n"
            "- The 'SourceIn Method' typically provides the cleanest results with perfect transparency"
        )
        instructions.setWordWrap(True)
        main_layout.addWidget(instructions)

        # Initial setup
        self.update_backgrounds()

    def update_backgrounds(self):
        """Update background styles based on current settings"""
        # Gradient background
        if self.show_checkerboard.isChecked():
            self.gradient_frame.setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                "stop:0 #6a11cb, stop:1 #2575fc);"
                "background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAI0lEQVQoU2P8/"
                "/8/AxKA0UgK8QMGJIXGjCgK///HSAhjFAIAL+UKy8Lw/FEAAAAASUVORK5CYII=);"
            )
        else:
            self.gradient_frame.setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                "stop:0 #6a11cb, stop:1 #2575fc);"
            )

    def update_solid_background(self, frame):
        """Update solid background based on current theme"""
        is_dark = theme_manager.get_active_theme() == theme_manager.DARK
        if is_dark:
            frame.setStyleSheet("background-color: #333333;")
        else:
            frame.setStyleSheet("background-color: #e0e0e0;")

    def change_theme(self, theme):
        """Change the application theme"""
        # Update theme
        theme_manager.set_theme(theme)

        # Apply theme
        app = QApplication.instance()
        theme_manager.apply_theme(app)

        # Update this window
        is_dark = theme_manager.get_active_theme() == theme_manager.DARK
        for frame in self.findChildren(QFrame):
            if frame != self.gradient_frame:
                self.update_solid_background(frame)

        self.statusBar().showMessage(f"Theme changed to {theme}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply initial theme
    theme_manager.apply_theme(app)

    window = TransparencyTestWindow()
    window.show()
    sys.exit(app.exec())