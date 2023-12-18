from typing import Literal, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QApplication, QVBoxLayout, QWidget


class ButtonGroup:
    def __init__(self):
        self.buttons: list[LinkedButton] = list()
        self.last_selected: Optional[LinkedButton] = None

    def ask_for_check(self, button: "LinkedButton", modifier: None | Literal["ctrl", "shift"]):
        if modifier == "shift":
            if self.last_selected is not None:
                select_range = (button.index, self.last_selected.index)
            else:
                # ↓ When there is no `last_selected` yet, expand from the top.
                select_range = (0, button.index)

            select_range = range(min(select_range), max(select_range) + 1)
            for index, linked_button in enumerate(self.buttons):
                if index in select_range:
                    linked_button.setChecked(True)
                else:
                    linked_button.setChecked(False)

        elif modifier == "ctrl":
            button.setChecked(not button.isChecked())
        else:
            for index, linked_button in enumerate(self.buttons):
                if index == button.index:
                    linked_button.setChecked(not linked_button.isChecked())
                else:
                    linked_button.setChecked(False)

        if modifier != "shift":
            # ↑ shift-clicking retains the former `last_selected` in case the user wants to change the expanded area.
            self.last_selected = button

    def add(self, button: "LinkedButton"):
        button.button_group = self
        button.index = len(self.buttons)
        self.buttons.append(button)


class LinkedButton(QPushButton):
    index: int
    button_group: "ButtonGroup"

    def __init__(self, control_group: ButtonGroup, text: str = ""):
        super().__init__(text)
        self.setCheckable(True)
        self.clicked.connect(self.delegate)
        control_group.add(self)

    def delegate(self):
        # ↓ Due to this method only being linked to the click event
        # and not actually overriding it, the button will be checked in any case.
        # So before delegating, its state has to be reverted.
        # This method is chosen over using `mousePressEvent` as
        # to prevent having to define a custom implementation of a mouse "click" logic.
        self.setChecked(not self.isChecked())
        modifiers = QApplication.keyboardModifiers()

        # region: Determine the keyboard modifier.
        # When both, ctrl and shift, are pressed, shift takes precedence as it encompasses the behaviour of ctrl.
        ctrl_pressed = modifiers & Qt.KeyboardModifier.ControlModifier
        shift_pressed = modifiers & Qt.KeyboardModifier.ShiftModifier

        if shift_pressed:
            modifier = "shift"
        elif ctrl_pressed:
            modifier = "ctrl"
        else:
            modifier = None
        # endregion

        self.button_group.ask_for_check(self, modifier=modifier)
        ...


if __name__ == '__main__':
    app = QApplication()
    wid = QWidget()
    layout = QVBoxLayout()
    wid.setLayout(layout)
    t_button_group = ButtonGroup()
    layout.addWidget(LinkedButton(t_button_group, "A"))
    layout.addWidget(LinkedButton(t_button_group, "B"))
    layout.addWidget(LinkedButton(t_button_group, "C"))
    layout.addWidget(LinkedButton(t_button_group, "D"))

    wid.show()
    app.exec()
