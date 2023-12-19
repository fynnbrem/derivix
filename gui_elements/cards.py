from dataclasses import dataclass, field
from typing import Optional, Type, Union

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFrame, QGridLayout, QLabel, QLineEdit, QHBoxLayout, QBoxLayout

from gui_elements.abstracts import WidgetControl
from gui_elements.linked_buttons import LinkedButton, ButtonGroup


@dataclass
class CardData:
    name: str
    value: Optional[float] = None
    linked_widget: Optional[QWidget] = field(init=False)
    container: Optional["CardContainer"] = field(init=False)

    def unlink(self):
        """Unlinks this card from its container by removing the reference to it and deleting the widget."""
        self.linked_widget.parentWidget().layout().removeWidget(self.linked_widget)
        self.linked_widget.deleteLater()
        self.linked_widget = None
        self.container = None


class CardButton(LinkedButton):
    """Extends on the `LinkedButton` by offering an attribute to refer to the corresponding `CardData`.
    Helps in jumping from a button action to the corresponding card.
    """

    def __init__(self, card: CardData, control_group: ButtonGroup, text: str = ""):
        super().__init__(control_group=control_group, text=text)
        self.card = card



class SquareCard(CardButton):
    def __init__(self, card: CardData, button_group: ButtonGroup):
        super().__init__(card, button_group, text=card.name)
        self.setFixedSize(30, 30)
        self.setCheckable(True)
        card.linked_widget = self


class CardContainer(QFrame):
    card_widget_type: Union[Type["SquareCard"], Type["InputCard"]]

    def __init__(self):
        super().__init__()
        self.cards: list[CardData] = list()
        self.button_group = ButtonGroup(allow_shift=False)

    def add_card(self, card: CardData):
        self.cards.append(card)
        card.container = self
        self.card_widget_type(card, button_group=self.button_group)
        self._reorder_cards()
        self._place_cards()

    def remove_card(self, card: CardData):
        card.unlink()
        card.container = None
        self.cards.remove(card)
        self._place_cards()

    def _reorder_cards(self):
        def key(c: CardData): return c.name

        self.cards.sort(key=key)

    def _place_cards(self):
        """Places all cards anew, according to their current order."""
        raise NotImplementedError()


class SquareCardContainer(CardContainer, WidgetControl):
    card_widget_type = SquareCard

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
            row = index // self.width
            column = index % self.width
            self.layout_.addWidget(card.linked_widget, row, column)

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
        self.display = CardButton(self.card, self.button_group)
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
    card_widget_type = InputCard

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
            self.layout_.addWidget(card.linked_widget)
