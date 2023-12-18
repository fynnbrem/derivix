from typing import Literal, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QApplication, QVBoxLayout, QWidget


class ButtonGroup:
    """A button group to link multiple `LinkedButton`.
    All clicks on those buttons get delegated to this object to manage which buttons
    should get checked and remain checked, depending on the keyboard modified (ctrl, shift or none).

    The logic applied here closely mimics Windows file explorer:
    - With no modifier:
        The clicked button will be toggled.
        All other buttons will be un-checked.
    - With ctrl:
        The clicked button will be toggled.
        All other buttons keep their respective state.
    - With shift:
        All buttons between the last-clicked button and the clicked button will be checked.
        All other buttons will be un-checked.
        If there is no last-clicked button, the selection will expand from the top instead.

        As this behaviour requires clean indexing of the managed buttons, this modifier can be disabled
        with `allow_shift`.

    That logic is managed by `ask_for_check()`.
    """
    exclusive_groups: list["ButtonGroup"]
    """A list of of `ButtonGroup` which are on the same control level as this one.
    All `ButtonGroup` listed here will become unchecked when any button in this group gets clicked."""

    def __init__(self, allow_shift = True):
        self.buttons: list[LinkedButton] = list()
        self.last_selected: Optional[LinkedButton] = None
        self.allow_shift = allow_shift
        self.exclusive_groups = list()

    def ask_for_check(self, button: "LinkedButton", modifier: None | Literal["ctrl", "shift"]):
        """Should be called after invoking a button.
        Decides the new check-state of this very button and the buttons in the same group.
        Also unchecks any other group listed in `exclusive_groups`.

        For details, refer to the DocString of this Class.

        :param button:
            The button that invoked this method.
        :param modifier:
            The keyboard modifier that was pressed during invocation of the button.
        """
        for group in self.exclusive_groups:
            group.set_all(False)
        if modifier == "shift" and self.allow_shift:
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
        """Adds the `button` to this group and correspondingly assigns the `button.index` and `button.button_group`."""
        button.button_group = self
        button.index = len(self.buttons)
        self.buttons.append(button)

    def set_all(self, state: bool):
        """Sets the checked `state` of all buttons of this group."""
        for button in self.buttons:
            button.setChecked(state)

    def get_by_check_state(self, state=True):
        """Returns all buttons for which the checked-state is `state`.
        `state` is `True` by default, so it returns all checked buttons."""
        return [button for button in self.buttons if button.isChecked() == state]


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
