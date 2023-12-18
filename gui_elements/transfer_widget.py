from dataclasses import dataclass, field
from typing import Optional, Type, TypeVar

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QFrame, QLabel, QApplication, QPushButton, QLineEdit, QBoxLayout, \
    QVBoxLayout, QHBoxLayout

from gui_elements.abstracts import WidgetControl


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

    @property
    def layout_(self) -> QGridLayout:
        return self.layout()


T = TypeVar("T")


@dataclass
class CardData:
    name: str
    value: Optional[float] = None
    linked_widget: Optional[QWidget] = field(init=False)

    def unlink_widget(self):
        self.linked_widget.parentWidget().layout().removeWidget(self.linked_widget)
        self.linked_widget.deleteLater()
        self.linked_widget = None


class SquareCard(QPushButton):
    def __init__(self, card: CardData):
        super().__init__(card.name)
        self.setFixedSize(30, 30)
        self.setCheckable(True)
        card.linked_widget = self


class SquareCardContainer(QFrame, WidgetControl):
    def __init__(self):
        super().__init__()
        self.cards: list[CardData] = list()
        self.width = 3
        self.init_widget()

    def init_positions(self):
        self.setLayout(QGridLayout())
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.layout_.setSpacing(0)
        self.layout_.setContentsMargins(0, 0, 0, 0)

    def add_card(self, card: CardData):
        card_widget = SquareCard(card)
        row = len(self.cards) // self.width
        column = (len(self.cards)) % self.width
        self.layout_.addWidget(card_widget, row, column)
        self.cards.append(card)

    @property
    def layout_(self) -> QGridLayout:
        return self.layout()


class InputCard(QFrame, WidgetControl):
    def __init__(self, card: CardData):
        super().__init__()
        self.card = card
        card.linked_widget = self
        self.init_widget()

    def init_content(self):
        self.display = QPushButton()
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


class InputCardContainer(QFrame, WidgetControl):
    def __init__(self):
        super().__init__()
        self.cards: list[CardData] = list()
        self.width = 3
        self.init_widget()

    def init_positions(self):
        self.setLayout(QBoxLayout(QBoxLayout.Direction.TopToBottom))
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter)
        self.layout_.setContentsMargins(0, 0, 0, 0)

    def add_card(self, card: CardData):
        card_widget = InputCard(card)
        self.layout_.addWidget(card_widget)
        self.cards.append(card)

    @property
    def layout_(self) -> QGridLayout:
        return self.layout()


if __name__ == '__main__':
    app = QApplication()
    win = TransferWidget()

    win.left_container.add_card(CardData("A"))
    win.left_container.add_card(CardData("B"))
    win.left_container.add_card(CardData("C"))
    win.left_container.add_card(CardData("D"))
    win.right_container.add_card(CardData("A", 1.234))
    win.right_container.add_card(CardData("B", 2.234))
    win.right_container.add_card(CardData("C"))
    win.right_container.add_card(CardData("D"))
    win.show()
    app.exec()
