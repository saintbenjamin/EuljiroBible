from PySide6.QtCore import Qt
from PySide6.QtWidgets import ( 
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, 
    QComboBox, QTextEdit, QScrollArea, 
    QGridLayout, QSplitter
)
from PySide6.QtGui import QStandardItemModel

from gui.ui.common import create_svg_text_button, LoadingIndicator

class TabVerseUI:
    def init_ui(self, version_list):
        self.version_scroll = QScrollArea()
        self.version_scroll.setWidgetResizable(True)
        self.version_widget = QWidget()
        self.version_layout = QGridLayout(self.version_widget)
        self.version_scroll.setWidget(self.version_widget)

        for version in enumerate(version_list):
            if isinstance(version, tuple):
                _, version_name = version
            else:
                version_name = version

            checkbox = self.create_version_checkbox(version_name)
            self.version_layout.addWidget(checkbox)

        self.update_grid_layout()

        self.enter_state = 0
        self.use_alias = False

        self.alias_toggle_btn = QPushButton(self.tr("label_alias_full"))
        self.alias_toggle_btn.setCheckable(True)
        self.alias_toggle_btn.setChecked(False)
        self.alias_toggle_btn.clicked.connect(self.toggle_alias_mode)

        self.version_summary_label = QLabel(self.tr("msg_nothing"))
        version_label_layout = QHBoxLayout()
        version_label_layout.addWidget(self.alias_toggle_btn)
        version_label_layout.addWidget(self.version_summary_label)
        version_label_layout.addStretch()

        self.book_label = QLabel(self.tr("label_book"))
        self.chapter_label = QLabel(self.tr("label_chapter"))
        self.verse_label = QLabel(self.tr("label_verse"))

        self.book_combo = QComboBox()
        self.book_combo.setModel(QStandardItemModel(self.book_combo))
        self.book_combo.setEditable(True)
        self.book_combo.setInsertPolicy(QComboBox.NoInsert)
        self.book_combo.currentTextChanged.connect(self.update_chapter_dropdown)

        self.chapter_input = QComboBox()
        self.chapter_input.setEditable(True)

        self.verse_input = QLineEdit()
        self.verse_input.setPlaceholderText(self.tr("verse_input_hint"))
        self.verse_input.returnPressed.connect(self.handle_enter)

        self.search_btn = create_svg_text_button(
            "resources/svg/btn_search.svg",
            self.tr("btn_search"),
            30,
            "Search",
            self.display_verse
        )
        self.save_btn = create_svg_text_button(
            "resources/svg/btn_output.svg",
            self.tr("btn_output"),
            30,
            "Start slide show",
            self.save_verse
        )
        self.clear_display_btn = create_svg_text_button(
            "resources/svg/btn_clear.svg",
            self.tr("btn_clear"),
            30,
            "Stop slide show",
            self.clear_outputs
        )
        self.prev_verse_btn = create_svg_text_button(
            "resources/svg/btn_prev.svg",
            self.tr("btn_prev"),
            30,
            "Go to previous verse",
            lambda: self.shift_verse(-1)
        )
        self.next_verse_btn = create_svg_text_button(
            "resources/svg/btn_next.svg",
            self.tr("btn_next"),
            30,
            "Go to next verse",
            lambda: self.shift_verse(1)
        )

        input_layout = QHBoxLayout()
        self.input_layout = input_layout
        input_layout.addWidget(self.book_label)
        input_layout.addWidget(self.book_combo)
        input_layout.addWidget(self.chapter_label)
        input_layout.addWidget(self.chapter_input)
        input_layout.addWidget(self.verse_label)
        input_layout.addWidget(self.verse_input)

        input_layout.setStretch(1, 2)
        input_layout.setStretch(3, 1)
        input_layout.setStretch(5, 1)

        button_layout = QHBoxLayout()
        self.button_layout = button_layout
        button_layout.addWidget(self.prev_verse_btn)
        button_layout.addWidget(self.search_btn)
        poll_enabled = self.settings.get("poll_enabled", False)
        if poll_enabled:
            button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.next_verse_btn)
        if poll_enabled:
            button_layout.addWidget(self.clear_display_btn)

        input_layout.addLayout(button_layout)

        self.display_box = QTextEdit()
        self.display_box.setReadOnly(True)

        self.loading_indicator = LoadingIndicator(self.display_box.viewport())
        self.loading_indicator.hide()

        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.addLayout(input_layout)
        bottom_layout.addWidget(self.display_box)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.version_scroll)
        splitter.addWidget(bottom_widget)
        splitter.setSizes([150, 400]) 

        layout = QVBoxLayout()
        layout.addLayout(version_label_layout)
        layout.addWidget(splitter)

        self.setLayout(layout)
        layout.addWidget(self.loading_indicator)  # For loading animation