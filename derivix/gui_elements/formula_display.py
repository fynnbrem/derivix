import logging
from pathlib import Path
from typing import Optional, Literal

import pyperclip
from PySide6.QtGui import Qt, QPixmap
from PySide6.QtWidgets import QLabel, QBoxLayout, QFrame, QPushButton, QVBoxLayout, QSizePolicy, \
    QApplication

from derivix.gui_elements.abstracts import WidgetControl
from derivix.gui_elements.animations import JumpyDots
from data import ToolIcons


class FormulaDisplay(QFrame, WidgetControl):
    default_height = 60
    default_width = 240
    loading_animation_base = lambda: JumpyDots(3, 8, Qt.GlobalColor.darkGray)
    loading_animation: Optional[JumpyDots]
    mode: Literal["s", "l", "d", "e"]

    def __init__(self, show_copy: bool = True):
        super().__init__()

        self.formula: Optional[str] = None
        self.show_copy = show_copy
        self.init_widget()
        self.standby_mode()

    def init_positions(self):
        self.button_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self.formula_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.formula_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(QVBoxLayout())

        self.layout_.addLayout(self.button_layout)
        self.layout_.addLayout(self.formula_layout)
        self.formula_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_layout.addWidget(self.copy_button)
        self.formula_layout.addWidget(self.formula_widget)

    def init_values(self):
        self.copy_button.setToolTip("Copy Formula to Clipboard")

    def init_content(self):
        self.loading_animation = None
        self.copy_button = QPushButton()
        self.formula_widget = QLabel()

    def init_style(self):
        self.setFrameShape(QFrame.Shape.Box)
        self.setMinimumWidth(self.default_width)  # The height is set by the individual modes.
        self.copy_button.setIcon(ToolIcons.copy.get_pixmap(16))
        self.copy_button.setFixedHeight(20)
        self.copy_button.setContentsMargins(6, 0, 0, 0)

    def init_control(self):
        def copy_formula_to_clipboard():
            pyperclip.copy(self.formula)

        self.copy_button.clicked.connect(copy_formula_to_clipboard)

    @property
    def layout_(self) -> QBoxLayout:
        return self.layout()

    def loading_mode(self):
        # ↓ Prevent resetting the loading animation if it is already running.
        if self.mode == "l":
            return
        self.mode = "l"
        self.clear()
        self.loading_animation = self.__class__.loading_animation_base()
        self.formula_layout.addWidget(self.loading_animation)

    def display_mode(self, svg_file: Path, formula: Optional[str]):
        self.mode = "d"
        self.clear()
        self.formula = formula
        if self.show_copy:
            self.copy_button.show()
        pix = QPixmap(svg_file)
        screen_width = QApplication.primaryScreen().geometry().width()
        max_width = int(screen_width * 0.9)
        if pix.width() > max_width:
            pix = pix.scaledToWidth(max_width, Qt.TransformationMode.SmoothTransformation)
        self.formula_widget.setPixmap(pix)
        self.setFixedWidth(pix.width() + 50)
        self.setFixedHeight(int(pix.height() * 1.1 + 30))

    def standby_mode(self):
        self.mode = "s"
        self.clear()
        self.formula_widget.setText("Your formula will be shown here")

    def error_mode(self, err: Exception):
        self.clear()
        self.mode = "e"
        error_text = str(err)
        if isinstance(err, RuntimeError):
            text = "Unable to parse formula:\n"
            if "Undefined control sequence" in error_text:
                text += "Undefined control sequence in formula."
            else:
                text += "Unknown error."
                logging.error(err)
        else:
            text = f"An unexpected error occurred during parsing:\n{str(err)}"
            logging.error(err)

        self.formula_widget.setText(text)

    def clear(self):
        self.copy_button.hide()
        self.formula_widget.setText("")
        self.formula = None
        self.setFixedHeight(self.default_height)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        if self.loading_animation is not None:
            self.loading_animation.deleteLater()
            self.loading_animation = None
        self.formula_widget.setPixmap(QPixmap())
