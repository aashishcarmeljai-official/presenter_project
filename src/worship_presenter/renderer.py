import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from models import Background, GlobalDefaults, Slide, Style

def apply_text_case(text, case):
    if case == "upper":
        return text.upper()

    elif case == "lower":
        return text.lower()

    elif case == "sentence":
        return text.capitalize()

    elif case == "title":
        return text.title()

    return text


def apply_brightness_contrast(image: QImage, brightness: int, contrast: int) -> QImage:
    """Return a NEW QImage with brightness/contrast applied.

    brightness: -100..100, added directly to each RGB channel.
    contrast:   0..200, where 100 means "no change". Values are scaled
                around the 128 midpoint so contrast darkens shadows /
                brightens highlights symmetrically.

    This is the single source of truth for the adjustment math, used both
    for the final rendered slide and for the small live preview thumbnail
    in the editor, so what you see in the preview always matches the
    actual slide.
    """
    image = image.convertToFormat(QImage.Format_RGBA8888)

    width = image.width()
    height = image.height()
    bytes_per_line = image.bytesPerLine()

    ptr = image.bits()

    # Older PySide6 returns a sip.voidptr that needs an explicit size
    # before it can be read; newer PySide6 (6.4+) returns a plain
    # memoryview that is already correctly sized, and has no setsize().
    if hasattr(ptr, "setsize"):
        ptr.setsize(height * bytes_per_line)

    buffer = np.frombuffer(ptr, dtype=np.uint8)

    # Rows may be padded to a 4-byte boundary -- slice off the padding
    # before reshaping into (height, width, 4).
    raw = buffer[: height * bytes_per_line].reshape((height, bytes_per_line))
    pixels = raw[:, : width * 4].reshape((height, width, 4)).copy()

    rgb = pixels[:, :, :3].astype(np.float32)
    alpha = pixels[:, :, 3]

    contrast_factor = contrast / 100.0
    rgb = (rgb - 128.0) * contrast_factor + 128.0
    rgb = rgb + brightness
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)

    result = np.dstack((rgb, alpha))

    output = QImage(
        result.tobytes(),
        width,
        height,
        width * 4,
        QImage.Format_RGBA8888,
    )

    # .copy() detaches the QImage from the numpy buffer so it stays valid
    # after this function returns and `result` gets garbage collected.
    return output.copy()


class SlideRenderer:
    def render(
        self,
        slide: Slide,
        global_defaults: GlobalDefaults,
        width: int,
        height: int,
    ):
        widget = QWidget()
        widget.setFixedSize(width, height)

        # Resolve effective style/background: use the slide's own data only
        # if it has opted out of the shared default.
        primary_style: Style = (
            slide.primary.style if slide.use_custom_style else global_defaults.primary_style
        )
        secondary_style: Style = (
            slide.secondary.style if slide.use_custom_style else global_defaults.secondary_style
        )
        background: Background = (
            slide.background if slide.use_custom_background else global_defaults.background
        )

        # Background
        background_pixmap = self.create_background(
            background,
            width,
            height,
        )

        background_label = QLabel(widget)
        background_label.setPixmap(background_pixmap)
        background_label.setGeometry(
            0,
            0,
            width,
            height,
        )

        # Content container
        content = QWidget(widget)
        content.setGeometry(
            60,
            60,
            width - 120,
            height - 120,
        )

        layout = QVBoxLayout(content)
        layout.setAlignment(Qt.AlignCenter)

        primary_lines = [
            apply_text_case(line, primary_style.case)
            for line in slide.primary.content.splitlines()
        ]

        secondary_lines = [
            apply_text_case(line, secondary_style.case)
            for line in slide.secondary.content.splitlines()
        ]

        # Safety check
        if len(primary_lines) != len(secondary_lines):
            error = QLabel(
                "ERROR: Primary and Secondary language "
                "line counts do not match."
            )

            error.setStyleSheet(
                "color: red; font-size: 30px;"
            )

            error.setAlignment(Qt.AlignCenter)

            layout.addWidget(error)

            return widget

        for primary, secondary in zip(
            primary_lines,
            secondary_lines,
        ):
            primary_label = QLabel(primary)
            secondary_label = QLabel(secondary)

            self.apply_style(
                primary_label,
                primary_style,
            )

            self.apply_style(
                secondary_label,
                secondary_style,
            )

            primary_label.setAlignment(
                Qt.AlignCenter
            )

            secondary_label.setAlignment(
                Qt.AlignCenter
            )

            layout.addWidget(primary_label)
            layout.addWidget(secondary_label)

        return widget

    def apply_style(self, label, style: Style):
        font = QFont(style.font_family)
        font.setPointSize(style.font_size)
        font.setBold(style.bold)
        font.setItalic(style.italic)

        label.setFont(font)

        label.setStyleSheet(
            f"""
            QLabel {{
                color: {style.font_color};
                background: transparent;
            }}
            """
        )

    def create_background(
        self,
        background: Background,
        width,
        height,
    ):
        image_path = background.image_path

        if image_path:
            pixmap = QPixmap(image_path)

            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    width,
                    height,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation,
                )

                return self.process_background(
                    pixmap,
                    background.brightness,
                    background.contrast,
                    width,
                    height,
                )

        # Default black background
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor("#000000"))

        return pixmap

    def process_background(
        self,
        pixmap,
        brightness,
        contrast,
        width,
        height,
    ):
        image = pixmap.toImage().convertToFormat(
            QImage.Format_RGBA8888
        )

        # Create output image
        output = QImage(
            width,
            height,
            QImage.Format_RGBA8888,
        )

        output.fill(Qt.black)

        painter = QPainter()
        painter.begin(output)

        # Center the image
        x = (width - pixmap.width()) // 2
        y = (height - pixmap.height()) // 2

        painter.drawImage(
            x,
            y,
            image,
        )

        painter.end()

        adjusted = apply_brightness_contrast(output, brightness, contrast)

        return QPixmap.fromImage(adjusted)