import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QFontComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from models import Slide, SlideType
from renderer import SlideRenderer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Worship Presenter")
        self.resize(1400, 850)

        self.slides = []
        self.current_slide = None
        self.renderer = SlideRenderer()

        self.build_ui()

    # =========================================================
    # MAIN UI
    # =========================================================

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)

        # -----------------------------------------------------
        # LEFT SIDEBAR
        # -----------------------------------------------------

        sidebar = QWidget()
        sidebar.setFixedWidth(220)

        sidebar_layout = QVBoxLayout(sidebar)

        title = QLabel("Slides")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )

        self.add_button = QPushButton("+ Add Slide")
        self.delete_button = QPushButton("Delete Slide")

        self.slide_list = QListWidget()

        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(self.add_button)
        sidebar_layout.addWidget(self.delete_button)
        sidebar_layout.addWidget(self.slide_list)

        self.add_button.clicked.connect(self.add_slide)
        self.delete_button.clicked.connect(self.delete_slide)
        self.slide_list.currentRowChanged.connect(
            self.select_slide
        )

        # -----------------------------------------------------
        # EDITOR
        # -----------------------------------------------------

        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)

        editor_title = QLabel("Slide Editor")
        editor_title.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )

        editor_layout.addWidget(editor_title)

        # Slide type
        type_layout = QHBoxLayout()

        type_label = QLabel("Slide Type:")

        self.type_combo = QComboBox()

        for slide_type in SlideType:
            self.type_combo.addItem(
                slide_type.value.title(),
                slide_type,
            )

        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()

        editor_layout.addLayout(type_layout)

        # -----------------------------------------------------
        # LANGUAGE EDITORS
        # -----------------------------------------------------

        language_layout = QHBoxLayout()

        # Primary
        primary_group = QGroupBox("Primary Language")
        primary_layout = QVBoxLayout(primary_group)

        self.primary_text = QTextEdit()
        self.primary_text.setPlaceholderText(
            "Paste primary language lyrics here..."
        )

        primary_layout.addWidget(self.primary_text)

        self.primary_font = QFontComboBox()

        self.primary_size = QSpinBox()
        self.primary_size.setRange(8, 150)
        self.primary_size.setValue(36)

        self.primary_color_button = QPushButton(
            "Choose Text Color"
        )

        self.primary_bold = QCheckBox("Bold")
        self.primary_italic = QCheckBox("Italic")

        primary_style = QFormLayout()

        primary_style.addRow(
            "Font:",
            self.primary_font,
        )

        primary_style.addRow(
            "Size:",
            self.primary_size,
        )

        primary_style.addRow(
            self.primary_color_button
        )

        primary_style.addRow(
            self.primary_bold
        )

        primary_style.addRow(
            self.primary_italic
        )

        primary_layout.addLayout(primary_style)

        # Secondary
        secondary_group = QGroupBox("Secondary Language")
        secondary_layout = QVBoxLayout(secondary_group)

        self.secondary_text = QTextEdit()
        self.secondary_text.setPlaceholderText(
            "Paste secondary language lyrics here..."
        )

        secondary_layout.addWidget(self.secondary_text)

        self.secondary_font = QFontComboBox()

        self.secondary_size = QSpinBox()
        self.secondary_size.setRange(8, 150)
        self.secondary_size.setValue(30)

        self.secondary_color_button = QPushButton(
            "Choose Text Color"
        )

        self.secondary_bold = QCheckBox("Bold")
        self.secondary_italic = QCheckBox("Italic")

        secondary_style = QFormLayout()

        secondary_style.addRow(
            "Font:",
            self.secondary_font,
        )

        secondary_style.addRow(
            "Size:",
            self.secondary_size,
        )

        secondary_style.addRow(
            self.secondary_color_button
        )

        secondary_style.addRow(
            self.secondary_bold
        )

        secondary_style.addRow(
            self.secondary_italic
        )

        secondary_layout.addLayout(secondary_style)

        language_layout.addWidget(primary_group)
        language_layout.addWidget(secondary_group)

        editor_layout.addLayout(language_layout, 1)

        # -----------------------------------------------------
        # BACKGROUND
        # -----------------------------------------------------

        background_group = QGroupBox("Background")

        background_layout = QHBoxLayout(background_group)

        self.background_button = QPushButton(
            "Choose Image"
        )

        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)

        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(0, 200)
        self.contrast_slider.setValue(100)

        background_layout.addWidget(
            self.background_button
        )

        background_layout.addWidget(
            QLabel("Brightness")
        )

        background_layout.addWidget(
            self.brightness_slider
        )

        background_layout.addWidget(
            QLabel("Contrast")
        )

        background_layout.addWidget(
            self.contrast_slider
        )

        editor_layout.addWidget(background_group)

        # -----------------------------------------------------
        # SAVE / PREVIEW
        # -----------------------------------------------------

        bottom_layout = QHBoxLayout()

        self.save_button = QPushButton("Apply Changes")
        self.preview_button = QPushButton("Preview")

        bottom_layout.addWidget(self.save_button)
        bottom_layout.addWidget(self.preview_button)
        bottom_layout.addStretch()

        editor_layout.addLayout(bottom_layout)

        # -----------------------------------------------------
        # ADD TO MAIN WINDOW
        # -----------------------------------------------------

        main_layout.addWidget(sidebar)
        main_layout.addWidget(editor_container, 1)

        # -----------------------------------------------------
        # SIGNALS
        # -----------------------------------------------------

        self.type_combo.currentIndexChanged.connect(
            self.update_slide_type
        )

        self.save_button.clicked.connect(
            self.save_current_slide
        )

        self.preview_button.clicked.connect(
            self.preview_slide
        )

        self.primary_color_button.clicked.connect(
            lambda: self.choose_color("primary")
        )

        self.secondary_color_button.clicked.connect(
            lambda: self.choose_color("secondary")
        )

        self.background_button.clicked.connect(
            self.choose_background
        )

    # =========================================================
    # SLIDE MANAGEMENT
    # =========================================================

    def add_slide(self):
        slide = Slide()

        self.slides.append(slide)

        self.slide_list.addItem(
            f"{len(self.slides)} - Custom"
        )

        self.slide_list.setCurrentRow(
            len(self.slides) - 1
        )

    def delete_slide(self):
        index = self.slide_list.currentRow()

        if index < 0:
            return

        self.slides.pop(index)
        self.slide_list.takeItem(index)

        if self.slides:
            new_index = min(
                index,
                len(self.slides) - 1,
            )

            self.slide_list.setCurrentRow(
                new_index
            )

        else:
            self.current_slide = None

    def select_slide(self, index):
        if index < 0 or index >= len(self.slides):
            self.current_slide = None
            return

        self.current_slide = self.slides[index]

        self.load_slide_into_editor(
            self.current_slide
        )

    # =========================================================
    # LOAD SLIDE
    # =========================================================

    def load_slide_into_editor(self, slide):
        # Type
        type_index = self.type_combo.findData(
            slide.type
        )

        if type_index >= 0:
            self.type_combo.blockSignals(True)
            self.type_combo.setCurrentIndex(
                type_index
            )
            self.type_combo.blockSignals(False)

        # Primary
        self.primary_text.setPlainText(
            slide.primary.content
        )

        self.primary_font.setCurrentFont(
            QFont(slide.primary.style.font_family)
        )

        self.primary_size.setValue(
            slide.primary.style.font_size
        )

        self.primary_bold.setChecked(
            slide.primary.style.bold
        )

        self.primary_italic.setChecked(
            slide.primary.style.italic
        )

        # Secondary
        self.secondary_text.setPlainText(
            slide.secondary.content
        )

        self.secondary_font.setCurrentFont(
            QFont(slide.secondary.style.font_family)
        )

        self.secondary_size.setValue(
            slide.secondary.style.font_size
        )

        self.secondary_bold.setChecked(
            slide.secondary.style.bold
        )

        self.secondary_italic.setChecked(
            slide.secondary.style.italic
        )

        # Background
        self.brightness_slider.setValue(
            slide.background.brightness
        )

        self.contrast_slider.setValue(
            slide.background.contrast
        )

    # =========================================================
    # SAVE SLIDE
    # =========================================================

    def save_current_slide(self):
        if self.current_slide is None:
            return

        slide = self.current_slide

        # Type
        slide.type = self.type_combo.currentData()

        # Primary
        slide.primary.content = (
            self.primary_text.toPlainText()
        )

        slide.primary.style.font_family = (
            self.primary_font.currentFont().family()
        )

        slide.primary.style.font_size = (
            self.primary_size.value()
        )

        slide.primary.style.bold = (
            self.primary_bold.isChecked()
        )

        slide.primary.style.italic = (
            self.primary_italic.isChecked()
        )

        # Secondary
        slide.secondary.content = (
            self.secondary_text.toPlainText()
        )

        slide.secondary.style.font_family = (
            self.secondary_font.currentFont().family()
        )

        slide.secondary.style.font_size = (
            self.secondary_size.value()
        )

        slide.secondary.style.bold = (
            self.secondary_bold.isChecked()
        )

        slide.secondary.style.italic = (
            self.secondary_italic.isChecked()
        )

        # Background
        slide.background.brightness = (
            self.brightness_slider.value()
        )

        slide.background.contrast = (
            self.contrast_slider.value()
        )

        # Update sidebar label
        index = self.slide_list.currentRow()

        if index >= 0:
            self.slide_list.item(index).setText(
                f"{index + 1} - {slide.type.value.title()}"
            )

    # =========================================================
    # SLIDE TYPE
    # =========================================================

    def update_slide_type(self):
        if self.current_slide is None:
            return

        self.current_slide.type = (
            self.type_combo.currentData()
        )

        index = self.slide_list.currentRow()

        if index >= 0:
            self.slide_list.item(index).setText(
                f"{index + 1} - "
                f"{self.current_slide.type.value.title()}"
            )

    # =========================================================
    # COLORS
    # =========================================================

    def choose_color(self, language):
        color = QColorDialog.getColor()

        if not color.isValid():
            return

        if language == "primary":
            self.primary_color_button.setStyleSheet(
                f"background-color: {color.name()};"
            )

            if self.current_slide:
                self.current_slide.primary.style.font_color = (
                    color.name()
                )

        else:
            self.secondary_color_button.setStyleSheet(
                f"background-color: {color.name()};"
            )

            if self.current_slide:
                self.current_slide.secondary.style.font_color = (
                    color.name()
                )

    # =========================================================
    # BACKGROUND
    # =========================================================

    def choose_background(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Background Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)",
        )

        if not file_path:
            return

        if self.current_slide:
            self.current_slide.background.image_path = (
                file_path
            )

    def preview_slide(self):
        if self.current_slide is None:
            return

        self.save_current_slide()

        self.preview_window = self.renderer.render(
            self.current_slide,
            1280,
            720,
        )

        self.preview_window.setWindowTitle(
            "Worship Presenter - Preview"
        )

        self.preview_window.show()


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()