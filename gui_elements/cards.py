from dataclasses import dataclass, field
from typing import Optional, Type, Union

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFrame, QGridLayout, QLabel, QLineEdit, QHBoxLayout, QBoxLayout

from gui_elements.abstracts import WidgetControl
from gui_elements.linked_buttons import LinkedButton, ButtonGroup
from gui_elements.number_line_edit import NumberEntry


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

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value


class CardButton(LinkedButton):
    """Extends on the `LinkedButton` by offering an attribute to refer to the corresponding `CardData`.
    Helps in jumping from a button action to the corresponding card.
    """

    def __init__(self, card: CardData, control_group: ButtonGroup, text: str = ""):
        super().__init__(control_group=control_group, text=text)
        self.card = card


class SquareCard(CardButton):
    default_height = 30
    default_width = 30

    def __init__(self, card: CardData, button_group: ButtonGroup):
        super().__init__(card, button_group, text=card.name)
        self.setFixedSize(self.default_width, self.default_height)
        self.setCheckable(True)
        card.linked_widget = self


class CardContainer(QFrame):
    card_widget_type: Union[Type["SquareCard"], Type["InputCard"]]

    def __init__(self):
        super().__init__()
        self.cards: list[CardData] = list()
        self.button_group = ButtonGroup(allow_shift=False)

    def add_card(self, card: CardData, place=True):
        self.cards.append(card)
        card.container = self
        self.card_widget_type(card, button_group=self.button_group)
        if place:
            self._reorder_cards()
            self._place_cards()

    def remove_card(self, card: CardData, do_place=True):
        card.unlink()
        card.container = None
        self.cards.remove(card)
        if do_place:
            self._place_cards()

    def remove_all(self):
        for card in self.cards:
            self.remove_card(card, do_place=False)
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

    def init_style(self):
        self.setFixedWidth(self.width * SquareCard.default_width)
        self.setMinimumHeight(SquareCard.default_height)

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
    default_width = 150
    default_height = 40

    def __init__(self, card: CardData, button_group: ButtonGroup):
        super().__init__()
        self.card = card
        card.linked_widget = self
        self.button_group = button_group
        self.init_widget()

    def init_content(self):
        self.display = CardButton(self.card, self.button_group)
        self.equals = QLabel()
        self.input = NumberEntry(self.card.get_value, self.card.set_value)

    def init_values(self):
        self.display.setText(self.card.name)
        self.equals.setText("=")

    def init_positions(self):
        self.setLayout(QHBoxLayout())
        self.layout_.addWidget(self.display)
        self.layout_.addWidget(self.equals)
        self.layout_.addWidget(self.input)

    def init_style(self):
        self.layout_.setContentsMargins(3, 1, 3, 1)
        self.setFixedWidth(self.default_width)
        self.setMinimumHeight(self.default_height)
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

    def init_style(self):
        self.setFixedWidth(InputCard.default_width)

    @property
    def layout_(self) -> QGridLayout:
        return self.layout()

    def _place_cards(self):
        while self.layout_.count() != 0:
            self.layout_.takeAt(0)
        for card in self.cards:
            self.layout_.addWidget(card.linked_widget)
