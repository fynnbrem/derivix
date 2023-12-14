import math
import sys
from typing import Generator

from PySide6.QtWidgets import QApplication, QWidget, QFrame, QMainWindow, QVBoxLayout
from PySide6.QtGui import QPainter, QBrush, Qt, QColor
from PySide6.QtCore import QPropertyAnimation, QPoint, QTimer, QRect


class JumpyDots(QFrame):
    default_spacing = 30
    default_diameter = 20
    default_jump_height = 40

    def __init__(self, count: int = 1, diameter: int = default_diameter, color: QColor = Qt.GlobalColor.black):
        super().__init__()

        self._scale = diameter / self.default_diameter
        self.diameter = int(self.default_diameter * self._scale)
        self.spacing = int(self.default_spacing * self._scale)
        self.jump_height = int(self.default_jump_height * self._scale)

        self._brush = QBrush(color)

        # ↑ A buffer used for extra space for anti-aliasing. Approximately 1 pixel for default settings.
        # Will always be at least 1px.

        self.coords = tuple(
            (c * self.spacing, self.jump_height)
            for c
            in range(count)
        )
        self.coords_loop = jump(self.coords, self.jump_height, 4)

        self.timer = QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start()

        x_size = self.diameter + self.spacing * (count - 1)
        y_size = self.diameter + self.jump_height

        self.setFixedSize(x_size, y_size)

    def update_animation(self):
        self.coords = next(self.coords_loop)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self._brush)
        painter.setPen(Qt.GlobalColor.transparent)
        for x, y in self.coords:
            painter.drawEllipse(
                QRect(x, y, self.diameter, self.diameter)
            )


def jump(start_coords: tuple[tuple[int, int], ...], base_height: int, steepness: int):
    base_coords = list(start_coords)
    offset = 0
    curve = list(hill(60, 1 / 3))
    while True:
        coords = [
            (x, y - int(base_height * curve[(int(index * steepness) - offset) % len(curve)]))
            for index, (x, y)
            in enumerate(base_coords)
        ]  # `offset` must be subtracted so the wave goes from left to right
        offset = (offset + 1) % len(curve)
        yield coords


def hill(step_size: int, flat_share: float) -> Generator[float, None, None]:
    """Generates a curve with values in [0;1].
    The curve starts flat and then has a hill in the shape of sin**2.

    :param step_size:
        Sets the total length of this curve (The length of the resulting generator).
    :param flat_share:
        Sets the share of the `step_size` that is flat. The hill will be stretched accordingly.
    """
    flat_range = int(flat_share * step_size)
    hill_range = step_size - flat_range
    for _ in range(flat_range):
        yield 0
    for index in range(hill_range):
        yield (1 + math.cos(2 * math.pi * (index / hill_range) + math.pi)) / 2


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = QMainWindow()
    jumpy_dots = JumpyDots(3, 10, QColor(55, 55, 55))
    wid = QWidget()
    layout = QVBoxLayout()
    wid.setLayout(layout)
    layout.addWidget(jumpy_dots)
    win.setCentralWidget(wid)
    win.show()
    sys.exit(app.exec())
