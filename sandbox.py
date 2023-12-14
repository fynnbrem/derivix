import sys

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout
from PySide6.QtGui import QColor

from gui_elements.animations import JumpyDots

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = QMainWindow()
    jumpy_dots = JumpyDots(100, 10, QColor(55, 55, 55))
    wid = QWidget()
    layout = QVBoxLayout()
    wid.setLayout(layout)
    layout.addWidget(jumpy_dots)
    win.setCentralWidget(wid)
    win.show()
    sys.exit(app.exec())
