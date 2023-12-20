from typing import Dict, Union

from PySide6.QtWidgets import QWidget, QGridLayout, QFrame, QApplication, QPushButton

from gui_elements.abstracts import WidgetControl
from gui_elements.cards import CardData, SquareCardContainer, InputCardContainer, CardButton


class TransferWidget(QWidget, WidgetControl):
    containers: Dict[str, Union["SquareCardContainer", "InputCardContainer"]]
    transfer_buttons: Dict[str, QPushButton]

    def __init__(self):
        super().__init__()

        self.init_widget()

    def init_content(self):
        self.containers = dict()
        self.containers["left"] = SquareCardContainer()
        self.containers["right"] = InputCardContainer()
        self.transfer_buttons = dict()
        self.transfer_buttons["left"] = QPushButton()
        self.transfer_buttons["right"] = QPushButton()

    def init_values(self):
        self.transfer_buttons["left"].setText("<")
        self.transfer_buttons["right"].setText(">")

    def init_positions(self):
        self.setLayout(QGridLayout())
        self.layout_.addWidget(self.containers["left"], 1, 1, 5, 1)
        self.layout_.addWidget(self.containers["right"], 1, 5, 5, 1)
        self.layout_.addWidget(self.transfer_buttons["left"], 4, 3)
        self.layout_.addWidget(self.transfer_buttons["right"], 2, 3)

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
        self.containers["left"].button_group.exclusive_groups.append(self.containers["right"].button_group)
        self.containers["right"].button_group.exclusive_groups.append(self.containers["left"].button_group)
        # endregion
        for key, button in self.transfer_buttons.items():
            button.clicked.connect(lambda *, k=key: self.transfer_cards(k))
            # ↑ Must use keyword-only for the parameters,
            # as otherwise Qt will use its overloaded variant and pass in the button state.

    @property
    def layout_(self) -> QGridLayout:
        return self.layout()

    def transfer_cards(self, direction: str):

        if direction == "left":
            from_container = "right"
            to_container = "left"
        else:
            from_container = "left"
            to_container = "right"

        card_buttons: list[CardButton] = self.containers[from_container].button_group.get_by_check_state()
        for card_button in card_buttons:
            card = card_button.card
            self.containers[from_container].remove_card(card)
            self.containers[to_container].add_card(card)


if __name__ == '__main__':
    app = QApplication()
    win = TransferWidget()

    win.containers["left"].add_card(CardData("A"))
    win.containers["left"].add_card(CardData("C"))
    win.containers["left"].add_card(CardData("B"))
    win.containers["left"].add_card(CardData("D"))
    win.containers["right"].add_card(CardData("A", 1.234))
    win.containers["right"].add_card(CardData("B", 2.234))
    win.containers["right"].add_card(CardData("C"))
    win.containers["right"].add_card(CardData("D"))
    win.show()
    app.exec()
