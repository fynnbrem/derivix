from dataclasses import dataclass, field
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFrame, QGridLayout, QLabel, QLineEdit, QHBoxLayout, QBoxLayout

from gui_elements.abstracts import WidgetControl
from gui_elements.linked_buttons import LinkedButton, ButtonGroup


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


class CardButton(LinkedButton):
    def __init__(self, card: CardData, control_group: ButtonGroup, text: str = ""):
        super().__init__(control_group=control_group, text=text)
        self.card = card


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
