from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from models import Slide


class SlideRenderer:
    def render(self, slide: Slide, width: int, height: int):
        widget = QWidget()
        widget.setFixedSize(width, height)

        # Background
        background = self.create_background(
            slide,
            width,
            height,
        )

        background_label = QLabel(widget)
        background_label.setPixmap(background)
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

        primary_lines = slide.primary.content.splitlines()
        secondary_lines = slide.secondary.content.splitlines()

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
                slide.primary.style,
            )

            self.apply_style(
                secondary_label,
                slide.secondary.style,
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

    def apply_style(self, label, style):
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
        slide,
        width,
        height,
    ):
        image_path = slide.background.image_path

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
                    slide.background.brightness,
                    slide.background.contrast,
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

        painter = QPainter()

        # Create output image
        output = QImage(
            width,
            height,
            QImage.Format_RGBA8888,
        )

        output.fill(Qt.black)

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

        return QPixmap.fromImage(output)