from enum import Flag
from typing import Dict, Union

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QFrame, QApplication, QPushButton, QLabel

from derivix.gui_elements.abstracts import WidgetControl
from derivix.gui_elements.cards import CardData, SquareCardContainer, InputCardContainer, CardButton, MeasurandCardContainer


class Filter(Flag):
    """The two categories that a symbol can have.
    `Include` will have its partial derivation included in the total formula while `Exclude` will not.

    Can be handled like booleans."""
    Include = True
    Exclude = False


class TransferWidget(QWidget, WidgetControl):
    containers: Dict[Filter, Union["SquareCardContainer", "InputCardContainer"]]
    transfer_buttons: Dict[Filter, QPushButton]

    def __init__(self):
        super().__init__()

        self.init_widget()

    def init_content(self):
        self.containers = dict()
        self.containers[Filter.Include] = MeasurandCardContainer()
        self.containers[Filter.Exclude] = InputCardContainer()
        self.transfer_buttons = dict()
        self.transfer_buttons[Filter.Include] = QPushButton()
        self.transfer_buttons[Filter.Exclude] = QPushButton()

    def init_values(self):
        self.transfer_buttons[Filter.Include].setText("<")
        self.transfer_buttons[Filter.Exclude].setText(">")

    def init_positions(self):
        self.setLayout(QGridLayout())
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout_.addWidget(QLabel("Include"), 1, 1)
        self.layout_.addWidget(QLabel("Exclude"), 1, 5)
        self.layout_.addWidget(self.containers[Filter.Include], 2, 1, 5, 1)
        self.layout_.addWidget(self.containers[Filter.Exclude], 2, 5, 5, 1)
        self.layout_.addWidget(self.transfer_buttons[Filter.Include], 5, 3)
        self.layout_.addWidget(self.transfer_buttons[Filter.Exclude], 3, 3)

    def init_style(self):
        self.layout_.setRowMinimumHeight(3, 20)
        self.layout_.setColumnMinimumWidth(2, 30)
        self.layout_.setColumnMinimumWidth(4, 30)
        for button in self.transfer_buttons.values():
            button.setFixedSize(30, 30)

        for container in self.containers.values():
            container.setFrameShape(QFrame.Shape.Box)

    def init_control(self):
        # region: Link the two button groups as exclusive:
        self.containers[Filter.Include].button_group.exclusive_groups. \
            append(self.containers[Filter.Exclude].button_group)
        self.containers[Filter.Exclude].button_group.exclusive_groups. \
            append(self.containers[Filter.Include].button_group)
        # endregion
        for key, button in self.transfer_buttons.items():
            button.clicked.connect(lambda *, k=key: self.transfer_cards(k))
            # ↑ Must use keyword-only for the parameters,
            # as otherwise Qt will use its overloaded variant and pass in the button state.

    @property
    def layout_(self) -> QGridLayout:
        return self.layout()

    def transfer_cards(self, direction: Filter):
        from_container = ~direction
        to_container = direction

        card_buttons: list[CardButton] = self.containers[from_container].button_group.get_by_check_state()
        for card_button in card_buttons:
            card = card_button.card
            self.containers[from_container].remove_card(card)
            self.containers[to_container].add_card(card)
            card.filter = to_container


if __name__ == '__main__':
    app = QApplication()
    win = TransferWidget()

    win.containers[Filter.Include].add_card(CardData("A"))
    win.containers[Filter.Include].add_card(CardData("C"))
    win.containers[Filter.Include].add_card(CardData("B"))
    win.containers[Filter.Include].add_card(CardData("D"))
    win.containers[Filter.Exclude].add_card(CardData("A", 1.234))
    win.containers[Filter.Exclude].add_card(CardData("B", 2.234))
    win.containers[Filter.Exclude].add_card(CardData("C"))
    win.containers[Filter.Exclude].add_card(CardData("D"))
    win.show()
    app.exec()
