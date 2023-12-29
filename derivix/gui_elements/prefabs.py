"""This module contains slightly modified Qt widgets to more easily fill a defined role."""
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QApplication, QSizePolicy

from data import ToolIcons


class LabelWithLine(QWidget):
    """A label with an added horizontal line.
    Can be used as section header with an indicative, separating line as opposed to just the text.

    Also supports having a symbol added, which will then be shown left to the label.
    """
    def __init__(self, text: str = "", pixmap: QPixmap | None = None):
        super().__init__()
        self.setLayout(QHBoxLayout())
        image = QLabel()
        self.label = QLabel(text)
        if pixmap is not None:
            image.setPixmap(pixmap)
        line = QFrame()
        if pixmap is not None:
            self.layout().addWidget(image)
        self.layout().addWidget(self.label)
        self.layout().addWidget(line)
        image.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        line.setFrameShape(QFrame.Shape.HLine)

        self.setText = self.label.setText
        self.text = self.label.text


if __name__ == '__main__':
    app = QApplication()
    wid = LabelWithLine("Label", pixmap=ToolIcons.var_x.get_pixmap())
    wid.show()
    app.exec()



