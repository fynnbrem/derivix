from dataclasses import dataclass, field
from typing import Optional, Type, TypeVar

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QFrame, QLabel, QApplication, QPushButton, QLineEdit, QBoxLayout, \
    QVBoxLayout, QHBoxLayout

from gui_elements.abstracts import WidgetControl
from gui_elements.linked_buttons import LinkedButton, ButtonGroup


class TransferWidget(QWidget, WidgetControl):
    left_container: "SquareCardContainer"
    right_container: "InputCardContainer"
    transfer_right: QPushButton
    transfer_left: QPushButton

    def __init__(self):
        super().__init__()

        self.init_widget()

    def init_content(self):
        self.left_container = SquareCardContainer()
        self.right_container = InputCardContainer()
        self.transfer_right = QPushButton()
        self.transfer_left = QPushButton()

    def init_values(self):
        self.transfer_right.setText(">")
        self.transfer_left.setText("<")

    def init_positions(self):
        self.setLayout(QGridLayout())
        self.layout_.addWidget(self.left_container, 1, 1, 5, 1)
        self.layout_.addWidget(self.right_container, 1, 5, 5, 1)
        self.layout_.addWidget(self.transfer_left, 4, 3)
        self.layout_.addWidget(self.transfer_right, 2, 3)

    def init_style(self):
        self.layout_.setRowMinimumHeight(3, 20)
        self.layout_.setColumnMinimumWidth(2, 30)
        self.layout_.setColumnMinimumWidth(4, 30)

        self.transfer_left.setFixedSize(30, 30)
        self.transfer_right.setFixedSize(30, 30)

        self.left_container.setFrameShape(QFrame.Shape.Box)
        self.right_container.setFrameShape(QFrame.Shape.Box)


    def init_control(self):
        # region: Link the two button groups as exclusive:
        self.left_container.button_group.exclusive_groups.append(self.right_container.button_group)
        self.right_container.button_group.exclusive_groups.append(self.left_container.button_group)
        # endregion

    @property
    def layout_(self) -> QGridLayout:
        return self.layout()


T = TypeVar("T", bound=QWidget)


@dataclass
class CardData:
    name: str
    value: Optional[float] = None
    linked_widget: Optional[QWidget] = field(init=False)

    def unlink_widget(self):
        """Deletes the linked widget and clears this object's reference to it."""
        self.linked_widget.parentWidget().layout().removeWidget(self.linked_widget)
        self.linked_widget.deleteLater()
        self.linked_widget = None


class SquareCard(LinkedButton):
    def __init__(self, card: CardData, button_group: ButtonGroup):
        super().__init__(button_group, text=card.name)
        self.setFixedSize(30, 30)
        self.setCheckable(True)
        card.linked_widget = self


class CardContainer(QFrame):
    def __init__(self):
        super().__init__()
        self.cards: list[CardData] = list()
        self.button_group = ButtonGroup(allow_shift=False)

    def add_card(self, card: CardData):
        self.cards.append(card)
        self._place_cards()

    def remove_card(self, card: CardData):
        card.unlink_widget()
        self.cards.remove(card)
        self._place_cards()

    def _reorder_cards(self):
        def key(c: CardData): return c.name

        self.cards.sort(key=key)


    def _place_cards(self):
        """Sorts and places all cards according to that order."""
        raise NotImplementedError()


class SquareCardContainer(CardContainer, WidgetControl):
    def __init__(self):
        super().__init__()
        self.width = 3
        self.init_widget()

    def init_positions(self):
        self.setLayout(QGridLayout())
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.layout_.setSpacing(0)
        self.layout_.setContentsMargins(0, 0, 0, 0)

    def _place_cards(self):
        while self.layout_.count() != 0:
            self.layout_.takeAt(0)
        for index, card in enumerate(self.cards):
            card_widget = SquareCard(card, self.button_group)
            row = index // self.width
            column = index % self.width
            self.layout_.addWidget(card_widget, row, column)

    @property
    def layout_(self) -> QGridLayout:
        return self.layout()


class InputCard(QFrame, WidgetControl):
    def __init__(self, card: CardData, button_group: ButtonGroup):
        super().__init__()
        self.card = card
        card.linked_widget = self
        self.button_group = button_group
        self.init_widget()

    def init_content(self):
        self.display = LinkedButton(self.button_group)
        self.equals = QLabel()
        self.input = QLineEdit()

    def init_values(self):
        self.display.setText(self.card.name)
        self.equals.setText("=")
        if self.card.value is not None:
            self.input.setText(str(self.card.value))

    def init_positions(self):
        self.setLayout(QHBoxLayout())
        self.layout_.addWidget(self.display)
        self.layout_.addWidget(self.equals)
        self.layout_.addWidget(self.input)

    def init_style(self):
        self.layout_.setContentsMargins(3, 1, 3, 1)
        self.setFixedWidth(150)
        self.display.setFixedSize(30, 30)

        self.equals.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setFrameShape(QFrame.Shape.Box)

    def init_control(self):
        self.display.setCheckable(True)

    @property
    def layout_(self) -> QHBoxLayout:
        return self.layout()


class InputCardContainer(CardContainer, WidgetControl):
    def __init__(self):
        super().__init__()
        self.width = 3
        self.init_widget()

    def init_positions(self):
        self.setLayout(QBoxLayout(QBoxLayout.Direction.TopToBottom))
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter)
        self.layout_.setContentsMargins(0, 0, 0, 0)

    @property
    def layout_(self) -> QGridLayout:
        return self.layout()

    def _place_cards(self):
        while self.layout_.count() != 0:
            self.layout_.takeAt(0)
        for card in self.cards:
            card_widget = InputCard(card, self.button_group)
            self.layout_.addWidget(card_widget)


if __name__ == '__main__':
    app = QApplication()
    win = TransferWidget()

    win.left_container.add_card(CardData("A"))
    win.left_container.add_card(CardData("C"))
    win.left_container.add_card(CardData("B"))
    win.left_container.add_card(CardData("D"))
    win.right_container.add_card(CardData("A", 1.234))
    win.right_container.add_card(CardData("B", 2.234))
    win.right_container.add_card(CardData("C"))
    win.right_container.add_card(CardData("D"))
    win.show()
    app.exec()
