"""This module contains the `NumberEntry` used to manage and validate numbers in a text entry.
This module does not contain the corresponding formatting logic itself."""

from PySide6 import QtGui
from PySide6.QtWidgets import QLineEdit, QApplication, QWidget, QVBoxLayout

from res.strings import invalid_number_format_error
from utils.number_formatting import congregate_zeroes, number_to_scientific


class NumberEntry(QLineEdit):
    """A ´QLineEdit´ dedicated to working with numbers.
    The number will have different, user-friendly representations during editing and pure display, while the actual
    number will also be stored in the backend.
    Also handles validation of the input text.
    """

    number: float | int | None
    """The represented number. Always contains the original value, 
    which might not be shown to its full extent by `display_mode()`"""
    _valid: bool

    def __init__(self, number: float | int | None = None):
        super().__init__()
        self.number = number
        self.textEdited.connect(self.update_number)
        self._valid = True

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        """Switch to edit mode when gaining focus."""
        super().focusInEvent(event)
        self.edit_mode()

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        """Switch to display mode when losing focus."""
        super().focusOutEvent(event)
        self.display_mode()

    @property
    def valid(self):
        """Whether the current input is valid."""
        return self._valid

    @valid.setter
    def valid(self, valid):
        """Sets valid and invokes the corresponding style changes if the value changes."""
        if self._valid != valid:
            # ↑ Only invoke any action if the valid-state actually changed.
            self._valid = valid
            if not valid:
                self.setStyleSheet("QLineEdit {border: 1px solid red}")
                self.setToolTip(invalid_number_format_error)
            else:
                self.setStyleSheet("")
                self.setToolTip("")

    def update_number(self):
        """Update the `self.number` by parsing the input text.
        Also determines `self.valid`.

        `self.number` will be `None` if the input is not valid or the input is empty.
        """
        valid = True

        if self.text().strip() == "":
            self.number = None
        else:
            text = self.text().replace(",", "_")
            # ↑ Replace group-separating commas with underscores so Python can evaluate them normally.
            try:
                self.number = int(text)
            except ValueError:
                try:
                    self.number = float(text)
                except ValueError:
                    self.number = None
                    valid = False
        self.valid = valid

    def edit_mode(self):
        """Change to edit mode. This will show the full number and will only congregate trailing zeroes.
        Does nothing while the input is not valid.
        """
        if not self.valid:
            return
        if self.number is not None:
            f_number = congregate_zeroes(self.number)
            self.setText(f_number)
        else:
            self.setText("")

    def display_mode(self):
        """Change to display mode. This will shorten the shown number with the scientific notation.
        Does nothing while the input is not valid.
        """
        if not self.valid:
            return
        if self.number is not None:
            f_number = number_to_scientific(self.number)
            self.setText(f_number)
        else:
            self.setText("")


if __name__ == '__main__':
    app = QApplication()
    win = QWidget()
    layout = QVBoxLayout()
    win.setLayout(layout)
    layout.addWidget(NumberEntry())
    layout.addWidget(NumberEntry())
    win.show()
    app.exec()
