import json
import os
from presentation import SequenceItem
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTabWidget,
    QWidget,
    QFormLayout,
    QFontComboBox,
    QSpinBox,
    QCheckBox,
    QComboBox,
    QLineEdit,
    QDialogButtonBox,
    QLabel,
)


SETTINGS_FILE = os.path.join(
    os.path.dirname(__file__),
    "presenter_settings.json"
)


def save_presenter_settings(global_defaults, presentation):
    data = {
        "primary_style": {
            "font_family": global_defaults.primary_style.font_family,
            "font_size": global_defaults.primary_style.font_size,
            "font_color": global_defaults.primary_style.font_color,
            "bold": global_defaults.primary_style.bold,
            "italic": global_defaults.primary_style.italic,
            "case": global_defaults.primary_style.case,
        },
        "secondary_style": {
            "font_family": global_defaults.secondary_style.font_family,
            "font_size": global_defaults.secondary_style.font_size,
            "font_color": global_defaults.secondary_style.font_color,
            "bold": global_defaults.secondary_style.bold,
            "italic": global_defaults.secondary_style.italic,
            "case": global_defaults.secondary_style.case,
        },
        "beginning": [
            item.token for item in presentation.beginning.items
        ],
        "main": [
            item.token for item in presentation.main.items
        ],
        "end": [
            item.token for item in presentation.end.items
        ],
    }

    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_presenter_settings(global_defaults, presentation):
    if not os.path.exists(SETTINGS_FILE):
        return

    with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    for key, value in data.get("primary_style", {}).items():
        setattr(global_defaults.primary_style, key, value)

    for key, value in data.get("secondary_style", {}).items():
        setattr(global_defaults.secondary_style, key, value)

    presentation.beginning.items = [
        SequenceItem(token=token)
        for token in data.get("beginning", [])
    ]

    presentation.main.items = [
        SequenceItem(token=token)
        for token in data.get("main", [])
    ]

    presentation.end.items = [
        SequenceItem(token=token)
        for token in data.get("end", [])
    ]

class PresenterDefaultsWindow(QDialog):
    def __init__(self, global_defaults, presentation, parent=None):
        super().__init__(parent)

        self.global_defaults = global_defaults
        self.presentation = presentation

        self.setWindowTitle("Presenter Defaults")
        self.resize(600, 500)

        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        # -------------------------
        # FORMATTING DEFAULTS
        # -------------------------
        formatting_tab = QWidget()
        formatting_layout = QVBoxLayout(formatting_tab)

        form = QFormLayout()

        self.primary_font = QFontComboBox()
        self.primary_font.setCurrentFont(
            self._font(self.global_defaults.primary_style.font_family)
        )

        self.primary_size = QSpinBox()
        self.primary_size.setRange(8, 150)
        self.primary_size.setValue(
            self.global_defaults.primary_style.font_size
        )

        self.primary_bold = QCheckBox("Bold")
        self.primary_bold.setChecked(
            self.global_defaults.primary_style.bold
        )

        self.primary_italic = QCheckBox("Italic")
        self.primary_italic.setChecked(
            self.global_defaults.primary_style.italic
        )

        self.primary_case = self._case_combo(
            self.global_defaults.primary_style.case
        )

        self.secondary_font = QFontComboBox()
        self.secondary_font.setCurrentFont(
            self._font(self.global_defaults.secondary_style.font_family)
        )

        self.secondary_size = QSpinBox()
        self.secondary_size.setRange(8, 150)
        self.secondary_size.setValue(
            self.global_defaults.secondary_style.font_size
        )

        self.secondary_bold = QCheckBox("Bold")
        self.secondary_bold.setChecked(
            self.global_defaults.secondary_style.bold
        )

        self.secondary_italic = QCheckBox("Italic")
        self.secondary_italic.setChecked(
            self.global_defaults.secondary_style.italic
        )

        self.secondary_case = self._case_combo(
            self.global_defaults.secondary_style.case
        )

        form.addRow(QLabel("PRIMARY LANGUAGE"), QLabel(""))
        form.addRow("Font:", self.primary_font)
        form.addRow("Font Size:", self.primary_size)
        form.addRow("Text Case:", self.primary_case)
        form.addRow("", self.primary_bold)
        form.addRow("", self.primary_italic)

        form.addRow(QLabel("SECONDARY LANGUAGE"), QLabel(""))
        form.addRow("Font:", self.secondary_font)
        form.addRow("Font Size:", self.secondary_size)
        form.addRow("Text Case:", self.secondary_case)
        form.addRow("", self.secondary_bold)
        form.addRow("", self.secondary_italic)

        formatting_layout.addLayout(form)
        formatting_layout.addStretch()

        # -------------------------
        # SLIDE ORDER DEFAULTS
        # -------------------------
        order_tab = QWidget()
        order_layout = QFormLayout(order_tab)

        self.beginning_order = QLineEdit()
        self.main_order = QLineEdit()
        self.end_order = QLineEdit()

        self.beginning_order.setText(
            ", ".join(item.token for item in self.presentation.beginning.items)
        )
        self.main_order.setText(
            ", ".join(item.token for item in self.presentation.main.items)
        )
        self.end_order.setText(
            ", ".join(item.token for item in self.presentation.end.items)
        )

        self.beginning_order.setPlaceholderText(
            "Example: BLANK, CHORUS"
        )
        self.main_order.setPlaceholderText(
            "Example: VERSE_1, CHORUS, VERSE_2"
        )
        self.end_order.setPlaceholderText(
            "Example: CHORUS, BLANK"
        )

        order_layout.addRow("Beginning:", self.beginning_order)
        order_layout.addRow("Main:", self.main_order)
        order_layout.addRow("End:", self.end_order)

        order_layout.addRow(
            QLabel(
                "Enter sequence tokens separated by commas. "
                "Leave a section empty if it should have no items."
            )
        )

        tabs.addTab(formatting_tab, "Formatting Defaults")
        tabs.addTab(order_tab, "Slide Order Defaults")

        layout.addWidget(tabs)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def _font(self, family):
        from PySide6.QtGui import QFont
        return QFont(family)

    def _case_combo(self, current_case):
        combo = QComboBox()

        options = [
            ("Normal", "normal"),
            ("UPPERCASE", "upper"),
            ("lowercase", "lower"),
            ("Sentence case", "sentence"),
            ("Title Case", "title"),
        ]

        for label, value in options:
            combo.addItem(label, value)

        index = combo.findData(current_case)
        combo.setCurrentIndex(index if index >= 0 else 0)

        return combo

    def save_settings(self):
        primary = self.global_defaults.primary_style
        secondary = self.global_defaults.secondary_style

        primary.font_family = self.primary_font.currentFont().family()
        primary.font_size = self.primary_size.value()
        primary.bold = self.primary_bold.isChecked()
        primary.italic = self.primary_italic.isChecked()
        primary.case = self.primary_case.currentData()

        secondary.font_family = self.secondary_font.currentFont().family()
        secondary.font_size = self.secondary_size.value()
        secondary.bold = self.secondary_bold.isChecked()
        secondary.italic = self.secondary_italic.isChecked()
        secondary.case = self.secondary_case.currentData()

        self.presentation.beginning.items = [
            SequenceItem(token=token.strip())
            for token in self.beginning_order.text().split(",")
            if token.strip()
        ]

        self.presentation.main.items = [
            SequenceItem(token=token.strip())
            for token in self.main_order.text().split(",")
            if token.strip()
        ]

        self.presentation.end.items = [
            SequenceItem(token=token.strip())
            for token in self.end_order.text().split(",")
            if token.strip()
        ]

        save_presenter_settings(
            self.global_defaults,
            self.presentation
        )

        self.accept()