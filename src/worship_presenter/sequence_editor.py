from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from presentation import (
    Presentation,
    PresentationSection,
    SequenceItem,
    SequenceResolver,
    available_sequence_tokens,
)


class SequenceEditor(QWidget):

    def __init__(
        self,
        slides,
        presentation,
        parent=None,
    ):
        super().__init__(parent)

        # Without this, a QWidget that has a parent renders as a child
        # widget INSIDE the parent's own coordinate space (pinned at its
        # top-left corner, drawn over whatever else is there) instead of
        # opening as its own separate window. This makes it a proper
        # top-level window while still being owned/kept alive by `parent`.
        self.setWindowFlag(Qt.Window, True)

        self.slides = slides
        self.presentation = presentation

        self.setWindowTitle(
            "Worship Presenter - Presentation Sequence"
        )

        self.resize(
            1000,
            700,
        )

        self.build_ui()

    # =========================================================
    # UI
    # =========================================================

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        title = QLabel(
            "Presentation Sequence"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 24px;
                font-weight: bold;
            }
            """
        )

        main_layout.addWidget(title)

        # -----------------------------------------------------
        # THREE SECTIONS
        # -----------------------------------------------------

        sections_layout = QHBoxLayout()

        self.section_widgets = {}

        self.create_section(
            self.presentation.beginning,
            sections_layout,
        )

        self.create_section(
            self.presentation.main,
            sections_layout,
        )

        self.create_section(
            self.presentation.end,
            sections_layout,
        )

        main_layout.addLayout(
            sections_layout,
            1,
        )

        # -----------------------------------------------------
        # BUILD
        # -----------------------------------------------------

        self.build_button = QPushButton(
            "Build / Resolve Presentation"
        )

        self.build_button.clicked.connect(
            self.build_presentation
        )

        main_layout.addWidget(
            self.build_button
        )

        # -----------------------------------------------------
        # RESULT
        # -----------------------------------------------------

        self.result_list = QListWidget()

        main_layout.addWidget(
            QLabel("Resolved Presentation:"
                   )
        )

        main_layout.addWidget(
            self.result_list
        )

    # =========================================================
    # SECTION
    # =========================================================

    def create_section(
        self,
        section,
        parent_layout,
    ):

        container = QWidget()

        layout = QVBoxLayout(
            container
        )

        title = QLabel(
            section.name
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(
            title
        )

        # -----------------------------------------------------
        # LIST
        # -----------------------------------------------------

        list_widget = QListWidget()

        layout.addWidget(
            list_widget,
            1,
        )

        # -----------------------------------------------------
        # COMBO
        # -----------------------------------------------------

        combo = QComboBox()

        combo.addItems(
            available_sequence_tokens(
                self.slides
            )
        )

        layout.addWidget(
            combo
        )

        # -----------------------------------------------------
        # BUTTONS
        # -----------------------------------------------------

        button_row = QHBoxLayout()

        add_button = QPushButton(
            "+"
        )

        remove_button = QPushButton(
            "-"
        )

        up_button = QPushButton(
            "↑"
        )

        down_button = QPushButton(
            "↓"
        )

        button_row.addWidget(
            add_button
        )

        button_row.addWidget(
            remove_button
        )

        button_row.addWidget(
            up_button
        )

        button_row.addWidget(
            down_button
        )

        layout.addLayout(
            button_row
        )

        # -----------------------------------------------------
        # CONNECTIONS
        # -----------------------------------------------------

        add_button.clicked.connect(
            lambda: self.add_item(
                section,
                list_widget,
                combo,
            )
        )

        remove_button.clicked.connect(
            lambda: self.remove_item(
                section,
                list_widget,
            )
        )

        up_button.clicked.connect(
            lambda: self.move_item(
                section,
                list_widget,
                -1,
            )
        )

        down_button.clicked.connect(
            lambda: self.move_item(
                section,
                list_widget,
                1,
            )
        )

        # -----------------------------------------------------
        # LOAD EXISTING ITEMS
        # -----------------------------------------------------

        for item in section.items:

            list_widget.addItem(
                item.token
            )

        # Save references
        self.section_widgets[
            section.name
        ] = {
            "section": section,
            "list": list_widget,
            "combo": combo,
        }

        parent_layout.addWidget(
            container
        )

    # =========================================================
    # ADD
    # =========================================================

    def add_item(
        self,
        section,
        list_widget,
        combo,
    ):

        token = combo.currentText()

        if not token:
            return

        item = SequenceItem(
            token=token
        )

        section.items.append(
            item
        )

        list_widget.addItem(
            token
        )

        list_widget.setCurrentRow(
            list_widget.count() - 1
        )

    # =========================================================
    # REMOVE
    # =========================================================

    def remove_item(
        self,
        section,
        list_widget,
    ):

        row = list_widget.currentRow()

        if row < 0:
            return

        section.items.pop(
            row
        )

        list_widget.takeItem(
            row
        )

    # =========================================================
    # MOVE
    # =========================================================

    def move_item(
        self,
        section,
        list_widget,
        direction,
    ):

        row = list_widget.currentRow()

        if row < 0:
            return

        new_row = row + direction

        if new_row < 0:
            return

        if new_row >= len(
            section.items
        ):
            return

        # Swap data
        section.items[row], section.items[new_row] = (
            section.items[new_row],
            section.items[row],
        )

        # Swap UI
        item = list_widget.takeItem(
            row
        )

        list_widget.insertItem(
            new_row,
            item,
        )

        list_widget.setCurrentRow(
            new_row
        )

    # =========================================================
    # BUILD
    # =========================================================

    def build_presentation(self):

        self.result_list.clear()

        resolver = SequenceResolver(
            self.slides
        )

        resolved = resolver.resolve_presentation(
            self.presentation
        )

        for index, slide in enumerate(
            resolved,
            start=1,
        ):

            label = (
                f"{index}. "
                f"{slide.type.value.title()}"
            )

            self.result_list.addItem(
                label
            )